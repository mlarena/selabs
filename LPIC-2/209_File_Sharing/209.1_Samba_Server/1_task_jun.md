[Оглавление](?file=LPIC-2%2Fhome.md)

**Практическая работа №1: Установка и настройка Samba (standalone)**

**Задание:**
1. Установите Samba.
2. Создайте каталог общего ресурса.
3. Опишите ресурс в `smb.conf`.
4. Проверьте конфигурацию.
5. Запустите службу.

**Решение и пояснения:**
```bash
sudo apt install -y samba
sudo mkdir -p /srv/samba/public && sudo chmod 777 /srv/samba/public
sudo tee -a /etc/samba/smb.conf >/dev/null <<'EOF'
[public]
   path = /srv/samba/public
   browseable = yes
   read only = no
   guest ok = yes
EOF
testparm                                    # 4. Проверка конфигурации
sudo systemctl enable --now smbd nmbd
```
**Пояснения:**
Samba предоставляет SMB/CIFS-ресурсы для Windows/Linux. `/etc/samba/smb.conf` описывает глобальные параметры и ресурсы. `testparm` проверяет синтаксис. Демоны: `smbd` (файлы/печать), `nmbd` (NetBIOS).

---

**Практическая работа №2: Пользователи и аутентификация**

**Задание:**
1. Создайте системного пользователя для Samba.
2. Добавьте его в базу Samba.
3. Настройте защищённый ресурс.
4. Проверьте доступ через smbclient.
5. Объясните разницу user/share/AD security.

**Решение и пояснения:**
```bash
sudo useradd -M -s /usr/sbin/nologin smbuser
sudo smbpasswd -a smbuser                   # 2. Добавить в базу Samba
sudo pdbedit -L                             # 2. Список пользователей
# Ресурс: [private] path=/srv/samba/private valid users=smbuser read only=no
smbclient -L localhost -U smbuser           # 4. Просмотр ресурсов
smbclient //localhost/private -U smbuser    # 4. Подключение
```
**Пояснения:**
Samba использует отдельную базу паролей (`smbpasswd`/`pdbedit`). Режимы безопасности: `user` (аутентификация по пользователю), `share` (устаревший, по ресурсу), `ads` (Active Directory). `smbclient` — клиент SMB из Linux.

---

**Практическая работа №3: Монтирование CIFS и права**

**Задание:**
1. Установите `cifs-utils`.
2. Смонтируйте ресурс Samba.
3. Настройте автомонтирование в fstab.
4. Проверьте права и владельца.
5. Объясните сопоставление пользователей Windows/Linux.

**Решение и пояснения:**
```bash
sudo apt install -y cifs-utils
sudo mkdir -p /mnt/smb
sudo mount -t cifs //server/public /mnt/smb -o username=smbuser,uid=$(id -u)
# fstab: //server/public /mnt/smb cifs credentials=/root/.smbcred,uid=1000 0 0
ls -l /mnt/smb
```
**Пояснения:**
`mount.cifs` монтирует SMB-ресурс. Опции `uid`/`gid` сопоставляют владельца. Учётные данные хранят в защищённом файле (`credentials=`) с правами 600. Сопоставление пользователей важно для корректных прав.

---

**Практическая работа №4: Диагностика Samba**

**Задание:**
1. Проверьте статус демонов.
2. Посмотрите активные сессии.
3. Проверьте журналы Samba.
4. Определите занятые ресурсы.
5. Объясните типовые проблемы Samba.

**Решение и пояснения:**
```bash
systemctl status smbd nmbd
sudo smbstatus                              # 2. Сессии и ресурсы
sudo tail -f /var/log/samba/log.smbd        # 3. Журнал
testparm -s                                 # 4. Действующая конфигурация
smbclient -L localhost -N                   # Проверка без пароля
```
**Пояснения:**
`smbstatus` показывает активные соединения, блокировки и ресурсы. Журналы — в `/var/log/samba/`. Типовые проблемы: права на каталог, SELinux/AppArmor, неверный `security`, занятый порт 445, пароль не в базе Samba.
