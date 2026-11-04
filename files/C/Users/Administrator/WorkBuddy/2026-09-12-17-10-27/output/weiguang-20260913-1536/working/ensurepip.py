import subprocess

VENV_PY = r"C:\Users\Administrator\.venv-html-to-docx\Scripts\python.exe"
OUT = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\working\ensurepip_result.txt"
)
steps = [
    [VENV_PY, "-m", "ensurepip", "--upgrade"],
]
log = ""
for cmd in steps:
    r = subprocess.run(cmd, capture_output=True)
    log += "CMD:" + " ".join(cmd) + "\nRC:" + str(r.returncode) + "\nSTDOUT:\n"
    log += r.stdout.decode("utf-8", errors="replace")
    log += "\nSTDERR:\n" + r.stderr.decode("utf-8", errors="replace") + "\n\n"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(log)
