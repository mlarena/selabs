[Оглавление](LPIC-2home.md)

**Практическая работа №1: Установка и базовая конфигурация OpenVPN**

**Задание:**
1. Установите OpenVPN и easy-rsa.
2. Создайте собственный CA.
3. Сгенерируйте ключи сервера.
4. Создайте конфигурацию сервера.
5. Запустите сервер.

**Решение / Команды:**
```bash
sudo apt install -y openvpn easy-rsa
make-cadir ~/openvpn-ca && cd ~/openvpn-ca
./easyrsa init-pki
./easyrsa build-ca nopass                 # 2. CA
./easyrsa gen-req server nopass           # 3. Ключ сервера
./easyrsa sign-req server server
./easyrsa gen-dh
# /etc/openvpn/server.conf: port, proto udp, dev tun, ca/cert/key, dh
sudo systemctl enable --now openvpn@server
```
**Пояснения:**
OpenVPN строит VPN на TLS. CA подписывает сертификаты сервера и клиентов. Конфигурация сервера в `/etc/openvpn/server.conf` задаёт протокол, устройство (`tun`), сертификаты. Клиенты аутентифицируются сертификатами.

---

**Практическая работа №2: Клиентский профиль**

**Задание:**
1. Сгенерируйте ключ клиента.
2. Подпишите клиентский сертификат.
3. Создайте файл `.ovpn` для клиента.
4. Подключитесь с клиента.
5. Проверьте туннель.

**Решение / Команды:**
```bash
cd ~/openvpn-ca
./easyrsa gen-req client1 nopass
./easyrsa sign-req client client1
# Собрать client1.ovpn: ca.crt, client1.crt, client1.key + параметры
openvpn --config client1.ovpn &           # 4. Подключение
ip addr show tun0                         # 5. Туннельный интерфейс
ping -c2 10.8.0.1                         # 5. Проверка
```
**Пояснения:**
Клиентский профиль `.ovpn` содержит сертификаты, ключ и параметры подключения. После подключения создаётся интерфейс `tun0` с адресом из VPN-подсети. Трафик шифруется и идёт через сервер.

---

**Практическая работа №3: Маршрутизация и перенаправление трафика**

**Задание:**
1. Включите IP-форвардинг на сервере.
2. Настройте push маршрутов клиентам.
3. Настройте NAT для выхода через VPN.
4. Проверьте маршруты на клиенте.
5. Объясните routed и bridged VPN.

**Решение / Команды:**
```bash
sudo sysctl -w net.ipv4.ip_forward=1
# server.conf: push "route 192.168.1.0 255.255.255.0"
sudo iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
ip route show                             # 4. Маршруты клиента
```
**Пояснения:**
Routed VPN (tun) маршрутизирует трафик между подсетями, bridged VPN (tap) объединяет в один L2-сегмент. `push "route ..."` передаёт маршруты клиентам. NAT позволяет клиентам выходить в интернет через сервер.

---

**Практическая работа №4: Диагностика и безопасность VPN**

**Задание:**
1. Посмотрите статус VPN-соединения.
2. Проверьте журнал OpenVPN.
3. Ограничьте доступ по firewall.
4. Настройте отзыв сертификата клиента.
5. Объясните типовые проблемы.

**Решение / Команды:**
```bash
sudo systemctl status openvpn@server
sudo journalctl -u openvpn@server | tail
./easyrsa revoke client1 && ./easyrsa gen-crl   # 4. Отзыв
# server.conf: crl-verify ~/openvpn-ca/pki/crl.pem
sudo iptables -A INPUT -p udp --dport 1194 -j ACCEPT
```
**Пояснения:**
Отзыв сертификата (`revoke`) и CRL блокируют доступ скомпрометированного клиента. Журнал показывает этапы рукопожатия. Типовые проблемы: несовпадение CA, неверные маршруты, firewall, конфликт подсетей.
