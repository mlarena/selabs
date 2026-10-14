import os, glob

BASE = r"C:\_selabs\selabs"

for level in ["LPIC-1", "LPIC-2"]:
    level_base = os.path.join(BASE, level)
    total = 0
    with_4 = 0
    with_5 = 0
    for dirpath, _, filenames in os.walk(level_base):
        for fn in filenames:
            if fn == "task.md":
                fp = os.path.join(dirpath, fn)
                with open(fp, encoding="utf-8-sig") as f:
                    c = f.read()
                count = c.count("Практическая работа №")
                total += 1
                if count == 4:
                    with_4 += 1
                elif count == 5:
                    with_5 += 1
    print(f"{level}: total={total}, 4-tasks={with_4}, 5-tasks={with_5}")