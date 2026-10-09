[Оглавление](LPIC-3-Mixed-Environmentshome.md)

**Практическая работа №1: Доступ к CIFS-ресурсу из Linux**

**Задание:**
1. Установите `cifs-utils`.
2. Посмотрите ресурсы сервера.
3. Подключитесь через `smbclient`.
4. Смонтируйте ресурс.
5. Проверьте доступ.

**Решение и пояснения:**
```bash
sudo apt install -y cifs-utils smbclient
smbclient -L //server -U user1            # 2. Список ресурсов
smbclient //server/docs -U user1          # 3. Интерактивно
sudo mkdir -p /mnt/cifs
sudo mount -t cifs //server/docs /mnt/cifs -o username=user1,uid=$(id -u)
```
**Пояснения:**
`smbclient` — интерактивный клиент SMB, `mount.cifs` монтирует ресурс в файловую систему. Опции `uid`/`gid` задают владельца. Для автомонтирования используют `/etc/fstab` или `autofs`.

---

**Практическая работа №2: Безопасное хранение учётных данных**

**Задание:**
1. Создайте файл учётных данных.
2. Ограничьте права на файл.
3. Смонтируйте ресурс с файлом учётных данных.
4. Добавьте запись в fstab.
5. Объясните, почему нельзя хранить пароль в fstab.

**Решение и пояснения:**
```bash
sudo tee /root/.smbcred >/dev/null <<'EOF'
username=user1
password=Passw0rd!
EOF
sudo chmod 600 /root/.smbcred
# fstab: //server/docs /mnt/cifs cifs credentials=/root/.smbcred,uid=1000 0 0
sudo mount -a
```
**Пояснения:**
Пароль в открытом виде в `fstab` видят все пользователи. Поэтому используют `credentials=` с файлом прав 600. Это защищает учётные данные CIFS.

---

**Практическая работа №3: Автомонтирование домашних каталогов**

**Задание:**
1. Установите `libpam-mount`.
2. Настройте `pam_mount` для CIFS.
3. Проверьте автомонтирование при входе.
4. Проверьте размонтирование при выходе.
5. Объясните назначение pam_mount.

**Решение и пояснения:**
```bash
sudo apt install -y libpam-mount
# /etc/security/pam_mount.conf.xml:
# <volume user="*" fstype="cifs" server="server"
#   path="homes/%(USER)" mountpoint="~/smbhome" />
sudo systemctl restart sssd
# Проверка при входе пользователя:
ls ~/smbhome
```
**Пояснения:**
`pam_mount` монтирует ресурсы при входе пользователя и размонтирует при выходе, используя его учётные данные. Удобно для домашних каталогов и профилей в смешанной среде.

---

**Практическая работа №4: Права, ACL и квоты CIFS**

**Задание:**
1. Посмотрите ACL удалённого ресурса.
2. Измените ACL.
3. Проверьте квоты ресурса.
4. Загрузите файл через `smbget`.
5. Объясните особенности прав CIFS.

**Решение и пояснения:**
```bash
getcifsacl /mnt/cifs/file.txt
setcifsacl -a "ACL:user1:ALLOWED/0x0/READ" /mnt/cifs/file.txt
smbcquotas -L //server/docs -U user1      # 3. Квоты
smbget smb://server/docs/file.txt         # 4. Загрузка
```
**Пояснения:**
`getcifsacl`/`setcifsacl` управляют Windows-ACL удалённых ресурсов. `smbcquotas` — квотами. `smbget`/`smbtar` — скачивание. Права CIFS отличаются от POSIX, поэтому важна согласованность с сервером.
