[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 201: Linux Kernel

Задачи приближены к реальным заданиям экзамена **201-450**.

## Задача 1. Анализ компонентов ядра

**Условие:** Определите версию ядра, список загруженных модулей и параметры конкретного модуля.

**Ожидаемый результат:** Информация о ядре получена.

**Решение и пояснения:**
```bash
uname -r
lsmod | head
modinfo e1000
cat /proc/version
ls /lib/modules/$(uname -r)/
```
`uname -r` — версия, `lsmod` — загруженные модули, `modinfo` — параметры модуля. Модули хранятся в `/lib/modules/<версия>/`. Ядро может быть монолитным со сменными модулями.

## Задача 2. Управление модулями ядра

**Условие:** Загрузите модуль, выгрузите его и настройте автоматическую загрузку при старте.

**Ожидаемый результат:** Модуль загружается автоматически.

**Решение и пояснения:**
```bash
sudo modprobe dummy
lsmod | grep dummy
sudo modprobe -r dummy
# /etc/modules-load.d/dummy.conf: dummy
sudo systemctl restart systemd-modules-load
# Параметры: /etc/modprobe.d/dummy.conf: options dummy numdummies=2
```
`modprobe` учитывает зависимости, `modprobe -r` выгружает. Автозагрузка — `/etc/modules-load.d/`, параметры — `/etc/modprobe.d/`, blacklist запрещает загрузку.

## Задача 3. Компиляция ядра

**Условие:** Опишите процесс сборки ядра из исходников с включением новой функции.

**Ожидаемый результат:** Ядро собрано и установлено.

**Решение и пояснения:**
```bash
sudo apt install -y build-essential libncurses-dev flex bison libssl-dev
cd /usr/src/linux-6.x
make menuconfig                  # Настройка
make -j$(nproc)                  # Сборка
sudo make modules_install
sudo make install
sudo update-initramfs -c -k $(make kernelrelease)
sudo update-grub
```
`menuconfig` настраивает, `make -j` собирает параллельно. `modules_install`/`install` устанавливают модули и ядро. `update-initramfs` и `update-grub` завершают установку.

## Задача 4. Runtime-параметры ядра

**Условие:** Измените параметр ядра на работающей системе, сделайте его постоянным и примените параметр при загрузке.

**Ожидаемый результат:** Параметр применён.

**Решение и пояснения:**
```bash
sysctl net.ipv4.ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-forward.conf
sudo sysctl --system
# Параметр загрузчика: /etc/default/grub: GRUB_CMDLINE_LINUX="..."
sudo update-grub
```
`sysctl -w` меняет на лету, `/etc/sysctl.d/` — постоянно. Параметры загрузчика (в GRUB) применяются к ядру при старте. `sysctl -a` показывает все параметры.

## Задача 5. Устранение проблем с ядром

**Условие:** После обновления ядро не загружается. Загрузите предыдущее ядро и устраните проблему.

**Ожидаемый результат:** Система загружена со стабильным ядром.

**Решение и пояснения:**
```text
1. В меню GRUB выбрать "Advanced options" -> предыдущее ядро
2. Загрузиться, проверить: uname -r
3. Диагностика: journalctl -b -p err ; dmesg | grep -i error
4. Удалить проблемное ядро или переустановить модули:
   sudo apt install --reinstall linux-image-<версия>
5. sudo update-grub
```
Возможность загрузить старое ядро — критична. `journalctl -b`/`dmesg` показывают ошибки загрузки. Проблемы часто связаны с модулями (например, отсутствующими после обновления).
