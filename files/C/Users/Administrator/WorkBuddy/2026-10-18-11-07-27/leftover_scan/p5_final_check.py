# -*- coding: utf-8 -*-
"""最终核验：修正带空格路径解析，输出 report_data.json（供报告使用）"""
import json, os, re, pathlib, winreg, datetime

BASE = pathlib.Path(__file__).parent
apps = json.loads((BASE / "inventory.json").read_text(encoding="utf-8"))
facts = json.loads((BASE / "raw_facts.json").read_text(encoding="utf-8"))
plan = json.loads((BASE / "plan3.json").read_text(encoding="utf-8"))

EXE_RE = re.compile(r'^([A-Za-z]:\\.*?\.(?:exe|dll|bat|cmd|msi))', re.I)
def cmd_exe(s):
    """严格解析命令行里的可执行路径；未加引号且含空格时，取到 .exe 结尾为止"""
    if not s:
        return None
    s = str(s).strip()
    if s.startswith('"'):
        m = re.match(r'^"([^"]+)"', s)
        cand = m.group(1) if m else s
    else:
        m = EXE_RE.match(s)
        cand = m.group(1) if m else s.split(" ")[0].split(",")[0]
    cand = os.path.expandvars(cand).strip().strip('"')
    return cand

def exists(p):
    try:
        return os.path.exists(p) if p else False
    except Exception:
        return False

# 1) 卸载收据（无法卸载）
receipts = []
for a in apps:
    us = a.get("uninstall_string") or ""
    e = cmd_exe(us)
    if e and re.match(r'^[A-Za-z]:\\', e) and not exists(e):
        receipts.append({"name": a["name"], "publisher": a.get("publisher"),
                         "uninstall_string": us, "missing": e,
                         "install_location": a.get("install_location"),
                         "loc_exists": a.get("loc_exists"), "registry_key": a.get("registry_key")})

# 2) 服务
services = []
for s in facts["services"]:
    e = cmd_exe(s.get("path"))
    if not e or not re.match(r'^[A-Za-z]:\\', e):
        continue
    if "svchost" in e.lower():
        continue                      # svchost 宿主服务，非孤儿
    if not exists(e):
        services.append({"name": s["name"], "display": s.get("display"), "state": s.get("state"),
                         "start_mode": s.get("start_mode"), "path": s.get("path"), "missing": e})

# 3) 计划任务（排除系统自带）
TASK_SYS = re.compile(r'\\Microsoft\\Windows\\|MicrosoftEdgeUpdate|OneDrive', re.I)
tasks = []
for t in facts["tasks"]:
    ex = (t.get("Execute") or "").split("|")[0].strip()
    e = cmd_exe(ex)
    if not e or not re.match(r'^[A-Za-z]:\\', e) or exists(e):
        continue
    name = (t.get("TaskPath") or "") + (t.get("TaskName") or "")
    if TASK_SYS.search(name):
        continue
    tasks.append({"task": name, "state": t.get("State"), "exe": e})

# 4) 快捷方式
lnks = []
for s in facts["shortcuts"]:
    tg = s.get("Target") or ""
    if tg and re.match(r'^[A-Za-z]:\\', tg) and not exists(tg):
        lnks.append({"lnk": s["Lnk"], "target": tg})

# 5) PATH
path_broken = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path":
            for seg in str(v).split(";"):
                seg = seg.strip()
                if seg and re.match(r'^[A-Za-z]:\\', seg) and not exists(seg):
                    path_broken.append({"scope": scope, "entry": seg})

# 6) 环境变量
env_broken = []
for scope in ("user", "machine"):
    for k, v in facts["env"].get(scope, {}).items():
        if k.lower() == "path":
            continue
        vs = str(v)
        for m in re.findall(r'[A-Za-z]:\\[^;"]*', vs):
            if not exists(m):
                env_broken.append({"scope": scope, "name": k, "value": vs, "missing": m})

data = {"receipts": receipts, "services": services, "tasks": tasks,
        "shortcuts": lnks, "path": path_broken, "env": env_broken,
        "dirs": plan["dirs"], "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
(BASE / "report_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"无法卸载收据={len(receipts)}  孤儿服务={len(services)}  孤儿任务={len(tasks)}  "
      f"死快捷方式={len(lnks)}  失效PATH={len(path_broken)}  失效环境变量={len(env_broken)}")
print("\n== 无法卸载的收据（卸载器已缺失）==")
for r in receipts:
    print(f"  {r['name'][:40]:42s} 缺失: {r['missing']}")
print("\n== 孤儿服务 ==")
for s in services:
    print(f"  {s['name']:26s} [{s['state']}/{s['start_mode']}] -> {s['missing']}")
print("\n== 孤儿计划任务 ==")
for t in tasks:
    print(f"  {t['task'][:64]:66s} [{t['state']}] -> {t['exe']}")
print("\n== 死快捷方式 ==")
for l in lnks:
    print(f"  {l['lnk']}\n     -> {l['target']}")
print("\n== 失效 PATH / 环境变量 ==")
for p in path_broken: print("  PATH", p["scope"], p["entry"])
for e in env_broken: print("  ENV ", e["scope"], e["name"], "->", e["missing"])
