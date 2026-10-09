[Оглавление](LPIC-3-Securityhome.md)

**Практическая работа №1: Фильтрация через iptables**

**Задание:**
1. Посмотрите текущие правила.
2. Заблокируйте входящий порт.
3. Разрешите SSH из подсети.
4. Настройте политику по умолчанию DROP.
5. Сохраните правила.

**Решение и пояснения:**
```bash
sudo iptables -L -n -v
sudo iptables -A INPUT -p tcp --dport 23 -j DROP
sudo iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P INPUT DROP
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```
**Пояснения:**
iptables фильтрует по протоколу, порту, адресу, состоянию. Политика `DROP` блокирует всё, кроме разрешённого. `ESTABLISHED,RELATED` разрешает ответы. `iptables-save`/`restore` сохраняют правила.

---

**Практическая работа №2: nftables — современная замена**

**Задание:**
1. Посмотрите правила nftables.
2. Создайте таблицу и цепочку.
3. Добавьте правила фильтрации.
4. Настройте NAT.
5. Сохраните конфигурацию.

**Решение и пояснения:**
```bash
sudo nft list ruleset
sudo nft add table inet filter
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
sudo nft add rule inet filter input tcp dport 22 accept
sudo nft add rule inet filter input ct state established,related accept
sudo nft list ruleset
sudo nft list ruleset > /etc/nftables.conf
```
**Пояснения:**
nftables заменяет iptables/ip6tables/arptables единым синтаксисом. Таблицы (`inet` для IPv4+IPv6), цепочки с hooks, правила. `ct state` работает с conntrack. Конфигурация сохраняется в `/etc/nftables.conf`.

---

**Практическая работа №3: firewalld и зоны**

**Задание:**
1. Установите firewalld.
2. Посмотрите зоны.
3. Назначьте интерфейс зоне.
4. Разрешите службу в зоне.
5. Проверьте правила.

**Решение и пояснения:**
```bash
sudo apt install -y firewalld
sudo firewall-cmd --get-zones
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --zone=internal --add-source=192.168.1.0/24 --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```
**Пояснения:**
firewalld управляет правилами через зоны (уровни доверия). Интерфейсы/источники привязываются к зонам, службы разрешаются по имени. `--permanent` сохраняет изменения, `--reload` применяет. Удобнее ручных iptables/nftables.

---

**Практическая работа №4: Перенаправление и NAT**

**Задание:**
1. Настройте masquerade (SNAT).
2. Настройте DNAT (port forwarding).
3. Ограничьте перенаправление по источнику.
4. Проверьте трансляцию.
5. Объясните сценарии NAT.

**Решение и пояснения:**
```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.20:80
sudo iptables -t nat -L -n -v
# nftables: nft add rule inet nat prerouting tcp dport 8080 dnat to 192.168.1.20:80
```
**Пояснения:**
SNAT/masquerade подменяет источник (выход в интернет), DNAT — назначение (публикация сервиса). Ограничение по источнику повышает безопасность. Трансляция — основа шлюзов и балансировщиков.

---

**Практическая работа №5: UFW и диагностика фильтрации**

**Задание:**
1. Установите и включите UFW.
2. Разрешите SSH и HTTP.
3. Ограничьте порт по подсети.
4. Проверьте статус.
5. Диагностируйте блокировку трафика.

**Решение и пояснения:**
```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw allow from 192.168.1.0/24 to any port 22
sudo ufw allow 80/tcp
sudo ufw enable
sudo ufw status verbose
sudo journalctl -k | grep -i "UFW BLOCK" | tail   # 5. Блокировки
```
**Пояснения:**
UFW — простой интерфейс к iptables/nftables. Правила по умолчанию — запрет входящих. `ufw status` показывает правила. Блокировки видны в журнале ядра (`UFW BLOCK`). UFW подходит для хостов, firewalld — для сложных сред.
