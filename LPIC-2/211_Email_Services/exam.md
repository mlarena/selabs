[Оглавление](LPIC-2home.md)

# Экзаменационные боевые задачи — Тема 211: E-Mail Services

Задачи приближены к реальным заданиям экзамена **202-450**.

## Задача 1. Настройка Postfix

**Условие:** Настройте Postfix для отправки и приёма почты для локального домена.

**Ожидаемый результат:** Почта доставляется локальным пользователям.

**Решение и пояснения:**
```bash
sudo apt install -y postfix mailutils
sudo postconf -e "myhostname=mail.lab"
sudo postconf -e "mydomain=lab"
sudo postconf -e "myorigin=\$mydomain"
sudo postfix check && sudo systemctl restart postfix
echo "test" | mail -s "Тема" user1
```
Postfix — MTA. `/etc/postfix/main.cf` — основные параметры, `master.cf` — сервисы. `postconf -e` задаёт параметр, `postfix check` проверяет конфигурацию. `myhostname`/`mydomain` определяют идентичность.

## Задача 2. Виртуальные домены и алиасы

**Условие:** Настройте виртуальный домен и перенаправление почты (алиас).

**Ожидаемый результат:** Почта виртуального домена маршрутизируется.

**Решение и пояснения:**
```bash
# /etc/aliases: admin: user1 ; затем sudo newaliases
# main.cf:
# virtual_mailbox_domains = virtual.lab
# virtual_mailbox_maps = hash:/etc/postfix/vmailbox
# virtual_alias_maps = hash:/etc/postfix/virtual
sudo postmap /etc/postfix/vmailbox /etc/postfix/virtual
sudo systemctl reload postfix
postmap -q "user@virtual.lab" hash:/etc/postfix/vmailbox
```
Виртуальные домены позволяют обслуживать несколько доменов. `postmap` строит хэш-файлы из текстовых карт. `reload` применяет изменения без остановки.

## Задача 3. Управление очередью

**Условие:** Проверьте очередь писем, удалите застрявшие письма и найдите причину задержки.

**Ожидаемый результат:** Очередь очищена, причина найдена.

**Решение и пояснения:**
```bash
mailq
postqueue -p
postsuper -d ALL              # Удалить все
postsuper -d <queue_id>       # Удалить одно
sudo tail -f /var/log/mail.log
sudo postqueue -f             # Форсировать отправку
```
`mailq`/`postqueue -p` показывают очередь, `postsuper -d` удаляет. Логи (`/var/log/mail.log`) объясняют задержки (DNS, релей, отказ получателя). `postqueue -f` повторяет попытку.

## Задача 4. Dovecot: IMAP/POP3 и Sieve

**Условие:** Настройте Dovecot для IMAP и фильтрацию почты через Sieve.

**Ожидаемый результат:** Почта доступна по IMAP, фильтры работают.

**Решение и пояснения:**
```bash
sudo apt install -y dovecot-core dovecot-imapd dovecot-lmtpd dovecot-sieve
# 10-mail.conf: mail_location = maildir:~/Maildir
# dovecot.conf: protocols = imap lmtp
# Sieve: ~/.dovecot.sieve
sudo systemctl restart dovecot
ss -tlnp | grep 143
doveadm mailbox list -u user1
```
Dovecot — MDA/IMAP/POP3. Sieve фильтрует почту на сервере (сортировка, автоответы). Скрипты в `~/.dovecot.sieve`, проверка — `sievec`/`sieve-test`.

## Задача 5. TLS для почты

**Условие:** Настройте шифрование SMTP и IMAP с сертификатом.

**Ожидаемый результат:** Почта передаётся по TLS.

**Решение и пояснения:**
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/mail.key -out /etc/ssl/certs/mail.crt -subj "/CN=mail.lab"
sudo postconf -e "smtpd_tls_cert_file=/etc/ssl/certs/mail.crt"
sudo postconf -e "smtpd_tls_key_file=/etc/ssl/private/mail.key"
sudo postconf -e "smtpd_use_tls=yes"
sudo systemctl restart postfix
openssl s_client -starttls smtp -connect localhost:25 </dev/null
```
TLS шифрует SMTP-сессию (`smtpd_*` — сервер, `smtp_*` — клиент). STARTTLS включает шифрование в соединении. IMAPS/POP3S используют порты 993/995.

## Задача 6. Диагностика доставки

**Условие:** Письмо не доставляется. Найдите причину по логам.

**Ожидаемый результат:** Причина найдена.

**Решение и пояснения:**
```bash
sudo grep <message_id> /var/log/mail.log
sudo journalctl -u postfix | tail
dig -x <client_ip>            # PTR-проверка
sudo postconf -n | grep -i relay
sudo ss -tlnp | grep -E "25|587"
```
Причины: отклонение из-за PTR/SPF/DKIM/DMARC, неверная маршрутизация, firewall, квоты. Логи содержат статус доставки. `postconf -n` показывает не-дефолтные параметры.
