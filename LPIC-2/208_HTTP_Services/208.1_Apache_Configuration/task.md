[Оглавление](LPIC-2/home.md)

**Практическая работа №1: Установка и запуск Apache**

**Задание:**
1. Установите Apache 2.4.
2. Запустите и включите службу.
3. Проверьте работу через curl.
4. Посмотрите структуру конфигурации.
5. Проверьте синтаксис конфигурации.

**Решение и пояснения:**
```bash
sudo apt install -y apache2
sudo systemctl enable --now apache2
curl http://localhost                     # 3. Проверка
ls /etc/apache2/                          # 4. Структура
apache2ctl configtest                     # 5. Проверка синтаксиса
```
**Пояснения:**
Apache 2.4 в Debian использует модульную конфигурацию: `/etc/apache2/apache2.conf`, каталоги `sites-available`, `mods-available`, `conf-available`. `apache2ctl configtest` проверяет корректность до перезапуска.

---

**Практическая работа №2: Виртуальные хосты**

**Задание:**
1. Создайте каталог для нового сайта.
2. Создайте конфигурацию виртуального хоста.
3. Активируйте сайт.
4. Отключите сайт по умолчанию (опционально).
5. Проверьте работу.

**Решение и пояснения:**
```bash
sudo mkdir -p /var/www/site1/html
sudo tee /etc/apache2/sites-available/site1.conf >/dev/null <<'EOF'
<VirtualHost *:80>
    ServerName site1.lab
    DocumentRoot /var/www/site1/html
    ErrorLog ${APACHE_LOG_DIR}/site1_error.log
</VirtualHost>
EOF
sudo a2ensite site1 && sudo a2dissite 000-default
sudo systemctl reload apache2
curl -H "Host: site1.lab" http://localhost
```
**Пояснения:**
Виртуальные хосты позволяют обслуживать несколько сайтов на одном IP. `a2ensite`/`a2dissite` включают и отключают сайты (симлинки в `sites-enabled`). Разделение по имени (Name-based) использует заголовок `Host`.

---

**Практическая работа №3: Аутентификация и ограничение доступа**

**Задание:**
1. Создайте файл паролей через `htpasswd`.
2. Настройте basic-аутентификацию для каталога.
3. Ограничьте доступ по IP.
4. Настройте `.htaccess`.
5. Проверьте доступ.

**Решение и пояснения:**
```bash
sudo htpasswd -c /etc/apache2/.htpasswd user1     # 1. Файл паролей
# В конфигурации сайта:
# <Directory /var/www/site1/html/secure>
#   AuthType Basic
#   AuthName "Restricted"
#   AuthUserFile /etc/apache2/.htpasswd
#   Require valid-user
#   Require ip 192.168.1.0/24
# </Directory>
curl -u user1:pass http://localhost/secure/
```
**Пояснения:**
`mod_auth_basic` реализует базовую аутентификацию, `Require valid-user` требует логин/пароль, `Require ip` ограничивает по адресу. `.htaccess` позволяет настройки на уровне каталога (требует `AllowOverride`).

---

**Практическая работа №4: Логи и диагностика**

**Задание:**
1. Найдите файлы журналов Apache.
2. Пронаблюдайте журнал доступа в реальном времени.
3. Найдите ошибки в журнале.
4. Настройте отдельный журнал для сайта.
5. Проанализируйте коды ответов.

**Решение и пояснения:**
```bash
ls /var/log/apache2/                       # 1. access.log, error.log
sudo tail -f /var/log/apache2/access.log   # 2. Реальное время
sudo grep -i error /var/log/apache2/error.log | tail
awk '{print $9}' /var/log/apache2/access.log | sort | uniq -c | sort -nr   # 5
```
**Пояснения:**
`access.log` фиксирует запросы (формат Combined: IP, время, запрос, код, размер). `error.log` — ошибки. Анализ кодов ответа (`awk` по 9-му полю) показывает распределение 2xx/3xx/4xx/5xx.
