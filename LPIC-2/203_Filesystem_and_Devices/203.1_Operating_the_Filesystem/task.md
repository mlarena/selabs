[Оглавление](LPIC-2home.md)

**Практическая работа №1: Работа с fstab**

**Задание:**
1. Посмотрите текущий `/etc/fstab`.
2. Определите UUID корневого раздела.
3. Добавьте запись для монтирования по UUID.
4. Проверьте синтаксис без перезагрузки.
5. Смонтируйте всё из fstab.

**Решение и пояснения:**
```bash
cat /etc/fstab                        # 1. Текущие записи
blkid /dev/sda2                       # 2. UUID раздела
# Добавить: UUID=<uuid> /mnt/data ext4 defaults 0 2
sudo findmnt --verify                 # 4. Проверка синтаксиса
sudo mount -a                         # 5. Монтирование всего
```
**Пояснения:**
`/etc/fstab` описывает ФС для автомонтирования при загрузке. Использование UUID надёжнее имён устройств. `findmnt --verify` проверяет корректность, `mount -a` монтирует все записи (кроме `noauto`).

---

**Практическая работа №2: Swap: разделы и файлы**

**Задание:**
1. Посмотрите активные области подкачки.
2. Создайте swap-файл.
3. Включите и отключите swap.
4. Добавьте swap в fstab.
5. Настройте приоритеты swap.

**Решение и пояснения:**
```bash
swapon --show                         # 1. Активные области
sudo fallocate -l 512M /swapfile      # 2. Swap-файл
sudo chmod 600 /swapfile && sudo mkswap /swapfile
sudo swapon /swapfile                 # 3. Включение
sudo swapoff /swapfile                # 3. Отключение
# В fstab: /swapfile none swap sw,pri=10 0 0
```
**Пояснения:**
Swap расширяет память на диск. `mkswap` форматирует область, `swapon`/`swapoff` включают/отключают. Приоритет (`pri=`) определяет порядок использования областей. `free -h` показывает использование swap.

---

**Практическая работа №3: systemd mount units**

**Задание:**
1. Посмотрите сгенерированные mount-юниты.
2. Создайте собственный mount-юнит.
3. Включите и запустите его.
4. Проверьте статус монтирования.
5. Объясните связь fstab и systemd.

**Решение и пояснения:**
```bash
systemctl list-units --type=mount              # 1. Mount-юниты
sudo tee /etc/systemd/system/mnt-data.mount >/dev/null <<'EOF'
[Unit]
Description=Data mount
[Mount]
What=/dev/sdb1
Where=/mnt/data
Type=ext4
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now mnt-data.mount      # 3. Запуск
systemctl status mnt-data.mount                 # 4. Статус
```
**Пояснения:**
systemd генерирует mount-юниты из `/etc/fstab` через `systemd-fstab-generator`. Имя юнита — путь монтирования с заменой `/` на `-`. Можно создавать свои `.mount`-юниты для гибкого управления.

---

**Практическая работа №4: Идентификация ФС и монтирование**

**Задание:**
1. Выведите информацию обо всех блочных устройствах.
2. Посмотрите UUID и LABEL разделов.
3. Смонтируйте ФС по LABEL.
4. Проверьте точку монтирования.
5. Размонтируйте и проверьте `sync`.

**Решение и пояснения:**
```bash
lsblk -f                              # 1-2. Дерево с ФС, UUID, LABEL
sudo e2label /dev/sdb1 data           # Установить LABEL
sudo mount LABEL=data /mnt/data       # 3. Монтирование по LABEL
findmnt /mnt/data                     # 4. Проверка
sync && sudo umount /mnt/data         # 5. Сброс буферов и размонтирование
```
**Пояснения:**
`lsblk -f` показывает ФС, UUID и метки. Монтировать можно по устройству, UUID или LABEL. `sync` сбрасывает буферы на диск перед размонтированием. `umount` завершает монтирование (требуется, если ФС не занята).
