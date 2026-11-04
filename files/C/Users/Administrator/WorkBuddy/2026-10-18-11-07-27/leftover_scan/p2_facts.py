# -*- coding: utf-8 -*-
"""只读采集器：把需要跨工具/跨工具链的原始事实收集成 raw facts（不判定，不写入系统）"""
import json, os, subprocess, pathlib, re

OUT = pathlib.Path(__file__).parent
PS = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

def ps(cmd, timeout=180):
    # 强制 UTF-8 输出，否则中文路径在 GBK 代码页下会被解成乱码，导致存在性判断全线误判
    prelude = ("$OutputEncoding=[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
               "[Console]::InputEncoding=[System.Text.Encoding]::UTF8;")
    try:
        p = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                            "-Command", prelude + cmd],
                           capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.stdout
    except Exception as e:
        return json.dumps({"__error__": str(e)})

facts = {}

# 1) 运行中进程的可执行文件路径（L6 证据）
raw = ps("Get-CimInstance Win32_Process | Where-Object {$_.ExecutablePath} | "
         "Select-Object ProcessId,Name,ExecutablePath | ConvertTo-Json -Compress")
try:
    procs = json.loads(raw) or []
except Exception:
    procs = []
if isinstance(procs, dict):
    procs = [procs]
facts["processes"] = [{"pid": p.get("ProcessId"), "name": p.get("Name"), "path": p.get("ExecutablePath")} for p in procs]

# 2) 服务：名称 + ImagePath + 状态
raw = ps("""Get-CimInstance Win32_Service | Select-Object Name,DisplayName,State,StartMode,PathName |
ConvertTo-Json -Compress""")
try:
    svc = json.loads(raw) or []
except Exception:
    svc = []
if isinstance(svc, dict):
    svc = [svc]
facts["services"] = [{"name": s.get("Name"), "display": s.get("DisplayName"), "state": s.get("State"),
                      "start_mode": s.get("StartMode"), "path": s.get("PathName")} for s in svc]

# 3) 计划任务：动作目标
raw = ps("""Get-ScheduledTask | ForEach-Object {
  $t=$_; $acts=@(); foreach($a in $t.Actions){ if($a.Execute){$acts+=$a.Execute} }
  [PSCustomObject]@{ TaskPath=$t.TaskPath; TaskName=$t.TaskName; State=[string]$t.State; Execute=($acts -join '|') }
} | ConvertTo-Json -Compress""", timeout=240)
try:
    tasks = json.loads(raw) or []
except Exception:
    tasks = []
if isinstance(tasks, dict):
    tasks = [tasks]
facts["tasks"] = tasks

# 4) 快捷方式：位置 + 解析后的目标
raw = ps("""$sh=New-Object -ComObject WScript.Shell
$dirs=@("$env:USERPROFILE\\Desktop","$env:PUBLIC\\Desktop",
"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs",
"$env:ProgramData\\Microsoft\\Windows\\Start Menu\\Programs")
$res=@()
foreach($d in $dirs){ if(Test-Path $d){
  Get-ChildItem -Path $d -Filter *.lnk -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $t=''; try{$t=$sh.CreateShortcut($_.FullName).TargetPath}catch{}
    $res += [PSCustomObject]@{ Lnk=$_.FullName; Target=$t }
  }}}
$res | ConvertTo-Json -Compress""", timeout=180)
try:
    lnks = json.loads(raw) or []
except Exception:
    lnks = []
if isinstance(lnks, dict):
    lnks = [lnks]
facts["shortcuts"] = lnks

# 5) 环境变量（用户 + 系统） —— 用 winreg，避免依赖被策略拦截的 reg.exe
import winreg
envs = {}
for scope, (hive, key) in (("user", (winreg.HKEY_CURRENT_USER, "Environment")),
                           ("machine", (winreg.HKEY_LOCAL_MACHINE,
                                        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"))):
    vals = {}
    try:
        k = winreg.OpenKey(hive, key, 0, winreg.KEY_READ)
        userprof = os.environ.get("USERPROFILE", "")
        for i in range(winreg.QueryInfoKey(k)[1]):
            try:
                n, v, t = winreg.EnumValue(k, i)
            except OSError:
                continue
            if isinstance(v, str):
                vals[n] = v.replace("%USERPROFILE%", userprof).replace("%userprofile%", userprof)
        k.Close()
    except OSError:
        pass
    envs[scope] = vals
facts["env"] = envs

# 6) 磁盘卷信息
raw = ps("Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,DriveType,Size,FreeSpace,VolumeName | ConvertTo-Json -Compress")
try:
    facts["volumes"] = json.loads(raw) or []
except Exception:
    facts["volumes"] = []
if isinstance(facts["volumes"], dict):
    facts["volumes"] = [facts["volumes"]]

(OUT / "raw_facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
print("processes", len(facts["processes"]))
print("services ", len(facts["services"]))
print("tasks    ", len(facts["tasks"]))
print("shortcuts", len(facts["shortcuts"]))
print("env user ", len(envs["user"]), " machine", len(envs["machine"]))
print("volumes  ", [(v.get("DeviceID"), v.get("DriveType")) for v in facts["volumes"]])
