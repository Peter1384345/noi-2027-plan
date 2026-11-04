# -*- coding: utf-8 -*-
"""
P2/P3/P4: 候选枚举 + 证据打分 + 风险分级。全程只读。
输出: plan.json (机器可读) / candidates_debug.txt
"""
import json, os, re, time, winreg, pathlib, datetime, collections

BASE = pathlib.Path(__file__).parent
HOME = pathlib.Path(os.environ["USERPROFILE"])
LA = pathlib.Path(os.environ["LOCALAPPDATA"])
RA = pathlib.Path(os.environ["APPDATA"])
PD = pathlib.Path(os.environ["PROGRAMDATA"])
PF = pathlib.Path(os.environ["PROGRAMFILES"])
PF86 = pathlib.Path(os.environ["PROGRAMFILES(X86)"])

apps = json.loads((BASE / "inventory.json").read_text(encoding="utf-8"))
facts = json.loads((BASE / "raw_facts.json").read_text(encoding="utf-8"))
NOW = time.time()

# ---------------------------------------------------------------- 工具
CJK = re.compile(r'[\u4e00-\u9fff]+')
ASCII_W = re.compile(r'[a-z0-9]+')

def words(s):
    s = (s or "").lower()
    out = set(ASCII_W.findall(s))
    out |= set(CJK.findall(s))
    return {w for w in out if len(w) >= 2}

def norm(s):
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '', (s or "").lower())

def path_exists(p):
    try:
        return os.path.exists(p)
    except Exception:
        return False

def dir_size(p, budget=12.0, cap=400000):
    """返回 (bytes, files, truncated)。跳过 reparse point。"""
    total = files = 0
    t0 = time.time()
    stack = [str(p)]
    seen = 0
    while stack:
        if time.time() - t0 > budget or seen > cap:
            return total, files, True
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for e in it:
                    seen += 1
                    if seen % 2000 == 0 and time.time() - t0 > budget:
                        return total, files, True
                    try:
                        if e.is_dir(follow_symlinks=False):
                            if e.is_junction() if hasattr(e, "is_junction") else False:
                                continue
                            stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            total += e.stat(follow_symlinks=False).st_size
                            files += 1
                    except OSError:
                        continue
        except OSError:
            continue
    return total, files, False

def mtime_of(p):
    try:
        return os.stat(p, follow_symlinks=False).st_mtime
    except Exception:
        return None

