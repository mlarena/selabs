[Оглавление](LPIC-2/home.md)

**Практическая работа №1: Основы PAM**

**Задание:**
1. Посмотрите структуру `/etc/pam.d/`.
2. Найдите цепочку PAM для `login`.
3. Объясните типы модулей (auth, account, password, session).
4. Посмотрите, какие модули подключены для `su`.
5. Объясните управляющие флаги (required, requisite, sufficient, optional).

**Решение и пояснения:**
```bash
ls /etc/pam.d/                          # 1. Файлы служб
cat /etc/pam.d/login                    # 2. Цепочка login
cat /etc/pam.d/su                       # 4. Цепочка su
cat /etc/pam.d/common-auth              # 4. Общие модули
```
**Пояснения:**
PAM управляет аутентификацией по цепочкам модулей. Типы: `auth` (проверка), `account` (права/срок), `password` (смена пароля), `session` (окружение). Флаги: `required` (обязателен), `requisite` (обязателен и сразу отказ), `sufficient` (достаточен), `optional`.

---

**Практическая работа №2: Политики паролей**

**Задание:**
1. Установите модуль `pam_cracklib`/`pam_pwquality`.
2. Настройте минимальную длину и сложность пароля.
3. Ограничьте повторное использование паролей.
4. Настройте срок действия пароля.
5. Проверьте политику.

**Решение и пояснения:**
```bash
sudo apt install -y libpam-pwquality
# /etc/pam.d/common-password:
# password requisite pam_pwquality.so retry=3 minlen=12 dcredit=-1 ucredit=-1
# /etc/pam.d/common-password: remember=5 (pam_pwhistory)
sudo chage -M 90 user1                 # 4. Срок действия 90 дней
chage -l user1                         # 5. Проверка
```
**Пояснения:**
`pam_pwquality` проверяет сложность пароля (длина, цифры, регистр). `remember` запрещает повторное использование последних паролей. `chage` управляет сроком действия. Политики хранятся в `/etc/pam.d/` и `/etc/security/`.

---

**Практическая работа №3: Блокировка после неудачных попыток**

**Задание:**
1. Настройте `pam_faillock`/`pam_tally2`.
2. Заблокируйте учётную запись после 3 неудач.
3. Проверьте блокировку.
4. Разблокируйте пользователя.
5. Объясните защиту от подбора пароля.

**Решение и пояснения:**
```bash
# /etc/pam.d/common-auth:
# auth required pam_faillock.so preauth
# auth [default=die] pam_faillock.so authfail
# account required pam_faillock.so
faillock --user user1                   # 3. Счётчик неудач
faillock --user user1 --reset           # 4. Сброс
```
**Пояснения:**
`pam_faillock` блокирует учётную запись после N неудачных попыток входа, защищая от перебора пароля. Настройки в `/etc/security/faillock.conf`. `faillock` показывает и сбрасывает счётчики.

---

**Практическая работа №4: PAM и автоматическое создание домашних каталогов**

**Задание:**
1. Подключите модуль `pam_mkhomedir`.
2. Настройте создание домашнего каталога при входе.
3. Проверьте создание каталога.
4. Настройте ограничения ресурсов через `pam_limits`.
5. Проверьте применение лимитов.

**Решение и пояснения:**
```bash
# /etc/pam.d/common-session:
# session optional pam_mkhomedir.so skel=/etc/skel umask=0022
# /etc/security/limits.conf:
# user1 hard nproc 100
# user1 hard fsize 100000
sudo -u user1 -i
ulimit -u                              # 5. Проверка лимита процессов
```
**Пояснения:**
`pam_mkhomedir` создаёт домашний каталог при первом входе (важно для LDAP/AD-пользователей). `pam_limits` применяет лимиты из `/etc/security/limits.conf` (`nproc`, `fsize`, `nofile`). Проверка — через `ulimit`.
