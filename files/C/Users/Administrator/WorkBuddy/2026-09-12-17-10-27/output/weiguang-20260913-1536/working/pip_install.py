import subprocess

VENV_PY = r"C:\Users\Administrator\.venv-html-to-docx\Scripts\python.exe"
REQ = (
    r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docx"
    r"\5.5.6-wb.38337834.g5f969292.h7826dc9400fd\skills\html-to-docx\scripts\requirements.txt"
)
OUT = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\working\pip_install_result.txt"
)
r = subprocess.run(
    [VENV_PY, "-m", "pip", "install", "--only-binary=:all:",
     "-r", REQ],
    capture_output=True,
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("RC:" + str(r.returncode) + "\nSTDOUT:\n")
    f.write(r.stdout.decode("utf-8", errors="replace"))
    f.write("\nSTDERR:\n")
    f.write(r.stderr.decode("utf-8", errors="replace"))
