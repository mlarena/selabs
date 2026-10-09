[Оглавление](?file=LPIC-3-Security%2Fhome.md)

**Практическая работа №1: Права доступа, umask и владение**

**Задание:**
1. Посмотрите права файла в символьном и числовом виде.
2. Измените права файла.
3. Измените владельца и группу.
4. Настройте umask.
5. Проверьте права создаваемых файлов.

**Решение и пояснения:**
```bash
ls -l file.txt ; stat -c "%a %U:%G" file.txt
chmod 640 file.txt                        # 2. Права rw-r-----
sudo chown user1:smbgroup file.txt        # 3. Владелец/группа
umask 027                                 # 4. Умask
touch newfile && ls -l newfile            # 5. Права: 640
```
**Пояснения:**
DAC основан на правах владельца/группы/остальных (rwx). `chmod` меняет права, `chown` — владельца. umask вычитает биты при создании файлов. Символьная запись (`rw-r-----`) соответствует числовой (`640`).

---

**Практическая работа №2: Специальные биты: setuid, setgid, sticky**

**Задание:**
1. Найдите файлы с setuid.
2. Объясните действие setuid.
3. Настройте setgid на каталоге.
4. Настройте sticky-бит на каталоге.
5. Проверьте эффекты.

**Решение и пояснения:**
```bash
find / -perm -4000 -type f 2>/dev/null | head      # 1. setuid-файлы
sudo chmod g+s /srv/shared                         # 3. setgid на каталоге
sudo chmod +t /srv/shared                          # 4. sticky
ls -ld /srv/shared                                 # drwxrwsr-t
```
**Пояснения:**
setuid выполняет файл с правами владельца (опасен для root-владельцев). setgid на каталоге наследует группу, на файле — выполняет с правами группы. sticky на каталоге запрещает удалять чужие файлы (как `/tmp`). Спецбиты — часть тонкого управления доступом.

---

**Практическая работа №3: POSIX ACL**

**Задание:**
1. Проверьте поддержку ACL на ФС.
2. Установите ACL для пользователя.
3. Установите ACL для группы.
4. Настройте ACL по умолчанию для каталога.
5. Проверьте ACL.

**Решение и пояснения:**
```bash
mount | grep acl
sudo setfacl -m u:user1:rwx /srv/shared
sudo setfacl -m g:smbgroup:rx /srv/shared
sudo setfacl -d -m u:user1:rwx /srv/shared        # 4. Default ACL
sudo getfacl /srv/shared                          # 5. Просмотр
```
**Пояснения:**
POSIX ACL расширяют права: позволяют задавать доступ для нескольких пользователей/групп. `-d` задаёт ACL по умолчанию (наследуется новыми файлами). Наличие ACL отмечается `+` в `ls -l`. Маска ACL ограничивает эффективные права.

---

**Практическая работа №4: Атрибуты файлов и immutable**

**Задание:**
1. Посмотрите атрибуты файла.
2. Установите атрибут immutable.
3. Проверьте запрет изменения.
4. Снимите атрибут.
5. Объясните защиту критичных файлов.

**Решение и пояснения:**
```bash
lsattr /etc/passwd
sudo chattr +i /etc/passwd                # 2. Immutable
echo "test" | sudo tee -a /etc/passwd     # 3. Должно отказать
sudo chattr -i /etc/passwd                # 4. Снятие
lsattr /etc/passwd
```
**Пояснения:**
`chattr` задаёт атрибуты ФС (ext4). `+i` (immutable) запрещает любые изменения даже root, `+a` (append-only) — только добавление. Это защищает критичные файлы (passwd, sudoers, логи) от изменения, в том числе вредоносного.

---

**Практическая работа №5: Capabilities вместо setuid**

**Задание:**
1. Посмотрите capabilities бинарника.
2. Опишите проблему setuid-root.
3. Замените setuid на capability.
4. Проверьте работу программы.
5. Объясните принцип минимальных привилегий.

**Решение и пояснения:**
```bash
getcap /usr/bin/ping
sudo setcap cap_net_raw+ep /usr/bin/ping      # 3. Capability
getcap /usr/bin/ping
sudo getpcaps $$                              # 1. Capabilities процесса
sudo setcap -r /usr/bin/ping                  # Удаление
```
**Пояснения:**
Capabilities дробят root на отдельные права (`cap_net_raw`, `cap_net_bind_service`, `cap_dac_override`). Это безопаснее setuid-root: процесс получает только нужные права. `getcap`/`setcap` управляют ими. Реализация принципа минимальных привилегий.
