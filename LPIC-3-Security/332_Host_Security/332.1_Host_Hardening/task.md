[Оглавление](LPIC-3-Securityhome.md)

**Практическая работа №1: Минимизация поверхности атаки**

**Задание:**
1. Посмотрите запущенные службы.
2. Найдите ненужные службы.
3. Отключите лишнюю службу.
4. Посмотрите открытые порты.
5. Объясните принцип минимализма.

**Решение и пояснения:**
```bash
systemctl list-unit-files --state=enabled        # 1. Включённые службы
systemctl list-units --type=service --state=running
sudo systemctl disable --now telnet.socket       # 3. Отключение
ss -tulpn                                         # 4. Открытые порты
```
**Пояснения:**
Каждая запущенная служба — потенциальная уязвимость. Hardening начинается с удаления/отключения ненужного ПО и закрытия портов. Принцип минимализма снижает поверхность атаки и упрощает аудит.

---

**Практическая работа №2: Ужесточение sysctl и ядра**

**Задание:**
1. Посмотрите параметры безопасности.
2. Отключите IP-форвардинг и ICMP-редиректы.
3. Включите защиту от spoofing и SYN-флуда.
4. Ограничьте dmesg/kptr.
5. Сделайте настройки постоянными.

**Решение и пояснения:**
```bash
sudo tee /etc/sysctl.d/99-hardening.conf >/dev/null <<'EOF'
net.ipv4.ip_forward=0
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.all.rp_filter=1
net.ipv4.tcp_syncookies=1
kernel.dmesg_restrict=1
kernel.kptr_restrict=2
kernel.randomize_va_space=2
EOF
sudo sysctl --system
sudo sysctl -a | grep -E "rp_filter|syncookies|dmesg_restrict"
```
**Пояснения:**
Параметры ядра (`sysctl`) влияют на безопасность сети и памяти. Отключение redirects/forwarding, включение `rp_filter` и `syncookies`, ограничение `dmesg`/указателей, полный ASLR — базовый hardening. Настройки — в `/etc/sysctl.d/`.

---

**Практическая работа №3: Ограничение доступа и привилегий**

**Задание:**
1. Настройте политику паролей.
2. Ограничьте sudo.
3. Замените setuid на capabilities.
4. Настройте umask.
5. Проверьте применение.

**Решение и пояснения:**
```bash
# /etc/sudoers.d/admins: %admins ALL=(ALL) ALL
sudo getcap /usr/bin/ping
sudo setcap cap_net_raw+ep /usr/bin/ping
umask 027
# /etc/login.defs: UMASK 027
sudo passwd -S root
```
**Пояснения:**
Hardening включает управление привилегиями: строгие правила sudo, замена setuid на capabilities, ограничительный umask (027), политика паролей. Принцип минимальных привилегий ограничивает ущерб от компрометации.

---

**Практическая работа №4: Жёсткость SSH и сервисов**

**Задание:**
1. Отключите root-вход по SSH.
2. Отключите вход по паролю.
3. Ограничьте список пользователей.
4. Ограничьте ресурсы сервиса через systemd.
5. Проверьте конфигурацию.

**Решение и пояснения:**
```bash
# sshd_config: PermitRootLogin no ; PasswordAuthentication no ; AllowUsers user1
sudo sshd -t && sudo systemctl restart ssh
# /etc/systemd/system/nginx.service.d/override.conf:
# [Service]
# ProtectSystem=strict
# PrivateTmp=yes
# NoNewPrivileges=yes
sudo systemctl daemon-reload && systemctl restart nginx
systemd-analyze security nginx
```
**Пояснения:**
SSH — частая цель атак: отключают root-вход и пароли, ограничивают пользователей. systemd-sandbox (`ProtectSystem`, `PrivateTmp`, `NoNewPrivileges`) изолирует сервисы. `systemd-analyze security` оценивает изоляцию.

---

**Практическая работа №5: Управление обновлениями и целостностью ПО**

**Задание:**
1. Проверьте доступные обновления безопасности.
2. Настройте автоматические обновления безопасности.
3. Проверьте подписи пакетов.
4. Проверьте целостность установленного ПО.
5. Объясните важность патчей.

**Решение и пояснения:**
```bash
sudo apt update && apt list --upgradable 2>/dev/null | grep -i security
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades       # 2. Автообновления
apt-cache policy | grep -i security
debsums -s 2>/dev/null | head || echo "установите debsums"   # 4. Проверка
```
**Пояснения:**
Своевременное обновление закрывает известные уязвимости. `unattended-upgrades` автоматически ставит патчи безопасности. Проверка целостности (`debsums`) выявляет изменённые системные файлы. Регулярный патчинг — фундамент безопасности хоста.
