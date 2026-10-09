[Оглавление](LPIC-3-Security/home.md)

# Экзаменационные боевые задачи — Тема 334: Network Security

Задачи приближены к реальным заданиям экзамена **303-300**.

## Задача 1. Ужесточение сети

**Условие:** Отключите небезопасные сетевые функции ядра и ограничьте службы.

**Ожидаемый результат:** Сеть защищена.

**Решение и пояснения:**
```bash
sudo tee /etc/sysctl.d/99-network.conf >/dev/null <<'EOF'
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.all.accept_source_route=0
net.ipv4.conf.all.rp_filter=1
net.ipv4.icmp_echo_ignore_broadcasts=1
net.ipv6.conf.all.disable_ipv6=1
EOF
sudo sysctl --system
ss -tulpn
```
Отключение редиректов и source routing, `rp_filter` (защита от spoofing), запрет ответов на broadcast-ICMP. Отключение IPv6 сокращает поверхность атаки. `ss` — инвентаризация портов.

## Задача 2. Фильтрация пакетов (nftables)

**Условие:** Настройте nftables: политика DROP, разрешите SSH из подсети и HTTP.

**Ожидаемый результат:** Фильтрация работает.

**Решение и пояснения:**
```bash
sudo nft add table inet filter
sudo nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
sudo nft add rule inet filter input ct state established,related accept
sudo nft add rule inet filter input iif lo accept
sudo nft add rule inet filter input tcp dport 22 ip saddr 192.168.1.0/24 accept
sudo nft add rule inet filter input tcp dport 80 accept
sudo nft list ruleset
sudo nft list ruleset > /etc/nftables.conf
```
nftables заменяет iptables единым синтаксисом. Политика `drop` блокирует всё, `ct state` разрешает ответы, правила разрешают нужное. Конфигурация в `/etc/nftables.conf`.

## Задача 3. Обнаружение вторжений (Suricata)

**Условие:** Установите Suricata, обновите правила и добавьте своё правило.

**Ожидаемый результат:** IDS работает, правило срабатывает.

**Решение и пояснения:**
```bash
sudo apt install -y suricata
sudo suricata-update
echo 'alert icmp any any -> any any (msg:"ICMP ping"; sid:1000001; rev:1;)' \
  | sudo tee /var/lib/suricata/rules/local.rules
sudo suricata -T -c /etc/suricata/suricata.yaml -v
sudo systemctl restart suricata
sudo tail -f /var/log/suricata/fast.log
```
Suricata — IDS/IPS. Правила описывают действие, протокол, источник/назначение, опции. `-T` проверяет конфигурацию. Логи: `fast.log`, `eve.json`.

## Задача 4. IPS и блокировка

**Условие:** Переведите Suricata в режим IPS и заблокируйте трафик по правилу.

**Ожидаемый результат:** Трафик блокируется.

**Решение и пояснения:**
```bash
# suricata.yaml: nfq: mode: accept
sudo iptables -I FORWARD -j NFQUEUE
echo 'drop icmp any any -> any any (msg:"Block ICMP"; sid:1000002; rev:1;)' \
  | sudo tee -a /var/lib/suricata/rules/local.rules
sudo suricata -c /etc/suricata/suricata.yaml -q 0
```
IDS только обнаруживает, IPS блокирует в реальном времени через NFQUEUE. Ошибочные правила могут нарушить связность — тестируйте в режиме IDS перед IPS.

## Задача 5. VPN (WireGuard)

**Условие:** Настройте WireGuard-туннель между двумя узлами.

**Ожидаемый результат:** Туннель работает, узлы доступны.

**Решение и пояснения:**
```bash
sudo apt install -y wireguard
wg genkey | tee privatekey | wg pubkey > publickey
# /etc/wireguard/wg0.conf:
# [Interface] PrivateKey=... Address=10.0.0.1/24 ListenPort=51820
# [Peer] PublicKey=<peer> AllowedIPs=10.0.0.2/32
sudo wg-quick up wg0
sudo wg show
ping -c2 10.0.0.2
```
WireGuard — современный VPN с минимальной кодовой базой. Пары ключей и `AllowedIPs` задают маршрутизацию. Прост в настройке и быстр.

## Задача 6. Диагностика сетевой безопасности

**Условие:** Проверьте открытые порты, захватите подозрительный трафик и оцените фильтрацию.

**Ожидаемый результат:** Аномалии выявлены.

**Решение и пояснения:**
```bash
sudo nmap -sT localhost
sudo ss -tulpn
sudo tcpdump -i eth0 -c 20 -nn
sudo iptables -L -n -v
sudo grep -i "UFW BLOCK" /var/log/kern.log | tail
sudo fail2ban-client status sshd
```
Инвентаризация портов (`nmap`, `ss`), захват трафика (`tcpdump`), проверка правил фильтрации, анализ блокировок. Регулярный мониторинг выявляет аномалии и попытки вторжения.
