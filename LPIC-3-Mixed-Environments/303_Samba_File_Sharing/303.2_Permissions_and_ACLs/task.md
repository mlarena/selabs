[Оглавление](LPIC-3-Mixed-Environmentshome.md)

**Практическая работа №1: POSIX ACL в Linux**

**Задание:**
1. Проверьте поддержку ACL на ФС.
2. Установите ACL на каталог.
3. Посмотрите ACL.
4. Удалите ACL.
5. Объясните разницу обычных прав и ACL.

**Решение и пояснения:**
```bash
mount | grep acl                          # 1. Опция acl
sudo setfacl -m u:user1:rwx /srv/samba/docs
sudo getfacl /srv/samba/docs              # 3. Просмотр
sudo setfacl -x u:user1 /srv/samba/docs   # 4. Удаление
```
**Пояснения:**
POSIX ACL позволяют задавать права для нескольких пользователей/групп (сверх owner/group/other). `setfacl`/`getfacl` управляют ими. Расширенные права отображаются символом `+` в `ls -l`.

---

**Практическая работа №2: Маски и наследование в Samba**

**Задание:**
1. Настройте маски создания файлов.
2. Настройте наследование ACL.
3. Принудительно задайте владельца/группу.
4. Проверьте права новых файлов.
5. Объясните назначение масок.

**Решение и пояснения:**
```bash
# smb.conf:
# create mask = 0660
# directory mask = 2770
# inherit acls = yes
# force group = smbgroup
sudo systemctl reload smbd
touch /srv/samba/docs/testfile
ls -l /srv/samba/docs/testfile
```
**Пояснения:**
`create mask`/`directory mask` ограничивают права создаваемых объектов. `inherit acls` распространяет ACL родителя. `force group` назначает группу. Это обеспечивает единообразие прав для общих ресурсов.

---

**Практическая работа №3: Windows ACL и xattr**

**Задание:**
1. Включите хранение DOS-атрибутов.
2. Посмотрите расширенные атрибуты.
3. Включите VFS `acl_xattr`.
4. Проверьте Windows-ACL через `smbcacls`.
5. Объясните, как Samba хранит Windows-ACL.

**Решение и пояснения:**
```bash
# smb.conf: store dos attributes = yes ; vfs objects = acl_xattr
sudo systemctl reload smbd
getfattr -d /srv/samba/docs/testfile 2>/dev/null
smbcacls //localhost/docs /testfile -U user1
```
**Пояснения:**
Samba хранит Windows-ACL в расширенных атрибутах (`security.NTACL`) через VFS `acl_xattr`. `store dos attributes` сохраняет DOS-атрибуты. `smbcacls`/`sharesec` управляют Windows-ACL.

---

**Практическая работа №4: Шифрование CIFS-соединений**

**Задание:**
1. Включите шифрование SMB.
2. Проверьте параметр `smb encrypt`.
3. Включите подписи SMB.
4. Проверьте шифрование соединения.
5. Объясните разницу подписи и шифрования.

**Решение и пояснения:**
```bash
# smb.conf global: server signing = mandatory
# smb.conf share: smb encrypt = required
sudo systemctl reload smbd
smbstatus --locks
smbclient //localhost/docs -U user1 -c "smbstatus"
```
**Пояснения:**
Подпись SMB (signing) обеспечивает целостность и аутентификацию сообщений, шифрование (`smb encrypt`) скрывает содержимое. `required` обязывает использовать шифрование, иначе соединение отклоняется.
