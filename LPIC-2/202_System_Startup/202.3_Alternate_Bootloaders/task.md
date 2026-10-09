[Оглавление](LPIC-2home.md)

**Практическая работа №1: Знакомство с альтернативными загрузчиками**

**Задание:**
1. Установите пакеты SYSLINUX.
2. Посмотрите файлы `isolinux.bin`, `pxelinux.0`.
3. Найдите примеры конфигураций.
4. Определите, где применяется каждый загрузчик.
5. Объясните разницу между SYSLINUX, ISOLINUX и PXELINUX.

**Решение и пояснения:**
```bash
sudo apt install -y syslinux syslinux-common extlinux
dpkg -L syslinux-common | grep -E "isolinux.bin|pxelinux.0"
ls /usr/lib/syslinux/modules/bios/
```
**Пояснения:**
SYSLINUX — для загрузки с FAT/USB, ISOLINUX — с CD/DVD (ISO9660), PXELINUX — по сети (PXE). EXTLINUX — для ext2/3/4. Все используют общий формат конфигурации (`.cfg`).

---

**Практическая работа №2: Загрузка по сети (PXE)**

**Задание:**
1. Объясните принцип работы PXE.
2. Установите TFTP-сервер.
3. Разместите `pxelinux.0` и конфигурацию.
4. Настройте DHCP с опцией 66/67.
5. Опишите последовательность PXE-загрузки.

**Решение и пояснения:**
```bash
sudo apt install -y tftpd-hpa
sudo mkdir -p /srv/tftp/pxelinux.cfg
sudo cp /usr/lib/PXELINUX/pxelinux.0 /srv/tftp/
# /etc/dhcp/dhcpd.conf:
# next-server <tftp_ip>; filename "pxelinux.0";
```
**Пояснения:**
PXE: клиент получает IP по DHCP с опцией `next-server` (TFTP) и `filename` (загрузчик), скачивает загрузчик и конфигурацию по TFTP, затем ядро/initrd. Для UEFI используются `shim.efi`/`grubx64.efi`.

---

**Практическая работа №3: systemd-boot**

**Задание:**
1. Проверьте наличие systemd-boot.
2. Посмотрите структуру ESP.
3. Опишите формат конфигурации systemd-boot.
4. Установите systemd-boot (осторожно).
5. Сравните systemd-boot и GRUB.

**Решение / Описание:**
```bash
bootctl status                              # 1. Статус systemd-boot
ls /boot/efi/EFI/                           # 2. ESP
# /boot/efi/loader/entries/debian.conf:
# title Debian
# linux /vmlinuz-<ver>
# initrd /initrd.img-<ver>
sudo bootctl install                        # 4. Установка
```
**Пояснения:**
systemd-boot — простой UEFI-загрузчик, конфигурации в `/boot/efi/loader/entries/*.conf`. Легче GRUB, но поддерживает только UEFI и ограничен по функциям (нет скриптов, меньше поддержки ФС).

---

**Практическая работа №4: U-Boot (awareness)**

**Задание:**
1. Объясните назначение U-Boot.
2. Назовите типовые архитектуры, где применяется U-Boot.
3. Опишите переменные окружения U-Boot.
4. Приведите пример команды загрузки ядра.
5. Сравните U-Boot и GRUB.

**Решение / Описание:**
```text
# U-Boot используется на ARM/embedded (Raspberry Pi, роутеры, платы)
# Переменные: bootargs, bootcmd, ipaddr, serverip
# Загрузка:
# setenv bootargs 'root=/dev/mmcblk0p2 rw'
# fatload mmc 0:1 0x8000 zImage
# bootz 0x8000
```
**Пояснения:**
U-Boot — загрузчик для встраиваемых систем (ARM, MIPS, RISC-V), поддерживает сеть, USB, различные ФС. GRUB ориентирован на x86/PC. U-Boot настраивается переменными окружения и часто используется вместе с Device Tree.
