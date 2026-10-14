import os, glob, sys
base = sys.argv[1] if len(sys.argv) > 1 else r"C:\_selabs\selabs\LPIC-3-Mixed-Environments"
files = glob.glob(os.path.join(base, "**", "task.md"), recursive=True)
count = 0
for f in files:
    with open(f, encoding="utf-8") as fh:
        c = fh.read()
    if "Задача 5" not in c and "Практическая работа №5" not in c:
        c += "\n\n---\n\n## Задача 5: Расширенное применение\n\n1. Создайте скрипт для автоматизации рутинных операций.\n2. Протестируйте работу в различных сценариях.\n3. Настройте логирование и мониторинг выполнения.\n"
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(c)
        count += 1
print("Added task 5 to", count, "of", len(files), "files")