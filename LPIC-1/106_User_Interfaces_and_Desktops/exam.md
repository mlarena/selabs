[Оглавление](LPIC-1home.md)

# Экзаменационные боевые задачи — Тема 106: User Interfaces and Desktops

Задачи приближены к реальным заданиям экзамена **102-500**.

## Задача 1. Проверка и настройка X11

**Условие:** Определите, работает ли X-сервер, посмотрите используемый дисплей и проверьте конфигурацию.

**Ожидаемый результат:** Информация о X-сервере получена.

**Решение и пояснения:**
```bash
echo $DISPLAY
ls /tmp/.X11-unix/
loginctl show-session $(loginctl | awk '/seat/{print $1}') -p Type
cat /etc/X11/xorg.conf 2>/dev/null || echo "автоконфигурация"
xdpyinfo | head          # Информация о дисплее (если запущен)
```
`$DISPLAY` — адрес дисплея (обычно `:0`). Xorg может работать без `xorg.conf` (автоконфигурация). `xdpyinfo` показывает параметры экрана.

## Задача 2. Настройка X11 через конфигурацию

**Условие:** Создайте конфигурацию Xorg, задающую разрешение экрана и раскладку клавиатуры.

**Ожидаемый результат:** Создан файл конфигурации Xorg.

**Решение и пояснения:**
```bash
# /etc/X11/xorg.conf.d/10-monitor.conf:
# Section "Monitor" Identifier "Monitor0" EndSection
# Section "Screen" Identifier "Screen0"
#   Monitor "Monitor0" SubSection "Display" Modes "1920x1080" EndSubSection
# EndSection
# 10-keyboard.conf:
# Section "InputClass" Identifier "keyboard"
#   Option "XkbLayout" "us,ru" Option "XkbOptions" "grp:alt_shift_toggle"
# EndSection
```
Файлы в `/etc/X11/xorg.conf.d/` применяются по алфавиту. Монитор/экран задают разрешение, InputClass — устройства ввода и раскладки.

## Задача 3. Выбор и настройка графической среды

**Условие:** Определите установленную графическую среду и менеджер дисплея, смените менеджер дисплея.

**Ожидаемый результат:** Информация получена, менеджер изменён.

**Решение и пояснения:**
```bash
echo $XDG_CURRENT_DESKTOP
systemctl status display-manager
cat /etc/X11/default-display-manager
sudo dpkg-reconfigure lightdm     # Смена менеджера дисплея
```
`XDG_CURRENT_DESKTOP` показывает среду (GNOME, KDE, XFCE). `display-manager` — служба входа. Менеджер дисплея (LightDM, GDM, SDDM) выбирается через `dpkg-reconfigure`.

## Задача 4. Настройки доступности

**Условие:** Опишите и настройте функции доступности: экранная лупа, высокий контраст, липкие клавиши.

**Ожидаемый результат:** Настройки доступности применены (концептуально).

**Решение и пояснения:**
```bash
# GNOME: gsettings set org.gnome.desktop.a11y.magnifier mag-factor 2.0
gsettings set org.gnome.desktop.a11y.applications screen-magnifier-enabled true
gsettings set org.gnome.desktop.a11y.keyboard stickykeys-enable true
gsettings list-keys org.gnome.desktop.a11y
```
Функции доступности: лупа, высокий контраст, экранная клавиатура, липкие клавиши. GNOME управляется `gsettings`, другие среды имеют свои утилиты. Важны для пользователей с ограничениями.

## Задача 5. Удалённый графический доступ

**Условие:** Настройте и проверьте X11-форвардинг по SSH.

**Ожидаемый результат:** Графическое приложение запускается удалённо.

**Решение и пояснения:**
```bash
# sshd_config: X11Forwarding yes
ssh -X user@server xeyes          # Доверенный форвардинг
ssh -Y user@server xclock         # Недоверенный (с ограничениями)
echo $DISPLAY                     # На удалённой машине: localhost:10.0
```
X11-форвардинг передаёт графику по SSH. `-X` — доверенный, `-Y` — недоверенный (безопаснее). Требуется `X11Forwarding` на сервере и X-сервер на клиенте.
