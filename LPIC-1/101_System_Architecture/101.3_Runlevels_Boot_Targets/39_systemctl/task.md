**Практическая работа №1: Базовое управление службами**

**Задание:**
1. Просмотрите статус службы SSH.
2. Остановите службу SSH.
3. Запустите службу SSH.
4. Перезапустите службу SSH.
5. Перезагрузите конфигурацию службы без остановки.
6. Проверьте, запущена ли служба.

**Решение и пояснения:**
```bash
sudo systemctl status ssh         # 1. Статус службы (активна/не активна, логи)
sudo systemctl stop ssh           # 2. Остановка службы
sudo systemctl start ssh          # 3. Запуск службы
sudo systemctl restart ssh        # 4. Перезапуск службы
sudo systemctl reload ssh         # 5. Перезагрузка конфигурации (если поддерживается)
systemctl is-active ssh           # 6. Проверка активности (возвращает active/inactive)
```
**Пояснения:** `status` показывает состояние службы, последние логи, PID. `stop`/`start`/`restart` управляют жизненным циклом службы. `reload` применяет изменения конфигурации без остановки службы (если служба поддерживает). `is-active` возвращает код состояния для использования в скриптах.

---

**Практическая работа №2: Управление автозагрузкой**

**Задание:**
1. Проверьте, добавлена ли служба SSH в автозагрузку.
2. Отключите автозагрузку службы SSH.
3. Включите автозагрузку службы SSH.
4. Просмотрите все службы, добавленные в автозагрузку.
5. Запретите службе запускаться при загрузке, но не останавливайте сейчас.
6. Проверьте, включена ли автозагрузка.

**Решение и пояснения:**
```bash
systemctl is-enabled ssh          # 1. Проверка автозагрузки (enabled/disabled)
sudo systemctl disable ssh        # 2. Отключение автозагрузки
sudo systemctl enable ssh         # 3. Включение автозагрузки
systemctl list-unit-files --type=service | grep enabled  # 4. Все службы в автозагрузке
sudo systemctl mask ssh           # 5. Полное отключение (даже от зависимостей)
systemctl unmask ssh              # Отмена маскировки
```
**Пояснения:** `enable`/`disable` управляют автозапуском при загрузке, но не влияют на текущее состояние службы. `is-enabled` проверяет статус автозагрузки. `mask` делает службу полностью недоступной для запуска (в отличие от `disable`). `list-unit-files` показывает все службы и их статус автозагрузки.

---

**Практическая работа №3: Анализ и мониторинг служб**

**Задание:**
1. Просмотрите все запущенные службы.
2. Найдите службы, которые завершились с ошибкой.
3. Просмотрите логи конкретной службы за последний час.
4. Отслеживайте логи службы в реальном времени.
5. Просмотрите зависимости службы.
6. Проверьте, сколько памяти использует служба.

**Решение и пояснения:**
```bash
systemctl list-units --type=service --state=running  # 1. Все запущенные службы
systemctl --failed                  # 2. Службы с ошибками
sudo journalctl -u ssh --since "1 hour ago"  # 3. Логи службы за последний час
sudo journalctl -u ssh -f           # 4. Режим слежения (follow)
systemctl list-dependencies ssh     # 5. Зависимости службы
systemctl show ssh -p MemoryCurrent | cut -d= -f2  # 6. Память службы в байтах
```
**Пояснения:** `list-units` показывает все загруженные юниты. `--failed` фильтрует только сбойные службы. `journalctl -u` показывает логи конкретной службы. `-f` следит за новыми записями. `list-dependencies` показывает, от каких юнитов зависит служба. `show -p MemoryCurrent` показывает текущее использование памяти.

---

**Практическая работа №4: Создание и редактирование служб**

**Задание:**
1. Создайте простой скрипт для автоматизации.
2. Создайте unit-файл systemd для этого скрипта.
3. Включите и запустите созданную службу.
4. Измените параметры службы (например, добавить зависимость от сети).
5. Перезагрузите конфигурацию systemd.
6. Удалите созданную службу.

**Решение и пояснения:**
```bash
# 1. Создание скрипта
echo '#!/bin/bash' > /usr/local/bin/myscript.sh
echo 'echo "Скрипт запущен $(date)" >> /var/log/myscript.log' >> /usr/local/bin/myscript.sh
sudo chmod +x /usr/local/bin/myscript.sh

# 2. Создание unit-файла
sudo nano /etc/systemd/system/myscript.service
[Unit]
Description=Мой тестовый скрипт
After=network.target
[Service]
ExecStart=/usr/local/bin/myscript.sh
[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload      # 4. Перезагрузка конфигурации
sudo systemctl enable myscript    # 3. Включение автозагрузки
sudo systemctl start myscript     # 3. Запуск сейчас
sudo systemctl status myscript    # Проверка

# 5. Удаление службы
sudo systemctl stop myscript
sudo systemctl disable myscript
sudo rm /etc/systemd/system/myscript.service
sudo systemctl daemon-reload
```
**Пояснения:** Unit-файлы в `/etc/systemd/system/` определяют службы. `[Unit]` содержит описание и зависимости, `[Service]` — как запускать, `[Install]` — как включать в автозагрузку. `daemon-reload` нужно выполнять после создания или изменения unit-файлов. `WantedBy=multi-user.target` означает запуск службы в многопользовательском режиме.