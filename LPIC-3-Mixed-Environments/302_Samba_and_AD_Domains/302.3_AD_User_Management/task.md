[Оглавление](?file=LPIC-3-Mixed-Environments%2Fhome.md)

**Практическая работа №1: Управление пользователями и группами AD**

**Задание:**
1. Создайте пользователя AD.
2. Создайте группу безопасности.
3. Добавьте пользователя в группу.
4. Задайте пароль и требования.
5. Проверьте пользователя.

**Решение и пояснения:**
```bash
sudo samba-tool user create user1 'Passw0rd!' --given-name=User --surname=One
sudo samba-tool group add smbgroup
sudo samba-tool group addmembers smbgroup user1
sudo samba-tool user setpassword user1 --newpassword='NewPass1!'
sudo samba-tool user list
```
**Пояснения:**
`samba-tool user` и `group` управляют объектами AD. Пользователи хранятся в LDAP (`CN=Users`). Группы безопасности используются для назначения прав. Пароли подчиняются политике домена.

---

**Практическая работа №2: Политики паролей и сроки действия**

**Задание:**
1. Посмотрите политику паролей домена.
2. Задайте минимальную длину и сложность.
3. Задайте срок действия пароля.
4. Настройте блокировку учётной записи.
5. Проверьте применение.

**Решение и пояснения:**
```bash
sudo samba-tool domain passwordsettings show
sudo samba-tool domain passwordsettings set --min-pwd-length=10
sudo samba-tool domain passwordsettings set --complexity=on
sudo samba-tool domain passwordsettings set --max-pwd-age=90
sudo samba-tool domain passwordsettings set --account-lockout-threshold=5
```
**Пояснения:**
Политика паролей домена задаёт длину, сложность, срок действия, историю и блокировку. `samba-tool domain passwordsettings` управляет этими параметрами. Политика применяется ко всем пользователям домена.

---

**Практическая работа №3: Делегирование прав и SPN**

**Задание:**
1. Делегируйте право управления OU пользователю.
2. Посмотрите SPN пользователя.
3. Добавьте SPN сервиса.
4. Экспортируйте keytab.
5. Объясните назначение keytab и SPN.

**Решение и пояснения:**
```bash
sudo samba-tool spn add HTTP/web.lab.local user1
sudo samba-tool spn list user1
sudo samba-tool domain exportkeytab /tmp/user1.keytab --principal=user1@LAB.LOCAL
klist -k /tmp/user1.keytab
```
**Пояснения:**
SPN связывает сервис с учётной записью Kerberos. `exportkeytab` экспортирует ключи для аутентификации сервиса (например, веб-сервера). Делегирование прав позволяет разграничить администрирование AD.

---

**Практическая работа №4: RFC2307, SID, UPN**

**Задание:**
1. Включите поддержку RFC2307.
2. Задайте uidNumber и gidNumber пользователю.
3. Посмотрите SID пользователя.
4. Задайте UPN-суффикс.
5. Объясните назначение атрибутов RFC2307.

**Решение и пояснения:**
```bash
sudo samba-tool user add user2 'Passw0rd!' --uid=10001 --gid=10001 --use-rfc2307
sudo samba-tool user show user2 | grep -iE "uidNumber|gidNumber|objectSid"
# UPN: user@lab.local
sudo samba-tool domain exportkeytab --help
```
**Пояснения:**
RFC2307-атрибуты (`uidNumber`, `gidNumber`, `homeDirectory`) позволяют Linux-клиентам сопоставлять AD-пользователей с Unix-идентификаторами. SID — уникальный идентификатор объекта, UPN — имя входа вида `user@realm`.
