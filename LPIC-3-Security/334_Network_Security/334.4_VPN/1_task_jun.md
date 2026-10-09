[Оглавление](?file=LPIC-3-Security%2Fhome.md)

**Практическая работа №1: Основы VPN и IPsec**

**Задание:**
1. Опишите типы VPN (site-to-site, remote access).
2. Опишите протоколы (IPsec, OpenVPN, WireGuard).
3. Установите `strongswan`.
4. Посмотрите состояние IPsec.
5. Объясните разницу transport и tunnel.

**Решение и пояснения:**
```bash
sudo apt install -y strongswan
sudo ipsec status
sudo ipsec statusall
# /etc/ipsec.conf: conn %default ; conn lab  (keyexchange=ikev2)
```
**Пояснения:**
VPN шифрует трафик между узлами/сетями. IPsec работает на уровне IP: transport шифрует полезную нагрузку, tunnel — весь пакет (site-to-site). IKEv2 управляет ключами. strongswan — реализация IPsec.

---

**Практическая работа №2: OpenVPN — установка и настройка**

**Задание:**
1. Установите OpenVPN и easy-rsa.
2. Создайте CA и сертификаты.
3. Настройте сервер.
4. Запустите сервер.
5. Проверьте статус.

**Решение и пояснения:**
```bash
sudo apt install -y openvpn easy-rsa
make-cadir ~/openvpn-ca && cd ~/openvpn-ca
./easyrsa init-pki && ./easyrsa build-ca nopass
./easyrsa gen-req server nopass && ./easyrsa sign-req server server
./easyrsa gen-dh
# /etc/openvpn/server.conf: dev tun ; proto udp ; ca/cert/key ; dh
sudo systemctl enable --now openvpn@server
systemctl status openvpn@server
```
**Пояснения:**
OpenVPN строит VPN на TLS с сертификатами. CA подписывает сертификаты сервера/клиентов. Сервер работает на UDP/TCP, создаёт интерфейс `tun`. Клиенты аутентифицируются сертификатами.

---

**Практическая работа №3: WireGuard**

**Задание:**
1. Установите WireGuard.
2. Сгенерируйте ключи.
3. Создайте конфигурацию интерфейса.
4. Поднимите интерфейс.
5. Проверьте соединение.

**Решение и пояснения:**
```bash
sudo apt install -y wireguard
wg genkey | tee privatekey | wg pubkey > publickey      # 2. Ключи
# /etc/wireguard/wg0.conf:
# [Interface] PrivateKey=... Address=10.0.0.1/24 ListenPort=51820
# [Peer] PublicKey=... AllowedIPs=10.0.0.2/32
sudo wg-quick up wg0                                    # 4. Подъём
sudo wg show                                            # 5. Состояние
```
**Пояснения:**
WireGuard — современный VPN с минимальной кодовой базой и высокой производительностью. Использует пары ключей и `AllowedIPs`. Прост в настройке, часто предпочтительнее OpenVPN для новых развёртываний.

---

**Практическая работа №4: Маршрутизация и доступ в VPN**

**Задание:**
1. Включите IP-форвардинг.
2. Настройте NAT для клиентов VPN.
3. Настройте push маршрутов.
4. Проверьте маршруты на клиенте.
5. Объясните split tunneling.

**Решение и пояснения:**
```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
# OpenVPN: push "route 192.168.1.0 255.255.255.0"
# WireGuard: AllowedIPs = 0.0.0.0/0 (весь трафик)
ip route show
```
**Пояснения:**
Для выхода клиентов в интернет через VPN нужны форвардинг и NAT. Push маршрутов определяет, какой трафик идёт через туннель. Split tunneling направляет через VPN только часть трафика (`AllowedIPs`), full tunnel — весь.

---

**Практическая работа №5: Диагностика и безопасность VPN**

**Задание:**
1. Посмотрите состояние соединения.
2. Проверьте журналы.
3. Настройте отзыв сертификата/ключа.
4. Ограничьте VPN-порт firewall.
5. Объясните типовые проблемы.

**Решение и пояснения:**
```bash
sudo wg show
sudo journalctl -u openvpn@server | tail
# Отзыв: ./easyrsa revoke client1 && ./easyrsa gen-crl
sudo iptables -A INPUT -p udp --dport 51820 -j ACCEPT
sudo tcpdump -i wg0 -c 5 -nn
```
**Пояснения:**
Отзыв сертификата/смена ключа блокирует скомпрометированного клиента. Журналы показывают этапы рукопожатия. Типовые проблемы: несовпадение ключей/CA, конфликт подсетей, firewall, MTU. Диагностика — `wg show`, `tcpdump` на интерфейсе.
