import subprocess, json, os

VENV_PY = r"C:\Users\Administrator\.venv-html-to-docx\Scripts\python.exe"
SCRIPTS = (
    r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docx"
    r"\5.5.6-wb.38337834.g5f969292.h7826dc9400fd\skills\html-to-docx\scripts"
)
HTML = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\stage2\formatted-微光成炬-PPT附稿.html"
)
DOCX = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\stage3\微光成炬-PPT附稿.docx"
)
OUT = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\working\convert_result.json"
)

env = dict(os.environ)
env["PYTHONPATH"] = SCRIPTS
env["PYTHONIOENCODING"] = "utf-8"
r = subprocess.run(
    [VENV_PY, "-m", "html_to_docx", "convert", HTML, "-o", DOCX,
     "--page-size", "A4", "--orientation", "portrait"],
    capture_output=True, cwd=SCRIPTS, env=env,
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("RC:" + str(r.returncode) + "\nSTDOUT:\n")
    f.write(r.stdout.decode("utf-8", errors="replace"))
    f.write("\nSTDERR:\n")
    f.write(r.stderr.decode("utf-8", errors="replace"))
