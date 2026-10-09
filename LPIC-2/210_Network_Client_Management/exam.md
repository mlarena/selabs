[Оглавление](LPIC-2home.md)

# Экзаменационные боевые задачи — Тема 210: Network Client Management

Задачи приближены к реальным заданиям экзамена **202-450**.

## Задача 1. Настройка DHCP-сервера

**Условие:** Настройте DHCP-сервер для подсети с диапазоном, шлюзом и DNS.

**Ожидаемый результат:** Клиенты получают адреса.

**Решение и пояснения:**
```bash
sudo apt install -y isc-dhcp-server
# /etc/default/isc-dhcp-server: INTERFACESv4="eth0"
# /etc/dhcp/dhcpd.conf:
# subnet 192.168.1.0 netmask 255.255.255.0 {
#   range 192.168.1.100 192.168.1.200;
#   option routers 192.168.1.1;
#   option domain-name-servers 192.168.1.1; }
sudo systemctl enable --now isc-dhcp-server
grep -i lease /var/lib/dhcp/dhcpd.leases | tail
```
`dhcpd.conf` описывает подсети и параметры. Интерфейс прослушивания — в `/etc/default/isc-dhcp-server`. Выданные адреса фиксируются в `dhcpd.leases`.

## Задача 2. Резервирование адресов

**Условие:** Зарезервируйте постоянный адрес для принтера по MAC-адресу.

**Ожидаемый результат:** Устройство получает фиксированный адрес.

**Решение и пояснения:**
```bash
# /etc/dhcp/dhcpd.conf:
# host printer {
#   hardware ethernet aa:bb:cc:dd:ee:ff;
#   fixed-address 192.168.1.50; }
sudo systemctl restart isc-dhcp-server
grep printer /var/lib/dhcp/dhcpd.leases
```
Блок `host` с `hardware ethernet` и `fixed-address` выдаёт постоянный адрес. Это удобно для принтеров/серверов без ручной настройки на клиенте.

## Задача 3. Настройка PAM

**Условие:** Настройте политику паролей и блокировку после неудачных попыток входа.

**Ожидаемый результат:** Политики применяются.

**Решение и пояснения:**
```bash
# /etc/pam.d/common-password: pam_pwquality.so retry=3 minlen=12
# /etc/pam.d/common-auth: pam_faillock.so preauth / authfail
# /etc/security/faillock.conf: deny=3 unlock_time=900
sudo faillock --user user1
sudo faillock --user user1 --reset
chage -M 90 user1
```
`pam_pwquality` — сложность паролей, `pam_faillock` — блокировка после N неудач. Настройки в `/etc/security/`. `chage` управляет сроком действия. Политики применяются ко всем входам.

## Задача 4. LDAP-клиент и поиск

**Условие:** Настройте LDAP-клиент и проверьте разрешение пользователей через NSS.

**Ожидаемый результат:** Пользователи LDAP видны системе.

**Решение и пояснения:**
```bash
sudo apt install -y ldap-utils libnss-ldapd
# /etc/nsswitch.conf: passwd: files ldap ; group: files ldap
# /etc/ldap/ldap.conf: URI ldap://ldap.lab.local ; BASE dc=lab,dc=local
getent passwd user1
ldapsearch -x -b "dc=lab,dc=local" "(uid=user1)"
```
NSS позволяет системе получать пользователей из LDAP. `getent` проверяет разрешение. `ldapsearch` выполняет запросы к каталогу. PAM (`pam_ldap`) — для аутентификации.

## Задача 5. Настройка OpenLDAP-сервера

**Условие:** Создайте OU и пользователя в OpenLDAP, настройте ACL для защиты пароля.

**Ожидаемый результат:** Пользователь создан, доступ ограничен.

**Решение и пояснения:**
```bash
sudo dpkg-reconfigure slapd
cat > ou.ldif <<'EOF'
dn: ou=people,dc=lab,dc=local
objectClass: organizationalUnit
ou: people
EOF
ldapadd -x -D "cn=admin,dc=lab,dc=local" -W -f ou.ldif
# ACL: olcAccess: {0}to attrs=userPassword by self write by anonymous auth by * none
ldapsearch -x -b "ou=people,dc=lab,dc=local"
```
`ldapadd` добавляет записи из LDIF. ACL (`olcAccess`) защищают пароли: разрешают анонимную аутентификацию, но не чтение. Структура каталога — через OU.

## Задача 6. Диагностика клиентских служб

**Условие:** Клиент не получает адрес по DHCP. Найдите причину.

**Ожидаемый результат:** Проблема локализована.

**Решение и пояснения:**
```bash
sudo journalctl -u isc-dhcp-server | tail
sudo dhclient -v eth0
sudo tcpdump -i eth0 port 67 or port 68 -c 10
cat /var/lib/dhcp/dhcpd.leases
```
DHCP использует порты 67/68. `tcpdump` показывает обмен DISCOVER/OFFER/REQUEST/ACK. Проверяют: службу, конфигурацию, leases, firewall, интерфейс прослушивания, наличие свободных адресов в пуле.
