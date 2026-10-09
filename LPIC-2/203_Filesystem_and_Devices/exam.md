[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 203: Filesystem and Devices

Задачи приближены к реальным заданиям экзамена **201-450**.

## Задача 1. Создание и монтирование ФС

**Условие:** Создайте ext4 на новом разделе, смонтируйте по UUID и настройте автомонтирование.

**Ожидаемый результат:** Раздел монтируется автоматически.

**Решение и пояснения:**
```bash
sudo mkfs.ext4 /dev/sdb1
blkid /dev/sdb1
# /etc/fstab: UUID=<uuid> /mnt/data ext4 defaults 0 2
sudo findmnt --verify
sudo mount -a
findmnt /mnt/data
```
UUID надёжнее имени. `findmnt --verify` проверяет fstab до применения. `mount -a` монтирует все записи. Ошибка в fstab может помешать загрузке — проверяйте перед перезагрузкой.

## Задача 2. Создание swap

**Условие:** Создайте swap-файл 1 ГБ, включите его и добавьте в fstab.

**Ожидаемый результат:** Swap активен и сохраняется после перезагрузки.

**Решение и пояснения:**
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
swapon --show
free -h
# fstab: /swapfile none swap sw 0 0
```
`fallocate` создаёт файл, `mkswap` форматирует, `swapon` включает. Права 600 обязательны. Запись в fstab сохраняет swap после перезагрузки.

## Задача 3. Проверка и восстановление ФС

**Условие:** ФС повреждена после сбоя питания. Проверьте и восстановите её.

**Ожидаемый результат:** ФС проверена и смонтирована.

**Решение и пояснения:**
```bash
sudo umount /dev/sdb1
sudo e2fsck -f -y /dev/sdb1
sudo tune2fs -l /dev/sdb1 | grep -i state
sudo mount /dev/sdb1 /mnt/data
dmesg | grep -i ext4 | tail
```
`e2fsck` проверяет и исправляет ФС (только размонтированную). `-f` форсирует проверку, `-y` отвечает «да». `tune2fs -l` показывает состояние (clean/not clean).

## Задача 4. Работа с XFS и Btrfs

**Условие:** Создайте XFS и Btrfs, выполните базовые операции (информация, проверка, снимок).

**Ожидаемый результат:** ФС созданы и проверены.

**Решение и пояснения:**
```bash
sudo mkfs.xfs /dev/sdb2
sudo xfs_info /dev/sdb2
sudo xfs_repair -n /dev/sdb2        # Проверка (read-only)
sudo mkfs.btrfs /dev/sdb3
sudo mount /dev/sdb3 /mnt/btrfs
sudo btrfs subvolume create /mnt/btrfs/data
sudo btrfs subvolume snapshot /mnt/btrfs/data /mnt/btrfs/data-snap
```
XFS — для больших объёмов и параллельного I/O, проверка `xfs_repair` (только размонтированная). Btrfs — CoW с подтомами и мгновенными снимками.

## Задача 5. Мониторинг дисков SMART

**Условие:** Проверьте здоровье дисков и настройте оповещение о проблемах.

**Ожидаемый результат:** Состояние дисков проверено.

**Решение и пояснения:**
```bash
sudo apt install -y smartmontools
sudo smartctl -H /dev/sda
sudo smartctl -A /dev/sda | grep -iE "Reallocated|Pending"
sudo smartctl -t short /dev/sda
sudo systemctl enable --now smartd
```
SMART предсказывает отказы. `-H` — общее состояние, `-A` — атрибуты (Reallocated_Sector_Ct, Pending_Sector). `smartd` — демон мониторинга с оповещениями.

## Задача 6. Шифрование ФС (LUKS)

**Условие:** Создайте зашифрованный раздел, смонтируйте его и настройте автомонтирование через crypttab.

**Ожидаемый результат:** Зашифрованный раздел работает.

**Решение и пояснения:**
```bash
sudo cryptsetup luksFormat /dev/sdb4
sudo cryptsetup luksOpen /dev/sdb4 cryptdata
sudo mkfs.ext4 /dev/mapper/cryptdata
# /etc/crypttab: cryptdata UUID=<uuid> none luks
# /etc/fstab: /dev/mapper/cryptdata /mnt/crypt ext4 defaults 0 2
sudo mount /dev/mapper/cryptdata /mnt/crypt
```
LUKS шифрует блочное устройство. `luksOpen` создаёт `/dev/mapper/`, crypttab автоматизирует открытие при загрузке (пароль вводится при старте).
