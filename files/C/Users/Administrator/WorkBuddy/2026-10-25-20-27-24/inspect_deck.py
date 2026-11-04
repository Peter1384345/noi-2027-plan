# -*- coding: utf-8 -*-
import sys, io, zipfile, collections
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation

D = "D:/桌面/总文件夹/资料整合/"

def dump(path):
    print("=" * 70)
    print(path)
    prs = Presentation(path)
    sl = prs.slides
    print("页数:", len(sl))
    for i, s in enumerate(sl, 1):
        texts = []
        for sh in s.shapes:
            if sh.has_text_frame:
                t = sh.text_frame.text.replace("\n", " / ").strip()
                if t:
                    texts.append(t)
        print(f"P{i:02d} | " + " || ".join(texts)[:150])
    # zip duplicate check
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        c = collections.Counter(names)
        dup = [k for k, v in c.items() if v > 1]
        print("ZIP 重名条目:", dup if dup else "无")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        dump(D + p)
