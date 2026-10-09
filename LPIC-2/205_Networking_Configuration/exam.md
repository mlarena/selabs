[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 205: Networking Configuration

Задачи приближены к реальным заданиям экзамена **201-450**.

## Задача 1. Настройка интерфейсов и маршрутизации

**Условие:** Настройте два интерфейса в разных подсетях и статический маршрут между ними.

**Ожидаемый результат:** Маршрутизация работает.

**Решение и пояснения:**
```bash
sudo ip addr add 10.0.1.1/24 dev eth1
sudo ip addr add 10.0.2.1/24 dev eth2
sudo ip route add 10.0.3.0/24 via 10.0.2.2 dev eth2
ip route show
ip route get 10.0.3.5
```
`ip addr` добавляет адреса, `ip route` — маршруты. `ip route get` показывает, каким маршрутом пойдёт пакет. Longest prefix match выбирает наиболее специфичный маршрут.

## Задача 2. Настройка беспроводного соединения

**Условие:** Подключитесь к WPA2-сети через `wpa_supplicant` и получите IP.

**Ожидаемый результат:** Беспроводное соединение установлено.

**Решение и пояснения:**
```bash
sudo ip link set wlan0 up
iw dev wlan0 scan | grep SSID
wpa_passphrase MyNet 'password' | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf
sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
sudo dhclient wlan0
iw dev wlan0 link
```
`iw` — современный инструмент для wireless. `wpa_supplicant` аутентифицирует WPA/WPA2. `dhclient` получает IP. NetworkManager обычно управляет этим автоматически.

## Задача 3. Анализ сетевого трафика

**Условие:** Захватите трафик, отфильтруйте по порту и сохраните для анализа.

**Ожидаемый результат:** Захват выполнен.

**Решение и пояснения:**
```bash
sudo tcpdump -i eth0 -c 20 -nn
sudo tcpdump -i eth0 port 22
sudo tcpdump -i eth0 host 8.8.8.8 and port 443
sudo tcpdump -i eth0 -w /tmp/cap.pcap
sudo tcpdump -r /tmp/cap.pcap -nn | head
```
`tcpdump` — анализатор трафика. Фильтры BPF выбирают пакеты. `-w` пишет pcap (открывается в Wireshark), `-r` читает. Захват требует root.

## Задача 4. Диагностика сетевых соединений

**Условие:** Найдите процессы, слушающие порты, и соединения в необычных состояниях.

**Ожидаемый результат:** Соединения проанализированы.

**Решение и пояснения:**
```bash
sudo ss -tlnp
sudo ss -tan state time-wait | wc -l
sudo lsof -i :80
ss -tan | awk '{print $1}' | sort | uniq -c
```
`ss` заменяет `netstat`. Состояния TCP: LISTEN, ESTABLISHED, TIME_WAIT, CLOSE_WAIT. Много TIME_WAIT — норма при интенсивных коротких соединениях. `lsof -i` связывает порт с процессом.

## Задача 5. Устранение неполадок сети

**Условие:** Пользователь не может открыть сайт. Локализуйте проблему.

**Ожидаемый результат:** Причина найдена.

**Решение и пояснения:**
```bash
ping -c2 127.0.0.1 ; ping -c2 <gateway> ; ping -c2 8.8.8.8
getent hosts example.com
dig example.com @8.8.8.8
traceroute 8.8.8.8
curl -v http://example.com 2>&1 | head
```
Порядок: интерфейс → шлюз → маршрут → DNS → приложение. Если ping по IP работает, а имя нет — DNS. `curl -v` показывает этап отказа (DNS, соединение, TLS, HTTP).

## Задача 6. Постоянная конфигурация через NetworkManager

**Условие:** Создайте статическое подключение, задайте DNS и метрику, активируйте его.

**Ожидаемый результат:** Подключение сохранено и активно.

**Решение и пояснения:**
```bash
nmcli con add type ethernet ifname eth0 con-name static1 ip4 192.168.1.50/24 gw4 192.168.1.1
nmcli con mod static1 ipv4.dns "192.168.1.1 8.8.8.8"
nmcli con mod static1 ipv4.dns-search "lab.local"
nmcli con mod static1 ipv4.route-metric 100
nmcli con up static1
nmcli -f all con show static1
```
NetworkManager хранит подключения в `/etc/NetworkManager/system-connections/`. `nmcli con mod` меняет параметры. Метрика определяет приоритет маршрута при нескольких подключениях.
