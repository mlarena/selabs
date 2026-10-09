[Оглавление](LPIC-2home.md)

**Практическая работа №1: Ограничение доступа к BIND**

**Задание:**
1. Настройте прослушивание только нужных интерфейсов.
2. Разрешите запросы только своей подсети.
3. Запретите рекурсию для внешних.
4. Проверьте конфигурацию.
5. Объясните риск открытого рекурсивного DNS.

**Решение и пояснения:**
```bash
# /etc/bind/named.conf.options:
# listen-on { 127.0.0.1; 192.168.1.10; };
# allow-query { localhost; 192.168.1.0/24; };
# allow-recursion { localhost; 192.168.1.0/24; };
sudo named-checkconf
sudo systemctl restart bind9
```
**Пояснения:**
Открытый рекурсивный DNS — мишень для amplification-атак. Ограничивают `listen-on`, `allow-query`, `allow-recursion`. Внутренние клиенты получают рекурсию, внешние — только авторитетные ответы.

---

**Практическая работа №2: Работа в chroot**

**Задание:**
1. Проверьте, работает ли BIND в chroot (пакет `bind9` в Debian).
2. Посмотрите каталог chroot.
3. Убедитесь, что процесс запущен от непривилегированного пользователя.
4. Проверьте права на каталоги.
5. Объясните преимущества chroot.

**Решение и пояснения:**
```bash
ps -o user,cmd -C named                 # 3. Пользователь bind
grep -E "directory|chroot" /etc/default/bind9 /etc/bind/named.conf.options
ls -ld /var/cache/bind /var/lib/bind    # 4. Права
```
**Пояснения:**
BIND запускается от пользователя `bind` и может работать в chroot (`/var/cache/bind`). Это ограничивает ущерб при компрометации: процесс видит только свою «тюрьму». В Debian chroot настраивается опцией `-t` в `/etc/default/bind9`.

---

**Практическая работа №3: TSIG — защищённый обмен**

**Задание:**
1. Сгенерируйте TSIG-ключ.
2. Настройте ключ в конфигурации.
3. Разрешите передачу зоны только с ключом.
4. Проверьте передачу зоны с ключом.
5. Объясните назначение TSIG.

**Решение и пояснения:**
```bash
sudo tsig-keygen -a hmac-sha256 transferkey > /etc/bind/transfer.key
# Включить в named.conf:
# include "/etc/bind/transfer.key";
# zone "example.lab" { ... allow-transfer { key transferkey; }; };
sudo systemctl restart bind9
dig AXFR example.lab @localhost -y hmac-sha256:transferkey:<secret>   # 4
```
**Пояснения:**
TSIG использует общий секрет для аутентификации DNS-сообщений (например, при передаче зон или динамических обновлениях). Без ключа AXFR запрещён. Ключ генерируют `tsig-keygen`/`dnssec-keygen`.

---

**Практическая работа №4: DNSSEC (awareness)**

**Задание:**
1. Проверьте, поддерживает ли сервер DNSSEC.
2. Сгенерируйте пару ключей для зоны (ZSK).
3. Подпишите зону.
4. Проверьте подписи в ответе.
5. Объясните назначение DNSSEC.

**Решение и пояснения:**
```bash
dnssec-keygen -a ECDSAP256SHA256 -n ZONE example.lab   # 2. ZSK
dnssec-signzone -o example.lab -k <KSK> db.example.lab # 3. Подпись
# В named.conf.options: dnssec-validation auto;
dig +dnssec example.lab @localhost                     # 4. Проверка RRSIG
```
**Пояснения:**
DNSSEC защищает от подмены DNS-ответов цифровыми подписями (RRSIG, DNSKEY, DS). Зону подписывают ZSK (зона) и KSK (ключ подписи). Валидация на резолвере проверяет цепочку доверия от корня.
