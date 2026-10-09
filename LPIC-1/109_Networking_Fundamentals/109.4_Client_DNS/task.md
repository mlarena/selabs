[Оглавление](LPIC-1/home.md)

**Практическая работа №1: Настройка разрешения имён**

**Задание:**
1. Посмотрите текущий файл `/etc/resolv.conf`.
2. Проверьте порядок разрешения имён в `/etc/nsswitch.conf`.
3. Добавьте локальную запись в `/etc/hosts`.
4. Проверьте, что имя разрешается локально.
5. Объясните роль `systemd-resolved`.

**Решение и пояснения:**
```bash
cat /etc/resolv.conf                    # 1. DNS-серверы
grep ^hosts /etc/nsswitch.conf          # 2. Порядок (files dns)
echo "127.0.0.1 local.test" | sudo tee -a /etc/hosts   # 3
getent hosts local.test                 # 4. Локальное разрешение
resolvectl status                       # 5. Состояние systemd-resolved
```
**Пояснения:**
`/etc/resolv.conf` задаёт DNS-серверы, `/etc/hosts` — статические записи, `/etc/nsswitch.conf` определяет порядок источников. `systemd-resolved` управляет DNS и часто подменяет `resolv.conf` символьной ссылкой на stub-файл.

---

**Практическая работа №2: Утилиты dig и host**

**Задание:**
1. Запросите A-запись для `example.com`.
2. Запросите MX-записи домена.
3. Запросите NS-записи зоны.
4. Используйте конкретный DNS-сервер (8.8.8.8).
5. Выполните обратный запрос (PTR) по IP.

**Решение и пояснения:**
```bash
dig example.com A                       # 1. A-запись
dig example.com MX                      # 2. Почтовые записи
dig example.com NS                      # 3. Серверы имён
dig @8.8.8.8 example.com A              # 4. Конкретный сервер
dig -x 8.8.8.8                          # 5. Обратный запрос
host example.com                        # Краткий формат
```
**Пояснения:**
`dig` — основной инструмент DNS-диагностики: показывает ответ, авторитетность, время. `@server` задаёт DNS-сервер, `-x` делает обратный запрос. `host` выводит результат в краткой форме. MX — почтовые серверы, NS — серверы зоны.

---

**Практическая работа №3: Диагностика разрешения имён**

**Задание:**
1. Проверьте, разрешается ли имя через `getent`.
2. Сравните результат с `dig`.
3. Временно укажите недоступный DNS-сервер.
4. Проверьте, как это влияет на разрешение.
5. Верните рабочий DNS-сервер.

**Решение и пояснения:**
```bash
getent hosts example.com                # 1. Через NSS (hosts + dns)
dig example.com +short                  # 2. Через DNS напрямую
sudo cp /etc/resolv.conf /etc/resolv.conf.bak
echo "nameserver 10.255.255.1" | sudo tee /etc/resolv.conf   # 3
getent hosts example.com                # 4. Разрешение не работает
sudo mv /etc/resolv.conf.bak /etc/resolv.conf                # 5. Возврат
```
**Пояснения:**
`getent` использует NSS (учитывает `/etc/hosts` и `/etc/nsswitch.conf`), а `dig` обращается напрямую к DNS. Если `getent` не разрешает имя, а `dig` — разрешает, проблема в порядке NSS или в `resolv.conf`.

---

**Практическая работа №4: Кэш и systemd-resolved**

**Задание:**
1. Проверьте, используется ли `systemd-resolved`.
2. Посмотрите статистику кэша.
3. Выполните запрос и проверьте попадание в кэш.
4. Очистите кэш DNS.
5. Объясните преимущества локального кэша.

**Решение и пояснения:**
```bash
systemctl is-active systemd-resolved    # 1. Проверка
resolvectl statistics                   # 2. Статистика кэша
resolvectl query example.com            # 3. Запрос через resolved
resolvectl flush-caches                 # 4. Очистка кэша
```
**Пояснения:**
`systemd-resolved` предоставляет локальный DNS-кэш и разрешает имена через stub-слушатель `127.0.0.53`. Кэш ускоряет повторные запросы и снижает нагрузку на внешние серверы. `flush-caches` сбрасывает кэш после изменений DNS.
