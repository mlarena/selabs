[Оглавление](LPIC-3-Mixed-Environmentshome.md)

**Практическая работа №1: Создание CIFS-ресурса**

**Задание:**
1. Создайте каталог общего ресурса.
2. Опишите ресурс в `smb.conf`.
3. Настройте права и доступ.
4. Проверьте конфигурацию.
5. Подключитесь к ресурсу.

**Решение и пояснения:**
```bash
sudo mkdir -p /srv/samba/docs && sudo chown root:smbgroup /srv/samba/docs
sudo chmod 2770 /srv/samba/docs
sudo tee -a /etc/samba/smb.conf >/dev/null <<'EOF'
[docs]
   path = /srv/samba/docs
   valid users = @smbgroup
   read only = no
   create mask = 0660
   directory mask = 2770
EOF
testparm && sudo systemctl reload smbd
smbclient //localhost/docs -U user1
```
**Пояснения:**
Ресурс описывается секцией `[name]`. `valid users` ограничивает доступ, `read only = no` разрешает запись. `create mask`/`directory mask` задают права новых файлов. SGID на каталоге (`2770`) сохраняет группу.

---

**Практическая работа №2: Параметры доступа к ресурсу**

**Задание:**
1. Ограничьте ресурс по хостам.
2. Настройте список чтения и записи.
3. Скрытый ресурс (не browsable).
4. Ограничьте доступ к `IPC$`.
5. Проверьте параметры.

**Решение и пояснения:**
```bash
# smb.conf:
# [reports] path=/srv/samba/reports read only=yes read list=@smbgroup
# [secure] path=/srv/samba/secure browseable=no write list=@admins
# [IPC$] hosts allow = 192.168.1.0/24
testparm -sv | grep -A5 "\[reports\]"
```
**Пояснения:**
`hosts allow`/`hosts deny` ограничивают по IP. `read list`/`write list` задают права на чтение/запись для групп. `browseable = no` скрывает ресурс из списка. Ограничение `IPC$` снижает поверхность атаки.

---

**Практическая работа №3: Ресурсы профилей и домашних каталогов**

**Задание:**
1. Настройте ресурс `[homes]`.
2. Настройте ресурс профилей.
3. Включите хранение профилей.
4. Проверьте доступ к домашнему ресурсу.
5. Объясните назначение `[homes]` и `[profiles]`.

**Решение и пояснения:**
```bash
# smb.conf:
# [homes] browseable=no read only=no
# [profiles] path=/srv/samba/profiles read only=no profile acls=yes
sudo systemctl reload smbd
smbclient //localhost/user1 -U user1     # 4. Домашний ресурс
```
**Пояснения:**
`[homes]` — динамический ресурс: при подключении подставляется домашний каталог пользователя. `[profiles]` хранит перемещаемые профили Windows. `profile acls = yes` обеспечивает корректные права профилей.

---

**Практическая работа №4: Планирование миграции и квоты**

**Задание:**
1. Спланируйте перенос файлового сервиса.
2. Настройте квоты на ресурсе.
3. Проверьте использование квот.
4. Настройте аудит доступа (VFS).
5. Объясните этапы миграции.

**Решение и пояснения:**
```bash
# smb.conf: [docs] vfs objects = full_audit
#   full_audit:prefix = %u|%I|%S
#   full_audit:success = connect open
sudo smbcquotas -L //localhost/docs -U user1   # 3. Квоты
rsync -aAXv /oldshare/ /srv/samba/docs/        # Миграция данных
```
**Пояснения:**
Миграция: инвентаризация, перенос данных (`rsync`), проверка прав/ACL, переключение клиентов, мониторинг. Квоты (`smbcquotas`) ограничивают объём. VFS `full_audit` логирует доступ для аудита.
