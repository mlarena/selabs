[Оглавление](?file=LPIC-3-Mixed-Environments%2Fhome.md)

# Экзаменационные боевые задачи — Тема 301: Samba Basics

Задачи приближены к реальным заданиям экзамена **300-300**.

## Задача 1. Диагностика компонентов Samba

**Условие:** Определите, какие демоны Samba запущены, на каких портах слушают и в какой роли работает сервер.

**Ожидаемый результат:** Информация о ролях и портах получена.

**Решение и пояснения:**
```bash
systemctl status smbd nmbd winbind
ss -tlnp | grep -E "445|139|137|138"
testparm -sv | grep -E "server role|security"
smbd -V
```
`smbd` — файлы/печать (445/139), `nmbd` — NetBIOS, `winbindd` — AD. `testparm -sv` показывает действующие параметры, включая роль и режим безопасности.

## Задача 2. Настройка общего ресурса

**Условие:** Создайте ресурс для группы `sales` с правом записи и масками, сохраняющими группу.

**Ожидаемый результат:** Ресурс доступен группе, права корректны.

**Решение и пояснения:**
```bash
sudo mkdir -p /srv/samba/sales && sudo chown root:sales /srv/samba/sales
sudo chmod 2770 /srv/samba/sales
sudo tee -a /etc/samba/smb.conf >/dev/null <<'EOF'
[sales]
   path = /srv/samba/sales
   valid users = @sales
   read only = no
   create mask = 0660
   directory mask = 2770
   force group = sales
EOF
sudo testparm && sudo systemctl reload smbd
```
`valid users` ограничивает, маски задают права новых файлов, `force group` назначает группу, SGID на каталоге сохраняет её. `testparm` проверяет конфигурацию.

## Задача 3. Конфигурация через реестр

**Условие:** Переключите Samba на хранение конфигурации в реестре и задайте параметр через `net conf`.

**Ожидаемый результат:** Конфигурация хранится в реестре.

**Решение и пояснения:**
```bash
# smb.conf: config backend = registry
sudo systemctl restart smbd
net conf list
net conf setparm global "server string" "Lab Server"
net conf getparm global "server string"
net conf showshare sales
```
`config backend = registry` переключает источник конфигурации. `net conf` управляет параметрами в `registry.tdb`. Это позволяет динамически менять настройки.

## Задача 4. Резервное копирование Samba

**Условие:** Сделайте резервную копию критичных данных Samba и проверьте целостность.

**Ожидаемый результат:** Бэкап создан и проверен.

**Решение и пояснения:**
```bash
sudo tdbbackup /var/lib/samba/private/secrets.tdb
sudo tdbbackup /var/lib/samba/registry.tdb
sudo tar -czf /backup/samba_$(date +%F).tar.gz /etc/samba /var/lib/samba
sudo tdbdump /var/lib/samba/private/secrets.tdb | head
```
TDB-файлы хранят секреты и реестр. `tdbbackup` делает согласованную копию, `tdbdump` проверяет содержимое. Полный бэкап включает `/etc/samba` и `/var/lib/samba`.

## Задача 5. Устранение неполадок Samba

**Условие:** Пользователь не может подключиться к ресурсу. Найдите причину.

**Ожидаемый результат:** Причина найдена и устранена.

**Решение и пояснения:**
```bash
sudo testparm -s
sudo smbstatus
sudo tail -f /var/log/samba/log.smbd
sudo pdbedit -L -v -u user1
getfacl /srv/samba/sales
sudo smbclient -L localhost -U user1
```
Проверяют: конфигурацию, активные сессии, журнал, запись в базе паролей, права/ACL, подключение клиентом. Типовые причины: неверный пароль, права каталога, SELinux/AppArmor, firewall, `valid users`.

## Задача 6. Работа с ldb контроллера домена

**Условие:** Найдите пользователей в базе Samba AD и измените атрибут объекта.

**Ожидаемый результат:** Атрибут изменён.

**Решение и пояснения:**
```bash
sudo ldbsearch -H /var/lib/samba/private/sam.ldb "(objectClass=user)" cn | head
sudo ldbedit -H /var/lib/samba/private/sam.ldb "CN=user1,CN=Users,DC=lab,DC=local"
sudo samba-tool dbcheck
```
Samba AD хранит данные в `sam.ldb` (LDAP-совместимо). `ldbsearch`/`ldbedit`/`ldbmodify` работают напрямую. `samba-tool dbcheck` проверяет целостность.
