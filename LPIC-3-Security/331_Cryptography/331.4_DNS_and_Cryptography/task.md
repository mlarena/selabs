[Оглавление](?file=LPIC-3-Security%2Fhome.md)

**Практическая работа №1: Основы DNSSEC**

**Задание:**
1. Проверьте, поддерживает ли резолвер DNSSEC.
2. Запросите записи DNSKEY домена.
3. Запросите DS-запись.
4. Проверьте подпись RRSIG.
5. Объясните цепочку доверия.

**Решение и пояснения:**
```bash
dig +dnssec example.com A @8.8.8.8
dig DNSKEY example.com @8.8.8.8 +short
dig DS example.com @8.8.8.8 +short
dig RRSIG example.com @8.8.8.8
```
**Пояснения:**
DNSSEC защищает DNS от подмены цифровыми подписями. DNSKEY — открытые ключи зоны, DS — ссылка на ключ в родительской зоне, RRSIG — подпись записей. Цепочка доверия идёт от корня до зоны.

---

**Практическая работа №2: Подпись зоны**

**Задание:**
1. Сгенерируйте ZSK и KSK.
2. Подпишите зону.
3. Проверьте подписанные файлы.
4. Загрузите подписанную зону.
5. Проверьте подписи в ответе.

**Решение и пояснения:**
```bash
dnssec-keygen -a ECDSAP256SHA256 -n ZONE example.lab      # ZSK
dnssec-keygen -a ECDSAP256SHA256 -f KSK -n ZONE example.lab  # KSK
dnssec-signzone -o example.lab -k Kexample.lab.+013+*.key db.example.lab
ls db.example.lab.signed
# named.conf: file "db.example.lab.signed";
dig +dnssec example.lab @localhost
```
**Пояснения:**
ZSK (Zone Signing Key) подписывает записи, KSK (Key Signing Key) подписывает DNSKEY. `dnssec-signzone` создаёт подписанную зону с RRSIG. Резолверы проверяют подписи и цепочку DS.

---

**Практическая работа №3: TSIG для аутентификации DNS**

**Задание:**
1. Сгенерируйте TSIG-ключ.
2. Подключите ключ в конфигурацию.
3. Разрешите передачу зоны только с ключом.
4. Выполните AXFR с ключом.
5. Проверьте отказ без ключа.

**Решение и пояснения:**
```bash
sudo tsig-keygen -a hmac-sha256 transferkey > /etc/bind/transfer.key
# named.conf: include "/etc/bind/transfer.key";
#   allow-transfer { key transferkey; };
sudo systemctl restart bind9
dig AXFR example.lab @localhost -y hmac-sha256:transferkey:<secret>   # 4
dig AXFR example.lab @localhost                                        # 5. Отказ
```
**Пояснения:**
TSIG аутентифицирует DNS-сообщения общим секретом (HMAC). Используется для передачи зон (AXFR) и динамических обновлений. Без ключа операция запрещена. Это защищает от несанкционированного копирования зон.

---

**Практическая работа №4: Защищённый транспорт DNS**

**Задание:**
1. Опишите DNS-over-TLS (DoT).
2. Опишите DNS-over-HTTPS (DoH).
3. Проверьте DoT-соединение.
4. Опишите DANE/TLSA.
5. Объясните, от чего защищают DoT/DoH.

**Решение и пояснения:**
```bash
# DoT (порт 853):
openssl s_client -connect 1.1.1.1:853 -servername cloudflare-dns.com </dev/null
# DANE: запрос TLSA-записи
dig TLSA _443._tcp.example.com @8.8.8.8
# DoH:
curl -H "accept: application/dns-json" "https://cloudflare-dns.com/dns-query?name=example.com&type=A"
```
**Пояснения:**
DoT/DoH шифруют DNS-запросы, предотвращая прослушивание и подмену. DANE использует DNSSEC для публикации сертификатов (TLSA), привязывая сертификат к домену. Эти технологии дополняют DNSSEC.

---

**Практическая работа №5: Диагностика DNSSEC**

**Задание:**
1. Проверьте валидацию через `delv`.
2. Проверьте зону на `dnssec-verify`.
3. Найдите проблемы цепочки.
4. Проверьте сроки действия подписей.
5. Объясните типовые ошибки DNSSEC.

**Решение и пояснения:**
```bash
delv @localhost example.lab A +rtrace
dnssec-verify -o example.lab db.example.lab.signed
dig +dnssec example.lab @localhost | grep -i rrsig
dig DNSKEY example.lab @localhost +short
```
**Пояснения:**
`delv` проверяет валидацию DNSSEC, `dnssec-verify` — подпись зоны. Типовые ошибки: истёкшие RRSIG, отсутствие DS у родителя, неверные KSK/ZSK, неподписанные зоны. Сроки подписей требуют регулярного обновления (rollover).
