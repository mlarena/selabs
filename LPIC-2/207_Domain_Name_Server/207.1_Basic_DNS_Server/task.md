[Оглавление](LPIC-2home.md)

**Практическая работа №1: Установка и базовая настройка BIND**

**Задание:**
1. Установите BIND 9.
2. Посмотрите структуру конфигурации.
3. Настройте кэширующий DNS-сервер.
4. Проверьте конфигурацию.
5. Запустите и проверьте службу.

**Решение и пояснения:**
```bash
sudo apt install -y bind9 bind9utils bind9-doc
ls /etc/bind/                              # 2. Конфигурация
# /etc/bind/named.conf.options: настроить recursion и forwarders
sudo named-checkconf                       # 4. Проверка конфигурации
sudo systemctl enable --now bind9          # 5. Запуск
```
**Пояснения:**
BIND — основной DNS-сервер. Основной файл — `/etc/bind/named.conf` (Debian), подключает `named.conf.options`, `named.conf.local`, `named.conf.default-zones`. Кэширующий сервер пересылает запросы (`forwarders`) и кэширует ответы.

---

**Практическая работа №2: Зоны и зональные файлы**

**Задание:**
1. Объявите прямую зону в конфигурации.
2. Создайте файл зоны с записями A и CNAME.
3. Проверьте зону на ошибки.
4. Перезагрузите зоны.
5. Проверьте разрешение имён.

**Решение и пояснения:**
```bash
# named.conf.local:
# zone "lab.local" { type master; file "/etc/bind/db.lab.local"; };
# db.lab.local:
# $TTL 3600
# @   IN SOA ns.lab.local. admin.lab.local. (1 3600 1800 604800 86400)
# @   IN NS  ns.lab.local.
# ns  IN A   192.168.1.10
# www IN A   192.168.1.20
sudo named-checkzone lab.local /etc/bind/db.lab.local   # 3. Проверка
sudo rndc reload                                        # 4. Перезагрузка
dig @localhost www.lab.local                            # 5. Проверка
```
**Пояснения:**
Зона описывает домен. SOA — начальная запись, NS — серверы имён, A — адреса, CNAME — псевдонимы. `named-checkzone` проверяет синтаксис, `rndc reload` перечитывает зоны.

---

**Практическая работа №3: Обратная зона**

**Задание:**
1. Объявите обратную зону для сети.
2. Создайте файл обратной зоны.
3. Добавьте записи PTR.
4. Проверьте зону.
5. Выполните обратный запрос.

**Решение и пояснения:**
```bash
# named.conf.local:
# zone "1.168.192.in-addr.arpa" { type master; file "/etc/bind/db.192.168.1"; };
# db.192.168.1:
# $TTL 3600
# @ IN SOA ns.lab.local. admin.lab.local. (1 3600 1800 604800 86400)
# @ IN NS ns.lab.local.
# 10 IN PTR ns.lab.local.
# 20 IN PTR www.lab.local.
sudo named-checkzone 1.168.192.in-addr.arpa /etc/bind/db.192.168.1
dig -x 192.168.1.20 @localhost             # 5. Обратный запрос
```
**Пояснения:**
Обратная зона (`in-addr.arpa`) сопоставляет IP → имя через записи PTR. Для сети 192.168.1.0/24 имя зоны — `1.168.192.in-addr.arpa`, а номер узла идёт первым в записи.

---

**Практическая работа №4: Управление BIND через rndc**

**Задание:**
1. Сгенерируйте ключ для rndc.
2. Настройте `rndc`.
3. Проверьте статус сервера.
4. Перезагрузите конфигурацию и зоны.
5. Посмотрите статистику.

**Решение и пояснения:**
```bash
sudo rndc-confgen -a                       # 1. Генерация ключа
sudo systemctl restart bind9
rndc status                                # 3. Статус сервера
sudo rndc reload                           # 4. Перезагрузка зон
sudo rndc reload-config                    # 4. Перезагрузка конфигурации
sudo rndc stats                            # 5. Статистика
```
**Пояснения:**
`rndc` — удалённое управление BIND по ключу (по умолчанию `/etc/bind/rndc.key`). `reload` перечитывает зоны, `reload-config` — конфигурацию, `status` показывает состояние сервера, `stats` — статистику запросов.
