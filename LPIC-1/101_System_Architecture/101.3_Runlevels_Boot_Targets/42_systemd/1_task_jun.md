**Практическая работа №1: Работа с целевыми состояниями (targets)**

**Задание:**
1. Определите текущий целевой режим (target) по умолчанию.
2. Просмотрите список всех доступных targets.
3. Переключитесь в multi-user.target (без графики).
4. Вернитесь обратно в graphical.target.
5. Измените target по умолчанию на multi-user.target.
6. Проверьте зависимости текущего target.

**Решение и пояснения:**
```bash
systemctl get-default                 # 1. Текущий target по умолчанию
systemctl list-units --type=target    # 2. Все загруженные targets
sudo systemctl isolate multi-user.target  # 3. Переключение в консольный режим
sudo systemctl isolate graphical.target   # 4. Возврат в графический режим
sudo systemctl set-default multi-user.target  # 5. Установка по умолчанию
systemctl list-dependencies graphical.target  # 6. Зависимости graphical.target
```
**Пояснения:** Targets в systemd аналогичны runlevels в SysVinit. `multi-user.target` — многопользовательский режим без GUI (уровень 3), `graphical.target` — с GUI (уровень 5). `isolate` переключает текущий режим, `set-default` устанавливает для будущих загрузок. `list-dependencies` показывает иерархию целей и служб.

---

**Практическая работа №2: Управление службами пользователя**

**Задание:**
1. Запустите службу от имени текущего пользователя (user service).
2. Проверьте статус пользовательской службы.
3. Просмотрите все запущенные службы текущего пользователя.
4. Остановите пользовательскую службу.
5. Включите автозапуск пользовательской службы.
6. Проверьте логи пользовательской службы.

**Решение и пояснения:**
```bash
# 1. Создайте простую службу пользователя (пример):
systemctl --user start myapp.service   # Запуск службы (если есть юнит)
systemctl --user status myapp.service  # 2. Статус пользовательской службы
systemctl --user list-units --type=service  # 3. Все пользовательские службы
systemctl --user stop myapp.service    # 4. Остановка
systemctl --user enable myapp.service  # 5. Включение автозапуска
journalctl --user -u myapp.service     # 6. Логи пользовательской службы
```
**Пояснения:** `--user` позволяет управлять службами, запущенными от имени текущего пользователя (не требующими sudo). Пользовательские службы определяются в `~/.config/systemd/user/`. Они запускаются при входе пользователя в систему и управляются его пользовательским экземпляром systemd.

---

**Практическая работа №3: Анализ и устранение проблем служб**

**Задание:**
1. Найдите все службы, завершившиеся с ошибкой.
2. Проанализируйте причину ошибки конкретной службы.
3. Перезапустите службу с повышенным уровнем логирования.
4. Проверьте, какие службы зависят от сетевого подключения.
5. Сбросьте состояние службы после сбоя.
6. Замаскируйте службу, чтобы предотвратить её запуск.

**Решение и пояснения:**
```bash
systemctl --failed                    # 1. Службы с ошибками
journalctl -u failing.service -xe     # 2. Логи ошибки (-xe подробно)
sudo systemctl restart failing.service -l  # 3. Перезапуск с полными логами
systemctl list-dependencies --reverse network.target  # 4. Службы, зависящие от сети
sudo systemctl reset-failed failing.service  # 5. Сброс состояния "failed"
sudo systemctl mask unwanted.service   # 6. Маскировка (невозможно запустить)
sudo systemctl unmask unwanted.service # Снятие маскировки
```
**Пояснения:** `--failed` показывает все юниты, завершившиеся ошибкой. `journalctl -xe` показывает последние ошибки с пояснениями. `list-dependencies --reverse` показывает, какие службы зависят от указанного юнита. `reset-failed` очищает состояние "failed". `mask` создает симлинк на `/dev/null`, делая службу полностью недоступной.

---

**Практическая работа №4: Создание и настройка таймеров (timers)**

**Задание:**
1. Создайте простую службу для периодического выполнения.
2. Создайте таймер для запуска службы каждый час.
3. Активируйте и запустите таймер.
4. Просмотрите все активные таймеры в системе.
5. Проверьте следующее время срабатывания таймера.
6. Измените расписание таймера на ежедневное в 3:00.

**Решение и пояснения:**
```bash
# 1. Создание службы
sudo nano /etc/systemd/system/hourlytask.service
[Service]
Type=oneshot
ExecStart=/usr/local/bin/myscript.sh

# 2. Создание таймера
sudo nano /etc/systemd/system/hourlytask.timer
[Unit]
Description=Запуск задачи каждый час
[Timer]
OnCalendar=hourly
Persistent=true
[Install]
WantedBy=timers.target

sudo systemctl daemon-reload
sudo systemctl enable hourlytask.timer  # 3. Включение автозапуска
sudo systemctl start hourlytask.timer   # 3. Запуск таймера

systemctl list-timers --all            # 4. Все таймеры
systemctl list-timers | grep hourlytask # 5. Проверка следующего запуска
# 6. Изменение на 3:00 ежедневно:
sudo sed -i 's/OnCalendar=hourly/OnCalendar=daily\nOnCalendar=*-*-* 03:00:00/' /etc/systemd/system/hourlytask.timer
sudo systemctl daemon-reload
```
**Пояснения:** Таймеры systemd — современная замена cron. Они состоят из пары файлов: `.service` (что выполнять) и `.timer` (когда выполнять). `OnCalendar` поддерживает гибкие форматы времени. `Persistent=true` выполняет пропущенные запуски (например, после выключения ПК). `timers.target` группирует все таймеры.