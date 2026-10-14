import os, glob

BASE = r"C:\_selabs\selabs"
sec_base = os.path.join(BASE, "LPIC-3-Security")
for dirpath, _, filenames in os.walk(sec_base):
    for fn in filenames:
        if fn == "task.md":
            fp = os.path.join(dirpath, fn)
            with open(fp, encoding="utf-8-sig") as f:
                c = f.read()
            count = c.count("Практическая работа №")
            print(f"{count} - {os.path.relpath(fp, BASE)}")