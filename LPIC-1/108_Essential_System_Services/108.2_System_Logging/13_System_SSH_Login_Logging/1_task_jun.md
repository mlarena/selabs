[Оглавление](https://gitflic.ru/project/ml/selabs/blob?file=home.md)

**Практическая работа №1: Базовый мониторинг SSH входов**     

**Задание:**     
1. Найдите файл логов SSH.     
2. Просмотрите последние 10 успешных входов по SSH.     
3. Просмотрите последние 10 неудачных попыток входа.     
4. Определите, с каких IP-адресов были успешные входы сегодня.     
5. Проверьте время последнего успешного входа.     
6. Отслеживайте SSH логи в реальном времени.     

**Решение и пояснения:**
```bash
sudo ls -la /var/log/auth.log*          # 1. Файлы логов аутентификации
sudo grep "Accepted" /var/log/auth.log | tail -10  # 2. Успешные входы
sudo grep "Failed" /var/log/auth.log | tail -10    # 3. Неудачные попытки
sudo grep "Accepted.*$(date +%Y-%m-%d)" /var/log/auth.log | awk '{print $11}' | sort -u  # 4. IP сегодня
sudo grep "Accepted" /var/log/auth.log | tail -1 | awk '{print $1,$2,$3}'  # 5. Время последнего входа
sudo tail -f /var/log/auth.log | grep sshd  # 6. Режим слежения
```
**Пояснения:**      
SSH логи обычно в `/var/log/auth.log`.           
"Accepted" — успешный вход, "Failed" — неудачная попытка.      
`$(date +%Y-%m-%d)` — текущая дата.      
`tail -f` показывает новые записи в реальном времени.      
IP-адрес обычно в 11-м поле.

---

**Практическая работа №2: Анализ подозрительной активности SSH**     

**Задание:**     
1. Найдите IP-адреса с более чем 5 неудачными попытками входа.     
2. Определите, какие пользователи подвергались атакам.     
3. Проверьте, были ли попытки входа под несуществующими пользователями.
4. Найдите использование запрещенных методов аутентификации.
5. Определите географическое расположение подозрительных IP (используя whois).     
6. Создайте отчет о подозрительной активности.     

**Решение и пояснения:**     
```bash
sudo grep "Failed" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -nr | head -10  # 1. Топ IP
sudo grep "Failed" /var/log/auth.log | awk '{print $9}' | sort | uniq -c | sort -nr  # 2. Атакуемые пользователи
sudo grep "invalid user" /var/log/auth.log | awk '{print $8,$11}' | sort -u  # 3. Несуществующие пользователи
sudo grep -E "(authentication failure|Connection closed)" /var/log/auth.log  # 4. Проблемы аутентификации
sudo grep "Failed" /var/log/auth.log | awk '{print $11}' | sort -u | head -3 | xargs -I{} whois {} | grep -i country  # 5. Страны IP
sudo grep -E "(Failed|invalid)" /var/log/auth.log > ssh_suspicious.log  # 6. Отчет
```
**Пояснения:**      
`uniq -c` подсчитывает количество попыток.      
`invalid user` указывает на попытку входа под несуществующим пользователем.      
`whois` показывает информацию об IP-адресе. Отчет помогает документировать инциденты безопасности.

---

**Практическая работа №3: Настройка детального логирования SSH**     

**Задание:**     
1. Измените уровень логирования SSH в конфигурации.     
2. Настройте логирование отдельных сессий SSH.     
3. Включите логирование времени сессий SSH.     
4. Проверьте корректность конфигурации.     
5. Примените изменения и проверьте новые логи.     
6. Создайте отдельный лог-файл для SSH.     

**Решение и пояснения:**
```bash
sudo nano /etc/ssh/sshd_config          # 1. Редактирование конфига
# Добавить или изменить:
# LogLevel VERBOSE                     # 1. Более детальные логи
# SyslogFacility AUTH                  # 2. Отдельные логи
# PrintLastLog yes                     # 3. Время последнего входа

sudo sshd -t                           # 4. Проверка конфигурации
sudo systemctl restart ssh             # 5. Применение изменений
sudo grep "sshd" /var/log/auth.log | tail -5  # 5. Проверка логов

# 6. В /etc/rsyslog.conf или /etc/rsyslog.d/:
# auth,authpriv.* /var/log/ssh.log
# sudo systemctl restart rsyslog
```
**Пояснения:**      
`LogLevel VERBOSE` дает детальную информацию.      
`sshd -t` проверяет конфиг на ошибки.      
`PrintLastLog` показывает время последнего входа при аутентификации.      
Отдельный лог-файл упрощает анализ.      
После изменений всегда перезапускайте службу.     

---

**Практическая работа №4: Автоматизация мониторинга SSH логов**     
     
**Задание:**     
1. Напишите скрипт для ежедневного анализа SSH логов.     
2. Скрипт должен считать успешные и неудачные входы.     
3. Определять наиболее активные подозрительные IP.     
4. Отправлять уведомление при обнаружении атаки (более 10 попыток с одного IP).     
5. Архивировать старые логи (старше 30 дней).     
6. Настроить запуск скрипта по расписанию.     

**Решение и пояснения:**
```bash
#!/bin/bash
# ssh_monitor.sh
LOG="/var/log/auth.log"
REPORT="/var/log/ssh_report_$(date +%Y%m%d).log"

echo "=== SSH Report $(date) ===" > $REPORT
echo "Successful logins: $(grep -c "Accepted" $LOG)" >> $REPORT
echo "Failed attempts: $(grep -c "Failed" $LOG)" >> $REPORT

# 3,4. Поиск подозрительных IP
grep "Failed" $LOG | awk '{print $11}' | sort | uniq -c | while read count ip; do
  if [ $count -gt 10 ]; then
    echo "ALERT: $ip made $count failed attempts" >> $REPORT
    # echo "Alert" | mail -s "SSH Alert" admin@example.com  # Отправка почты
  fi
done

# 5. Архивация
find /var/log -name "auth.log.*" -mtime +30 -exec gzip {} \;

# 6. Добавить в cron: 0 2 * * * /path/to/ssh_monitor.sh
```
**Пояснения:**      
Скрипт автоматизирует анализ.      
`-gt 10` — порог для алерта.      
`mail` можно использовать для отправки уведомлений.      
`find -mtime +30` находит файлы старше 30 дней.      
Cron запускает скрипт ежедневно в 2:00. Регулярный мониторинг повышает безопасность.     

[Оглавление](https://gitflic.ru/project/ml/selabs/blob?file=home.md)
