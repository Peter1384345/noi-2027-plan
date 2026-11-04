# -*- coding: utf-8 -*-
"""open_file(等待就绪) -> 补写 6 页插页备注 -> save_file -> close_file v2"""
import json
import re
import subprocess
import time

EDSDK = r"E:\LenovoSoftstore\Install\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit\edsdk.py"
PY = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
BASE = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
SRC = BASE + r"\微光成炬-星火自有燎原时-复件.pptx"
FALLBACK = BASE + r"\output\video_page_notes_fallback.json"
LOG = BASE + r"\output\video_notes_log.txt"
ARGS = BASE + r"\output\vp_args.json"


def call(tool, payload):
    with open(ARGS, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    r = subprocess.run([PY, EDSDK, "call", tool, "--json-file", ARGS], capture_output=True)
    return (r.stdout or b"").decode("utf-8", "replace")


out = []
open_resp = call("open_file", {"file_path": SRC})
out.append("open: " + open_resp[:200])

# 从响应中提取 file_id
m = re.search(r'"file_id"\s*:\s*"([^"]+)"', open_resp)
fid = m.group(1) if m else SRC.replace("\\", "//")
out.append(f"file_id={fid!r}")

time.sleep(6)  # 等待编辑器就绪

with open(FALLBACK, encoding="utf-8") as f:
    items = json.load(f)
for it in items:
    body = call("slide_add_notes", {"file_id": fid, "page_index": it["page_index"], "text": it["text"]})
    ok = '"ok": true' in body or '"ok":true' in body
    out.append(f"notes page[{it['page_index']}] ok={ok} {body[:100]}")

save_resp = call("save_file", {"file_id": fid})
out.append("save: " + save_resp[:200])
out.append("close: " + call("close_file", {"file_id": fid})[:150])

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("DONE")
