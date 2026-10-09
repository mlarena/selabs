[Оглавление](?file=LPIC-2%2Fhome.md)

**Практическая работа №1: Установка OpenLDAP и базовая конфигурация**

**Задание:**
1. Установите `slapd`.
2. Задайте пароль администратора.
3. Посмотрите конфигурацию (OLC).
4. Проверьте запуск службы.
5. Проверьте суффикс каталога.

**Решение и пояснения:**
```bash
sudo apt install -y slapd ldap-utils
sudo dpkg-reconfigure slapd              # 2. Пароль и суффикс
sudo slapcat | head                      # 3. Содержимое БД
sudo systemctl status slapd              # 4. Статус
ldapsearch -x -b "" -s base namingContexts   # 5. Суффиксы
```
**Пояснения:**
OpenLDAP в Debian хранит конфигурацию в `cn=config` (OLC — on-line configuration) в `/etc/ldap/slapd.d/`. `slapcat` выгружает содержимое базы. Суффикс (`dc=example,dc=com`) — корень каталога.

---

**Практическая работа №2: Схемы, объекты и атрибуты**

**Задание:**
1. Посмотрите установленные схемы.
2. Определите обязательные атрибуты `inetOrgPerson`.
3. Создайте структурные OU.
4. Добавьте пользователя с нужными атрибутами.
5. Проверьте запись.

**Решение и пояснения:**
```bash
ldapsearch -x -b "cn=schema,cn=config" -s base 2>/dev/null | head
# OU:
# dn: ou=people,dc=example,dc=com  objectClass: organizationalUnit  ou: people
ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f ou.ldif
ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f user1.ldif
```
**Пояснения:**
Схемы определяют объектные классы и атрибуты. `inetOrgPerson` требует `cn` и `sn`. `organizationalUnit` (OU) группирует записи. Соблюдение схемы обязательно при добавлении записей.

---

**Практическая работа №3: Access Control (ACL)**

**Задание:**
1. Посмотрите текущие ACL.
2. Разрешите анонимное чтение атрибутов.
3. Запретите чтение паролей всем, кроме admin.
4. Примените ACL.
5. Проверьте доступ.

**Решение и пояснения:**
```bash
# В cn=config (olcAccess) или через ldapmodify:
# olcAccess: {0}to attrs=userPassword by self write by anonymous auth by * none
# olcAccess: {1}to * by self read by users read by * none
ldapsearch -x -b "dc=example,dc=com" "(uid=user1)"
ldapsearch -x -b "dc=example,dc=com" "(uid=user1)" userPassword
```
**Пояснения:**
ACL (`olcAccess`) управляют доступом к атрибутам. Правило `userPassword ... by self write by anonymous auth` разрешает пользователю менять свой пароль и анонимную аутентификацию, но не чтение. Правила применяются по порядку.

---

**Практическая работа №4: Резервное копирование и обслуживание**

**Задание:**
1. Сделайте резервную копию каталога.
2. Посмотрите статистику базы.
3. Переиндексируйте базу.
4. Восстановите из резервной копии.
5. Объясните назначение slapcat/slapadd.

**Решение и пояснения:**
```bash
sudo slapcat -l /backup/ldap_backup.ldif     # 1. Резервная копия
sudo slapindex                                # 3. Переиндексация
sudo systemctl stop slapd
sudo slapadd -l /backup/ldap_backup.ldif      # 4. Восстановление
sudo systemctl start slapd
```
**Пояснения:**
`slapcat` выгружает базу в LDIF (офлайн-бэкап), `slapadd` загружает. `slapindex` перестраивает индексы. Перед офлайн-операциями останавливают `slapd`. Резервные копии каталога критичны для восстановления аутентификации.
