[Оглавление](LPIC-3-Securityhome.md)

**Практическая работа №1: Управление ресурсами через systemd**

**Задание:**
1. Посмотрите параметры ресурсов сервиса.
2. Ограничьте память и CPU сервиса.
3. Примените изменения.
4. Проверьте ограничения.
5. Объясните cgroups v2.

**Решение и пояснения:**
```bash
systemctl show nginx | grep -iE "Memory|CPU"
# /etc/systemd/system/nginx.service.d/limits.conf:
# [Service]
# MemoryMax=256M
# CPUQuota=50%
sudo systemctl daemon-reload && sudo systemctl restart nginx
systemctl show nginx | grep -iE "MemoryMax|CPUQuota"
systemd-cgtop                                 # 4. Использование cgroups
```
**Пояснения:**
systemd управляет ресурсами через cgroups v2. Директивы `MemoryMax`, `CPUQuota`, `IOWeight`, `TasksMax` ограничивают потребление. Это защищает систему от «шумных соседей» и утечек ресурсов.

---

**Практическая работа №2: Лимиты пользователей (ulimit и limits.conf)**

**Задание:**
1. Посмотрите текущие лимиты.
2. Настройте лимиты в `limits.conf`.
3. Примените лимиты к пользователю.
4. Проверьте лимиты.
5. Объясните жёсткие и мягкие лимиты.

**Решение и пояснения:**
```bash
ulimit -a
# /etc/security/limits.conf:
# user1 hard nproc 100
# user1 hard nofile 4096
# user1 soft fsize 100000
sudo -u user1 -i
ulimit -u                                     # 4. Проверка
```
**Пояснения:**
`ulimit` ограничивает ресурсы процесса (процессы, файлы, память). Мягкий лимит можно повысить до жёсткого; жёсткий — только root. Настройки в `/etc/security/limits.conf`, применяются через PAM (`pam_limits`).

---

**Практическая работа №3: Планирование приоритетов CPU и I/O**

**Задание:**
1. Посмотрите приоритет процесса.
2. Запустите процесс с низким приоритетом.
3. Измените приоритет работающего процесса.
4. Настройте приоритет ввода-вывода.
5. Объясните nice/ionice.

**Решение и пояснения:**
```bash
nice -n 10 tar -czf /tmp/big.tar.gz /var/log      # 2. Низкий приоритет
renice -n 5 -p <PID>                              # 3. Изменение
ionice -c2 -n7 -p <PID>                           # 4. Приоритет I/O
ps -o pid,ni,cmd -p <PID>
```
**Пояснения:**
`nice` (-20..19) задаёт приоритет CPU, `ionice` — приоритет дисковых операций (классы 1-3). Это позволяет фоновым задачам (бэкапы, индексация) не мешать интерактивным. Планирование ресурсов — часть Resource Control.

---

**Практическая работа №4: Namespaces и изоляция**

**Задание:**
1. Посмотрите существующие namespaces.
2. Запустите процесс в изолированном namespace.
3. Изолируйте сеть.
4. Проверьте изоляцию.
5. Объясните связь с контейнерами.

**Решение и пояснения:**
```bash
lsns
sudo unshare --pid --fork --mount-proc /bin/bash      # 2. PID namespace
sudo unshare --net /bin/bash                          # 3. Network namespace
sudo ip netns add testns                              # 3. Именованный netns
ip netns list
```
**Пояснения:**
Namespaces изолируют PID, mount, network, user, IPC, UTS. Это основа контейнеров (Docker, Podman, LXC). Изоляция ограничивает влияние процесса на систему и позволяет запускать несколько экземпляров.

---

**Практическая работа №5: Квоты и управление дисковым пространством**

**Задание:**
1. Включите квоты на ФС.
2. Настройте квоту для пользователя.
3. Проверьте использование.
4. Настройте квоту для группы.
5. Объясните защиту от переполнения.

**Решение и пояснения:**
```bash
# /etc/fstab: /dev/sdb1 /mnt/data ext4 defaults,usrquota,grpquota 0 2
sudo mount -o remount /mnt/data
sudo quotacheck -cugm /mnt/data
sudo quotaon /mnt/data
sudo setquota -u user1 1000000 1100000 0 0 /mnt/data   # 2. Квота
repquota -a                                            # 3. Проверка
```
**Пояснения:**
Квоты ограничивают дисковое пространство пользователей/групп. `usrquota`/`grpquota` включают учёт, `setquota` задаёт лимиты (мягкий/жёсткий). Это предотвращает заполнение диска и отказ сервисов.
