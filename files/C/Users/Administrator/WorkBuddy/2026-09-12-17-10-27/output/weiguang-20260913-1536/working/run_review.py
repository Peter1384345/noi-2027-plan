import subprocess, json

PY = r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe"
REVIEW = (
    r"C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\tencent-docx"
    r"\5.5.6-wb.38337834.g5f969292.h7826dc9400fd\skills\html-review\scripts\review_html.py"
)
HTML = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\stage2\formatted-微光成炬-PPT附稿.html"
)
OUT = (
    r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27"
    r"\output\weiguang-20260913-1536\working\review_result.json"
)

r = subprocess.run([PY, REVIEW, "--html", HTML, "--genre", "general"], capture_output=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("RC:" + str(r.returncode) + "\nSTDOUT:\n")
    f.write(r.stdout.decode("utf-8", errors="replace"))
    f.write("\nSTDERR:\n")
    f.write(r.stderr.decode("utf-8", errors="replace"))
