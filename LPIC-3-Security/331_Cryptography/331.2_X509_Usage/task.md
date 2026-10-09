[Оглавление](LPIC-3-Security/home.md)

**Практическая работа №1: Шифрование данных открытым ключом**

**Задание:**
1. Сгенерируйте пару ключей.
2. Зашифруйте файл открытым ключом.
3. Расшифруйте файл закрытым ключом.
4. Сравните с симметричным шифрованием.
5. Объясните гибридную схему.

**Решение и пояснения:**
```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out key.pem
openssl pkey -in key.pem -pubout -out pub.pem
openssl pkeyutl -encrypt -pubin -inkey pub.pem -in secret.bin -out secret.enc   # 2
openssl pkeyutl -decrypt -inkey key.pem -in secret.enc -out secret.out          # 3
```
**Пояснения:**
Асимметричное шифрование (RSA) медленное и ограничено по размеру. На практике применяют гибридную схему: сессионный ключ шифруется открытым ключом, а данные — симметрично (AES). Именно так работает TLS.

---

**Практическая работа №2: Подпись и проверка подлинности**

**Задание:**
1. Создайте цифровую подпись файла.
2. Проверьте подпись.
3. Измените файл и повторите проверку.
4. Создайте подпись, встроенную в документ (CMS).
5. Объясните назначение подписи.

**Решение и пояснения:**
```bash
openssl dgst -sha256 -sign key.pem -out file.sig file.txt       # 1. Подпись
openssl dgst -sha256 -verify pub.pem -signature file.sig file.txt   # 2. Проверка
echo "tampered" >> file.txt
openssl dgst -sha256 -verify pub.pem -signature file.sig file.txt   # 3. Должно отказать
openssl cms -sign -in file.txt -signer cert.crt -inkey key.pem -out file.p7s -outform DER   # 4
```
**Пояснения:**
Цифровая подпись подтверждает целостность и авторство: подписывается хэш документа. Любое изменение файла делает подпись недействительной. CMS/PKCS#7 объединяет данные и подпись (используется в S/MIME).

---

**Практическая работа №3: Клиентские сертификаты и mutual TLS**

**Задание:**
1. Выпустите клиентский сертификат.
2. Настройте сервер на требование клиентских сертификатов.
3. Подключитесь с клиентским сертификатом.
4. Проверьте отказ без сертификата.
5. Объясните применение.

**Решение и пояснения:**
```bash
openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "/CN=client1" -out client.csr
openssl x509 -req -in client.csr -CA int.crt -CAkey int.key \
  -CAcreateserial -days 365 -extfile <(echo "extendedKeyUsage=clientAuth") -out client.crt
# Apache: SSLVerifyClient require ; SSLCACertificateFile int.crt
curl --cert client.crt --key client.key --cacert root.crt https://web.lab.local
```
**Пояснения:**
Клиентский сертификат с `clientAuth` аутентифицирует клиента. Mutual TLS применяется для API, сервис-сервис, VPN. Сервер проверяет клиентский сертификат по доверенному CA, что исключает пароли.

---

**Практическая работа №4: GPG: шифрование, подпись, управление ключами**

**Задание:**
1. Сгенерируйте ключ GPG.
2. Зашифруйте файл для получателя.
3. Подпишите файл.
4. Проверьте подпись.
5. Экспортируйте/импортируйте ключи.

**Решение и пояснения:**
```bash
gpg --full-generate-key
gpg --encrypt --recipient user@lab.local file.txt        # 2. Шифрование
gpg --armor --detach-sign file.txt                       # 3. Подпись
gpg --verify file.txt.asc file.txt                       # 4. Проверка
gpg --armor --export user@lab.local > pub.asc            # 5. Экспорт
gpg --import pub.asc
```
**Пояснения:**
GPG (OpenPGP) обеспечивает шифрование, подпись и управление ключами. Ключ содержит открытую и закрытую части. Экспорт публичного ключа позволяет другим шифровать и проверять подписи. Применяется для почты, пакетов, бэкапов.

---

**Практическая работа №5: Диагностика TLS-соединений**

**Задание:**
1. Проверьте цепочку сервера.
2. Посмотрите согласованный протокол и шифр.
3. Проверьте конкретную версию TLS.
4. Проверьте проверку имени хоста.
5. Объясните типовые ошибки.

**Решение и пояснения:**
```bash
openssl s_client -connect web.lab.local:443 -showcerts </dev/null
openssl s_client -connect web.lab.local:443 </dev/null 2>/dev/null | grep -E "Protocol|Cipher"
openssl s_client -connect web.lab.local:443 -tls1_2 </dev/null
openssl s_client -connect web.lab.local:443 -verify_hostname web.lab.local -verify_return_error </dev/null
```
**Пояснения:**
`s_client` диагностирует TLS. Вывод показывает протокол и набор шифров. `-verify_hostname` проверяет соответствие имени SAN. Типовые ошибки: истёкший сертификат, неполная цепочка, недоверенный CA, несовпадение имени.
