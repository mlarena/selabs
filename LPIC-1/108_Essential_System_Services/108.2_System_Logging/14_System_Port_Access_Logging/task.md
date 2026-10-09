[Оглавление](https://gitflic.ru/project/ml/selabs/blobhome.md)

**Практическая работа №1: Мониторинг обращений к портам через журналы**     

**Задание:**     
1. Найдите логи, содержащие информацию о сетевых подключениях.     
2. Просмотрите обращения к порту 22 (SSH) за последние 24 часа.     
3. Определите, какие IP-адреса чаще всего обращались к порту 80 (HTTP).     
4. Найдите неудачные попытки подключения (отказы соединения).     
5. Проверьте логи обращений к нестандартным портам (>1024).     
6. Отслеживайте обращения к портам в реальном времени.     

**Решение и пояснения:**
```bash
sudo journalctl -u systemd-networkd --since "24 hours ago"  # 1. Сетевые логи
sudo journalctl | grep ":22" | grep -E "(ACCEPT|CONNECT)" | tail -20  # 2. Обращения к порту 22
sudo grep ":80" /var/log/syslog | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr  # 3. Топ IP порта 80
sudo journalctl | grep -E "(refused|rejected)" | tail -10  # 4. Отказы соединения
sudo netstat -tulnp 2>/dev/null | grep -E ":([1-9][0-9]{3,}|[6-9][0-9]{2})"  # 5. Нестандартные порты
sudo tail -f /var/log/syslog | grep -E "port|Port"  # 6. Реальное время
```
**Пояснения:**      
`journalctl -u systemd-networkd` показывает сетевые события.      
`grep ":22"` ищет обращения к порту.      
`refused` или `rejected` указывают на отказы.      
`netstat` показывает текущие подключения.      
Регулярные выражения помогают фильтровать нестандартные порты.     

---

**Практическая работа №2: Анализ логов брандмауэра (iptables/ufw)**     

**Задание:**     
1. Включите логирование для UFW (если используется).     
2. Просмотрите логи блокировок брандмауэра.     
3. Определите, какие порты чаще всего блокируются.     
4. Найдите IP-адреса, с которых идут частые блокировки.     
5. Проанализируйте логи разрешенных подключений.     
6. Настройте отдельный файл логов для блокировок.     

**Решение и пояснения:**     
```bash
sudo ufw logging on                     # 1. Включение логирования UFW
sudo grep "\[UFW BLOCK\]" /var/log/ufw.log | tail -20  # 2. Логи блокировок
sudo awk '/\[UFW BLOCK\]/ {print $8}' /var/log/ufw.log | sort | uniq -c | sort -nr  # 3. Часто блокируемые порты
sudo awk '/\[UFW BLOCK\]/ {print $7}' /var/log/ufw.log | cut -d= -f2 | sort | uniq -c | sort -nr  # 4. Топ IP
sudo grep "\[UFW ALLOW\]" /var/log/ufw.log | tail -10  # 5. Разрешенные подключения
echo "kern.* /var/log/ufw_block.log" | sudo tee /etc/rsyslog.d/ufw.conf && sudo systemctl restart rsyslog  # 6
```
**Пояснения:** 
UFW логирует блокировки с меткой `[UFW BLOCK]`.      
`$8` обычно содержит порт,      
`$7` — IP. Раздельные логи упрощают анализ.      
Для iptables аналогично используются `LOG` правила и просмотр через `dmesg` или `/var/log/kern.log`.

---

**Практическая работа №3: Логирование с использованием tcpdump**

**Задание:**      
1. Запишите сетевой трафик на порт 22 в течение 30 секунд.      
2. Проанализируйте записанный трафик (источники и цели).      
3. Отфильтруйте трафик только с определенного IP.      
4. Подсчитайте количество пакетов на разные порты.      
5. Найдите подозрительные пакеты (например, сканирование портов).      
6. Сохраните результаты анализа в файл.      

**Решение и пояснения:**      
```bash
sudo tcpdump -i any port 22 -w ssh_capture.pcap -G 30  # 1. Запись 30 сек
sudo tcpdump -r ssh_capture.pcap | awk '{print $3,$5}' | head -20  # 2. Анализ
sudo tcpdump -r ssh_capture.pcap src host 192.168.1.1  # 3. Фильтр по IP
sudo tcpdump -r ssh_capture.pcap | awk -F'.' '{print $NF}' | cut -d: -f1 | sort | uniq -c  # 4. Подсчет пакетов по портам
sudo tcpdump -r ssh_capture.pcap 'tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0'  # 5. SYN-сканирование
sudo tcpdump -r ssh_capture.pcap > port_analysis.txt   # 6. Сохранение
```
**Пояснения:**       
`tcpdump` — сниффер сетевого трафика.       
`-w` записывает в файл,       
`-r` читает.       
`port 22` фильтрует по порту.       
`src host` фильтрует по IP источника.       
Флаги `tcp-syn` без `tcp-ack` часто указывают на сканирование. 

**Внимание:** Используйте только на своих системах или с разрешения.

---

**Практическая работа №4: Автоматизация анализа обращений к портам**

**Задание:**      
1. Напишите скрипт для ежедневного анализа обращений к портам.      
2. Определяйте топ-10 IP по количеству обращений.      
3. Выявляйте сканирование портов (много SYN к разным портам).      
4. Уведомляйте о подозрительной активности (например, >100 обращений с одного IP).      
5. Архивируйте логи старше 7 дней.      
6. Настройте запуск скрипта раз в час через cron.      

**Решение и пояснения:**
```bash
#!/bin/bash
# port_monitor.sh
LOG="/var/log/syslog"
REPORT="/var/log/port_report_$(date +%Y%m%d).log"

echo "=== Port Access Report $(date) ===" > $REPORT
echo "Top 10 source IPs:" >> $REPORT
grep -E "port [0-9]+" $LOG | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -10 >> $REPORT

# 3,4. Обнаружение сканирования
grep "SYN" $LOG | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | while read count ip; do
  if [ $count -gt 100 ]; then
    echo "ALERT: Possible port scan from $ip ($count SYN packets)" >> $REPORT
  fi
done

# 5. Архивация старых логов
find /var/log -name "syslog.*" -mtime +7 -exec gzip {} \;

# 6. Cron: 0 * * * * /path/to/port_monitor.sh
```
**Пояснения:** 
Скрипт автоматизирует рутинный анализ.       
`grep -E "port [0-9]+"` ищет упоминания портов.       
Подсчет SYN-пакетов помогает обнаружить сканирование.       
Порог в 100 пакетов настраивается.       
`find -mtime +7` находит файлы старше 7 дней.       
Регулярные отчеты улучшают безопасность.

[Оглавление](https://gitflic.ru/project/ml/selabs/blobhome.md)