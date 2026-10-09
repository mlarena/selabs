[Оглавление](LPIC-2home.md)

# Экзаменационные боевые задачи — Тема 202: System Startup

Задачи приближены к реальным заданиям экзамена **201-450**.

## Задача 1. Настройка целевого юнита загрузки

**Условие:** Настройте сервер на загрузку в многопользовательском режиме без графики и проверьте текущую цель.

**Ожидаемый результат:** Цель по умолчанию изменена.

**Решение и пояснения:**
```bash
systemctl get-default
sudo systemctl set-default multi-user.target
systemctl list-units --type=target
sudo systemctl isolate multi-user.target
systemctl get-default
```
`set-default` задаёт цель загрузки (симлинк `default.target`). `isolate` переключает немедленно. Графическая цель — `graphical.target`, без графики — `multi-user.target`.

## Задача 2. Создание пользовательского сервиса

**Условие:** Создайте systemd-юнит для собственного приложения, включите автозапуск и проверьте.

**Ожидаемый результат:** Сервис запускается автоматически.

**Решение и пояснения:**
```bash
sudo tee /etc/systemd/system/myapp.service >/dev/null <<'EOF'
[Unit]
Description=My App
After=network.target
[Service]
ExecStart=/usr/local/bin/myapp
Restart=on-failure
User=nobody
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now myapp
systemctl status myapp
```
`[Unit]` описывает зависимости, `[Service]` — команду запуска, `[Install]` — цель автозапуска. `daemon-reload` перечитывает юниты, `enable` включает автозапуск.

## Задача 3. Восстановление системы

**Условие:** Система загрузилась, но служба входа недоступна. Восстановите доступ через rescue-режим.

**Ожидаемый результат:** Доступ восстановлен.

**Решение и пояснения:**
```text
1. Загрузиться в rescue.target (через GRUB: systemd.unit=rescue.target)
2. Ввести пароль root
3. mount -o remount,rw /   (если нужно)
4. Проверить службу: systemctl status <service>
5. Исправить конфигурацию, перезапустить
6. systemctl default / reboot
```
Rescue-режим загружает минимум служб. `emergency.target` — ещё минимальнее (только корневая ФС). Используется при поломке критичных служб.

## Задача 4. Сброс пароля root

**Условие:** Пароль root утерян. Восстановите доступ.

**Ожидаемый результат:** Пароль root сброшен.

**Решение и пояснения:**
```text
1. В GRUB нажать e, добавить к строке ядра: init=/bin/bash
2. Ctrl+X для загрузки
3. mount -o remount,rw /
4. passwd root
5. Смонтировать /usr при необходимости: mount -o remount,rw /usr
6. exec /sbin/init   (или reboot -f)
```
`init=/bin/bash` запускает оболочку вместо init. `remount,rw` даёт запись. Мера защиты — пароль на GRUB (`grub-mkpasswd-pbkdf2`).

## Задача 5. Альтернативные загрузчики

**Условие:** Опишите установку и настройку альтернативного загрузчика (LILO/EXTLINUX) и сравните с GRUB.

**Ожидаемый результат:** Продемонстрировано понимание альтернатив.

**Решение и пояснения:**
```bash
sudo apt install -y extlinux syslinux
sudo extlinux --install /boot/extlinux
# /boot/extlinux/extlinux.conf: LABEL, KERNEL, APPEND
sudo dd if=/usr/lib/syslinux/mbr/mbr.bin of=/dev/sda bs=440 count=1
```
EXTLINUX/SYSLINUX — легковесные загрузчики. LILO устарел (не поддерживает современные ФС/меню). GRUB 2 — стандарт, поддерживает скрипты, меню, множество ФС. Альтернативы применяют в embeded и особых случаях.

## Задача 6. Анализ и оптимизация загрузки

**Условие:** Определите время загрузки и найдите службы, которые можно отключить.

**Ожидаемый результат:** Время загрузки проанализировано.

**Решение и пояснения:**
```bash
systemd-analyze
systemd-analyze blame | head -15
systemd-analyze critical-chain
systemctl list-unit-files --state=enabled
sudo systemctl disable <service>
```
`systemd-analyze` показывает общее время, `blame` — вклад каждого юнита, `critical-chain` — критический путь. Отключение ненужных служб ускоряет загрузку и снижает поверхность атаки.
