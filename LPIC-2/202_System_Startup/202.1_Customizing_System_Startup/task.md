[Оглавление](?file=LPIC-2%2Fhome.md)

**Практическая работа №1: Управление целями systemd**

**Задание:**
1. Определите цель по умолчанию.
2. Переключитесь в аварийный режим и обратно.
3. Посмотрите зависимости цели.
4. Измените цель по умолчанию.
5. Объясните связь целей и runlevels.

**Решение и пояснения:**
```bash
systemctl get-default                       # 1. Цель по умолчанию
sudo systemctl isolate rescue.target        # 2. Режим восстановления
sudo systemctl isolate multi-user.target    # 2. Обратно
systemctl list-dependencies multi-user.target | head   # 3
sudo systemctl set-default multi-user.target            # 4
```
**Пояснения:**
Цели systemd заменяют runlevels: `multi-user.target` ≈ runlevel 3, `graphical.target` ≈ 5, `rescue.target` ≈ 1. `isolate` переключает режим сейчас, `set-default` — при следующей загрузке. `list-dependencies` показывает дерево зависимостей.

---

**Практическая работа №2: Совместимость с SysV init**

**Задание:**
1. Посмотрите скрипты SysV в `/etc/init.d`.
2. Включите службу через `update-rc.d`.
3. Проверьте символические ссылки в rc-каталогах.
4. Отключите службу.
5. Объясните, как systemd обрабатывает SysV-скрипты.

**Решение и пояснения:**
```bash
ls /etc/init.d/                             # 1. SysV-скрипты
sudo update-rc.d cron defaults              # 2. Включение
ls -l /etc/rc3.d/ | grep cron               # 3. Ссылки S..K..
sudo update-rc.d cron disable               # 4. Отключение
systemctl list-unit-files | grep cron       # 5. Статус
```
**Пояснения:**
systemd генерирует юниты из SysV-скриптов через `systemd-sysv-generator`. `update-rc.d` управляет ссылками в `/etc/rc*.d/`. `systemd-delta` показывает, какие юниты переопределены.

---

**Практическая работа №3: Настройка поведения служб**

**Задание:**
1. Посмотрите параметры юнита службы.
2. Создайте override-файл для службы.
3. Измените параметр через `systemctl edit`.
4. Перезагрузите конфигурацию systemd.
5. Проверьте применённые изменения.

**Решение и пояснения:**
```bash
systemctl cat ssh                           # 1. Содержимое юнита
sudo systemctl edit ssh                     # 3. Override (drop-in)
# В редакторе: [Service] Restart=on-failure
sudo systemctl daemon-reload                # 4. Перечитать юниты
systemctl show ssh -p Restart               # 5. Проверка
```
**Пояснения:**
`systemctl edit` создаёт drop-in в `/etc/systemd/system/<unit>.d/override.conf`, не меняя исходный юнит. `daemon-reload` перечитывает конфигурацию. `systemctl show` выводит действующие параметры.

---

**Практическая работа №4: Анализ процесса загрузки**

**Задание:**
1. Посмотрите общее время загрузки.
2. Найдите службы, замедляющие загрузку.
3. Проанализируйте цепочку запуска.
4. Посмотрите журнал текущей загрузки.
5. Объясните, как оптимизировать загрузку.

**Решение и пояснения:**
```bash
systemd-analyze                             # 1. Общее время
systemd-analyze blame | head                # 2. Медленные юниты
systemd-analyze critical-chain               # 3. Критический путь
journalctl -b                               # 4. Журнал загрузки
```
**Пояснения:**
`systemd-analyze blame` показывает время инициализации каждого юнита. `critical-chain` — критический путь загрузки. Оптимизация: отключение ненужных служб, `After`/`Before` упорядочивание, параллельный запуск.
