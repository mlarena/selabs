[Оглавление](?file=LPIC-2%2Fhome.md)

**Практическая работа №1: Включение mod_ssl и самоподписанный сертификат**

**Задание:**
1. Включите модуль SSL.
2. Сгенерируйте самоподписанный сертификат.
3. Настройте виртуальный хост HTTPS.
4. Проверьте работу через curl.
5. Объясните назначение сертификата.

**Решение и пояснения:**
```bash
sudo a2enmod ssl
sudo mkdir -p /etc/ssl/lab
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/lab/site.key -out /etc/ssl/lab/site.crt \
  -subj "/CN=site1.lab"
# <VirtualHost *:443> SSLEngine on; SSLCertificateKeyFile ...; SSLCertificateFile ...
sudo a2ensite default-ssl && sudo systemctl reload apache2
curl -k https://localhost
```
**Пояснения:**
`mod_ssl` обеспечивает HTTPS. Самоподписанный сертификат годится для тестов, но браузеры ему не доверяют. В продакшене используют сертификат от CA. `-k` в curl игнорирует проверку сертификата.

---

**Практическая работа №2: CSR и подпись через собственный CA**

**Задание:**
1. Создайте закрытый ключ сервера.
2. Создайте CSR (запрос на сертификат).
3. Создайте собственный CA.
4. Подпишите CSR своим CA.
5. Установите подписанный сертификат.

**Решение и пояснения:**
```bash
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=site1.lab"
openssl req -x509 -newkey rsa:2048 -nodes -keyout ca.key -out ca.crt -days 3650 -subj "/CN=Lab CA"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365
# Указать server.crt и server.key в конфигурации Apache
```
**Пояснения:**
CSR содержит открытый ключ и данные организации, подписывается закрытым ключом. CA подписывает CSR, выпуская сертификат. Клиент доверяет серверу, если доверяет CA (импорт `ca.crt`).

---

**Практическая работа №3: Строгие протоколы и шифры**

**Задание:**
1. Отключите устаревшие протоколы (SSLv3, TLS 1.0/1.1).
2. Задайте современный набор шифров.
3. Отключите информацию о версии сервера.
4. Проверьте поддерживаемые протоколы.
5. Объясните риск устаревших шифров.

**Решение и пояснения:**
```bash
# В конфигурации SSL:
# SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
# SSLCipherSuite HIGH:!aNULL:!MD5:!3DES
# ServerTokens Prod
# ServerSignature Off
sudo systemctl reload apache2
openssl s_client -connect localhost:443 -tls1_1 </dev/null   # Должно отказать
nmap --script ssl-enum-ciphers -p443 localhost
```
**Пояснения:**
Устаревшие протоколы и шифры (SSLv3, RC4, 3DES) уязвимы. `SSLProtocol`/`SSLCipherSuite` ограничивают безопасные варианты. `ServerTokens Prod` скрывает версию и ОС сервера.

---

**Практическая работа №4: SNI и HSTS**

**Задание:**
1. Настройте два HTTPS-сайта на одном IP (SNI).
2. Включите HSTS-заголовок.
3. Настройте перенаправление HTTP→HTTPS.
4. Проверьте SNI через openssl.
5. Объясните назначение SNI и HSTS.

**Решение и пояснения:**
```bash
# Два <VirtualHost *:443> с разными ServerName и сертификатами
# HSTS: Header always set Strict-Transport-Security "max-age=31536000"
# Redirect: Redirect permanent / https://site1.lab/
openssl s_client -connect localhost:443 -servername site1.lab </dev/null
```
**Пояснения:**
SNI позволяет серверу выбрать сертификат по имени из TLS-рукопожатия (несколько сайтов на одном IP). HSTS заставляет браузер использовать только HTTPS. Перенаправление переводит старые HTTP-ссылки на HTTPS.
