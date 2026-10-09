Мониторинг SSH подключений в Debian:

## Мониторинг SSH подключений на стандартном порту (22)

### Настройка расширенного логирования в SSH
```bash
# Редактируем конфиг SSH
sudo nano /etc/ssh/sshd_config

# Добавляем/проверяем параметры:
LogLevel VERBOSE  # или INFO
SyslogFacility AUTH
```

### Просмотр логов
```bash
# Основные логи аутентификации
sudo tail -f /var/log/auth.log

# Только SSH логи
sudo journalctl -u ssh -f
sudo grep sshd /var/log/auth.log

# С подробной информацией
sudo journalctl -u ssh --since "1 hour ago" -o verbose
```


## Базовые команды для просмотра логов SSH

### Только логи SSH (sshd):
```bash
# Все логи SSH из auth.log
sudo grep sshd /var/log/auth.log

# Только за сегодня
sudo grep sshd /var/log/auth.log | grep "$(date +'%b %d')"

# С контекстом (строки до и после)
sudo grep -B2 -A2 sshd /var/log/auth.log
```

### В реальном времени:
```bash
# Все логи в реальном времени
sudo tail -f /var/log/auth.log

# Только SSH логи в реальном времени
sudo tail -f /var/log/auth.log | grep --line-buffered sshd

# С цветовой подсветкой
sudo tail -f /var/log/auth.log | grep --color=always -E "(sshd|Failed|Invalid)"
```

## Информативные способы просмотра логов

### С журналом systemd (journalctl):
```bash
# Все логи SSH службы
sudo journalctl -u ssh

# В реальном времени
sudo journalctl -u ssh -f

# С подробной информацией
sudo journalctl -u ssh -o verbose

# За конкретный период
sudo journalctl -u ssh --since "2024-01-17 00:00:00" --until "2024-01-17 23:59:59"

# Логи с приоритетом (err, warning, info)
sudo journalctl -u ssh -p err
```

### С фильтрацией по ключевым словам:
```bash
# Только неудачные попытки
sudo grep "Failed password" /var/log/auth.log

# Только несуществующие пользователи
sudo grep "Invalid user" /var/log/auth.log

# Успешные подключения
sudo grep "Accepted password" /var/log/auth.log
sudo grep "session opened" /var/log/auth.log

# Все вместе с цветами
sudo grep -E "(Accepted|Failed|Invalid)" /var/log/auth.log | \
  sed 's/Accepted/\x1b[32m&\x1b[0m/g; s/Failed/\x1b[31m&\x1b[0m/g; s/Invalid/\x1b[33m&\x1b[0m/g'
```


### Создание информативных скриптов:

**Скрипт информативного вывода:**
```bash
#!/bin/bash
# ssh_log_viewer.sh

LOG_FILE="/var/log/auth.log"

echo -e "\n$(tput setaf 6)=== SSH LOGS - $(date) ===$(tput sgr0)\n"

# Successful connections (green)
echo -e "$(tput setaf 2)SUCCESSFUL CONNECTIONS:$(tput sgr0)"
grep "Accepted" $LOG_FILE | tail -5 | while read line; do
    echo "  $line"
done

# Failed attempts (red)
echo -e "\n$(tput setaf 1)FAILED ATTEMPTS:$(tput sgr0)"
grep "Failed password" $LOG_FILE | tail -5 | while read line; do
    echo "  $line"
done

# Invalid users (yellow)
echo -e "\n$(tput setaf 3)INVALID USERS:$(tput sgr0)"
grep "Invalid user" $LOG_FILE | tail -5 | while read line; do
    echo "  $line"
done

# Statistics
echo -e "\n$(tput setaf 4)TODAY STATISTICS:$(tput sgr0)"
echo "  Successful: $(grep "$(date +'%b %d')" $LOG_FILE | grep -c "Accepted")"
echo "  Failed: $(grep "$(date +'%b %d')" $LOG_FILE | grep -c "Failed password")"
echo "  Invalid users: $(grep "$(date +'%b %d')" $LOG_FILE | grep -c "Invalid user")"
```

**Мониторинг в реальном времени с детализацией:**
```bash
#!/bin/bash
# ssh_monitor.sh

watch -n 5 -c '
echo "=== SSH CONNECTIONS LIVE ==="
echo "Time: $(date)"
echo "============================="
echo ""
echo "Active SSH sessions:"
netstat -tn | grep ":22" | wc -l
echo ""
echo "Recent events:"
tail -10 /var/log/auth.log | grep sshd | \
  sed "s/Accepted/\x1b[32m&\x1b[0m/g;
       s/Failed/\x1b[31m&\x1b[0m/g;
       s/Invalid/\x1b[33m&\x1b[0m/g"
echo ""
echo "Top attacking IPs:"
grep "Failed password" /var/log/auth.log | \
  grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | \
  sort | uniq -c | sort -nr | head -5
'
```
