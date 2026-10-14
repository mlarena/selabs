import os

BASE = r"C:\_selabs\selabs"

ha_base = os.path.join(BASE, "LPIC-3-High-Availability-and-Storage-Clusters")
ha_topics = {
    "306.1_Clustering_Fundamentals": "Основы кластеризации",
    "306.2_Corosync_and_Pacemaker": "Corosync и Pacemaker",
    "306.3_NFS_and_Distributed_Filesystems": "NFS и распределённые файловые системы",
    "306.4_DRBD_and_Storage_Replication": "DRBD и репликация хранилищ",
    "306.5_Cluster_Monitoring_and_Maintenance": "Мониторинг и обслуживание кластеров",
}

home_lines = ["# LPIC-3 306: High Availability and Storage Clusters\n", "\n", "## Навигация\n", "\n", "[Оглавление проекта](../home.md)\n", "\n", "## Темемы\n", "\n"]

for topic_dir, topic_name in ha_topics.items():
    topic_path = os.path.join(ha_base, topic_dir)
    os.makedirs(topic_path, exist_ok=True)
    
    # exam.md
    exam = f"# {topic_name} ({topic_dir})\n\n[Оглавление экзамена](../home.md)\n\n## Содержание\n\nОписание темы: {topic_name}\n"
    with open(os.path.join(topic_path, "exam.md"), "w", encoding="utf-8-sig") as f:
        f.write(exam)
    
    # task.md
    task = f"""[Оглавление](../home.md)

**Практическая работа №1: Базовые операции по теме {topic_name}**

**Задание:**
1. Изучите основные концепции {topic_name}.
2. Определите ключевые компоненты и их назначение.
3. Проверьте наличие необходимых пакетов.
4. Выполните базовую настройку.
5. Проверьте работоспособность.

**Решение и пояснения:**
```bash
# Изучение темы
man {topic_dir.lower().split('_')[0]}
dpkg -l | grep {topic_dir.lower().split('.')[1][:5]}
```
**Пояснения:**
Изучение основ — первый шаг к глубокому пониманию темы.

---

**Практическая работа №2: Конфигурация {topic_name}**

**Задание:**
1. Создайте конфигурационный файл.
2. Настройте основные параметры.
3. Примените конфигурацию.
4. Проверьте синтаксис.
5. Запустите сервис.

**Решение и пояснения:**
```bash
sudo nano /etc/
sudo systemctl restart
systemctl status
```
**Пояснения:**
Конфигурация — ключевой навык администратора.

---

**Практическая работа №3: Диагностика и устранение проблем**

**Задание:**
1. Проверьте логи службы.
2. Используйте утилиты диагностики.
3. Смоделируйте типичную проблему.
4. Устраните проблему.
5. Проверьте работоспособность.

**Решение и пояснения:**
```bash
journalctl -u
sudo dmesg | tail
```
**Пояснения:**
Диагностика — критически важный навык.

---

**Практическая работа №4: Оптимизация и настройка производительности**

**Задание:**
1. Измерьте базовые метрики.
2. Определите узкие места.
3. Примените оптимизации.
4. Проверьте эффект.
5. Задокументируйте изменения.

**Решение и пояснения:**
```bash
perf stat -a sleep 10
iostat -x 1 5
```
**Пояснения:**
Оптимизация на основе данных.

---

**Практическая работа №5: Автоматизация и мониторинг**

**Задание:**
1. Создайте скрипт мониторинга.
2. Настройте алерты.
3. Автоматизируйте рутинные операции.
4. Настройте резервное копирование.
5. Проверьте работу скриптов.

**Решение и пояснения:**
```bash
#!/bin/bash
echo 'Monitoring and automation for {topic_name}'
```
**Пояснения:**
Автоматизация снижает риск человеческих ошибок.

---

[Оглавление](../home.md)
"""
    with open(os.path.join(topic_path, "task.md"), "w", encoding="utf-8-sig") as f:
        f.write(task)
    
    home_lines.append(f"- [{topic_name}](./{topic_dir}/exam.md) | [Задачи](./{topic_dir}/task.md)\n")

with open(os.path.join(ha_base, "home.md"), "w", encoding="utf-8-sig") as f:
    f.writelines(home_lines)

print("Created LPIC-3-High-Availability-and-Storage-Clusters with", len(ha_topics), "topics")