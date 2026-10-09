[Оглавление](LPIC-2/home.md)

**Практическая работа №1: Запросы к LDAP**

**Задание:**
1. Установите LDAP-утилиты.
2. Выполните анонимный запрос к каталогу.
3. Ограничьте вывод нужными атрибутами.
4. Найдите конкретную запись по фильтру.
5. Объясните структуру DN.

**Решение и пояснения:**
```bash
sudo apt install -y ldap-utils
ldapsearch -x -H ldap://localhost -b "dc=example,dc=com"     # 2. Анонимный запрос
ldapsearch -x -H ldap://localhost -b "dc=example,dc=com" cn mail   # 3. Атрибуты
ldapsearch -x -b "dc=example,dc=com" "(uid=user1)"           # 4. По фильтру
```
**Пояснения:**
`ldapsearch` выполняет запросы к LDAP. `-x` — простая аутентификация, `-H` — URI сервера, `-b` — база поиска. DN (Distinguished Name) — уникальный путь записи, например `uid=user1,ou=people,dc=example,dc=com`.

---

**Практическая работа №2: Добавление и изменение записей**

**Задание:**
1. Создайте LDIF-файл для нового пользователя.
2. Добавьте запись через `ldapadd`.
3. Измените атрибут через `ldapmodify`.
4. Удалите запись.
5. Смените пароль пользователя.

**Решение и пояснения:**
```bash
cat > user1.ldif <<'EOF'
dn: uid=user1,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
uid: user1
cn: User One
sn: One
mail: user1@example.com
EOF
ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f user1.ldif   # 2. Добавление
ldapmodify -x -D "cn=admin,dc=example,dc=com" -W -f change.ldif   # 3. Изменение
ldapdelete -x -D "cn=admin,dc=example,dc=com" -W "uid=user1,ou=people,dc=example,dc=com"  # 4
ldappasswd -x -D "cn=admin,dc=example,dc=com" -W -S "uid=user1,..."   # 5
```
**Пояснения:**
LDIF — текстовый формат записей и изменений. `ldapadd` добавляет, `ldapmodify` изменяет, `ldapdelete` удаляет, `ldappasswd` меняет пароль. `-D` — bind DN администратора, `-W` — запрос пароля.

---

**Практическая работа №3: Поиск и фильтры**

**Задание:**
1. Найдите всех пользователей в `ou=people`.
2. Используйте фильтр по атрибуту.
3. Используйте wildcard в фильтре.
4. Ограничьте глубину поиска.
5. Выведите только DN.

**Решение и пояснения:**
```bash
ldapsearch -x -b "ou=people,dc=example,dc=com" "(objectClass=inetOrgPerson)"
ldapsearch -x -b "dc=example,dc=com" "(cn=User*)"
ldapsearch -x -b "dc=example,dc=com" -s one "(uid=*)"      # 4. Уровень one
ldapsearch -x -b "dc=example,dc=com" "(uid=user1)" dn       # 5. Только DN
```
**Пояснения:**
Фильтры LDAP: `(attr=value)`, `(attr=*)` (есть атрибут), `(cn=User*)` (wildcard). `-s base|one|sub` задаёт глубину поиска. Указание атрибута (например, `dn`) ограничивает вывод.

---

**Практическая работа №4: Интеграция с NSS/PAM**

**Задание:**
1. Установите `libnss-ldap`/`sssd`.
2. Настройте источник LDAP в `nsswitch.conf`.
3. Проверьте разрешение пользователя через `getent`.
4. Настройте PAM для LDAP.
5. Проверьте вход LDAP-пользователя.

**Решение и пояснения:**
```bash
# /etc/nsswitch.conf: passwd: files ldap
# /etc/ldap/ldap.conf: URI, BASE, binddn
getent passwd user1                    # 3. Разрешение через NSS
getent passwd | grep user1
# PAM: pam_ldap.so или pam_sss.so в /etc/pam.d/common-*
```
**Пояснения:**
NSS позволяет системе получать пользователей из LDAP, PAM — аутентифицировать их. `getent` проверяет разрешение через NSS. На практике чаще используют SSSD (`pam_sss`/`nss_sss`) для кэширования и офлайн-входа.
