[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 204: Advanced Storage Device Administration

Задачи приближены к реальным заданиям экзамена **201-450**.

## Задача 1. Создание RAID-массива

**Условие:** Создайте программный RAID 1 из двух дисков, отформатируйте и смонтируйте.

**Ожидаемый результат:** Зеркальный массив работает.

**Решение и пояснения:**
```bash
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
cat /proc/mdstat
sudo mkfs.ext4 /dev/md0
sudo mount /dev/md0 /mnt/raid
sudo mdadm --detail /dev/md0
sudo mdadm --detail --scan >> /etc/mdadm/mdadm.conf
sudo update-initramfs -u
```
RAID 1 — зеркало (отказоустойчивость). `mdadm --create` создаёт массив, `--detail` показывает состояние. Конфигурацию сохраняют в `mdadm.conf` для сборки при загрузке.

## Задача 2. Замена сбойного диска в RAID

**Условие:** Один диск массива отказал. Замените его и восстановите массив.

**Ожидаемый результат:** Массив восстановлен.

**Решение и пояснения:**
```bash
cat /proc/mdstat                       # Диск помечен faulty
sudo mdadm /dev/md0 --fail /dev/sdb --remove /dev/sdb
sudo mdadm /dev/md0 --add /dev/sdd     # Новый диск
cat /proc/mdstat                       # Идёт rebuild
sudo mdadm --detail /dev/md0 | grep -i state
```
Отказ диска помечается `faulty`. `--fail`/`--remove` исключают диск, `--add` добавляет новый, начинается ребилд. RAID 1/5/6 переживают отказ без потери данных.

## Задача 3. Создание и расширение LVM

**Условие:** Создайте VG из двух дисков, LV на 100 МБ, затем расширьте LV и ФС.

**Ожидаемый результат:** LV расширен.

**Решение и пояснения:**
```bash
sudo pvcreate /dev/sdb /dev/sdc
sudo vgcreate vgdata /dev/sdb /dev/sdc
sudo lvcreate -L 100M -n lvdata vgdata
sudo mkfs.ext4 /dev/vgdata/lvdata
sudo mount /dev/vgdata/lvdata /mnt/lvm
sudo lvextend -L +50M -r /dev/vgdata/lvdata   # -r: resize ФС
df -h /mnt/lvm
```
LVM: PV → VG → LV. `lvextend -r` расширяет LV и ФС. Гибкость LVM — возможность менять размеры и добавлять диски без простоя.

## Задача 4. Снимок LVM для бэкапа

**Условие:** Создайте снимок LV и сделайте согласованный бэкап без остановки сервиса.

**Ожидаемый результат:** Бэкап создан из снимка.

**Решение и пояснения:**
```bash
sudo lvcreate -L 100M -s -n lvdata_snap /dev/vgdata/lvdata
sudo mkdir -p /mnt/snap && sudo mount /dev/vgdata/lvdata_snap /mnt/snap
tar -czf /backup/lvdata.tar.gz /mnt/snap
sudo umount /mnt/snap && sudo lvremove /dev/vgdata/lvdata_snap
```
Снимок фиксирует состояние тома (CoW). Бэкап делается из снимка, пока сервис работает. После бэкапа снимок удаляют, чтобы не расходовать место.

## Задача 5. Настройка доступа к устройству хранения

**Условие:** Ограничьте доступ к диску по WWID и настройте планировщик I/O для SSD.

**Ожидаемый результат:** Настройки применены.

**Решение и пояснения:**
```bash
lsblk -d -o NAME,ROTA,MODEL
cat /sys/block/sda/queue/scheduler
echo none | sudo tee /sys/block/nvme0n1/queue/scheduler
# Постоянно: /etc/udev/rules.d/60-iosched.rules
# ACTION=="add|change", KERNEL=="nvme0n1", ATTR{queue/scheduler}="none"
sudo udevadm control --reload && sudo udevadm trigger
```
`ROTA=0` — SSD. Для NVMe оптимален планировщик `none`, для HDD — `bfq`/`mq-deadline`. Правила udev применяют настройки постоянно.

## Задача 6. iSCSI: подключение удалённого хранилища

**Условие:** Настройте iSCSI-инициатор и подключите удалённый LUN.

**Ожидаемый результат:** Удалённое устройство доступно.

**Решение и пояснения:**
```bash
sudo apt install -y open-iscsi
sudo systemctl enable --now iscsid
sudo iscsiadm -m discovery -t sendtargets -p 192.168.1.10
sudo iscsiadm -m node --login
lsblk
sudo iscsiadm -m session
```
iSCSI передаёт блочные устройства по TCP/IP (SAN). `iscsiadm` управляет обнаружением и подключением. LUN появляется как локальное блочное устройство. Автозагрузка — `iscsiadm -m node --op update -n node.startup -v automatic`.
