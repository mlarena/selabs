[Оглавление](LPIC-3-Securityhome.md)

# Экзаменационные боевые задачи — Тема 333: Access Control

Задачи приближены к реальным заданиям экзамена **303-300**.

## Задача 1. Настройка дискреционного доступа

**Условие:** Настройте общий каталог для группы с наследованием прав через ACL.

**Ожидаемый результат:** Доступ настроен.

**Решение и пояснения:**
```bash
sudo mkdir -p /srv/project
sudo chown root:devs /srv/project
sudo chmod 2770 /srv/project
sudo setfacl -m g:devs:rwx /srv/project
sudo setfacl -d -m g:devs:rwx /srv/project     # Default ACL
sudo getfacl /srv/project
```
SGID (`2770`) сохраняет группу новых файлов, default ACL наследуется. `setfacl`/`getfacl` управляют ACL. Маска ACL ограничивает эффективные права.

## Задача 2. Специальные биты

**Условие:** Найдите файлы с setuid, объясните риск и замените один на capability.

**Ожидаемый результат:** Риск оценён, setuid заменён.

**Решение и пояснения:**
```bash
find / -perm -4000 -type f 2>/dev/null
sudo setcap cap_net_raw+ep /usr/bin/ping
getcap /usr/bin/ping
sudo chmod u-s /usr/bin/ping
sudo getpcaps $$
```
setuid-программы дают права владельца (опасно для root). Capabilities дробят root на отдельные права, реализуя минимальные привилегии. `getcap`/`setcap` управляют ими.

## Задача 3. Защита критичных файлов

**Условие:** Защитите `/etc/passwd` и `/etc/sudoers` от изменений.

**Ожидаемый результат:** Файлы защищены.

**Решение и пояснения:**
```bash
sudo chattr +i /etc/passwd
lsattr /etc/passwd
sudo chmod 440 /etc/sudoers
sudo chown root:root /etc/sudoers
echo "test" | sudo tee -a /etc/passwd    # Должно отказать
sudo chattr -i /etc/passwd               # Снятие при необходимости
```
`chattr +i` (immutable) запрещает любые изменения даже root. Права 440 на sudoers — стандарт. Защита критичных файлов затрудняет закрепление атакующего.

## Задача 4. Мандатный доступ (AppArmor)

**Условие:** Настройте профиль AppArmor для сервиса в режиме enforce.

**Ожидаемый результат:** Профиль применяется.

**Решение и пояснения:**
```bash
sudo aa-status
ls /etc/apparmor.d/
sudo aa-enforce /etc/apparmor.d/usr.sbin.cupsd
sudo aa-complain /etc/apparmor.d/usr.sbin.cupsd   # Режим отладки
sudo journalctl -k | grep -i apparmor | tail
```
AppArmor — MAC по путям. `enforce` блокирует запрещённое, `complain` логирует (для отладки). Профили в `/etc/apparmor.d/`. Даже при компрометации сервис ограничен профилем.

## Задача 5. SELinux (awareness)

**Условие:** Опишите работу с SELinux: режимы, контексты, booleans.

**Ожидаемый результат:** Продемонстрировано понимание SELinux.

**Решение и пояснения:**
```bash
getenforce ; sestatus
ls -Z /var/www/html/
sudo chcon -t httpd_sys_content_t /var/www/html/index.html
restorecon -v /var/www/html/index.html
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on
sudo ausearch -m avc -ts recent
```
SELinux использует типы (домен процесса и тип файла). `chcon` меняет контекст временно, `restorecon` — по политике. Booleans переключают разрешения. Отказы — AVC в audit.log.

## Задача 6. Аудит доступа и привилегий

**Условие:** Настройте журналирование действий sudo и аудит критичных файлов.

**Ожидаемый результат:** Действия логируются.

**Решение и пояснения:**
```bash
sudo grep sudo /var/log/auth.log | tail
sudo journalctl -u sudo
sudo auditctl -w /etc/sudoers -p wa -k sudoers_changes
sudo ausearch -k sudoers_changes
sudo -l -U user1
```
Аудит привилегий фиксирует, кто и что делал с правами. sudo логирует команды, auditd — изменения файлов. Необходимо для расследований и compliance.
