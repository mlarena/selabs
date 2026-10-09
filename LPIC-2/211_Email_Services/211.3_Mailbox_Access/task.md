[Оглавление](LPIC-2/home.md)

**Практическая работа №1: Настройка Dovecot для IMAP/POP3**

**Задание:**
1. Установите Dovecot с IMAP и POP3.
2. Настройте тип почтового ящика (Maildir).
3. Включите протоколы IMAP и POP3.
4. Перезапустите службу.
5. Проверьте доступ через `openssl`/клиент.

**Решение и пояснения:**
```bash
sudo apt install -y dovecot-core dovecot-imapd dovecot-pop3d
# /etc/dovecot/conf.d/10-mail.conf: mail_location = maildir:~/Maildir
# /etc/dovecot/dovecot.conf: protocols = imap pop3
sudo systemctl restart dovecot
ss -tlnp | grep -E "143|110"
```
**Пояснения:**
Dovecot — MDA/IMAP/POP3-сервер. Maildir хранит письма отдельными файлами (надёжнее mbox). IMAP хранит почту на сервере и синхронизирует; POP3 обычно скачивает и удаляет. Порты: IMAP 143/993, POP3 110/995.

---

**Практическая работа №2: Аутентификация и TLS**

**Задание:**
1. Настройте метод аутентификации (PAM/системные пользователи).
2. Сгенерируйте сертификат.
3. Включите SSL/TLS.
4. Настройте защищённые порты.
5. Проверьте шифрованное соединение.

**Решение и пояснения:**
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/dovecot.key -out /etc/ssl/certs/dovecot.crt \
  -subj "/CN=mail.lab"
# 10-ssl.conf: ssl = yes; ssl_cert = <...crt; ssl_key = <...key
sudo systemctl restart dovecot
openssl s_client -connect localhost:993 </dev/null
```
**Пояснения:**
Dovecot может аутентифицировать через PAM (системные пользователи), LDAP или SQL. `ssl = yes` включает TLS. Порты 993 (IMAPS) и 995 (POP3S) используют шифрование. Сертификат настраивают в `10-ssl.conf`.

---

**Практическая работа №3: Управление ящиками через doveadm**

**Задание:**
1. Выведите список почтовых ящиков.
2. Посмотрите статус ящика.
3. Переиндексируйте ящик.
4. Очистите удалённые письма.
5. Объясните назначение doveadm.

**Решение и пояснения:**
```bash
sudo doveadm mailbox list -u user1           # 1. Список ящиков
sudo doveadm mailbox status -u user1 all INBOX   # 2. Статус
sudo doveadm force-resync -u user1 INBOX     # 3. Переиндексация
sudo doveadm expunge -u user1 mailbox Trash all  # 4. Очистка
```
**Пояснения:**
`doveadm` — административная утилита Dovecot. Она управляет ящиками, переиндексирует, очищает, выполняет поиск и миграцию. Полезна при повреждении индексов или массовых операциях.

---

**Практическая работа №4: Квоты и диагностика**

**Задание:**
1. Включите поддержку квот в Dovecot.
2. Настройте лимит на ящик.
3. Проверьте использование квоты.
4. Посмотрите журнал Dovecot.
5. Объясните типовые проблемы.

**Решение и пояснения:**
```bash
# 10-mail.conf: mail_plugins = $mail_plugins quota
# 90-quota.conf: plugin { quota_rule = *:storage=1G }
sudo systemctl restart dovecot
sudo doveadm quota get -u user1              # 3. Использование
sudo journalctl -u dovecot | tail            # 4. Журнал
```
**Пояснения:**
Квоты ограничивают размер ящика. Включаются плагином `quota` и правилами `quota_rule`. `doveadm quota get` показывает использование. Типовые проблемы: права на Maildir, неверный `mail_location`, конфликты UID/GID.
