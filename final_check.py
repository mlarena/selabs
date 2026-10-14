import os, glob

BASE = r"C:\_selabs\selabs"

print("=== Итоговая статистика проекта ===\n")

levels = {
    "LPIC-1": "LPIC-1 (101-500, 102-500)",
    "LPIC-2": "LPIC-2 (201-450, 202-450)",
    "LPIC-3-Mixed-Environments": "LPIC-3 Mixed Environments (300-300)",
    "LPIC-3-Security": "LPIC-3 Security (303-300)",
    "LPIC-3-High-Availability-and-Storage-Clusters": "LPIC-3 High Availability (306-300)",
    "LPIC-3-Virtualization-and-Containerization": "LPIC-3 Virtualization (305-300)",
}

for level, desc in levels.items():
    level_base = os.path.join(BASE, level)
    if not os.path.exists(level_base):
        print(f"MISSING: {level}")
        continue
    
    task_files = list(glob.glob(os.path.join(level_base, "**", "task.md"), recursive=True))
    exam_files = list(glob.glob(os.path.join(level_base, "**", "exam.md"), recursive=True))
    home_file = os.path.join(level_base, "home.md")
    has_home = os.path.exists(home_file)
    
    task5_count = 0
    task4_count = 0
    for f in task_files:
        with open(f, encoding="utf-8-sig") as fh:
            c = fh.read()
        count = c.count("Практическая работа №")
        if count >= 5:
            task5_count += 1
        elif count == 4:
            task4_count += 1
    
    print(f"{desc}")
    print(f"  Topics: {len(task_files)} task.md, {len(exam_files)} exam.md")
    print(f"  home.md: {'YES' if has_home else 'NO'}")
    print(f"  Tasks: {task5_count} with 5+, {task4_count} with 4")
    print()