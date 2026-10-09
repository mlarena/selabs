[Оглавление](LPIC-2home.md)

**Практическая работа №1: Установка и базовый запуск Squid**

**Задание:**
1. Установите Squid.
2. Проверьте конфигурацию.
3. Запустите службу.
4. Настройте клиент на использование прокси.
5. Проверьте прохождение запроса через прокси.

**Решение и пояснения:**
```bash
sudo apt install -y squid
sudo squid -k parse                        # 2. Проверка конфигурации
sudo systemctl enable --now squid          # 3. Запуск
# Клиент: export http_proxy=http://proxy.lab:3128
curl -x http://localhost:3128 http://example.com   # 5. Через прокси
```
**Пояснения:**
Squid — кэширующий HTTP-прокси. Основной конфигурационный файл — `/etc/squid/squid.conf`, порт по умолчанию 3128. `squid -k parse` проверяет конфигурацию без запуска.

---

**Практическая работа №2: ACL и правила доступа**

**Задание:**
1. Создайте ACL для локальной подсети.
2. Разрешите доступ только этой подсети.
3. Запретите доступ к нежелательному домену.
4. Примените правила и перезагрузите.
5. Проверьте ограничения.

**Решение и пояснения:**
```bash
# /etc/squid/squid.conf:
# acl localnet src 192.168.1.0/24
# acl blocked dstdomain .example.com
# http_access allow localnet
# http_access deny blocked
# http_access deny all
sudo squid -k reconfigure
curl -x http://localhost:3128 http://example.com   # Должен быть запрещён
```
**Пояснения:**
ACL описывают условия (источник, назначение, время, порт). `http_access` применяет правила по порядку (первое совпадение). `deny all` в конце закрывает всё, что не разрешено явно.

---

**Практическая работа №3: Аутентификация клиентов**

**Задание:**
1. Создайте файл паролей для basic-аутентификации.
2. Настройте программу аутентификации в Squid.
3. Требуйте аутентификацию для доступа.
4. Перезапустите Squid.
5. Проверьте доступ с логином/паролем.

**Решение и пояснения:**
```bash
sudo htpasswd -c /etc/squid/passwd proxyuser
# /etc/squid/squid.conf:
# auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
# acl auth_users proxy_auth REQUIRED
# http_access allow auth_users
sudo systemctl restart squid
curl -x http://proxyuser:pass@localhost:3128 http://example.com
```
**Пояснения:**
Squid поддерживает basic-аутентификацию через внешнюю программу (`basic_ncsa_auth`). ACL с `proxy_auth REQUIRED` требует учётные данные. Это позволяет контролировать доступ и вести персональный учёт.

---

**Практическая работа №4: Кэширование и логи**

**Задание:**
1. Настройте размер кэша и каталог.
2. Инициализируйте кэш.
3. Пронаблюдайте попадания в кэш.
4. Проанализируйте журнал доступа.
5. Объясните механизм кэширования.

**Решение и пояснения:**
```bash
# cache_dir ufs /var/spool/squid 100 16 256
# cache_mem 64 MB
sudo squid -z                              # 2. Инициализация кэша
sudo systemctl restart squid
sudo tail -f /var/log/squid/access.log     # 4. Журнал (HIT/MISS)
```
**Пояснения:**
`cache_dir` задаёт дисковый кэш, `cache_mem` — память. `squid -z` создаёт структуру каталогов. В `access.log` код `TCP_HIT` — ответ из кэша, `TCP_MISS` — с сервера. Кэш снижает нагрузку на канал.
