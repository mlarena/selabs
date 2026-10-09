[Оглавление](LPIC-3-Security/home.md)

**Практическая работа №1: Аудит событий через auditd**

**Задание:**
1. Установите и запустите `auditd`.
2. Добавьте правило наблюдения за файлом.
3. Добавьте правило для системного вызова.
4. Посмотрите события.
5. Сформируйте отчёт.

**Решение и пояснения:**
```bash
sudo apt install -y auditd audispd-plugins
sudo systemctl enable --now auditd
sudo auditctl -w /etc/passwd -p wa -k passwd_changes      # 2. Наблюдение
sudo auditctl -a always,exit -F arch=b64 -S execve -k exec  # 3. Syscall
sudo ausearch -k passwd_changes                            # 4. События
sudo aureport -s                                           # 5. Отчёт по syscall
```
**Пояснения:**
auditd фиксирует события безопасности: доступ к файлам, системные вызовы, изменения. Правила (`-w` файлы, `-a` syscall, `-k` ключ) определяют, что логировать. `ausearch`/`aureport` анализируют журнал.

---

**Практическая работа №2: Проверка целостности файлов (AIDE)**

**Задание:**
1. Установите AIDE.
2. Инициализируйте базу.
3. Измените файл.
4. Выполните проверку.
5. Посмотрите отчёт об изменениях.

**Решение и пояснения:**
```bash
sudo apt install -y aide
sudo aideinit                                    # 2. Инициализация базы
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
echo "test" | sudo tee -a /etc/hosts >/dev/null  # 3. Изменение
sudo aide --check                                # 4. Проверка
sudo aide --update                               # 5. Обновление базы
```
**Пояснения:**
AIDE вычисляет хэши файлов и сравнивает с базой, выявляя несанкционированные изменения. База инициализируется (`aideinit`) и хранится в защищённом месте. Регулярные проверки (через cron) — часть HIDS.

---

**Практическая работа №3: Поиск руткитов и вредоносного ПО**

**Задание:**
1. Установите `rkhunter` и `chkrootkit`.
2. Обновите базы сигнатур.
3. Запустите проверку системы.
4. Проанализируйте отчёт.
5. Настройте регулярный запуск.

**Решение и пояснения:**
```bash
sudo apt install -y rkhunter chkrootkit
sudo rkhunter --update
sudo rkhunter --check --sk                # 3. Проверка
sudo chkrootkit | grep INFECTED
# cron: 0 3 * * * /usr/bin/rkhunter --check --sk
```
**Пояснения:**
`rkhunter`/`chkrootkit` ищут известные руткиты, подозрительные файлы и изменения. Их запускают регулярно и проверяют отчёты. Ложные срабатывания возможны, поэтому важна ручная оценка результатов.

---

**Практическая работа №4: Мониторинг логов и обнаружение вторжений**

**Задание:**
1. Настройте централизованный сбор логов.
2. Установите `logwatch`.
3. Проанализируйте попытки входа.
4. Настройте уведомления о событиях.
5. Объясните корреляцию событий.

**Решение и пояснения:**
```bash
sudo apt install -y logwatch
sudo logwatch --detail high --range today    # 3. Отчёт
sudo grep "Failed password" /var/log/auth.log | wc -l
sudo journalctl -p err -b                    # Ошибки текущей загрузки
# rsyslog: *.* @logserver:514 (централизованный сбор)
```
**Пояснения:**
Мониторинг логов выявляет аномалии (много неудачных входов, ошибки). `logwatch` формирует сводки, journalctl фильтрует по приоритету. Централизованный сбор (`rsyslog`) защищает логи от удаления атакующим и позволяет коррелировать события.

---

**Практическая работа №5: HIDS и SELinux/AppArmor отказы**

**Задание:**
1. Проверьте отказы AVC (SELinux) или AppArmor.
2. Установите `sealert`/`aa-logprof`.
3. Проанализируйте отказ.
4. Настройте уведомления.
5. Объясните роль MAC в HIDS.

**Решение и пояснения:**
```bash
sudo ausearch -m avc -ts recent 2>/dev/null || sudo journalctl -k | grep -i apparmor | tail
sudo apt install -y apparmor-utils
sudo aa-logprof
sudo sealert -a /var/log/audit/audit.log 2>/dev/null
```
**Пояснения:**
MAC (SELinux/AppArmor) фиксирует попытки запрещённых операций — это источник данных для HIDS. Отказы AVC/AppArmor указывают на аномальное поведение. Инструменты `sealert`/`aa-logprof` помогают анализировать и корректировать политики.
