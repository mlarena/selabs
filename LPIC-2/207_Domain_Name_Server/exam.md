[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 207: Domain Name Server

Задачи приближены к реальным заданиям экзамена **202-450**.

## Задача 1. Настройка кэширующего DNS

**Условие:** Настройте BIND как кэширующий резолвер с форвардерами и ограничьте доступ.

**Ожидаемый результат:** Сервер разрешает имена для своей подсети.

**Решение и пояснения:**
```bash
sudo apt install -y bind9
# named.conf.options:
# recursion yes; forwarders { 8.8.8.8; 1.1.1.1; };
# allow-recursion { localhost; 192.168.1.0/24; };
sudo named-checkconf && sudo systemctl restart bind9
dig @localhost example.com
```
Кэширующий сервер пересылает запросы и кэширует ответы. `forwarders` задаёт вышестоящие серверы, `allow-recursion` ограничивает круг клиентов (защита от amplification-атак).

## Задача 2. Создание прямой зоны

**Условие:** Создайте зону `lab.local` с записями A, CNAME, MX и NS.

**Ожидаемый результат:** Зона работает.

**Решение и пояснения:**
```bash
# named.conf.local: zone "lab.local" { type master; file "/etc/bind/db.lab.local"; };
# db.lab.local:
# $TTL 3600
# @   IN SOA ns.lab.local. admin.lab.local. (2024010101 3600 1800 604800 86400)
# @   IN NS  ns.lab.local.
# @   IN MX  10 mail.lab.local.
# ns  IN A   192.168.1.10
# www IN A   192.168.1.20
# ftp IN CNAME www
sudo named-checkzone lab.local /etc/bind/db.lab.local
sudo rndc reload
dig @localhost www.lab.local
```
SOA — начальная запись (серийный номер, таймеры). A — адрес, CNAME — псевдоним, MX — почта, NS — сервер имён. `named-checkzone` проверяет, `rndc reload` применяет.

## Задача 3. Обратная зона

**Условие:** Настройте обратную зону для сети 192.168.1.0/24 с записями PTR.

**Ожидаемый результат:** Обратное разрешение работает.

**Решение и пояснения:**
```bash
# named.conf.local: zone "1.168.192.in-addr.arpa" { type master; file "/etc/bind/db.192.168.1"; };
# db.192.168.1:
# @ IN SOA ns.lab.local. admin.lab.local. (2024010101 3600 1800 604800 86400)
# @ IN NS ns.lab.local.
# 10 IN PTR ns.lab.local.
# 20 IN PTR www.lab.local.
sudo named-checkzone 1.168.192.in-addr.arpa /etc/bind/db.192.168.1
dig -x 192.168.1.20 @localhost
```
Обратная зона (`in-addr.arpa`) сопоставляет IP → имя (PTR). Имя зоны — обратный порядок октетов. Обратные записи важны для логов, почты (PTR-проверки), диагностики.

## Задача 4. Делегирование подзоны

**Условие:** Делегируйте подзону `dev.lab.local` другому серверу.

**Ожидаемый результат:** Делегирование работает.

**Решение и пояснения:**
```bash
# В зоне lab.local:
# dev     IN NS ns.dev.lab.local.
# ns.dev  IN A  192.168.1.40
# На сервере подзоны: zone "dev.lab.local" { type master; ... };
dig @localhost www.dev.lab.local
dig @localhost NS dev.lab.local
```
Делегирование передаёт управление подзоной через NS-записи и glue-записи (A для сервера подзоны). Это распределяет администрирование DNS между организациями.

## Задача 5. Защита DNS

**Условие:** Ограничьте передачу зон, настройте TSIG и включите DNSSEC.

**Ожидаемый результат:** Сервер защищён.

**Решение и пояснения:**
```bash
# Ограничение передачи:
# zone "lab.local" { ... allow-transfer { 192.168.1.10; }; };
# TSIG:
sudo tsig-keygen -a hmac-sha256 xferkey > /etc/bind/xfer.key
# allow-transfer { key xferkey; };
# DNSSEC:
dnssec-keygen -a ECDSAP256SHA256 -n ZONE lab.local
dnssec-signzone -o lab.local db.lab.local
sudo named-checkconf && sudo rndc reload
```
`allow-transfer` ограничивает AXFR, TSIG аутентифицирует обмен, DNSSEC подписывает записи. Вместе они защищают от утечки зон и подмены ответов.

## Задача 6. Диагностика DNS

**Условие:** Клиенты не могут разрешить имена. Найдите причину.

**Ожидаемый результат:** Проблема локализована.

**Решение и пояснения:**
```bash
sudo systemctl status bind9
sudo named-checkconf
sudo named-checkzone lab.local /etc/bind/db.lab.local
sudo journalctl -u bind9 | tail
dig @localhost lab.local SOA
sudo ss -tlnp | grep :53
```
Проверяют: статус службы, синтаксис конфигурации и зон, журнал, ответ сервера, слушающие порты. Типовые ошибки: пропущенная точка в FQDN, неверный serial, firewall, права на файлы зон.
