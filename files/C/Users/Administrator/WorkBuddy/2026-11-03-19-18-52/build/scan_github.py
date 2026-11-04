# -*- coding: utf-8 -*-
"""抓取用户 GitHub 全部仓库的递归文件清单。"""
import subprocess, json, os

OWNER = "Peter1384345"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github.json")


def run(args):
    r = subprocess.run(args, capture_output=True, text=True,
                        encoding="utf-8", timeout=180)
    if r.returncode != 0:
        raise RuntimeError(" ".join(args[:3]) + " -> " + r.stderr.strip()[:200])
    return r.stdout.strip()


def main():
    repos = json.loads(run(["gh", "repo", "list", OWNER, "--limit", "200",
                            "--json", "name,isPrivate,url,defaultBranchRef,description"]))
    print("仓库数", len(repos), flush=True)
    result = []
    for rp in repos:
        name = rp["name"]
        branch = (rp.get("defaultBranchRef") or {}).get("name") or "main"
        item = {"name": name, "private": rp.get("isPrivate"),
                "url": rp.get("url"), "description": rp.get("description") or "",
                "branch": branch, "files": [], "error": None}
        try:
            t = json.loads(run(["gh", "api",
                               "repos/%s/%s/git/trees/%s?recursive=1" %
                               (OWNER, name, branch)]))
            for e in t.get("tree", []):
                if e.get("type") != "blob":
                    continue
                item["files"].append({"p": e["path"], "s": e.get("size", 0),
                                     "sha": e["sha"][:8]})
        except Exception as ex:
            item["error"] = str(ex)[:200]
        result.append(item)
        print("  %-38s %5d 文件 %s" %
              (name, len(item["files"]), item["error"] or ""), flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"owner": OWNER, "count": len(result),
                   "total_files": sum(len(i["files"]) for i in result),
                   "repos": result}, f, ensure_ascii=False)
    print("合计 %d 仓库 / %d 文件 -> %s" %
          (len(result), sum(len(i["files"]) for i in result), OUT), flush=True)


if __name__ == "__main__":
    main()
