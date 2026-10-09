[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Файловая конфигурация smb.conf**

**Задание:**
1. Посмотрите структуру `smb.conf`.
2. Определите секцию `[global]`.
3. Добавьте общий ресурс.
4. Проверьте конфигурацию.
5. Примените изменения.

**Решение и пояснения:**
```bash
cat /etc/samba/smb.conf | head -40
sudo tee -a /etc/samba/smb.conf >/dev/null <<'EOF'
[data]
   path = /srv/samba/data
   browseable = yes
   read only = no
   valid users = @smbgroup
EOF
testparm                                   # 4. Проверка
sudo systemctl reload smbd                 # 5. Применение
```
**Пояснения:**
`smb.conf` состоит из секции `[global]` и секций ресурсов. `testparm` проверяет конфигурацию и предупреждает об ошибках. `reload` применяет изменения без разрыва соединений. Параметр `include` подключает внешние файлы.

---

**Практическая работа №2: Реестровая конфигурация**

**Задание:**
1. Посмотрите текущие параметры реестра Samba.
2. Настройте `config backend = registry`.
3. Перенесите конфигурацию в реестр.
4. Измените параметр через `net conf`.
5. Проверьте результат.

**Решение и пояснения:**
```bash
# smb.conf: config backend = registry
sudo systemctl restart smbd
net conf list                              # 2. Список в реестре
net conf setparm global "server string" "Lab Samba"
net conf getparm global "server string"
net conf showshare data
```
**Пояснения:**
Samba может хранить конфигурацию в реестре (`registry.tdb`), а не только в файле. `net conf` управляет параметрами в реестре. `config backend = registry` переключает источник конфигурации.

---

**Практическая работа №3: TLS и проверка конфигурации**

**Задание:**
1. Сгенерируйте сертификат для Samba.
2. Включите TLS в `smb.conf`.
3. Укажите файлы ключа и сертификата.
4. Проверьте конфигурацию.
5. Проверьте TLS-соединение.

**Решение и пояснения:**
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/samba/tls.key -out /etc/samba/tls.crt -subj "/CN=dc1.lab"
# smb.conf:
# tls enabled = yes
# tls keyfile = /etc/samba/tls.key
# tls certfile = /etc/samba/tls.crt
sudo testparm && sudo systemctl restart smbd
openssl s_client -connect localhost:445 </dev/null
```
**Пояснения:**
Samba 4 поддерживает TLS для LDAP-трафика контроллера домена. Параметры `tls enabled`, `tls keyfile`, `tls certfile` задают шифрование. Проверка — через `openssl s_client` на порт 445.

---

**Практическая работа №4: Отладка и Windows-инструменты**

**Задание:**
1. Включите расширенное логирование.
2. Проверьте конфигурацию на типовые ошибки.
3. Посмотрите журнал Samba.
4. Опишите Windows-инструменты (RSAT, ADSI Edit).
5. Объясните порядок отладки.

**Решение и пояснения:**
```bash
# smb.conf: log level = 3
sudo systemctl restart smbd
sudo tail -f /var/log/samba/log.smbd
testparm -sv | grep -iE "log level|server role"
```
**Пояснения:**
`log level` задаёт детализацию логов (`/var/log/samba/`). Windows-инструменты: RSAT (оснастки), ADSI Edit, LDP, Regedit, MMC — для управления AD и реестром Samba. Отладку ведут от логов к конфигурации.
