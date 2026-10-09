[Оглавление](LPIC-3-Security/home.md)

**Практическая работа №1: Захват и анализ трафика**

**Задание:**
1. Захватите трафик на интерфейсе.
2. Отфильтруйте по протоколу.
3. Отфильтруйте по хосту и порту.
4. Сохраните захват.
5. Проанализируйте сохранённый файл.

**Решение и пояснения:**
```bash
sudo tcpdump -i eth0 -c 20 -nn
sudo tcpdump -i eth0 icmp
sudo tcpdump -i eth0 host 8.8.8.8 and port 443
sudo tcpdump -i eth0 -w /tmp/cap.pcap
sudo tcpdump -r /tmp/cap.pcap -nn | head
```
**Пояснения:**
`tcpdump` — базовый анализатор трафика (libpcap). Фильтры BPF выбирают пакеты по протоколу, хосту, порту. Сохранённый pcap открывают в Wireshark для детального разбора. Захват — основа сетевого мониторинга и IDS.

---

**Практическая работа №2: Установка и настройка Suricata**

**Задание:**
1. Установите Suricata.
2. Проверьте конфигурацию.
3. Обновите правила.
4. Запустите IDS на интерфейсе.
5. Посмотрите срабатывания.

**Решение и пояснения:**
```bash
sudo apt install -y suricata
sudo suricata -T -c /etc/suricata/suricata.yaml -v      # 2. Проверка
sudo suricata-update                                    # 3. Правила
sudo systemctl enable --now suricata
sudo tail -f /var/log/suricata/fast.log                 # 5. Срабатывания
```
**Пояснения:**
Suricata — IDS/IPS с поддержкой сигнатур и анализа протоколов. Правила обновляются `suricata-update`. Логи: `fast.log` (быстрые события), `eve.json` (структурированные). Режим IPS требует интеграции с firewall.

---

**Практическая работа №3: Написание правил и Snort**

**Задание:**
1. Опишите синтаксис правила Suricata/Snort.
2. Создайте простое правило.
3. Проверьте правило.
4. Сравните Suricata и Snort.
5. Объясните пороговые значения.

**Решение и пояснения:**
```bash
# /var/lib/suricata/rules/local.rules:
# alert icmp any any -> any any (msg:"ICMP ping"; sid:1000001; rev:1;)
sudo suricata -T -c /etc/suricata/suricata.yaml -v
# Порог: threshold: type limit, track by_src, count 5, seconds 60;
```
**Пояснения:**
Правило описывает действие, протокол, источник/назначение, опции (`msg`, `sid`, `rev`). `sid` уникален. Пороги (`threshold`) ограничивают число срабатываний, снижая ложные тревоги. Suricata многопоточна, Snort — классический IDS.

---

**Практическая работа №4: IPS и блокировка трафика**

**Задание:**
1. Переведите Suricata в режим IPS.
2. Интегрируйте с nftables/iptables.
3. Заблокируйте подозрительный трафик.
4. Проверьте блокировку.
5. Объясните разницу IDS и IPS.

**Решение и пояснения:**
```bash
# suricata.yaml: nfq: mode: accept ; затем:
sudo iptables -I FORWARD -j NFQUEUE
# Правило с drop:
# drop icmp any any -> any any (msg:"Block ICMP"; sid:1000002; rev:1;)
sudo suricata -c /etc/suricata/suricata.yaml -q 0
```
**Пояснения:**
IDS только обнаруживает и уведомляет, IPS блокирует трафик в реальном времени. Suricata в режиме IPS использует NFQUEUE для перехвата. Ошибочные правила могут нарушить связность, поэтому IPS тестируют в режиме IDS.

---

**Практическая работа №5: Мониторинг и корреляция событий**

**Задание:**
1. Настройте отправку логов Suricata в `eve.json`.
2. Проанализируйте события.
3. Настройте уведомления.
4. Коррелируйте с системными логами.
5. Объясните централизованный SIEM.

**Решение и пояснения:**
```bash
sudo jq -c 'select(.event_type=="alert")' /var/log/suricata/eve.json | head
sudo grep -i alert /var/log/suricata/fast.log | tail
# Отправка в syslog/ELK:
# suricata.yaml: outputs: - eve-log: enabled: yes
```
**Пояснения:**
`eve.json` содержит структурированные события (алерты, DNS, HTTP). Корреляция с системными логами и централизация в SIEM (ELK, Graylog, Wazuh) выявляют сложные атаки. Мониторинг без анализа бесполезен.
