# -*- coding: utf-8 -*-
"""P1: 建立已安装应用存活集 (inventory.json) —— 全程只读"""
import json, os, re, sys, winreg, pathlib

OUT = pathlib.Path(__file__).parent

UNINSTALL_ROOTS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_WOW64_64KEY),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_WOW64_32KEY),
    (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0),
]

FIELDS = ("DisplayName", "DisplayVersion", "Publisher", "InstallLocation",
          "DisplayIcon", "UninstallString", "InstallDate", "EstimatedSize",
          "SystemComponent", "ParentKeyName", "ReleaseType")

def read_values(hive, path, view):
    out = {}
    try:
        k = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | view)
    except OSError:
        return None
    try:
        n = winreg.QueryInfoKey(k)[1]
        for i in range(n):
            try:
                name, val, _ = winreg.EnumValue(k, i)
                out[name] = val
            except OSError:
                continue
    finally:
        k.Close()
    return out

def clean_exe(s):
    if not s:
        return None
    s = s.strip()
    m = re.match(r'^"([^"]+)"', s)
    if m:
        return m.group(1)
    m = re.match(r'^([A-Za-z]:\\[^,]*?\.(?:exe|dll|ico))', s, re.I)
    if m:
        return m.group(1)
    return s.split()[0] if s.split() else None

apps = []
seen = set()
for hive, root, view in UNINSTALL_ROOTS:
    try:
        k = winreg.OpenKey(hive, root, 0, winreg.KEY_READ | view)
    except OSError:
        continue
    cnt = winreg.QueryInfoKey(k)[0]
    for i in range(cnt):
        try:
            sub = winreg.EnumKey(k, i)
        except OSError:
            continue
        vals = read_values(hive, root + "\\" + sub, view)
        if not vals or not vals.get("DisplayName"):
            continue
        name = str(vals["DisplayName"]).strip()
        if not name:
            continue
        key_id = f"{'HKLM' if hive == winreg.HKEY_LOCAL_MACHINE else 'HKCU'}|{'64' if view == winreg.KEY_WOW64_64KEY else '32'}|{sub}"
        if key_id in seen:
            continue
        seen.add(key_id)
        loc = vals.get("InstallLocation") or ""
        loc = str(loc).strip().strip('"')
        icon = clean_exe(str(vals.get("DisplayIcon") or ""))
        uns = str(vals.get("UninstallString") or "")
        rec = {
            "name": name,
            "normalized": re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '', name.lower()),
            "version": str(vals.get("DisplayVersion") or ""),
            "publisher": str(vals.get("Publisher") or ""),
            "install_location": loc,
            "icon_exe": icon,
            "uninstall_string": uns,
            "install_date": str(vals.get("InstallDate") or ""),
            "estimated_kb": vals.get("EstimatedSize") if isinstance(vals.get("EstimatedSize"), int) else None,
            "system_component": int(vals.get("SystemComponent") or 0),
            "registry_key": ("HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU") + "\\" + root + "\\" + sub,
            "view": "64" if view == winreg.KEY_WOW64_64KEY else ("32" if view == winreg.KEY_WOW64_32KEY else "native"),
            "loc_exists": bool(loc) and os.path.isdir(loc),
            "icon_exists": bool(icon) and os.path.exists(icon),
        }
        apps.append(rec)
    k.Close()

# WOW6432Node 的 Uninstall 已由 32 视图覆盖；去重按 (name, version)
apps.sort(key=lambda a: a["name"].lower())
(OUT / "inventory.json").write_text(json.dumps(apps, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"installed entries: {len(apps)}")
print(f"  with existing InstallLocation: {sum(1 for a in apps if a['loc_exists'])}")
print(f"  with missing InstallLocation : {sum(1 for a in apps if a['install_location'] and not a['loc_exists'])}")
print(f"  no InstallLocation at all    : {sum(1 for a in apps if not a['install_location'])}")
print("\n-- 已安装应用（前 80）--")
for a in apps[:80]:
    print(f"  {a['name'][:58]:60s} | {a['publisher'][:26]:28s} | loc={'Y' if a['loc_exists'] else '-'} icon={'Y' if a['icon_exists'] else '-'}")
