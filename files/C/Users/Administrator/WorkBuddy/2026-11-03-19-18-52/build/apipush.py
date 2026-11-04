# -*- coding: utf-8 -*-
"""用 GitHub Git Data API 推送提交（绕过本机代理对 git 协议的阻断）
   请求体通过 --input 文件传递，避免 Windows 命令行长度限制。"""
import base64, json, subprocess, os, tempfile

REPO = "Peter1384345/noi-2027-plan"
ROOT = r"C:\Users\Administrator\WorkBuddy\2026-11-03-19-18-52\noi-2027"

def api(endpoint, body, method="POST", jq=None):
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(body, f, ensure_ascii=False)
        cmd = ["gh", "api", endpoint, "-X", method, "--input", tmp]
        if jq: cmd += ["--jq", jq]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
        if r.returncode != 0:
            raise RuntimeError("gh api %s 失败: %s" % (endpoint, r.stderr[:400]))
        return r.stdout.strip()
    finally:
        try: os.unlink(tmp)
        except OSError: pass

def main():
    head = api("repos/%s/commits/main" % REPO, {}, method="GET", jq=".sha")
    tree = api("repos/%s/commits/main" % REPO, {}, method="GET", jq=".commit.tree.sha")
    print("基线 commit", head[:7], "tree", tree[:7], flush=True)

    files = subprocess.run(["git", "diff", "--name-only", "51036ec", "HEAD"],
                           capture_output=True, text=True, cwd=ROOT).stdout.split()
    files = [f for f in files if os.path.isfile(os.path.join(ROOT, f.replace("/", os.sep)))]
    print("待上传文件", len(files), flush=True)

    entries = []
    for i, f in enumerate(files):
        p = os.path.join(ROOT, f.replace("/", os.sep))
        with open(p, "rb") as fp:
            b64 = base64.b64encode(fp.read()).decode()
        sha = api("repos/%s/git/blobs" % REPO,
                  {"content": b64, "encoding": "base64"}, jq=".sha")
        entries.append({"path": f, "mode": "100644", "type": "blob", "sha": sha})
        print("  blob %2d/%d %s -> %s" % (i + 1, len(files), f, sha[:7]), flush=True)

    tree = api("repos/%s/git/trees" % REPO, {"base_tree": tree, "tree": entries}, jq=".sha")
    print("tree", tree[:7], flush=True)

    msg = subprocess.run(["git", "log", "-1", "--pretty=%s"], capture_output=True,
                         text=True, cwd=ROOT).stdout.strip()
    commit = api("repos/%s/git/commits" % REPO,
                 {"message": msg, "tree": tree, "parents": [head]}, jq=".sha")
    print("commit", commit[:7], flush=True)

    api("repos/%s/git/refs/heads/main" % REPO,
        {"sha": commit, "force": False}, method="PATCH", jq=".object.sha")
    print("已更新 main ->", commit[:7], flush=True)

if __name__ == "__main__":
    main()
