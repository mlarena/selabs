[Оглавление](LPIC-2home.md)

**Практическая работа №1: Диагностика сетевых проблем**

**Задание:**
1. Проверьте базовую связность (loopback, шлюз, внешний узел).
2. Определите, где обрывается маршрут.
3. Проверьте разрешение имён.
4. Посмотрите сетевые логи.
5. Объясните порядок диагностики «снизу вверх».

**Решение и пояснения:**
```bash
ping -c2 127.0.0.1                 # 1. Loopback (стек)
ping -c2 <gateway>                 # 1. Шлюз (локальная сеть)
ping -c2 8.8.8.8                   # 1. Внешний узел (маршрут)
traceroute 8.8.8.8                 # 2. Где обрыв
getent hosts example.com           # 3. DNS
journalctl -k | tail               # 4. Ядро/сеть
```
**Пояснения:**
Диагностика идёт по уровням: интерфейс → шлюз → маршрут → DNS. Если ping до IP работает, а имя не разрешается — проблема в DNS. `traceroute`/`mtr` показывают, на каком узле теряются пакеты.

---

**Практическая работа №2: Конфигурационные файлы сети**

**Задание:**
1. Посмотрите `/etc/network/interfaces`.
2. Посмотрите конфигурацию NetworkManager.
3. Проверьте имя хоста и `/etc/hosts`.
4. Посмотрите `/etc/resolv.conf`.
5. Объясните, кто управляет сетью в системе.

**Решение и пояснения:**
```bash
cat /etc/network/interfaces        # 1. ifupdown
nmcli connection show              # 2. NetworkManager
cat /etc/hostname /etc/hosts       # 3. Имя хоста и локальные записи
cat /etc/resolv.conf               # 4. DNS
systemctl is-active NetworkManager systemd-networkd   # 5. Кто управляет
```
**Пояснения:**
В Debian сеть может управляться `ifupdown` (`/etc/network/interfaces`), NetworkManager (рабочие станции) или `systemd-networkd` (серверы). Важно, чтобы был один активный менеджер, иначе конфликты.

---

**Практическая работа №3: NetworkManager и nmcli**

**Задание:**
1. Посмотрите статус устройств.
2. Создайте статическое подключение.
3. Активируйте подключение.
4. Проверьте параметры.
5. Удалите подключение.

**Решение и пояснения:**
```bash
nmcli device status                        # 1. Устройства
nmcli con add type ethernet ifname eth0 con-name static1 \
  ip4 192.168.60.10/24 gw4 192.168.60.1    # 2. Статическое подключение
nmcli con up static1                       # 3. Активация
nmcli con show static1                     # 4. Параметры
nmcli con delete static1                   # 5. Удаление
```
**Пояснения:**
`nmcli` — CLI NetworkManager. Подключения («connections») описывают настройки и привязываются к устройствам. Статическая конфигурация сохраняется в `/etc/NetworkManager/system-connections/`.

---

**Практическая работа №4: Ограничения доступа на уровне хоста**

**Задание:**
1. Посмотрите `/etc/hosts.allow` и `/etc/hosts.deny`.
2. Разрешите сервис только для подсети.
3. Запретите всё остальное.
4. Проверьте системные логи на срабатывание.
5. Объясните, почему TCP Wrappers устаревают.

**Решение и пояснения:**
```bash
cat /etc/hosts.allow /etc/hosts.deny
echo "sshd: 192.168.1.0/255.255.255.0" | sudo tee -a /etc/hosts.allow
echo "ALL: ALL" | sudo tee -a /etc/hosts.deny
sudo journalctl -u ssh | tail
```
**Пояснения:**
TCP Wrappers фильтрует по хосту/IP на уровне демона. Порядок: allow, затем deny. Механизм устаревает: современные системы предпочитают nftables/iptables и настройки в самом демоне (например, `AllowUsers` в sshd).
