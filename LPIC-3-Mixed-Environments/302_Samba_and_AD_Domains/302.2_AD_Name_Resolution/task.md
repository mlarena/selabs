[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Внутренний DNS Samba**

**Задание:**
1. Проверьте зоны внутреннего DNS.
2. Посмотрите записи домена.
3. Создайте A-запись через `samba-tool`.
4. Проверьте разрешение имени.
5. Объясните роль DNS в AD.

**Решение и пояснения:**
```bash
sudo samba-tool dns zonelist 127.0.0.1
sudo samba-tool dns query 127.0.0.1 lab.local @ ALL
sudo samba-tool dns add 127.0.0.1 lab.local host1 A 192.168.1.50   # 3
dig @127.0.0.1 host1.lab.local                                       # 4
```
**Пояснения:**
AD требует DNS для разрешения имён сервисов (SRV-записи). Samba AD DC включает внутренний DNS-сервер. `samba-tool dns` управляет зонами и записями. Клиенты должны использовать DNS DC.

---

**Практическая работа №2: DNS-форвардинг и динамические обновления**

**Задание:**
1. Настройте DNS-форвардер.
2. Проверьте разрешение внешних имён.
3. Настройте разрешение динамических обновлений.
4. Проверьте регистрацию клиента в DNS.
5. Объясните роль samba_dnsupdate.

**Решение и пояснения:**
```bash
# smb.conf: dns forwarder = 8.8.8.8
sudo systemctl restart samba-ad-dc
dig @127.0.0.1 example.com
sudo samba_dnsupdate --verbose
sudo samba-tool dns update 127.0.0.1 lab.local
```
**Пояснения:**
`dns forwarder` задаёт сервер для внешних имён. `allow dns updates` управляет динамическими обновлениями (клиенты регистрируют свои записи). `samba_dnsupdate` обновляет SRV-записи DC в DNS.

---

**Практическая работа №3: Стандартные имена и mDNS**

**Задание:**
1. Посмотрите стандартные записи AD.
2. Найдите SRV-записи сервисов.
3. Проверьте запись `_ldap._tcp`.
4. Настройте multicast DNS (опционально).
5. Объясните назначение SRV-записей.

**Решение и пояснения:**
```bash
dig @127.0.0.1 _ldap._tcp.lab.local SRV
dig @127.0.0.1 _kerberos._tcp.lab.local SRV
dig @127.0.0.1 _gc._tcp.lab.local SRV
# smb.conf: multicast dns register = no
```
**Пояснения:**
SRV-записи указывают клиентам, где искать службы AD (LDAP, Kerberos, Global Catalog). Без них вход в домен не работает. Multicast DNS используется для локального разрешения имён.

---

**Практическая работа №4: BIND9 DLZ и NetBIOS (awareness)**

**Задание:**
1. Опишите назначение BIND9 DLZ.
2. Опишите роль NetBIOS/WINS.
3. Проверьте имя NetBIOS DC.
4. Объясните, почему WINS устаревает.
5. Сравните встроенный DNS и BIND9 DLZ.

**Решение и пояснения:**
```bash
sudo samba-tool domain info 127.0.0.1
nmblookup -A 127.0.0.1 2>/dev/null || echo "nmbd не используется"
```
**Пояснения:**
BIND9 DLZ позволяет хранить зоны AD в LDAP (используется крупными развёртываниями вместо внутреннего DNS Samba). NetBIOS/WINS — устаревший механизм разрешения имён Windows; в современных AD его заменяет DNS.
