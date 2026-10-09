[Оглавление](LPIC-3-Securityhome.md)

**Практическая работа №1: Основы сетевого hardening**

**Задание:**
1. Посмотрите сетевые параметры ядра.
2. Отключите ICMP-редиректы и source routing.
3. Включите защиту от spoofing.
4. Отключите IPv6 (если не используется).
5. Сделайте настройки постоянными.

**Решение и пояснения:**
```bash
sudo tee /etc/sysctl.d/99-network-hardening.conf >/dev/null <<'EOF'
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.all.accept_source_route=0
net.ipv4.conf.all.rp_filter=1
net.ipv4.icmp_echo_ignore_broadcasts=1
net.ipv6.conf.all.disable_ipv6=1
EOF
sudo sysctl --system
sudo sysctl -a | grep -E "accept_redirects|rp_filter"
```
**Пояснения:**
Сетевой hardening отключает небезопасные функции: редиректы, source routing, ответы на broadcast-ICMP. `rp_filter` защищает от IP-spoofing. Отключение IPv6 сокращает поверхность атаки, если он не нужен.

---

**Практическая работа №2: Ограничение сетевых служб**

**Задание:**
1. Посмотрите слушающие сокеты.
2. Привяжите службу к нужному интерфейсу.
3. Отключите ненужные сетевые службы.
4. Настройте TCP Wrappers (если поддерживается).
5. Проверьте результат.

**Решение и пояснения:**
```bash
ss -tulpn                                   # 1. Слушающие сокеты
# Служба слушает только localhost:
# в конфигурации: listen-address=127.0.0.1
sudo systemctl disable --now rpcbind        # 3. Отключение
# /etc/hosts.allow: sshd: 192.168.1.0/24
```
**Пояснения:**
Службы, доступные только локально, снижают риск. Привязка к `127.0.0.1`, отключение лишнего (rpcbind, telnet) и ограничение по хостам (TCP Wrappers) уменьшают поверхность атаки. Проверка — `ss -tulpn`.

---

**Практическая работа №3: Безопасность SSH на уровне сети**

**Задание:**
1. Ограничьте доступ к SSH по подсети (firewall).
2. Настройте rate limiting.
3. Смените порт SSH (опционально).
4. Ограничьте алгоритмы SSH.
5. Проверьте доступ.

**Решение и пояснения:**
```bash
sudo iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -m limit --limit 3/min -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j DROP
# sshd_config: Ciphers aes256-gcm@openssh.com ; KexAlgorithms curve25519-sha256
sudo sshd -t && sudo systemctl restart ssh
```
**Пояснения:**
Ограничение SSH по подсети и rate limiting затрудняют перебор. Ограничение алгоритмов (сильные шифры и обмен ключами) повышает стойкость. Смена порта — слабая мера, но снижает автоматизированный шум.

---

**Практическая работа №4: Порт knocking и защита от сканирования**

**Задание:**
1. Опишите концепцию port knocking.
2. Настройте `knockd` (концептуально).
3. Опишите fail2ban для сетевых служб.
4. Настройте защиту от сканирования.
5. Объясните ограничения этих мер.

**Решение и пояснения:**
```bash
sudo apt install -y knockd
# /etc/knockd.conf:
# [openSSH]
# sequence = 7000,8000,9000
# command = /sbin/iptables -A INPUT -s %IP% -p tcp --dport 22 -j ACCEPT
sudo systemctl enable --now knockd
sudo fail2ban-client status sshd
```
**Пояснения:**
Port knocking открывает порт только после «секретной» последовательности. fail2ban блокирует IP после неудач. Эти меры повышают барьер, но не заменяют аутентификацию и шифрование. Важно не создавать ложного чувства безопасности.

---

**Практическая работа №5: Сегментация и мониторинг сети**

**Задание:**
1. Опишите сегментацию сети.
2. Настройте отдельные подсети/VLAN (концептуально).
3. Ограничьте трафик между сегментами.
4. Настройте мониторинг трафика.
5. Объясните принцип наименьшего доступа.

**Решение и пояснения:**
```bash
ip -br addr show
sudo tcpdump -i eth0 -c 20 -nn
sudo iftop -t -s 5 2>/dev/null || echo "установите iftop"
# Firewall: разрешить только необходимые потоки между подсетями
sudo iptables -A FORWARD -s 192.168.10.0/24 -d 192.168.20.0/24 -p tcp --dport 443 -j ACCEPT
```
**Пояснения:**
Сегментация (VLAN, подсети) ограничивает распространение атак. Между сегментами разрешают только необходимые потоки (принцип наименьшего доступа). Мониторинг (`tcpdump`, iftop) помогает обнаруживать аномалии.
