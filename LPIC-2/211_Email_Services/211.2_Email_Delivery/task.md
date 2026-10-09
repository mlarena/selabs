[Оглавление](LPIC-2home.md)

**Практическая работа №1: Установка и настройка Dovecot с Sieve**

**Задание:**
1. Установите Dovecot и LMTP.
2. Включите Sieve-интерпретатор.
3. Настройте каталог скриптов Sieve.
4. Перезапустите Dovecot.
5. Проверьте, что Sieve активен.

**Решение и пояснения:**
```bash
sudo apt install -y dovecot-core dovecot-imapd dovecot-lmtpd dovecot-sieve
# /etc/dovecot/conf.d/20-lmtp.conf: mail_plugins = $mail_plugins sieve
# /etc/dovecot/conf.d/90-sieve.conf: sieve = ~/.dovecot.sieve
sudo systemctl restart dovecot
doveconf -n | grep -i sieve
```
**Пояснения:**
Sieve — язык фильтрации почты на стороне сервера. Dovecot выполняет Sieve-скрипты при доставке (LMTP). Скрипты обычно лежат в `~/.dovecot.sieve`. Это позволяет сортировать и фильтровать почту без клиента.

---

**Практическая работа №2: Написание Sieve-скрипта**

**Задание:**
1. Создайте Sieve-скрипт для фильтрации по отправителю.
2. Добавьте правило по теме письма.
3. Настройте перемещение в папку (`fileinto`).
4. Настройте отбрасывание спама (`discard`).
5. Проверьте синтаксис скрипта.

**Решение и пояснения:**
```sieve
require ["fileinto", "reject", "discard"];
if address :is "from" "boss@example.com" {
    fileinto "INBOX.Boss";
}
if header :contains "subject" "[SPAM]" {
    discard;
}
if size :over 10M {
    fileinto "INBOX.Large";
}
```
**Пояснения:**
Sieve использует условия (`if`) и действия: `keep`, `fileinto` (в папку), `redirect` (переслать), `reject` (отклонить), `discard` (удалить), `stop`. `require` объявляет используемые расширения. Проверка — `sievec`/`sieve-test`.

---

**Практическая работа №3: Проверка и отладка Sieve**

**Задание:**
1. Скомпилируйте Sieve-скрипт.
2. Проверьте его тестовым сообщением.
3. Посмотрите ошибки компиляции.
4. Проверьте права на файл скрипта.
5. Протестируйте доставку.

**Решение и пояснения:**
```bash
sievec ~/.dovecot.sieve                   # 1. Компиляция
sieve-test ~/.dovecot.sieve test.eml      # 2. Тест
ls -l ~/.dovecot.sieve                    # 4. Права
# Отправка тестового письма:
echo "test" | mail -s "[SPAM] test" user1
```
**Пояснения:**
`sievec` компилирует скрипт в бинарный формат, `sieve-test` проверяет применение правил к сообщению без реальной доставки. Ошибки синтаксиса видны при компиляции. Права на скрипт должны принадлежать владельцу ящика.

---

**Практическая работа №4: Автоответы и уведомления**

**Задание:**
1. Настройте автоответ (vacation).
2. Настройте пересылку на другой адрес.
3. Ограничьте автоответ по времени/отправителю.
4. Проверьте работу.
5. Объясните риск «писем-петель».

**Решение и пояснения:**
```sieve
require ["vacation", "redirect"];
vacation :days 7 :subject "Out of office"
         "Я в отпуске и отвечу позже.";
if address :is "from" "colleague@example.com" {
    redirect "backup@example.com";
}
```
**Пояснения:**
Расширение `vacation` реализует автоответы. `redirect` пересылает письмо. Чтобы избежать петель и спама, автоответы ограничивают по времени (`:days`), не отвечают на рассылки и `:addresses`. `redirect` сохраняет оригинал в зависимости от `keep`.
