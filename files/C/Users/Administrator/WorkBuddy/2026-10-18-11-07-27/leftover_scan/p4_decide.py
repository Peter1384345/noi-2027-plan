# -*- coding: utf-8 -*-
"""
v3 判定核心：以「路径归属」为第一证据。
  归属来源: 卸载收据路径 / 图标路径 / 快捷方式目标 / 运行中进程 / 服务 ImagePath / 计划任务动作
  任一无主路径落在某目录内 => 该目录属于在装应用 => 保留，绝不建议删除。
  同时引入"近期活跃"闸门：近 30 天有改动的无主目录不进候选（那是活跃工具数据，不是残留）。
全程只读。
"""
import json, os, re, time, winreg, pathlib, datetime

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

CJK = re.compile(r'[\u4e00-\u9fff]+'); ASCII_W = re.compile(r'[a-z0-9]+')
def words(s):
    s = (s or "").lower()
    return {w for w in (ASCII_W.findall(s) + CJK.findall(s)) if len(w) >= 2}
def norm(s): return re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '', (s or "").lower())
def exists(p):
    try: return os.path.exists(p)
    except Exception: return False
def human(n):
    if n is None: return "?"
    for u, d in (("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)):
        if n >= d: return f"{n/d:.1f} {u}"
    return f"{n} B"

def cmd_exe(s):
    """从命令行取 exe 路径（保留中文，展开环境变量）"""
    if not s: return None
    s = str(s).strip()
    m = re.match(r'^"([^"]+)"', s)
    cand = m.group(1) if m else s.split(" ")[0]
    cand = os.path.expandvars(cand)
    if cand.lower().endswith('.exe') or re.match(r'^[A-Za-z]:\\', cand):
        return cand
    return None

def is_absolute(p):
    return bool(p) and (re.match(r'^[A-Za-z]:\\', p) or p.startswith("\\\\"))

def dir_size(p, budget=8.0, cap=300000):
    total = files = 0; t0 = time.time(); stack = [str(p)]; seen = 0
    while stack:
        if time.time() - t0 > budget or seen > cap: return total, files, True
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for e in it:
                    seen += 1
                    if seen % 3000 == 0 and time.time() - t0 > budget: return total, files, True
                    try:
                        if e.is_dir(follow_symlinks=False): stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            total += e.stat(follow_symlinks=False).st_size; files += 1
                    except OSError: continue
        except OSError: continue
    return total, files, False

def probe(p, limit=10):
    exes, dlls, unins, subs = [], 0, [], []
    try:
        with os.scandir(p) as it:
            for e in it:
                if len(subs) + len(exes) >= limit * 2: break
                try:
                    if e.is_dir(follow_symlinks=False):
                        if len(subs) < limit: subs.append(e.name)
                    else:
                        ln = e.name.lower()
                        if ln.endswith(".exe"):
                            if len(exes) < limit: exes.append(e.name)
                            if re.match(r'(unins|uninstall|setup|installer|update)', ln): unins.append(e.name)
                        elif ln.endswith(".dll"): dlls += 1
                except OSError: continue
    except OSError: pass
    return {"exes": exes, "exe_n": len(exes), "dll_n": dlls, "uninstallers": unins[:3], "dirs": subs}

# ---------------- 归属证据池
ALIAS = {
    "微信": ["wechat", "weixin"], "wechat": ["wechat", "weixin"], "weixin": ["weixin", "wechat"],
    "wps": ["kingsoft", "wps", "ksolaunch"], "kingsoft": ["wps", "kingsoft"],
    "qq": ["tencent", "qq"], "抖音": ["douyin", "aweme", "bytedance"],
    "剪映": ["jianying", "capcut", "lv", "vedetector"], "百度网盘": ["baidu", "netdisk", "yunguanjia"],
    "夸克网盘": ["quark"], "豆包": ["doubao"], "豆包工作": ["doubao", "doubaowork"],
    "tabbit浏览器": ["tabbit"], "trae cn": ["trae"], "trae work cn": ["trae"],
    "workbuddy": ["workbuddy", "genieworkbuddy", "codebuddy"], "codebuddy": ["codebuddy", "workbuddy"],
    "deepseek harness": ["deepseek", "dsh"], "嘉立创eda": ["lceda", "easyeda"],
    "嘉立创eda(专业版)": ["lceda"], "anaconda": ["anaconda", "conda"], "python": ["python"],
    "node.js": ["nodejs"], "arduino ide": ["arduino"], "vlc": ["videolan", "vlc"],
    "wondershare": ["wondershare", "drfone", "imobie"], "dr.fone": ["wondershare", "drfone"],
    "avast": ["avast"], "lenovo": ["lenovo"], "华为": ["huawei"], "deveco": ["deveco", "huawei"],
    "codearts": ["codearts", "huawei"], "bonjour": ["bonjour", "apple"], "apple": ["apple", "bonjour"],
    "火绒": ["huorong"], "雷神": ["leigod"], "watt toolkit": ["watt", "steam++"],
    "7-zip": ["7-zip", "7zip"], "git": ["git"], "github cli": ["github"],
    "vmware": ["vmware"], "mumu": ["mumu", "netease"], "联想": ["lenovo"],
    "adobe": ["adobe"], "intel": ["intel"], "google": ["google", "chrome"],
    "obsidian": ["obsidian"], "libreoffice": ["libreoffice"], "rufus": ["rufus"],
    "bambu studio": ["bambu"], "mixly": ["mixly"], "dev-c++": ["devcpp", "dev-c++", "redpanda"],
    "geogebra": ["geogebra"], "canmv": ["canmv"], "marvis": ["marvis"],
    "图吧工具箱": ["tuba"], "微信输入法": ["wetype"],
}
GENERIC = {"desktop","runtime","windows","microsoft","browser","client","service","services",
           "helper","update","updater","setup","installer","version","tools","tool","shell","agent",
           "app","apps","core","standard","professional","edition","x64","x86","sdk","studio",
           "library","framework","driver","package","manager","monitor","plugin","extension",
           "module","server","remote","viewer","editor","reader","home","free","plus","pro","net",
           "platform","support","center","centre","utility","utilities","suite","bundle","install",
           "uninstall","data","cache","config","settings","profile","user","machine","system",
           "preview","beta","alpha","release","stable","latest","official","online","cloud",
           "mobile","phone","pc","mac","linux","windows","chrome","edge","firefox","tencent",
           "kingsoft","bytedance","alibaba","huawei","lenovo","xiaomi","google","apple"}

PUB_STOP = {"inc","ltd","llc","co","corp","corporation","technologies","technology","software",
            "systems","group","company","limited","gmbh","the","pte","labs","studio","authors",
            "shenzhen","beijing","shanghai","guangzhou","usa","cn","com","net","org","team",
            "foundation","深圳","北京","上海","广州","江苏","有限公司","科技","技术","公司",
            "信息技术","集团","股份","深圳市","北京市","广州市","苏州"}

app_sig = []
for a in apps:
    toks = words(a["name"]) | words(a.get("publisher"))
    for t in list(toks):
        toks |= set(ALIAS.get(t, []))
    toks |= set(ALIAS.get(a["normalized"], []))
    dirs = set()
    for v in (a.get("install_location") or "",):
        v = (v or "").strip().strip('"')
        if v: dirs.add(norm(os.path.basename(v.rstrip("\\/"))))
    if a.get("icon_exe"): dirs.add(norm(os.path.basename(os.path.dirname(a["icon_exe"]))))
    us = a.get("uninstall_string") or ""
    ue = cmd_exe(us)
    if ue: dirs.add(norm(os.path.basename(os.path.dirname(ue))))
    app_sig.append({"name": a["name"], "norm": a["normalized"],
                    "tokens": {t for t in toks if len(t) >= 2},
                    "strong": {t for t in toks if len(t) >= 4 and t not in PUB_STOP and t not in GENERIC},
                    "dirs": {d for d in dirs if d}})

# 路径归属池: 绝对路径 -> 归属描述
owned = []
def add_owned(path, who):
    if is_absolute(path) and exists(path):
        owned.append((os.path.normcase(os.path.abspath(path)), who))

for a in apps:
    if a.get("icon_exe"): add_owned(a["icon_exe"], a["name"])
    ue = cmd_exe(a.get("uninstall_string") or "")
    if ue: add_owned(ue, a["name"])
    if a.get("install_location") and a.get("loc_exists"): add_owned(a["install_location"], a["name"])
for s in facts["shortcuts"]:
    if s.get("Target"): add_owned(s["Target"], "快捷方式:" + os.path.basename(s["Lnk"]))
for p in facts["processes"]:
    if p.get("path"): add_owned(p["path"], "进程:" + (p.get("name") or ""))
for s in facts["services"]:
    e = cmd_exe(s.get("path"))
    if e: add_owned(e, "服务:" + s["name"])
for t in facts["tasks"]:
    for ex in (t.get("Execute") or "").split("|"):
        e = cmd_exe(ex)
        if e: add_owned(e, "任务:" + (t.get("TaskName") or ""))

def owner_of(dirpath):
    d = os.path.normcase(os.path.abspath(str(dirpath)))
    d = d if d.endswith("\\") else d + "\\"
    for p, who in owned:
        if p.startswith(d):
            return who
    return None

def match_name(name):
    nm = norm(name); w = words(name)
    for s in app_sig:
        if nm and (nm == s["norm"] or nm in s["dirs"]):
            return s, [{"code": "L1", "w": 100, "note": f"目录名与应用「{s['name']}」安装标识一致"}]
    strong = {t for t in w if len(t) >= 4}
    best = None
    for s in app_sig:
        h = strong & s["strong"]
        if h and (best is None or len(h) > len(best[1])): best = (s, h)
    if best: return best[0], [{"code": "L2", "w": 60, "note": f"与在装应用「{best[0]['name']}」共享标识 {sorted(best[1])[:3]}"}]
    for s in app_sig:
        for t in s["strong"]:
            if len(t) >= 6 and (t in nm or (len(nm) >= 6 and nm in t)):
                return s, [{"code": "L2", "w": 55, "note": f"命名片段 `{t}` 命中在装应用「{s['name']}」"}]
    return None, []

# ---------------- 排除表（不是"卸载残留"的目录）
SKIP = {
    # 个人目录
    "documents","desktop","downloads","pictures","music","videos","favorites","links","contacts",
    "saved games","searches","onedrive","my documents","my pictures","my music","my videos",
    "local settings","application data","recent","sendto","templates","桌面","文档","下载",
    "图片","音乐","视频","收藏夹","开始菜单","「开始」菜单","3d objects","objects",
    # 开发工具/包管理器缓存（活跃缓存，不是残留）
    "pip","npm-cache","pnpm-cache","pnpm","pnpm-state","pnpm-store","node","node-gyp","yarn",
    "ms-playwright","pipx","uv","conda","anaconda3","nuget","gradle","maven","cargo","go",
    "docker","jetbrains",".vscode",".vscode-shared",".conda",".cache",".config",".android",
    ".gradle",".m2",".npm",".nuget",".dotnet",".gitconfig",".ssh",".gnutls","recent",
    # Windows/系统组件
    "usoshared","usoprivate","comms","d3dscache","dwritecore","connecteddevicesplatform",
    "publishers","speech","crashdumps","package cache","boost_interprocess","packages",
    "microsoft","windows","windowsapps","windowsapps.tmp","temp","tmp","catroot","catroot2",
    "codecache","gpucache","dwm","fontcache","virtualstore","systemcertificates","whesvc",
    "softwareDistribution","ruxim","packagemManagement","packagemanagement","peerdistrepub",
    "placeholdertilelogofolder","squirreltemp","common files","reference assemblies","msbuild",
    "hyper-v","internet explorer","uninstall information","modifiablewindowsapps","recycler",
    "$recycle.bin","recovery","perflogs","system volume information","desktop.ini","efi",
    "regid.1991-06.com.microsoft","regid.1986-12.com.adobe","squirrelmachineinstalls",
    "microsoft.net","dotnet","wsl","windows defender","windows defender advanced threat protection",
    "microsoft update health tools","microsoft gameinput","windows mail","windows nt",
    "windows photo viewer","windows sidebar","windows powershell","reference assemblies",
    "application data","dolby","synaptics","realtek","nvidia","amd","intel","dell","hp","asus",
    "backup","program files","program files (x86)","sdk","mapdata","programs",
    "appdata","nethood","printhood","config.msi","deliveryoptimization","wudownloadcache",
    "cookies","undefined","administrator","default","public","all users","documents and settings",
    "my sharing folders","printer shortcuts","startup","recent","cache","code cache",
    "联想电脑管家","图吧工具箱","system32","syswow64","servicing","assembly","microsoft.net",
}
SKIP_NORM = {norm(x) for x in SKIP}
def skip(name):
    return norm(name) in SKIP_NORM

# ---------------- 目录评估
cands = []
ROOTS = [("Program Files", PF), ("Program Files (x86)", PF86), ("ProgramData", PD),
         ("AppData\\Local", LA), ("AppData\\Local\\Programs", LA / "Programs"),
         ("AppData\\Roaming", RA), ("用户主目录", HOME)]
for drv in ("D:\\", "E:\\"):
    if os.path.exists(drv): ROOTS.append((f"卷 {drv[:2]}", pathlib.Path(drv)))

RANDOM_NAME = re.compile(r'^[a-z0-9]{6,10}$', re.I)
UPDATER = re.compile(r'(updater|update|squirrel|crashpad|-cache$|cache$|logs?$)', re.I)

for group, root in ROOTS:
    try:
        with os.scandir(root) as it:
            for e in it:
                if not e.is_dir(follow_symlinks=False): continue
                name = e.name
                if skip(name): continue
                p = pathlib.Path(e.path)
                who = owner_of(p)
                meta = match_name(name)
                s, ev = (meta if meta[0] else (None, []))
                if who:
                    s = {"name": who}
                    ev = [{"code": "L4", "w": 95, "note": f"该目录下存在归属在装应用的绝对路径（{who}）"}]
                probed = probe(p)
                size, files, trunc = dir_size(p)
                try: mt = os.stat(p).st_mtime
                except Exception: mt = None
                age = int((NOW - mt) / 86400) if mt else None
                orphan = []
                if not s:
                    if probed["exe_n"] > 0:
                        orphan.append({"code": "O1", "w": 70, "note": f"含可执行文件 {probed['exes'][:2]}"})
                    elif probed["dll_n"] > 0:
                        orphan.append({"code": "O1", "w": 60, "note": f"含 {probed['dll_n']} 个 DLL"})
                    elif files == 0:
                        orphan.append({"code": "O4", "w": 55, "note": "空壳目录（无任何文件）"})
                    else:
                        orphan.append({"code": "O1", "w": 40, "note": "仅存数据/配置，无程序主体"})
                    if UPDATER.search(name):
                        orphan.append({"code": "O3", "w": 60, "note": "目录名指示更新器/缓存，属卸载后遗留"})
                    if RANDOM_NAME.match(name) and len(name) >= 6:
                        orphan.append({"code": "O5", "w": 50, "note": "随机命名目录，非用户主动创建"})
                    if age is not None and age > 365:
                        orphan.append({"code": "O6", "w": 40, "note": f"最后修改距今 {age} 天"})
                    elif age is not None and age > 120:
                        orphan.append({"code": "O6", "w": 20, "note": f"最后修改距今 {age} 天"})
                cands.append({"group": group, "name": name, "path": str(p), "owner": who,
                              "matched": s["name"] if s else None, "retain": ev,
                              "orphan": orphan,
                              "orphan_w": sum(o["w"] for o in orphan),
                              "size": size, "size_h": human(size), "files": files,
                              "truncated": trunc, "age_days": age,
                              "mtime": datetime.datetime.fromtimestamp(mt).strftime("%Y-%m-%d") if mt else None,
                              "probe": probed})
    except OSError as ex:
        print("skip", root, ex)

# ---------------- 三档收敛
for c in cands:
    if c["owner"] or c["retain"]:
        c["conclusion"] = "保留"
    elif c["orphan_w"] >= 70 and (c["age_days"] or 0) > 60:
        c["conclusion"] = "确证残留"
    elif c["orphan_w"] >= 45:
        c["conclusion"] = "疑似残留"
    elif (c["age_days"] or 0) <= 30:
        c["conclusion"] = "近期活跃"
    else:
        c["conclusion"] = "证据不足"

# ---------------- 其他来源
svc_broken = []
for s in facts["services"]:
    e = cmd_exe(s.get("path"))
    if e and is_absolute(e) and not exists(e):
        svc_broken.append({"name": s["name"], "display": s.get("display"), "state": s.get("state"),
                           "start_mode": s.get("start_mode"), "path": s.get("path"), "missing": e})
task_broken = []
WIN_ONLY = re.compile(r'%windir%|%systemroot%|\\windows\\', re.I)
for t in facts["tasks"]:
    ex = (t.get("Execute") or "").split("|")[0].strip()
    e = cmd_exe(ex) or (os.path.expandvars(ex) if is_absolute(ex) else None)
    if e and is_absolute(e) and not exists(e) and not WIN_ONLY.search(e):
        task_broken.append({"task": (t.get("TaskPath") or "") + (t.get("TaskName") or ""),
                            "state": t.get("State"), "exe": e})
lnk_broken = [s for s in facts["shortcuts"]
              if s.get("Target") and is_absolute(s["Target"]) and not exists(s["Target"])]
path_broken = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path":
            for seg in str(v).split(";"):
                seg = seg.strip()
                if seg and is_absolute(seg) and not exists(seg):
                    path_broken.append({"scope": scope, "entry": seg})
broken_receipt = []
for a in apps:
    us = a.get("uninstall_string") or ""
    ue = cmd_exe(us)
    if ue and is_absolute(ue) and not exists(ue):
        broken_receipt.append({"name": a["name"], "publisher": a.get("publisher"),
                               "uninstall_string": us, "missing": ue,
                               "install_location": a.get("install_location"),
                               "loc_exists": a.get("loc_exists"), "registry_key": a.get("registry_key")})

out = {"dirs": cands, "services_broken": svc_broken, "tasks_broken": task_broken,
       "shortcuts_broken": lnk_broken, "path_broken": path_broken,
       "broken_receipts": broken_receipt,
       "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
(BASE / "plan3.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

from collections import Counter
cnt = Counter(c["conclusion"] for c in cands)
print("目录结论分布:", dict(cnt))
for lvl in ("确证残留", "疑似残留"):
    rows = [c for c in cands if c["conclusion"] == lvl]
    print(f"\n== {lvl} ({len(rows)}) ==")
    for c in sorted(rows, key=lambda x: -(x["size"] or 0)):
        print(f'  {c["group"]:20s} {c["name"][:32]:34s} {c["size_h"]:>9s} {c["mtime"]} '
              f'exe={c["probe"]["exe_n"]:2d} | {c["orphan"][0]["note"][:46]} | w={c["orphan_w"]}')
