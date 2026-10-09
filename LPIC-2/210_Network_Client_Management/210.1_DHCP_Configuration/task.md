[Оглавление](LPIC-2/home.md)

**Практическая работа №1: Настройка DHCP-сервера**

**Задание:**
1. Установите DHCP-сервер.
2. Определите имя интерфейса для обслуживания.
3. Настройте подсеть и диапазон адресов.
4. Запустите службу.
5. Проверьте выдачу адресов.

**Решение и пояснения:**
```bash
sudo apt install -y isc-dhcp-server
# /etc/default/isc-dhcp-server: INTERFACESv4="eth0"
sudo tee /etc/dhcp/dhcpd.conf >/dev/null <<'EOF'
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option domain-name-servers 192.168.1.1;
}
EOF
sudo systemctl enable --now isc-dhcp-server
```
**Пояснения:**
DHCP автоматически выдаёт IP, шлюз и DNS. `dhcpd.conf` описывает подсети и диапазоны. Интерфейс прослушивания задают в `/etc/default/isc-dhcp-server`. Выданные адреса фиксируются в `dhcpd.leases`.

---

**Практическая работа №2: Статические хосты и резервирование**

**Задание:**
1. Зарезервируйте адрес по MAC.
2. Добавьте статический хост (fixed-address).
3. Настройте опции для конкретной подсети.
4. Перезапустите сервер.
5. Проверьте выдачу зарезервированного адреса.

**Решение и пояснения:**
```bash
# /etc/dhcp/dhcpd.conf:
# host printer {
#     hardware ethernet aa:bb:cc:dd:ee:ff;
#     fixed-address 192.168.1.50;
# }
sudo systemctl restart isc-dhcp-server
grep printer /var/lib/dhcp/dhcpd.leases
```
**Пояснения:**
Резервирование по MAC гарантирует постоянный адрес для устройства. Блок `host` с `fixed-address` выдаёт фиксированный IP. Это удобно для принтеров и серверов без ручной настройки на клиенте.

---

**Практическая работа №3: DHCP relay**

**Задание:**
1. Установите DHCP relay.
2. Настройте ретрансляцию на сервер.
3. Запустите службу.
4. Объясните, зачем нужен relay.
5. Проверьте прохождение запросов.

**Решение и пояснения:**
```bash
sudo apt install -y isc-dhcp-relay
# /etc/default/isc-dhcp-relay:
# SERVERS="192.168.1.10"
# INTERFACES="eth1"
sudo systemctl enable --now isc-dhcp-relay
journalctl -u isc-dhcp-relay | tail
```
**Пояснения:**
DHCP-запросы не маршрутизируются между подсетями (broadcast). Relay-агент принимает их и пересылает серверу по unicast. Это позволяет обслуживать несколько подсетей одним DHCP-сервером.

---

**Практическая работа №4: DHCPv6 и RA**

**Задание:**
1. Установите `radvd`.
2. Настройте объявления маршрутизатора.
3. Запустите службу.
4. Проверьте объявления на клиенте.
5. Объясните разницу DHCPv6 и SLAAC.

**Решение и пояснения:**
```bash
sudo apt install -y radvd
# /etc/radvd.conf:
# interface eth0 {
#     AdvSendAdvert on;
#     prefix 2001:db8:1::/64 { };
# };
sudo systemctl enable --now radvd
ip -6 addr show eth0 | grep 2001
```
**Пояснения:**
IPv6-адреса могут назначаться через SLAAC (на основе RA) или DHCPv6. `radvd` рассылает объявления маршрутизатора (RA) с префиксом. RA также сообщает шлюз по умолчанию для IPv6.
