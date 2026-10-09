[Оглавление](LPIC-2/home.md)

**Практическая работа №1: Установка и базовый веб-сервер Nginx**

**Задание:**
1. Установите Nginx.
2. Запустите службу.
3. Проверьте работу через curl.
4. Посмотрите структуру конфигурации.
5. Проверьте синтаксис конфигурации.

**Решение и пояснения:**
```bash
sudo apt install -y nginx
sudo systemctl enable --now nginx
curl http://localhost                       # 3. Проверка
ls /etc/nginx/                              # 4. Структура
sudo nginx -t                               # 5. Проверка синтаксиса
```
**Пояснения:**
Nginx — высокопроизводительный веб-сервер и прокси. Конфигурация — `/etc/nginx/nginx.conf` и `sites-available`/`conf.d`. `nginx -t` проверяет синтаксис. `nginx -s reload` перезагружает без разрыва соединений.

---

**Практическая работа №2: Виртуальные хосты (server blocks)**

**Задание:**
1. Создайте каталог сайта.
2. Создайте server block.
3. Активируйте сайт.
4. Проверьте работу.
5. Объясните, как Nginx выбирает server block.

**Решение и пояснения:**
```bash
sudo mkdir -p /var/www/site2/html
sudo tee /etc/nginx/sites-available/site2 >/dev/null <<'EOF'
server {
    listen 80;
    server_name site2.lab;
    root /var/www/site2/html;
    index index.html;
}
EOF
sudo ln -s /etc/nginx/sites-available/site2 /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
curl -H "Host: site2.lab" http://localhost
```
**Пояснения:**
Server block — аналог виртуального хоста. Nginx выбирает блок по `server_name` и `listen`. Симлинк в `sites-enabled` активирует конфигурацию. Директива `root` задаёт корневой каталог.

---

**Практическая работа №3: Reverse proxy**

**Задание:**
1. Настройте Nginx как обратный прокси.
2. Проксируйте запросы на локальный backend (Apache/приложение).
3. Передайте заголовки Host и X-Real-IP.
4. Проверьте проксирование.
5. Объясните преимущества обратного прокси.

**Решение и пояснения:**
```bash
# server block:
# location / {
#     proxy_pass http://127.0.0.1:8080;
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
# }
sudo nginx -t && sudo systemctl reload nginx
curl -H "Host: site2.lab" http://localhost
```
**Пояснения:**
Обратный прокси принимает запросы и передаёт их backend-серверу. Это даёт: TLS-терминацию, балансировку, кэширование, скрытие внутренней архитектуры. Заголовки `Host`/`X-Real-IP` сохраняют исходные данные клиента.

---

**Практическая работа №4: Балансировка нагрузки**

**Задание:**
1. Настройте upstream с двумя backend.
2. Включите балансировку.
3. Настройте проверку доступности.
4. Проверьте распределение запросов.
5. Объясните методы балансировки.

**Решение и пояснения:**
```bash
# http-блок:
# upstream backend {
#     server 127.0.0.1:8080;
#     server 127.0.0.1:8081;
# }
# location / { proxy_pass http://backend; }
sudo nginx -t && sudo systemctl reload nginx
for i in $(seq 1 6); do curl -s -H "Host: site2.lab" http://localhost | grep -o 'server[0-9]'; done
```
**Пояснения:**
`upstream` описывает пул серверов. По умолчанию — round-robin; доступны `least_conn`, `ip_hash`, веса. Это повышает отказоустойчивость и распределяет нагрузку между backend-серверами.
