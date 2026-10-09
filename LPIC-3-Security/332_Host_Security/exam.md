[Оглавление](?file=LPIC-3-Security%2Fhome.md)

# Экзаменационные боевые задачи — Тема 332: Host Security

Задачи приближены к реальным заданиям экзамена **303-300**.

## Задача 1. Ужесточение хоста

**Условие:** Проведите базовый hardening: отключите лишние службы, настройте sysctl и SSH.

**Ожидаемый результат:** Хост защищён.

**Решение и пояснения:**
```bash
systemctl list-units --type=service --state=running
sudo systemctl disable --now rpcbind
sudo tee /etc/sysctl.d/99-hardening.conf >/dev/null <<'EOF'
net.ipv4.conf.all.rp_filter=1
net.ipv4.tcp_syncookies=1
kernel.dmesg_restrict=1
kernel.kptr_restrict=2
EOF
sudo sysctl --system
# sshd_config: PermitRootLogin no ; PasswordAuthentication no
sudo sshd -t && sudo systemctl restart ssh
```
Минимизация служб снижает поверхность атаки. sysctl защищает сеть и память. Отключение root и паролей в SSH — обязательная мера.

## Задача 2. Аудит событий

**Условие:** Настройте аудит изменений `/etc/passwd` и системных вызовов, сформируйте отчёт.

**Ожидаемый результат:** События фиксируются.

**Решение и пояснения:**
```bash
sudo apt install -y auditd
sudo auditctl -w /etc/passwd -p wa -k passwd_changes
sudo auditctl -a always,exit -F arch=b64 -S execve -k exec
sudo ausearch -k passwd_changes
sudo aureport -f
```
auditd фиксирует доступ к файлам и системные вызовы. Правила (`-w`, `-a`, `-k`) определяют, что логировать. `ausearch`/`aureport` анализируют журнал — основа расследований.

## Задача 3. Проверка целостности файлов

**Условие:** Установите AIDE, инициализируйте базу и обнаружьте изменение файла.

**Ожидаемый результат:** Изменение обнаружено.

**Решение и пояснения:**
```bash
sudo apt install -y aide
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
echo "test" | sudo tee -a /etc/hosts
sudo aide --check
sudo aide --update
```
AIDE вычисляет хэши файлов и сравнивает с базой, выявляя несанкционированные изменения. Регулярные проверки — часть HIDS. База должна быть защищена от изменений.

## Задача 4. Управление ресурсами

**Условие:** Ограничьте память и CPU сервиса, настройте лимиты пользователя.

**Ожидаемый результат:** Ограничения применяются.

**Решение и пояснения:**
```bash
# /etc/systemd/system/nginx.service.d/limits.conf:
# [Service] MemoryMax=256M ; CPUQuota=50%
sudo systemctl daemon-reload && sudo systemctl restart nginx
systemctl show nginx | grep -iE "MemoryMax|CPUQuota"
# /etc/security/limits.conf: user1 hard nproc 100
ulimit -u
```
systemd управляет ресурсами через cgroups v2. `MemoryMax`/`CPUQuota` защищают от «шумных соседей». `limits.conf` (через `pam_limits`) ограничивает ресурсы пользователей.

## Задача 5. Обнаружение руткитов

**Условие:** Проверьте систему на руткиты и настройте регулярную проверку.

**Ожидаемый результат:** Проверка выполнена, расписание настроено.

**Решение и пояснения:**
```bash
sudo apt install -y rkhunter chkrootkit
sudo rkhunter --update
sudo rkhunter --check --sk
sudo chkrootkit | grep INFECTED
# cron: 0 3 * * * /usr/bin/rkhunter --check --sk
```
`rkhunter`/`chkrootkit` ищут известные руткиты и изменения. Регулярный запуск и анализ отчётов — часть HIDS. Ложные срабатывания требуют ручной оценки.

## Задача 6. Анализ отказов MAC

**Условие:** Найдите запрещённые операции SELinux/AppArmor и скорректируйте политику.

**Ожидаемый результат:** Отказы проанализированы.

**Решение и пояснения:**
```bash
sudo ausearch -m avc -ts recent 2>/dev/null || sudo journalctl -k | grep -i apparmor | tail
sudo apt install -y apparmor-utils
sudo aa-logprof
sudo sealert -a /var/log/audit/audit.log 2>/dev/null
```
Отказы MAC (AVC/AppArmor) указывают на аномальное поведение или неверную политику. `sealert`/`aa-logprof` помогают анализировать. Данные отказов — источник для HIDS.
