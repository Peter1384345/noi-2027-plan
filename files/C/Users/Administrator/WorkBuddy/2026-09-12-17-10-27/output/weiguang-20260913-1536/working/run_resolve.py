import subprocess

PY = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SCRIPT = r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docx\5.5.6-wb.38337834.g5f969292.h7826dc9400fd\scripts\wb\local\resolve_output_docx_path.py"

r = subprocess.run(
    [
        PY, SCRIPT,
        "--workspace", r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27",
        "--request-id", "weiguang-20260913-1536",
        "--filename", "微光成炬-PPT附稿.docx",
    ],
    capture_output=True, text=True, encoding="utf-8",
)
out = "STDOUT:\n" + (r.stdout or "") + "\nSTDERR:\n" + (r.stderr or "") + "\nRC:" + str(r.returncode)
open(
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\output\weiguang-20260913-1536\working\resolve_out_utf8.txt",
    "w", encoding="utf-8",
).write(out)
