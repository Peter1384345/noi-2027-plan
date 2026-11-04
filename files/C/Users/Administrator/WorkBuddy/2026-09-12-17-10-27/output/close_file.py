# -*- coding: utf-8 -*-
"""关闭 edsdk 中打开的《微光成炬》复件，释放编辑锁。"""
import subprocess

EDSDK = r"E:\LenovoSoftstore\Install\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit\edsdk.py"
PY = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
FILE_ID = "C://Users//Administrator//WorkBuddy//2026-09-12-17-10-27//微光成炬-星火自有燎原时-复件.pptx"
LOG = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\close_log.txt"

out_lines = []
for tool in ["close_file"]:
    r = subprocess.run([PY, EDSDK, "call", tool, "--json-file", "-"], capture_output=True)
    out_lines.append(f"[{tool}] rc={r.returncode} out={(r.stdout or b'').decode('utf-8', 'replace')} err={(r.stderr or b'').decode('utf-8', 'replace')}")

# close_file 需要 json 参数，改用 stdin 传参可能不支持，退回临时文件方式
import json, os
args_file = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\close_args.json"
with open(args_file, "w", encoding="utf-8") as f:
    json.dump({"file_id": FILE_ID}, f, ensure_ascii=False)
r = subprocess.run([PY, EDSDK, "call", "close_file", "--json-file", args_file], capture_output=True)
out_lines.append(f"[close_file retry] rc={r.returncode} out={(r.stdout or b'').decode('utf-8', 'replace')} err={(r.stderr or b'').decode('utf-8', 'replace')}")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("DONE")
