[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 208: HTTP Services

Задачи приближены к реальным заданиям экзамена **202-450**.

## Задача 1. Настройка виртуальных хостов Apache

**Условие:** Настройте два сайта на одном IP с разными DocumentRoot.

**Ожидаемый результат:** Оба сайта доступны по имени.

**Решение и пояснения:**
```bash
sudo tee /etc/apache2/sites-available/site1.conf >/dev/null <<'EOF'
<VirtualHost *:80>
    ServerName site1.lab
    DocumentRoot /var/www/site1
    ErrorLog ${APACHE_LOG_DIR}/site1_error.log
</VirtualHost>
EOF
sudo a2ensite site1 && sudo apache2ctl configtest && sudo systemctl reload apache2
curl -H "Host: site1.lab" http://localhost
```
Name-based виртуальные хосты используют заголовок `Host`. `a2ensite` включает сайт (симлинк в `sites-enabled`). `configtest` проверяет синтаксис.

## Задача 2. HTTPS с сертификатом

**Условие:** Настройте HTTPS с самоподписанным сертификатом и перенаправлением с HTTP.

**Ожидаемый результат:** Сайт доступен по HTTPS, HTTP перенаправляет.

**Решение и пояснения:**
```bash
sudo a2enmod ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/site.key -out /etc/ssl/certs/site.crt -subj "/CN=site1.lab"
# <VirtualHost *:443> SSLEngine on; SSLCertificateFile ...; SSLCertificateKeyFile ...
# Redirect permanent / https://site1.lab/
sudo a2ensite default-ssl && sudo systemctl reload apache2
curl -k https://localhost
```
`mod_ssl` включает HTTPS. Сертификат содержит открытый ключ, ключ хранится отдельно с правами 600. `Redirect permanent` переводит HTTP на HTTPS.

## Задача 3. Аутентификация и ограничение доступа

**Условие:** Защитите каталог паролем и ограничьте доступ по IP.

**Ожидаемый результат:** Доступ только с паролем и из подсети.

**Решение и пояснения:**
```bash
sudo htpasswd -c /etc/apache2/.htpasswd user1
# <Directory /var/www/site1/secure>
#   AuthType Basic
#   AuthName "Restricted"
#   AuthUserFile /etc/apache2/.htpasswd
#   Require valid-user
#   Require ip 192.168.1.0/24
# </Directory>
sudo systemctl reload apache2
curl -u user1:pass http://localhost/secure/
```
`mod_auth_basic` реализует basic-аутентификацию, `Require valid-user` требует логин/пароль, `Require ip` ограничивает по адресу. Для HTTPS пароль передаётся в защищённом виде.

## Задача 4. Настройка Nginx как reverse proxy

**Условие:** Настройте Nginx как обратный прокси к Apache с балансировкой двух backend.

**Ожидаемый результат:** Запросы распределяются между backend.

**Решение и пояснения:**
```bash
# /etc/nginx/sites-available/proxy:
# upstream backend { server 127.0.0.1:8080; server 127.0.0.1:8081; }
# server { listen 80; server_name site.lab;
#   location / { proxy_pass http://backend;
#     proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; } }
sudo nginx -t && sudo systemctl reload nginx
```
`upstream` описывает пул серверов (round-robin по умолчанию). Заголовки `Host`/`X-Real-IP` сохраняют данные клиента. Обратный прокси даёт TLS-терминацию, кэш, балансировку.

## Задача 5. Squid как кэширующий прокси

**Условие:** Настройте Squid, разрешите доступ только своей подсети и запретите один домен.

**Ожидаемый результат:** Прокси работает с ограничениями.

**Решение и пояснения:**
```bash
# /etc/squid/squid.conf:
# acl localnet src 192.168.1.0/24
# acl blocked dstdomain .example.com
# http_access allow localnet
# http_access deny blocked
# http_access deny all
sudo squid -k parse && sudo systemctl restart squid
curl -x http://localhost:3128 http://example.com
```
ACL описывают условия, `http_access` применяет по порядку. `deny all` в конце закрывает всё. Squid кэширует ответы (`cache_dir`, `cache_mem`).

## Задача 6. Анализ логов веб-сервера

**Условие:** Найдите топ-5 IP по числу запросов и распределение кодов ответа.

**Ожидаемый результат:** Анализ логов выполнен.

**Решение и пояснения:**
```bash
awk '{print $1}' /var/log/apache2/access.log | sort | uniq -c | sort -rn | head -5
awk '{print $9}' /var/log/apache2/access.log | sort | uniq -c | sort -rn
grep " 500 " /var/log/apache2/access.log | tail
sudo tail -f /var/log/apache2/error.log
```
Логи access/error — в `/var/log/apache2/` (или `/var/log/nginx/`). `awk` по полям извлекает IP и коды. Анализ выявляет атаки, ошибки, нагрузку. Ротация — через logrotate.
