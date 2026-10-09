[Оглавление](?file=LPIC-3-Mixed-Environments%2Fhome.md)

**Практическая работа №1: Управление пользователями и группами**

**Задание:**
1. Создайте пользователя FreeIPA.
2. Создайте группу.
3. Добавьте пользователя в группу.
4. Задайте пароль.
5. Проверьте пользователя.

**Решение и пояснения:**
```bash
kinit admin
ipa user-add user1 --first=User --last=One --password
ipa group-add devops --desc="DevOps team"
ipa group-add-member devops --users=user1
ipa user-show user1
ipa group-show devops
```
**Пояснения:**
`ipa user-*` и `ipa group-*` управляют объектами каталога. FreeIPA добавляет к LDAP удобные команды и политики. Группы используются для доступа и sudo-правил.

---

**Практическая работа №2: Управление хостами и сервисами**

**Задание:**
1. Посмотрите список хостов.
2. Добавьте хост.
3. Добавьте сервис хоста.
4. Получите keytab сервиса.
5. Объясните назначение keytab.

**Решение и пояснения:**
```bash
ipa host-find
ipa host-add client2.lab.local --ip-address=192.168.1.60
ipa service-add HTTP/client2.lab.local
ipa-getkeytab -s ipa.lab.local -p HTTP/client2.lab.local -k /tmp/http.keytab
klist -k /tmp/http.keytab
```
**Пояснения:**
FreeIPA управляет хостами и сервисами домена. Keytab содержит ключи Kerberos для сервиса (например, веб-сервера) и используется для аутентификации без пароля.

---

**Практическая работа №3: Роли, привилегии и доступ**

**Задание:**
1. Посмотрите роли RBAC.
2. Посмотрите привилегии.
3. Назначьте роль пользователю.
4. Настройте доступ к хосту (HBAC).
5. Проверьте применение.

**Решение и пояснения:**
```bash
ipa role-find
ipa privilege-find
ipa role-add-member "User Administrator" --users=user1
ipa hbacrule-add allow_devops
ipa hbacrule-add-user allow_devops --users=user1
ipa hbacrule-add-host allow_devops --hosts=client2.lab.local
```
**Пояснения:**
FreeIPA использует RBAC: роли → привилегии → права. HBAC (host-based access control) определяет, кто и куда может входить. Это централизует управление доступом.

---

**Практическая работа №4: ID views и интеграции**

**Задание:**
1. Создайте ID view.
2. Переопределите UID пользователя.
3. Примените ID view к хосту.
4. Опишите интеграции sudo/autofs/SSH.
5. Объясните назначение ID views.

**Решение и пояснения:**
```bash
ipa idview-add myview
ipa idview-add-user-override myview --user=user1 --uid=20001 --gid=20001
ipa idview-apply myview --hosts=client2.lab.local
ipa sudorule-add allow_admin --hostcat=all --cmdcat=all
```
**Пояснения:**
ID views позволяют переопределять POSIX-идентификаторы (UID/GID, домашний каталог) для пользователей AD/LDAP на конкретных хостах. FreeIPA интегрируется с sudo, autofs, SSH-ключами и SELinux.
