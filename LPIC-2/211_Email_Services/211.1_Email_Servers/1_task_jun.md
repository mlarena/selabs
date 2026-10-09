[Оглавление](?file=LPIC-2%2Fhome.md)

**Практическая работа №1: Установка и базовая настройка Postfix**

**Задание:**
1. Установите Postfix.
2. Посмотрите основные параметры конфигурации.
3. Настройте имя домена и хоста.
4. Проверьте конфигурацию.
5. Запустите службу и отправьте тестовое письмо.

**Решение и пояснения:**
```bash
sudo apt install -y postfix mailutils
postconf -n                              # 2. Не-дефолтные параметры
sudo postconf -e "myhostname=mail.lab"   # 3. Имя хоста
sudo postconf -e "mydomain=lab"          # 3. Домен
sudo postfix check                       # 4. Проверка
sudo systemctl restart postfix
echo "test" | mail -s "test" user1       # 5. Отправка
```
**Пояснения:**
Postfix — популярный MTA. Конфигурация в `/etc/postfix/main.cf` (основное) и `master.cf` (сервисы). `postconf -n` показывает изменённые параметры, `postconf -e` задаёт параметр. `postfix check` проверяет конфигурацию.

---

**Практическая работа №2: Алиасы, домены и виртуальные пользователи**

**Задание:**
1. Настройте алиасы в `/etc/aliases`.
2. Настройте виртуальный домен.
3. Настройте виртуальные почтовые ящики.
4. Примените изменения.
5. Проверьте маршрутизацию письма.

**Решение и пояснения:**
```bash
# /etc/aliases: admin: user1
sudo newaliases
# main.cf:
# virtual_mailbox_domains = virtual.lab
# virtual_mailbox_maps = hash:/etc/postfix/vmailbox
# virtual_alias_maps = hash:/etc/postfix/virtual
sudo postmap /etc/postfix/vmailbox
sudo systemctl reload postfix
postmap -q "user@virtual.lab" hash:/etc/postfix/vmailbox
```
**Пояснения:**
Алиасы перенаправляют почту (`/etc/aliases`). Виртуальные домены позволяют обслуживать несколько доменов и ящиков. `postmap` строит хэш-файлы из текстовых карт. `reload` применяет изменения без остановки.

---

**Практическая работа №3: Квоты и мониторинг очереди**

**Задание:**
1. Посмотрите очередь писем.
2. Поставьте письмо в очередь и удалите его.
3. Настройте квоты для ящиков.
4. Проанализируйте журнал.
5. Объясните причины задержки писем.

**Решение и пояснения:**
```bash
mailq                                    # 1. Очередь
postsuper -d ALL                         # 2. Очистить очередь
# main.cf: message_size_limit = 10240000
# Для квот обычно используется Dovecot
sudo tail -f /var/log/mail.log           # 4. Журнал
```
**Пояснения:**
`mailq`/`postqueue -p` показывает очередь, `postsuper -d` удаляет письма. `message_size_limit` ограничивает размер. Квоты ящиков реализуют на стороне MDA (Dovecot). Логи — в `/var/log/mail.log` и journal.

---

**Практическая работа №4: TLS для Postfix**

**Задание:**
1. Сгенерируйте сертификат для Postfix.
2. Настройте использование TLS.
3. Включите шифрование для входящих и исходящих.
4. Перезапустите Postfix.
5. Проверьте TLS-соединение.

**Решение и пояснения:**
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/mail.key -out /etc/ssl/certs/mail.crt \
  -subj "/CN=mail.lab"
sudo postconf -e "smtpd_tls_cert_file=/etc/ssl/certs/mail.crt"
sudo postconf -e "smtpd_tls_key_file=/etc/ssl/private/mail.key"
sudo postconf -e "smtpd_use_tls=yes"
sudo systemctl restart postfix
openssl s_client -starttls smtp -connect localhost:25 </dev/null
```
**Пояснения:**
TLS шифрует SMTP-сессию. `smtpd_*` — для входящих (сервер), `smtp_*` — для исходящих (клиент). `starttls` включает шифрование в существующем соединении. Проверка — через `openssl s_client -starttls smtp`.
