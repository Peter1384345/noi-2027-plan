import os, io, time
p = r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-41-24\dragon-raja-story\assets"
out = io.open(r"C:\Users\Administrator\WorkBuddy\2026-09-15-22-41-24\_diag2.txt", "w", encoding="utf-8")
out.write("gen exists: %s\n" % os.path.exists(os.path.join(p, "_gen")))
avs = sorted(f for f in os.listdir(p) if f.startswith("avatar_"))
recent = 0
for f in avs:
    st = os.stat(os.path.join(p, f))
    age_h = (time.time() - st.st_mtime) / 3600
    if age_h < 1:
        recent += 1
    out.write("%s  %.2fh  %dKB\n" % (f, age_h, st.st_size // 1024))
out.write("total avatars: %d, updated in last hour: %d\n" % (len(avs), recent))
out.close()
print("done")