def human(n):
    if n is None:
        return "?"
    for u, d in (("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)):
        if n >= d:
            return f"{n/d:.1f} {u}"
    return f"{n} B"

# ---------------------------------------------------------------- 在装应用签名索引
# 厂商词（publisher 里的组织名）——用于 L2 软证据，不作为保留的硬依据
PUB_STOP = {"inc", "ltd", "llc", "co", "corp", "corporation", "technologies", "technology",
            "software", "systems", "group", "company", "limited", "gmbh", "the",
            "co.,", "shenzhen", "beijing", "shanghai", "深圳", "北京", "上海", "有限公司",
            "科技", "技术", "公司", "inc.", "llc.", "pte", "pte.", "s", "a"}

app_sig = []   # [{name, norm_name, tokens, dirnames, pubs, version}]
for a in apps:
    dirnames = set()
    for k in ("install_location",):
        v = (a.get(k) or "").strip().strip('"')
        if v:
            dirnames.add(norm(os.path.basename(v.rstrip("\\/"))))
    for k in ("icon_exe",):
        v = a.get(k) or ""
        if v:
            dirnames.add(norm(os.path.basename(os.path.dirname(v))))
    us = a.get("uninstall_string") or ""
    m = re.search(r'"([^"]+\.exe)"|([A-Za-z]:\\[^ ]+\.exe)', us, re.I)
    if m:
        p = m.group(1) or m.group(2)
        dirnames.add(norm(os.path.basename(os.path.dirname(p))))
    app_sig.append({
        "name": a["name"],
        "norm_name": a["normalized"],
        "tokens": words(a["name"]) | words(a.get("publisher")),
        "pub_tokens": words(a.get("publisher")) - PUB_STOP,
        "dirnames": {d for d in dirnames if d},
        "publisher": a.get("publisher") or "",
        "loc": a.get("install_location") or "",
        "icon": a.get("icon_exe") or "",
    })

# 伴生组件表（L5）：父产品的子组件/更新器/运行时目录名
COMPANION = {
    "quarkclouddriveupdater": "夸克网盘", "quark": "夸克网盘",
    "keystone": "Google Chrome", "googleupdate": "Google Chrome",
    "crashpad": None,  # 多方共用，无明确归属 -> 不判
    "squirrel": None, "shipit": None,
    "bonjour": "Bonjour",
    "vc_redist": "Microsoft Visual C++", "vcredist": "Microsoft Visual C++",
    "dotnet": "Microsoft .NET", "nuget": "Microsoft Visual Studio",
}

# ---------------------------------------------------------------- 现存进程/服务/任务索引（保留证据 L6）
proc_paths = [p["path"] for p in facts["processes"] if p.get("path")]

def svc_exe(p):
    if not p:
        return None
    p = p.strip()
    m = re.match(r'^"([^"]+)"', p)
    s = m.group(1) if m else p.split(" ")[0]
    return os.path.expandvars(s)

svc_exes = []
for s in facts["services"]:
    e = svc_exe(s.get("path"))
    if e:
        svc_exes.append({"name": s["name"], "display": s.get("display"), "exe": e,
                         "state": s.get("state"), "start_mode": s.get("start_mode"),
                         "exists": path_exists(e)})

task_rows = []
for t in facts["tasks"]:
    for ex in (t.get("Execute") or "").split("|"):
        if ex.strip():
            task_rows.append({"task": (t.get("TaskPath") or "") + (t.get("TaskName") or ""),
                              "exe": os.path.expandvars(ex.strip()),
                              "exists": path_exists(os.path.expandvars(ex.strip()))})

startup_rows = []
for scope, key in (("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                   ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                   ("HKLM32", r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run")):
    try:
        hive = winreg.HKEY_CURRENT_USER if scope == "HKCU" else winreg.HKEY_LOCAL_MACHINE
        k = winreg.OpenKey(hive, key, 0, winreg.KEY_READ)
        for i in range(winreg.QueryInfoKey(k)[1]):
            try:
                n, v, _ = winreg.EnumValue(k, i)
            except OSError:
                continue
            p = svc_exe(str(v))
            startup_rows.append({"scope": scope, "name": n, "cmd": str(v),
                                 "exe": p, "exists": path_exists(p) if p else None})
        k.Close()
    except OSError:
        pass

# ---------------------------------------------------------------- 目录候选枚举
R0_NAMES = {
    "microsoft", "windows", "windowsapps", "windows defender", "windows nt", "windows mail",
    "windows photo viewer", "windows sidebar", "windows powershell", "common files",
    "internet explorer", "modifiablewindowsapps", "uninstall information", "reference assemblies",
    "msbuild", "dotnet", "packages", "temp", "tmp", "desktop.ini", "$recycle.bin",
    "system volume information", "perflogs", "recovery", "programdata", "users", "windowsapps.tmp",
    "microsoft update health tools", "microsoft gameinput", "hyper-v", "wsl",
    "windows defender advanced threat protection", "ruxim", "package management",
    "system32", "syswow64", "winsxs", "drivers", "config", "microsoft.net",
    "application data", "history", "temporary internet files", "programs",
}
R0_PATH_PARTS = {"\\windows", "\\windowsapps", "\\common files\\microsoft",
                 "\\programdata\\microsoft", "\\appdata\\local\\microsoft",
                 "\\appdata\\roaming\\microsoft", "\\appdata\\local\\packages",
                 "\\appdata\\roaming\\tencent\\wechat", "\\temp"}

DIR_ROOTS = [
    ("Program Files", PF, 1), ("Program Files (x86)", PF86, 1),
    ("ProgramData", PD, 1),
    ("AppData\\Local", LA, 1), ("AppData\\Roaming", RA, 1),
    ("AppData\\Local\\Programs", LA / "Programs", 1),
    ("UserProfile(root)", HOME, 1),
]
EXTRA_DRIVE_ROOTS = [pathlib.Path("D:\\"), pathlib.Path("E:\\")]

def is_r0(name, path):
    low = name.lower()
    if low in R0_NAMES:
        return True
    pl = str(path).lower()
    return any(seg in pl for seg in R0_PATH_PARTS)

cands = []

def make_dir_cand(root_label, p):
    name = p.name
    if is_r0(name, p):
        return None
    nm = norm(name)
    if not nm:
        return None
    ev = []
    matched = None
    # L1 精确/前缀命中在装应用
    for s in app_sig:
        if nm and (nm == s["norm_name"] or nm in s["dirnames"]):
            matched = s; ev.append({"code": "L1", "w": 100,
                                    "note": f"目录名与在装应用「{s['name']}」标识一致"}); break
        for d in s["dirnames"]:
            if d and len(d) >= 4 and (nm.startswith(d) or d.startswith(nm)):
                matched = s; ev.append({"code": "L1", "w": 95,
                                        "note": f"目录名与在装应用「{s['name']}」安装目录同族"}); break
        if matched:
            break
    if not matched and nm in COMPANION and COMPANION[nm]:
        target = COMPANION[nm]
        t = next((s for s in app_sig if norm(target) in s["norm_name"] or target.lower() in s["name"].lower()), None)
        if t:
            matched = t; ev.append({"code": "L5", "w": 80, "note": f"伴生组件，归属在装应用「{t['name']}」"})
    # L6 被运行中进程加载
    if not matched:
        for pp in proc_paths:
            try:
                if str(p).lower() in pp.lower():
                    matched = {"name": os.path.basename(pp)}
                    ev.append({"code": "L6", "w": 100, "note": f"被运行中进程加载: {pp}"})
                    break
            except Exception:
                pass
    # L2 厂商家族（软证据，45）
    if not matched:
        toks = words(name)
        for s in app_sig:
            inter = toks & s["tokens"]
            inter = {w for w in inter if len(w) >= 4 and w not in ("update", "helper", "setup", "data", "cache")}
            if inter:
                ev.append({"code": "L2", "w": 45,
                           "note": f"与在装应用「{s['name']}」共享词 {sorted(inter)[:3]}（同厂商/同族，非同一产品）"})
                break
    size, files, trunc = dir_size(p)
    mt = mtime_of(p)
    old_days = int((NOW - mt) / 86400) if mt else None
    # 孤儿证据
    if not matched:
        has_exe = False
        has_unins = False
        try:
            for e in os.scandir(p):
                if e.is_file() and e.name.lower().endswith(".exe"):
                    has_exe = True
                    if re.match(r'(unins|uninstall|uninst)', e.name.lower()):
                        has_unins = True
        except OSError:
            pass
        if files > 0:
            ev.append({"code": "O1", "w": 70 if has_exe else 55,
                       "note": "目录内存在程序文件，但系统中查无对应的已安装应用" if has_exe
                               else "目录内无程序主体，仅存数据/缓存，且系统中查无对应应用"})
        if files == 0:
            ev.append({"code": "O4", "w": 55, "note": "空壳目录，无任何文件"})
        if old_days is not None and old_days > 365:
            ev.append({"code": "O6", "w": 20, "note": f"最后修改距今 {old_days} 天"})
        # 是否被 PATH/环境变量/服务/任务 引用（弱引用证据 -> 不建议删）
        refs = []
        for scope in ("user", "machine"):
            for k, v in facts["env"].get(scope, {}).items():
                if str(p).lower() in v.lower():
                    refs.append(f"{scope} 环境变量 {k}")
        if refs:
            ev.append({"code": "L4", "w": 90, "note": "被引用: " + "; ".join(refs[:3])})
            matched = {"name": "(被环境变量引用)"}
    orphan_w = sum(e["w"] for e in ev if e["code"].startswith("O"))
    retain_w = max([e["w"] for e in ev if e["code"].startswith("L")] or [0])
    if matched:
        conclusion = "建议保留"
    elif orphan_w >= 60:
        conclusion = "确证残留"
    elif orphan_w >= 30:
        conclusion = "疑似残留"
    else:
        conclusion = "证据不足"
    return {"kind": "dir", "group": root_label, "name": name, "path": str(p),
            "size": size, "size_h": human(size), "files": files, "truncated": trunc,
            "mtime": datetime.datetime.fromtimestamp(mt).strftime("%Y-%m-%d") if mt else None,
            "age_days": old_days, "evidence": ev, "orphan_w": orphan_w, "retain_w": retain_w,
            "matched": matched["name"] if matched else None, "conclusion": conclusion}

for label, root, depth in DIR_ROOTS:
    try:
        for e in os.scandir(root):
            if not e.is_dir(follow_symlinks=False):
                continue
            c = make_dir_cand(label, pathlib.Path(e.path))
            if c:
                cands.append(c)
    except OSError as ex:
        print("skip root", root, ex)

for drv in EXTRA_DRIVE_ROOTS:
    if not drv.exists():
        continue
    try:
        for e in os.scandir(drv):
            if not e.is_dir(follow_symlinks=False):
                continue
            c = make_dir_cand(f"Drive {drv.drive}", pathlib.Path(e.path))
            if c:
                cands.append(c)
    except OSError:
        pass

# ---------------------------------------------------------------- 注册表候选
REG_ROOTS = [
    ("HKCU Software", winreg.HKEY_CURRENT_USER, r"SOFTWARE", winreg.KEY_WOW64_64KEY),
    ("HKLM Software", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE", winreg.KEY_WOW64_64KEY),
    ("HKLM Software(WOW64)", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node", winreg.KEY_WOW64_64KEY),
]
REG_R0 = {"microsoft", "windows", "classes", "clients", "policies", "registeredapplications",
          "google", "intel", "wow6432node", "mozilla", "ashampoo", "nvidia corporation",
          "odbc", "wow6432node", "system", "apple computer, inc.", "adobe", "realtek",
          "squirrelmachineinstalls"}

reg_cands = []
for label, hive, root, view in REG_ROOTS:
    try:
        k = winreg.OpenKey(hive, root, 0, winreg.KEY_READ | view)
    except OSError:
        continue
    n = winreg.QueryInfoKey(k)[0]
    for i in range(n):
        try:
            sub = winreg.EnumKey(k, i)
        except OSError:
            continue
        low = sub.lower()
        if low in REG_R0 or low.startswith("microsoft") or low.startswith("windows"):
            continue
        nm = norm(sub)
        if not nm:
            continue
        ev, matched = [], None
        for s in app_sig:
            if nm == s["norm_name"] or nm in s["dirnames"]:
                matched = s; ev.append({"code": "L1", "w": 100, "note": f"键名与在装应用「{s['name']}」一致"}); break
            for d in s["dirnames"]:
                if d and len(d) >= 4 and (nm.startswith(d) or d.startswith(nm)):
                    matched = s; ev.append({"code": "L1", "w": 90, "note": f"键名与在装应用「{s['name']}」安装目录同族"}); break
            if matched:
                break
        if not matched:
            toks = words(sub)
            for s in app_sig:
                inter = {w for w in (toks & s["tokens"]) if len(w) >= 4 and w not in ("update", "helper", "setup")}
                if inter:
                    ev.append({"code": "L2", "w": 45, "note": f"与在装应用「{s['name']}」共享词 {sorted(inter)[:3]}"})
                    break
            if not ev:
                ev.append({"code": "O1", "w": 70, "note": "注册表存在该厂商/产品键，但查无对应已安装应用"})
                ev.append({"code": "O7", "w": 15, "note": "未被任何在装应用配置引用（弱证据）"})
        orphan_w = sum(e["w"] for e in ev if e["code"].startswith("O"))
        retain_w = max([e["w"] for e in ev if e["code"].startswith("L")] or [0])
        conclusion = "建议保留" if matched else ("确证残留" if orphan_w >= 60 else "疑似残留")
        reg_cands.append({"kind": "registry", "group": label, "name": sub,
                          "path": ("HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM") + "\\" + root + "\\" + sub,
                          "evidence": ev, "orphan_w": orphan_w, "retain_w": retain_w,
                          "matched": matched["name"] if matched else None, "conclusion": conclusion})
    k.Close()

# ---------------------------------------------------------------- 服务 / 计划任务 / 启动项 / 快捷方式 / PATH / 环境变量 / 卸载收据
orphan_services = [s for s in svc_exes if not s["exists"]]
orphan_tasks = [t for t in task_rows if not t["exists"]]
orphan_startup = [s for s in startup_rows if s["exists"] is False]
shortcuts = facts["shortcuts"]
orphan_lnk = [s for s in shortcuts if s.get("Target") and not path_exists(s["Target"])]

path_entries = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path":
            for seg in v.split(";"):
                seg = seg.strip()
                if seg and "%" not in seg:
                    path_entries.append({"scope": scope, "entry": seg, "exists": path_exists(seg)})
orphan_path = [p for p in path_entries if not p["exists"]]

env_orphan = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path":
            continue
        if re.search(r'[A-Za-z]:\\', v):
            for m in re.findall(r'[A-Za-z]:\\[^;]*', v):
                if not path_exists(m):
                    env_orphan.append({"scope": scope, "name": k, "value": v, "missing": m})

# 卸载收据：UninstallString 目标不存在 => 无法正常卸载
broken_receipts = []
for a in apps:
    us = a.get("uninstall_string") or ""
    if not us:
        continue
    p = svc_exe(us)
    if p and not path_exists(p):
        broken_receipts.append({"name": a["name"], "publisher": a.get("publisher"),
                                "uninstall_string": us, "missing_exe": p,
                                "install_location": a.get("install_location"),
                                "loc_exists": a.get("loc_exists"),
                                "registry_key": a.get("registry_key")})

out = {"dirs": cands, "registry": reg_cands, "orphan_services": orphan_services,
       "orphan_tasks": orphan_tasks, "orphan_startup": orphan_startup,
       "orphan_shortcuts": orphan_lnk, "all_shortcuts": shortcuts,
       "orphan_path": orphan_path, "path_entries": path_entries,
       "env_orphan": env_orphan, "broken_receipts": broken_receipts,
       "svc_exes": svc_exes, "startup_all": startup_rows,
       "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
(BASE / "plan.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"dirs={len(cands)}  reg={len(reg_cands)}  orphan_svc={len(orphan_services)} "
      f"orphan_task={len(orphan_tasks)}  orphan_startup={len(orphan_startup)} "
      f"orphan_lnk={len(orphan_lnk)}  orphan_path={len(orphan_path)} "
      f"env_orphan={len(env_orphan)}  broken_receipts={len(broken_receipts)}")
print("\n-- 目录非保留项 --")
for c in sorted(cands, key=lambda x: -(x["size"] or 0)):
    if c["conclusion"] != "建议保留":
        print(f'  [{c["conclusion"]}] {c["group"]:22s} {c["name"][:36]:38s} {c["size_h"]:>9s} '
              f'{c["mtime"] or "?"}  w={c["orphan_w"]:3d} files={c["files"]}')
print("\n-- 注册表非保留项 --")
for c in reg_cands:
    if c["conclusion"] != "建议保留":
        print(f'  [{c["conclusion"]}] {c["path"]}  w={c["orphan_w"]}')
