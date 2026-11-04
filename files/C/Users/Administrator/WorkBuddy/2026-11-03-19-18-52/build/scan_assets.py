# -*- coding: utf-8 -*-
"""扫描 C/D/E 三盘，生成站内档案库所需的本地资产清单。"""
import os, json, time

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets.json")

ROOTS = ["C:/", "D:/", "E:/"]
SKIP_DIRS = {
    "windows", "program files", "program files (x86)", "programdata",
    "$recycle.bin", "system volume information", "appdata", "perflogs",
    "recovery", "boot", "efi", "system32", "syswow64", "winsxs",
    "node_modules", ".git", "__pycache__", ".cache", "temp", "tmp",
    "microsoft", "installer", "drivers", "softwaredistribution", "noi-2027",
}
CODE = {".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".hxx", ".pas", ".py", ".java"}
DOC = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".xlsm", ".md", ".markdown",
       ".txt", ".pptx", ".ppt", ".csv", ".tsv", ".ipynb"}
PKG = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}
EXTS = CODE | DOC | PKG


def kind(e):
    if e in CODE:
        return "code"
    if e in PKG:
        return "pkg"
    return "doc"


def main():
    files = []
    t0 = time.time()
    for root in ROOTS:
        if not os.path.isdir(root):
            print("跳过（不存在）", root, flush=True)
            continue
        n0 = len(files)
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fn in filenames:
                e = os.path.splitext(fn)[1].lower()
                if e not in EXTS:
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                rel = p.replace("\\", "/")
                files.append({
                    "p": rel,
                    "s": st.st_size,
                    "m": int(st.st_mtime),
                    "e": e.lstrip("."),
                    "k": kind(e),
                    "d": rel[0].upper() if len(rel) > 1 and rel[1] == ":" else "?",
                })
        print("%s -> %d 个" % (root, len(files) - n0), flush=True)

    files.sort(key=lambda x: x["p"])
    stats = {}
    for f in files:
        stats[f["k"]] = stats.get(f["k"], 0) + 1
    total = sum(f["s"] for f in files)
    with open(OUT, "w", encoding="utf-8") as fp:
        json.dump({"generated": int(time.time()), "count": len(files),
                   "bytes": total, "stats": stats, "files": files},
                  fp, ensure_ascii=False)
    print("合计 %d 个文件, %.1f MB, 耗时 %.1fs" %
          (len(files), total / 1048576, time.time() - t0), flush=True)
    print("分类", stats, flush=True)
    print("输出", OUT, flush=True)


if __name__ == "__main__":
    main()
