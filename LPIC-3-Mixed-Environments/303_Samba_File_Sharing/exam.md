[Оглавление](LPIC-3-Mixed-Environmentshome.md)

# Экзаменационные боевые задачи — Тема 303: Samba File Sharing

Задачи приближены к реальным заданиям экзамена **300-300**.

## Задача 1. CIFS-ресурс с ограничениями

**Условие:** Создайте ресурс с доступом по хостам, списками чтения/записи и скрытыми ресурсами.

**Ожидаемый результат:** Ресурс работает с ограничениями.

**Решение и пояснения:**
```bash
# smb.conf:
# [reports] path=/srv/samba/reports read only=yes read list=@sales
# [secure] path=/srv/samba/secure browseable=no write list=@admins
#   hosts allow = 192.168.1.0/24
sudo testparm && sudo systemctl reload smbd
smbclient //localhost/reports -U user1
```
`hosts allow` ограничивает по IP, `read list`/`write list` — по группам, `browseable = no` скрывает ресурс. Ограничение доступа снижает риск.

## Задача 2. Права и ACL

**Условие:** Настройте наследование прав и проверьте Windows-ACL ресурса.

**Ожидаемый результат:** Права наследуются, ACL видны.

**Решение и пояснения:**
```bash
# smb.conf: [docs] inherit acls=yes ; create mask=0660 ; directory mask=2770
sudo systemctl reload smbd
getfacl /srv/samba/docs
smbcacls //localhost/docs / -U user1
smbcacls //localhost/docs /testfile -U user1 -a "ACL:user1:ALLOWED/0x0/READ"
```
`inherit acls` распространяет ACL, маски задают права новых файлов. Samba хранит Windows-ACL в xattr (`acl_xattr`). `smbcacls` управляет ими.

## Задача 3. DFS-ссылки

**Условие:** Настройте DFS-корень с ссылкой на другой сервер.

**Ожидаемый результат:** DFS-ссылка работает.

**Решение и пояснения:**
```bash
# smb.conf: host msdfs = yes ; [dfs] path=/srv/samba/dfs msdfs root=yes
sudo mkdir -p /srv/samba/dfs
sudo ln -s "msdfs:server\\docs" /srv/samba/dfs/docs
sudo systemctl reload smbd
smbclient //localhost/dfs -U user1 -c "ls"
```
DFS объединяет ресурсы серверов в единое дерево. `host msdfs` включает поддержку, ссылки — симлинки `msdfs:server\share`. Упрощает доступ и миграцию.

## Задача 4. Печать через Samba

**Условие:** Настройте публикацию принтеров CUPS через Samba.

**Ожидаемый результат:** Принтеры доступны по SMB.

**Решение и пояснения:**
```bash
sudo apt install -y cups samba
# smb.conf: printing=cups ; printcap name=cups ; load printers=yes
#   [printers] path=/var/spool/samba printable=yes browseable=no
#   [print$] path=/var/lib/samba/printers write list=@admins
sudo systemctl restart smbd cups
smbclient -L localhost -N | grep -i print
```
Samba публикует принтеры CUPS. `[printers]` — динамический ресурс, `[print$]` — драйверы Windows. Задания буферизуются в `/var/spool/samba/`.

## Задача 5. Аудит доступа к ресурсам

**Условие:** Включите аудит операций с файлами ресурса.

**Ожидаемый результат:** Операции логируются.

**Решение и пояснения:**
```bash
# smb.conf: [docs]
#   vfs objects = full_audit
#   full_audit:prefix = %u|%I|%S
#   full_audit:success = connect open read write unlink
#   full_audit:failure = connect
sudo systemctl reload smbd
sudo grep full_audit /var/log/samba/log.smbd | tail
```
VFS `full_audit` логирует операции (кто, откуда, что делал). Аудит необходим для безопасности и расследований. Логи — в `/var/log/samba/`.

## Задача 6. Миграция файлового сервиса

**Условие:** Спланируйте и выполните перенос общего ресурса на новый сервер без простоя.

**Ожидаемый результат:** Данные перенесены, доступ сохранён.

**Решение и пояснения:**
```bash
rsync -aAXv --numeric-ids /srv/samba/oldsrv/ /srv/samba/newsrv/
# Проверка прав:
getfacl -R /srv/samba/newsrv | head
# DFS-прокси для плавного перехода:
# [oldshare] msdfs proxy = \\newserver\\docs
sudo systemctl reload smbd
```
Миграция: инвентаризация → `rsync` (права/ACL) → проверка → переключение (DFS-прокси) → мониторинг. `--numeric-ids` сохраняет UID/GID, `-aAX` — права и ACL.
