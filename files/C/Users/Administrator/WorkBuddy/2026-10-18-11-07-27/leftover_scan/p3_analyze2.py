# -*- coding: utf-8 -*-
"""
v2: 候选枚举 + 证据打分。相比 v1 修正:
  1) 在装应用签名扩展到 名称/发行商/安装目录/图标目录 的词集合
  2) 增加 已知品牌别名表（跨语言/跨命名: 微信->wechat, WPS->kingsoft, Tabbit->tabbit ...）
  3) 增加 非应用目录排除表（用户个人目录、开发工具缓存、Windows 组件）
  4) 结构探针: 是否含 exe/dll/卸载器、顶层样例
  5) 按技能噪声过滤: 仅 O7 弱证据的条目丢弃
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

CJK = re.compile(r'[\u4e00-\u9fff]+')
ASCII_W = re.compile(r'[a-z0-9]+')
def words(s):
    s = (s or "").lower()
    return {w for w in (ASCII_W.findall(s) + CJK.findall(s)) if len(w) >= 2}
def norm(s):
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '', (s or "").lower())
def path_exists(p):
    try:
        return os.path.exists(p)
    except Exception:
        return False
def human(n):
    if n is None: return "?"
    for u, d in (("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)):
        if n >= d: return f"{n/d:.1f} {u}"
    return f"{n} B"

def resolve_exe(s):
    """把命令行解析成真实 exe 全路径；裸 exe 名到 System32/Path 里找。"""
    if not s: return None
    s = s.strip()
    m = re.match(r'^"([^"]+)"', s)
    cand = m.group(1) if m else s.split(" ")[0]
    cand = os.path.expandvars(cand)
    if re.match(r'^[A-Za-z]:\\', cand) or cand.startswith("\\\\"):
        return cand
    for d in (os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32"),
              os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "SysWOW64")):
        p = os.path.join(d, cand)
        if os.path.exists(p): return p
    return cand  # 裸名，判存在性时特殊处理

def exe_exists(s):
    if not s: return True
    s = s.strip()
    m = re.match(r'^"([^"]+)"', s)
    cand = m.group(1) if m else s.split(" ")[0]
    cand = os.path.expandvars(cand)
    if not (re.match(r'^[A-Za-z]:\\', cand) or cand.startswith("\\\\") or cand.startswith("%")):
        return True   # 依赖 PATH / 系统组件，视为存在
    return os.path.exists(cand)

def dir_size(p, budget=10.0, cap=400000):
    total = files = 0
    t0 = time.time(); stack = [str(p)]; seen = 0
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

def probe(p, limit=8):
    """结构探针：顶层样例、是否含 exe/dll、是否有卸载器、是否有安装收据"""
    exes, dlls, unins, subs, files = [], 0, [], [], 0
    try:
        with os.scandir(p) as it:
            for e in it:
                if len(subs) >= limit: break
                try:
                    if e.is_dir(follow_symlinks=False): subs.append(e.name)
                    else:
                        files += 1
                        ln = e.name.lower()
                        if ln.endswith(".exe"): exes.append(e.name)
                        elif ln.endswith(".dll"): dlls += 1
                        if re.match(r'(unins|uninstall|setup|installer)', ln): unins.append(e.name)
                except OSError: continue
    except OSError: pass
    return {"exes": exes[:6], "exe_n": len(exes), "dll_n": dlls, "uninstallers": unins[:3], "dirs": subs}

# ------------------------------------------------ 在装应用签名（增强）
ALIAS = {
    "微信": ["wechat", "weixin"], "wechat": ["wechat", "weixin"],
    "wps": ["kingsoft", "wps"], "kingsoft": ["wps", "kingsoft"],
    "qq": ["tencent", "qq"], "抖音": ["douyin", "aweme", "bytedance"],
    "剪映": ["jianying", "capcut", "lv", "vedetector"], "jianying": ["jianying", "lv"],
    "百度网盘": ["baidu", "netdisk", "yunguanjia"], "夸克网盘": ["quark"],
    "豆包": ["doubao", "bytedance"], "豆包工作": ["doubao"],
    "tabbit浏览器": ["tabbit"], "trae cn": ["trae"], "trae": ["trae"],
    "workbuddy": ["workbuddy", "genieworkbuddy", "codebuddy"],
    "codebuddy": ["codebuddy", "workbuddy"], "deepseek harness": ["deepseek", "dsh"],
    "嘉立创eda": ["lceda", "easyeda"], "lceda": ["lceda"],
    "anaconda": ["anaconda", "conda"], "python": ["python"], "node.js": ["nodejs", "node"],
    "arduino ide": ["arduino"], "vlc": ["videolan", "vlc"],
    "wondershare": ["wondershare", "drfone", "imobie"], "avast": ["avast"],
    "lenovo": ["lenovo"], "华为": ["huawei", "deveco", "codearts"], "huawei": ["huawei"],
    "网易": ["netease", "163"], "米哈游": ["mihoyo", "hoyoverse"],
    "bonjour": ["bonjour", "apple"], "apple": ["apple", "bonjour", "imobie"],
    "火绒": ["huorong"], "雷神": ["leigod"], "瓦特": ["watt", "steam++"],
    "7-zip": ["7-zip", "7zip"], "git": ["git"], "github": ["github"],
    "vmware": ["vmware"], "mumu": ["mumu", "netease"], "联想": ["lenovo"],
    "kingsoft": ["kingsoft", "wps"], "adobe": ["adobe"], "intel": ["intel"],
    "google": ["google", "chrome"], "obsidian": ["obsidian"], "libreoffice": ["libreoffice"],
    "rufus": ["rufus"], "coze": ["coze"], "kimi": ["kimi", "moonshot"],
    "comfy": ["comfy", "comfyui"], "mixly": ["mixly"], "dev-c++": ["devcpp", "dev-c++"],
    "geogebra": ["geogebra"], "canmv": ["canmv"], "deveco": ["deveco", "huawei"],
}
PUB_STOP = {"inc","ltd","llc","co","corp","corporation","technologies","technology","software",
            "systems","group","company","limited","gmbh","the","pte","labs","studio","authors",
            "shenzhen","beijing","shanghai","usa","cn","com","net","org","team","foundation",
            "深圳","北京","上海","广州","江苏","有限公司","科技","技术","公司","信息技术","集团"}

app_sig = []
for a in apps:
    toks = words(a["name"]) | words(a.get("publisher"))
    for d in list(toks):
        for extra in ALIAS.get(d, []):
            toks.add(extra)
    nm = a["normalized"]
    for extra in ALIAS.get(nm, []):
        toks.add(extra)
    dirs = set()
    for v in (a.get("install_location") or "", ):
        v = (v or "").strip().strip('"')
        if v: dirs.add(norm(os.path.basename(v.rstrip("\\/"))))
    for v in (a.get("icon_exe") or "", ):
        if v: dirs.add(norm(os.path.basename(os.path.dirname(v))))
    app_sig.append({"name": a["name"], "norm": nm,
                    "tokens": {t for t in toks if len(t) >= 2},
                    "strong_tokens": {t for t in toks if len(t) >= 4 and t not in PUB_STOP},
                    "dirs": {d for d in dirs if d},
                    "publisher": a.get("publisher") or "", "loc": a.get("install_location") or ""})
all_tokens = set().union(*[s["tokens"] for s in app_sig]) if app_sig else set()
all_strong = set().union(*[s["strong_tokens"] for s in app_sig]) if app_sig else set()

# ------------------------------------------------ 保留：非应用/系统/个人目录
NOT_APP = {
    # 用户个人目录
    "documents","desktop","downloads","pictures","music","videos","favorites","links","contacts",
    "saved games","searches","onedrive","my documents","my pictures","my music","my videos",
    "local settings","application data","recent","sendto","templates","「开始」菜单","开始菜单",
    "桌面","文档","下载","图片","音乐","视频","收藏夹","cookies","netHood","PrintHood",
    # 开发工具/包管理器缓存（不是"卸载残留"，属于活跃缓存）
    "pip","npm-cache","pnpm-cache","pnpm","pnpm-store","node","node-gyp","yarn","ms-playwright",
    "pipx","uv","conda","anaconda3","nuget","gradle","maven","cargo","go","docker",
    ".vscode",".vscode-shared",".conda",".cache",".config",".android",".gradle",".m2",".npm",
    # Windows / 系统组件
    "usoShared","usoshared","usoprivate","usoshared","comms","d3dscache","dwritecore",
    "connecteddevicesplatform","publishers","speech","crashdumps","package cache",
    "boost_interprocess","packages","microsoft","windows","windowsapps","temp","tmp",
    "catroot","catroot2","codecache","gpucache","dwm","fontcache","regid.1991-06.com.microsoft",
    "regid.1986-12.com.adobe","squirrelmachineinstalls","pxgrid","virtualstore",
    "systemcertificates","whesvc","bitdefender","nvidia","realtek","intel","amd","dell",
    "sysceo","lenovo","backup","program files","sdk","mapdata","wpsystem","$recycle.bin",
    "recovery","perflogs","users","programdata","desktop.ini","efi","system volume information",
}
def is_not_app(name):
    return name.lower() in NOT_APP or norm(name).lower() in {norm(x) for x in NOT_APP}

def match_app(name, extra_tokens=()):
    """返回 (app_sig|None, evidence list)"""
    nm = norm(name)
    w = words(name) | set(extra_tokens)
    strong = {t for t in w if len(t) >= 4}
    # 1) 目录/键名与在装应用安装目录完全一致
    for s in app_sig:
        if nm and (nm == s["norm"] or nm in s["dirs"]):
            return s, [{"code": "L1", "w": 100, "note": f"与应用「{s['name']}」标识完全一致"}]
    # 2) 词级命中在装应用名称/发行商（>=4 字符）
    hits = [(s, strong & s["strong_tokens"]) for s in app_sig]
    hits = [(s, h) for s, h in hits if h]
    if hits:
        hits.sort(key=lambda x: -len(x[1]))
        s, h = hits[0]
        return s, [{"code": "L2", "w": 60,
                    "note": f"与在装应用「{s['name']}」共享标识 {sorted(h)[:3]}"}]
    # 3) 子串匹配（长词，容忍拼接命名，如 tabbitbrowser / quarkclouddrive）
    for s in app_sig:
        for t in s["strong_tokens"]:
            if len(t) >= 6 and (t in nm or (len(nm) >= 6 and nm in t)):
                return s, [{"code": "L2", "w": 55,
                            "note": f"命名片段 `{t}` 命中在装应用「{s['name']}」"}]
    return None, []

cands = []
existing_proc = [p["path"] for p in facts["processes"] if p.get("path")]

def eval_dir(group, p):
    name = p.name
    if is_not_app(name): return None
    if len(name.strip()) == 0: return None
    s, ev = match_app(name)
    probed = probe(p)
    size, files, trunc = dir_size(p)
    mt = None
    try: mt = os.stat(p).st_mtime
    except Exception: pass
    age = int((NOW - mt) / 86400) if mt else None
    live = any(str(p).lower() in pp.lower() for pp in existing_proc)
    if live and not s:
        s = {"name": "(运行中进程所在目录)"}
        ev = [{"code": "L6", "w": 100, "note": "该目录下有进程正在运行"}]
    if s and not ev:
        ev = [{"code": "L5", "w": 60, "note": "命中保留证据"}]
    if not s:
        # 孤儿证据
        if probed["exe_n"] > 0:
            ev.append({"code": "O1", "w": 70,
                       "note": f"含可执行文件 {probed['exes'][:2]}，但在装应用清单中查无对应产品"})
        elif probed["dll_n"] > 0:
            ev.append({"code": "O1", "w": 60, "note": f"含 {probed['dll_n']} 个 DLL，查无对应产品"})
        elif files == 0:
            ev.append({"code": "O4", "w": 55, "note": "空壳目录"})
        else:
            ev.append({"code": "O1", "w": 40, "note": "仅存数据/配置，查无对应产品"})
        if age is not None and age > 365:
            ev.append({"code": "O6", "w": 20, "note": f"最后修改距今 {age} 天"})
        # 被环境变量 / PATH / 服务 / 任务 引用 -> 保留
        refs = []
        for scope in ("user", "machine"):
            for k, v in facts["env"].get(scope, {}).items():
                if str(p).lower() in str(v).lower(): refs.append(f"{scope} 环境变量 {k}")
        for s2 in facts["services"]:
            if s2.get("path") and str(p).lower() in str(s2["path"]).lower() and s2.get("state") != "Stopped":
                refs.append(f"服务 {s2['name']}({s2.get('state')})")
        if refs:
            ev.append({"code": "L4", "w": 90, "note": "仍被引用: " + "; ".join(refs[:2])})
            s = {"name": "(被引用)"}
    orphan = sum(e["w"] for e in ev if e["code"].startswith("O"))
    retain = max([e["w"] for e in ev if e["code"].startswith("L")] or [0])
    if s: conclusion = "保留"
    elif orphan >= 60: conclusion = "确证残留"
    elif orphan >= 30: conclusion = "疑似残留"
    else: conclusion = "证据不足"
    # 风险
    if s: risk = "R0"
    elif group.startswith("Program Files") and (size or 0) > 200 * 1024**2: risk = "R1"
    elif re.search(r'data|profile|save|project|资料', name, re.I): risk = "R1"
    elif size and size > 1024**3: risk = "R1"
    elif files > 0 and probed["exe_n"] == 0: risk = "R2"
    else: risk = "R2"
    return {"kind": "dir", "group": group, "name": name, "path": str(p),
            "size": size, "size_h": human(size), "files": files, "truncated": trunc,
            "mtime": datetime.datetime.fromtimestamp(mt).strftime("%Y-%m-%d") if mt else None,
            "age_days": age, "evidence": ev, "orphan_w": orphan, "retain_w": retain,
            "matched": s["name"] if s else None, "conclusion": conclusion, "risk": risk,
            "probe": probed}

ROOTS = [("Program Files", PF), ("Program Files (x86)", PF86), ("ProgramData", PD),
         ("AppData\\Local", LA), ("AppData\\Local\\Programs", LA / "Programs"),
         ("AppData\\Roaming", RA), ("用户目录", HOME)]
for drv in (pathlib.Path("D:\\"), pathlib.Path("E:\\")):
    if drv.exists(): ROOTS.append((f"卷 {drv.drive}", drv))

for group, root in ROOTS:
    try:
        with os.scandir(root) as it:
            for e in it:
                if not e.is_dir(follow_symlinks=False): continue
                c = eval_dir(group, pathlib.Path(e.path))
                if c: cands.append(c)
    except OSError as ex:
        print("skip", root, ex)

# ------------------------------------------------ 注册表
REG_R0 = {"microsoft","windows","classes","clients","policies","registeredapplications","wow6432node",
          "odbc","system","squirrelmachineinstalls","intel","nvidia","realtek","amd","apple","adobe",
          "google","mozilla","python","node.js","7-zip","git","github","tencent","huawei","kingsoft",
          "bytedance","baidu","wondershare","vmware","avast","lenovo","steam","valve","oracle","ibm",
          "java","wow6432node","microsoft corporation","qualcomm","dell","hp","asus","acer","toshiba"}
reg_cands = []
for label, hive, root, view in (("HKCU\\Software", winreg.HKEY_CURRENT_USER, r"SOFTWARE", winreg.KEY_WOW64_64KEY),
                                ("HKLM\\Software", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE", winreg.KEY_WOW64_64KEY),
                                ("HKLM\\Software(WOW64)", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node", winreg.KEY_WOW64_64KEY)):
    try:
        k = winreg.OpenKey(hive, root, 0, winreg.KEY_READ | view)
    except OSError: continue
    for i in range(winreg.QueryInfoKey(k)[0]):
        try: sub = winreg.EnumKey(k, i)
        except OSError: continue
        if sub.lower() in REG_R0 or sub.lower().startswith(("microsoft","windows")): 
            continue
        s, ev = match_app(sub)
        if s: 
            continue   # 有归属 -> 不列
        nm = norm(sub)
        if nm in {norm(x) for x in NOT_APP}:
            continue
        ev = [{"code": "O1", "w": 70, "note": "存在该厂商/产品注册表键，但在装应用清单中查无对应产品"}]
        reg_cands.append({"kind": "registry", "group": label, "name": sub,
                          "path": ("HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM") + "\\" + root + "\\" + sub,
                          "evidence": ev, "orphan_w": 70, "retain_w": 0,
                          "matched": None, "conclusion": "确证残留", "risk": "R2"})
    k.Close()

# ------------------------------------------------ 服务 / 计划任务 / 启动项 / 快捷方式 / PATH / 环境变量 / 卸载收据
svc = []
for s in facts["services"]:
    e = resolve_exe(s.get("path"))
    if e and not exe_exists(s.get("path")):
        svc.append({"name": s["name"], "display": s.get("display"), "state": s.get("state"),
                    "start_mode": s.get("start_mode"), "path": s.get("path"), "missing": e})
tasks = []
for t in facts["tasks"]:
    ex = (t.get("Execute") or "").strip()
    if not ex: continue
    if not exe_exists(ex):
        tasks.append({"task": (t.get("TaskPath") or "") + (t.get("TaskName") or ""),
                      "state": t.get("State"), "exe": ex})
startup = []
for scope, key in (("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                   ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                   ("HKLM32", r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
                   ("HKCU-RunOnce", r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce")):
    hive = winreg.HKEY_CURRENT_USER if scope.startswith("HKCU") else winreg.HKEY_LOCAL_MACHINE
    try:
        k = winreg.OpenKey(hive, key, 0, winreg.KEY_READ)
        for i in range(winreg.QueryInfoKey(k)[1]):
            try: n, v, _ = winreg.EnumValue(k, i)
            except OSError: continue
            if not exe_exists(str(v)):
                startup.append({"scope": scope, "name": n, "cmd": str(v),
                                "missing": resolve_exe(str(v))})
        k.Close()
    except OSError:
        pass
lnks = [x for x in facts["shortcuts"] if x.get("Target") and not path_exists(x["Target"])]
path_orphan = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path":
            for seg in str(v).split(";"):
                seg = seg.strip()
                if seg and "%" not in seg and not path_exists(seg):
                    path_orphan.append({"scope": scope, "entry": seg})
env_orphan = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path": continue
        for m in re.findall(r'[A-Za-z]:\\[^;"]*', str(v)):
            if not path_exists(m):
                env_orphan.append({"scope": scope, "name": k, "value": str(v), "missing": m})

broken = []
for a in apps:
    us = a.get("uninstall_string") or ""
    if us and not exe_exists(us):
        broken.append({"name": a["name"], "publisher": a.get("publisher"),
                       "uninstall_string": us, "install_location": a.get("install_location"),
                       "loc_exists": a.get("loc_exists"), "registry_key": a.get("registry_key")})

out = {"dirs": cands, "registry": reg_cands, "services_broken": svc, "tasks_broken": tasks,
       "startup_broken": startup, "shortcuts_broken": lnks, "path_orphan": path_orphan,
       "env_orphan": env_orphan, "broken_receipts": broken, "generated": datetime.datetime.now().isoformat()}
(BASE / "plan.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

keep = [c for c in cands if c["conclusion"] != "保留"]
print(f"dirs total={len(cands)} 非保留={len(keep)} | reg={len(reg_cands)} | svc={len(svc)} "
      f"task={len(tasks)} startup={len(startup)} lnk={len(lnks)} path={len(path_orphan)} "
      f"env={len(env_orphan)} broken_receipt={len(broken)}")
print("\n-- 目录非保留项（按体积）--")
for c in sorted(keep, key=lambda x: -(x["size"] or 0)):
    print(f'  [{c["conclusion"]:4s}|{c["risk"]}] {c["group"]:20s} {c["name"][:34]:36s} '
          f'{c["size_h"]:>9s} {c["mtime"] or "?"} exe={c["probe"]["exe_n"]:2d} dll={c["probe"]["dll_n"]:2d} '
          f'| {c["evidence"][0]["note"][:52]}')
