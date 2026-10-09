[Оглавление](LPIC-3-Securityhome.md)

**Практическая работа №1: Структура сертификата X.509**

**Задание:**
1. Получите сертификат сервера.
2. Посмотрите его поля (issuer, subject, validity).
3. Посмотрите расширения (SAN, keyUsage).
4. Проверьте отпечаток сертификата.
5. Объясните назначение полей.

**Решение и пояснения:**
```bash
openssl s_client -connect example.com:443 -showcerts </dev/null 2>/dev/null | openssl x509 -noout -text
openssl x509 -in server.crt -noout -subject -issuer -dates
openssl x509 -in server.crt -noout -ext subjectAltName
openssl x509 -in server.crt -noout -fingerprint -sha256
```
**Пояснения:**
X.509-сертификат связывает открытый ключ с субъектом (subject), подписан издателем (issuer). Поля: срок действия (validity), серийный номер, расширения. SAN перечисляет допустимые имена, keyUsage — назначение ключа. Отпечаток — хэш сертификата.

---

**Практическая работа №2: Создание корневого CA и промежуточного CA**

**Задание:**
1. Создайте корневой закрытый ключ.
2. Создайте самоподписанный корневой сертификат.
3. Создайте промежуточный CA.
4. Подпишите промежуточный сертификат корневым.
5. Проверьте цепочку.

**Решение и пояснения:**
```bash
openssl genrsa -out root.key 4096
openssl req -x509 -new -nodes -key root.key -days 3650 \
  -subj "/CN=Lab Root CA" -out root.crt                       # 2. Корневой CA
openssl genrsa -out int.key 4096
openssl req -new -key int.key -subj "/CN=Lab Intermediate CA" -out int.csr
openssl x509 -req -in int.csr -CA root.crt -CAkey root.key \
  -CAcreateserial -days 1825 -extfile <(echo "basicConstraints=critical,CA:TRUE") -out int.crt
openssl verify -CAfile root.crt int.crt                       # 5. Проверка
```
**Пояснения:**
Иерархия PKI: корневой CA подписывает промежуточный, промежуточный — конечные сертификаты. Корневой ключ хранят офлайн. `basicConstraints CA:TRUE` помечает сертификат как CA. `verify` проверяет цепочку.

---

**Практическая работа №3: Выпуск серверного сертификата**

**Задание:**
1. Создайте ключ и CSR сервера.
2. Подготовьте extension-файл (SAN).
3. Подпишите CSR промежуточным CA.
4. Проверьте сертификат.
5. Соберите цепочку для сервера.

**Решение и пояснения:**
```bash
openssl genrsa -out web.key 2048
openssl req -new -key web.key -subj "/CN=web.lab.local" -out web.csr
cat > web.ext <<'EOF'
subjectAltName=DNS:web.lab.local,DNS:www.lab.local
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
EOF
openssl x509 -req -in web.csr -CA int.crt -CAkey int.key \
  -CAcreateserial -days 365 -extfile web.ext -out web.crt
cat web.crt int.crt > web-chain.crt    # 5. Полная цепочка
```
**Пояснения:**
CSR содержит открытый ключ и subject. SAN задаёт имена, которым доверяет сертификат. `extendedKeyUsage=serverAuth` указывает назначение. Цепочка (сертификат + промежуточные CA) нужна серверу для предъявления.

---

**Практическая работа №4: Проверка цепочки, CRL и OCSP**

**Задание:**
1. Проверьте цепочку сертификата.
2. Отзовите сертификат.
3. Сгенерируйте CRL.
4. Проверьте CRL.
5. Проверьте статус через OCSP (концептуально).

**Решение и пояснения:**
```bash
openssl verify -CAfile root.crt -untrusted int.crt web.crt
openssl ca -config openssl.cnf -revoke web.crt        # 2. Отзыв
openssl ca -config openssl.cnf -gencrl -out int.crl   # 3. CRL
openssl crl -in int.crl -noout -text | head
openssl ocsp -issuer int.crt -cert web.crt -url http://ocsp.lab.local   # 5. OCSP
```
**Пояснения:**
`verify -untrusted` проверяет цепочку с промежуточными сертификатами. Отзыв (`revoke`) и CRL информируют о недействительных сертификатах. OCSP — онлайн-проверка статуса. Проверяющая сторона обязана учитывать отзыв, иначе компрометированный сертификат останется доверенным.

---

**Практическая работа №5: Хранилища доверия и управление PKI**

**Задание:**
1. Добавьте корневой CA в доверенные системы.
2. Проверьте системное хранилище.
3. Проверьте, что приложение доверяет сертификату.
4. Удалите CA из доверия.
5. Объясните риски доверия CA.

**Решение и пояснения:**
```bash
sudo cp root.crt /usr/local/share/ca-certificates/lab-root-ca.crt
sudo update-ca-certificates                          # 1. Добавление
curl --cacert root.crt https://web.lab.local
ls /etc/ssl/certs | grep -i lab
sudo rm /usr/local/share/ca-certificates/lab-root-ca.crt && sudo update-ca-certificates --fresh
```
**Пояснения:**
Системное хранилище (`/etc/ssl/certs`, `ca-certificates.crt`) используют приложения для проверки. Доверенный CA может подписывать сертификаты для любых имён, поэтому добавлять только проверенные CA. Управление доверием — ключевой аспект PKI.
