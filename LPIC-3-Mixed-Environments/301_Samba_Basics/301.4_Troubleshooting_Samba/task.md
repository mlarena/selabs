[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Логирование и отладка**

**Задание:**
1. Настройте уровень логирования Samba.
2. Включите отдельный лог для клиента.
3. Посмотрите журналы по классам отладки.
4. Найдите ошибку аутентификации.
5. Объясните структуру логов Samba.

**Решение и пояснения:**
```bash
# smb.conf: log level = 3 auth:5
# log file = /var/log/samba/log.%m
sudo systemctl restart smbd
ls /var/log/samba/
sudo grep -i "auth" /var/log/samba/log.smbd | tail
```
**Пояснения:**
`log level` задаёт детализацию, классы (`auth`, `smb`, `winbind`) — отдельные области. `log file = ...%m` создаёт лог на клиента (`%m` — имя машины). Логи помогают выявить проблемы аутентификации и доступа.

---

**Практическая работа №2: Работа с TDB-файлами**

**Задание:**
1. Выгрузите содержимое TDB.
2. Посмотрите ключи реестра Samba.
3. Отредактируйте TDB.
4. Проверьте повреждение TDB.
5. Объясните назначение tdbdump/tdbtool.

**Решение и пояснения:**
```bash
sudo tdbdump /var/lib/samba/private/secrets.tdb | head
sudo tdbtool /var/lib/samba/registry.tdb
# В tdbtool: keys / check / exit
```
**Пояснения:**
`tdbdump` выгружает содержимое TDB, `tdbtool` позволяет просматривать и редактировать ключи. `check` проверяет целостность. Повреждённые TDB восстанавливают из бэкапа или пересоздают.

---

**Практическая работа №3: LDAP-контент контроллера домена**

**Задание:**
1. Выполните запрос к LDAP Samba AD.
2. Найдите пользователей и группы.
3. Измените объект через `ldbmodify`.
4. Включите корзину (recycle bin).
5. Объясните назначение ldb-утилит.

**Решение и пояснения:**
```bash
sudo ldbsearch -H /var/lib/samba/private/sam.ldb "(objectClass=user)" cn | head
sudo ldbedit -H /var/lib/samba/private/sam.ldb "CN=user1,CN=Users,DC=lab,DC=local"
sudo ldbmodify -H /var/lib/samba/private/sam.ldb change.ldif
sudo samba-tool domain enable recyclebin   # 4. Корзина
```
**Пояснения:**
Samba AD хранит данные в `sam.ldb` (LDAP-совместимо). `ldbsearch`, `ldbmodify`, `ldbedit`, `ldbadd`, `ldbdel` работают с ним напрямую. Корзина позволяет восстанавливать удалённые объекты.

---

**Практическая работа №4: rpcclient и клонирование DC**

**Задание:**
1. Запросите информацию через `rpcclient`.
2. Получите список пользователей.
3. Создайте переименованный клон DC (концептуально).
4. Проверьте целостность базы.
5. Объясните назначение клона для отладки.

**Решение и пояснения:**
```bash
rpcclient -U administrator%pass //dc1.lab -c "enumdomusers"
rpcclient -U administrator%pass //dc1.lab -c "querydominfo"
sudo samba-tool dbcheck
sudo samba-tool domain backup rename --help   # 3. Клон с переименованием
```
**Пояснения:**
`rpcclient` выполняет MS-RPC-запросы (пользователи, группы, домен). `samba-tool domain backup rename` создаёт переименованный клон DC для безопасной отладки. `dbcheck` подтверждает целостность.
