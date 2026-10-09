[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 212: System Security

Задачи приближены к реальным заданиям экзамена **202-450**.

## Задача 1. Настройка маршрутизатора и NAT

**Условие:** Настройте Linux-шлюз: IP-форвардинг, NAT и разрешение форвардинга.

**Ожидаемый результат:** Клиенты выходят в интернет через шлюз.

**Решение и пояснения:**
```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-forward.conf
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
```
IP-форвардинг позволяет маршрутизацию, NAT подменяет источник. Правило `ESTABLISHED,RELATED` разрешает ответы. Это основа интернет-шлюза.

## Задача 2. Перенаправление портов

**Условие:** Опубликуйте внутренний веб-сервер на внешнем порту 8080.

**Ожидаемый результат:** Внешние запросы попадают на внутренний сервер.

**Решение и пояснения:**
```bash
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.20:80
sudo iptables -A FORWARD -p tcp -d 192.168.1.20 --dport 80 -j ACCEPT
sudo iptables -t nat -L PREROUTING -n -v
```
DNAT перенаправляет входящие соединения (port forwarding). Используется для публикации сервисов. Ограничение по источнику (`-s`) повышает безопасность.

## Задача 3. Жёсткость SSH

**Условие:** Настройте SSH: только по ключам, без root, ограничьте пользователей и попытки.

**Ожидаемый результат:** SSH настроен безопасно.

**Решение и пояснения:**
```bash
# sshd_config:
# PermitRootLogin no
# PasswordAuthentication no
# PubKeyAuthentication yes
# AllowUsers user1 user2
# MaxAuthTries 3
sudo sshd -t && sudo systemctl restart ssh
ssh -o PreferredAuthentications=publickey user1@server
```
Отключение root и паролей, ограничение пользователей и попыток — базовый hardening SSH. `sshd -t` проверяет конфигурацию перед перезапуском (не потерять доступ).

## Задача 4. Fail2ban

**Условие:** Защитите SSH от перебора с помощью fail2ban.

**Ожидаемый результат:** IP блокируются после неудач.

**Решение и пояснения:**
```bash
sudo apt install -y fail2ban
# /etc/fail2ban/jail.local:
# [sshd] enabled = true
# maxretry = 3
# bantime = 3600
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd
sudo fail2ban-client status sshd | grep Banned
```
Fail2ban читает логи и блокирует IP после N неудачных попыток через iptables/nftables. `jail.local` переопределяет настройки. `fail2ban-client` показывает статус.

## Задача 5. FTP-сервер

**Условие:** Настройте vsftpd с локальными пользователями и пассивным режимом.

**Ожидаемый результат:** FTP работает с ограничениями.

**Решение и пояснения:**
```bash
sudo apt install -y vsftpd
# vsftpd.conf:
# anonymous_enable=NO
# local_enable=YES
# write_enable=YES
# pasv_enable=YES
# pasv_min_port=40000
# pasv_max_port=40100
sudo systemctl restart vsftpd
sudo iptables -A INPUT -p tcp --dport 40000:40100 -j ACCEPT
```
Пассивный режим предпочтителен за NAT: клиент подключается к серверу, нужен диапазон портов. FTP передаёт пароли открытым текстом — предпочитают SFTP/FTPS.

## Задача 6. VPN (OpenVPN)

**Условие:** Настройте OpenVPN-сервер с сертификатами и NAT для клиентов.

**Ожидаемый результат:** Клиенты подключаются и выходят в интернет через VPN.

**Решение и пояснения:**
```bash
sudo apt install -y openvpn easy-rsa
make-cadir ~/openvpn-ca && cd ~/openvpn-ca
./easyrsa init-pki && ./easyrsa build-ca nopass
./easyrsa gen-req server nopass && ./easyrsa sign-req server server
./easyrsa gen-dh
# server.conf: dev tun ; proto udp ; ca/cert/key ; dh ; push "redirect-gateway def1"
sudo iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
sudo systemctl enable --now openvpn@server
```
OpenVPN строит VPN на TLS. `push "redirect-gateway def1"` направляет весь трафик клиента через VPN. NAT нужен для выхода в интернет. Отзыв клиентов — `easyrsa revoke`.

## Задача 7. Аудит безопасности

**Условие:** Проведите базовый аудит: открытые порты, обновления, SUID-файлы, пустые пароли.

**Ожидаемый результат:** Отчёт по безопасности составлен.

**Решение и пояснения:**
```bash
sudo ss -tulpn
apt list --upgradable 2>/dev/null | grep -i security
find / -perm -4000 -type f 2>/dev/null
sudo awk -F: '($2==""){print $1}' /etc/shadow
sudo apt install -y lynis && sudo lynis audit system
```
Аудит выявляет: лишние порты, устаревшие пакеты, опасные SUID-файлы, пустые пароли. `lynis` автоматизирует проверки. Регулярный аудит — часть управления безопасностью.
