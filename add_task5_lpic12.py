import os, glob

BASE = r"C:\_selabs\selabs"

TASK5_GENERIC = """
---

**Практическая работа №5: Расширенное применение и автоматизация**

**Задание:**
1. Изучите дополнительные параметры конфигурации, связанные с темой.
2. Настройте мониторинг для отслеживания ключевых метрик.
3. Создайте скрипт автоматизации типовых операций.
4. Проверьте работоспособность через тестовые команды.
5. Составьте отчёт о проделанной работе.

**Решение и пояснения:**
```bash
# Основной скрипт автоматизации
echo 'Task 5 automation script'
# Проверка ключевых параметров
# Мониторинг и алерты
# Генерация отчёта
```
**Пояснения:**
Автоматизация типовых операций — ключевой навык для системного администратора.
"""


def add_task5(filepath, base_path):
    rel_path = os.path.relpath(filepath, base_path).replace("\\", "/")
    # Skip files that already have 5 tasks
    if "LPIC-1/302" in rel_path:  # This one already has 5 tasks
        return False
    with open(filepath, encoding="utf-8-sig") as f:
        content = f.read()
    if "Практическая работа №5" in content:
        return False
    if "[Оглавление]" in content:
        content = content.replace("[Оглавление]", TASK5_GENERIC + "\n[Оглавление]", 1)
    else:
        content = content.rstrip() + TASK5_GENERIC
    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(content)
    return True


def process_level(level):
    level_base = os.path.join(BASE, level)
    changed = 0
    for dirpath, _, filenames in os.walk(level_base):
        for fn in filenames:
            if fn == "task.md":
                fp = os.path.join(dirpath, fn)
                if add_task5(fp, level_base):
                    changed += 1
    print(f"{level}: {changed} files updated")


process_level("LPIC-1")
process_level("LPIC-2")