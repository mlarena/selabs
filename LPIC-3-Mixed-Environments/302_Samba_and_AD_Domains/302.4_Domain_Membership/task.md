[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Присоединение Linux к AD (member server)**

**Задание:**
1. Настройте DNS на AD DC.
2. Установите необходимые пакеты.
3. Присоедините сервер к домену.
4. Проверьте членство в домене.
5. Объясните роль winbind.

**Решение и пояснения:**
```bash
sudo apt install -y samba winbind libnss-winbind libpam-winbind krb5-user
# /etc/resolv.conf: nameserver <dc_ip>
sudo net ads join -U administrator
sudo net ads testjoin                    # 4. Проверка
```
**Пояснения:**
Member server входит в AD как файловый сервер, но не является DC. `net ads join` выполняет присоединение (требует корректный DNS и время). `winbindd` обеспечивает разрешение AD-пользователей и аутентификацию.

---

**Практическая работа №2: Настройка winbind и ID mapping**

**Задание:**
1. Настройте winbind в `smb.conf`.
2. Задайте диапазон ID для домена.
3. Настройте backend `rid`/`ad`.
4. Перезапустите службы.
5. Проверьте сопоставление пользователей.

**Решение и пояснения:**
```bash
# smb.conf:
# security = ads
# realm = LAB.LOCAL
# workgroup = LAB
# idmap config * : backend = tdb
# idmap config * : range = 3000-7999
# idmap config LAB : backend = rid
# idmap config LAB : range = 10000-999999
# winbind use default domain = yes
sudo systemctl restart smbd winbind
wbinfo -u                                 # 5. Список пользователей AD
```
**Пояснения:**
ID mapping сопоставляет SID AD с Unix UID/GID. Backends: `rid` (детерминированно из RID), `ad`/`rfc2307` (из атрибутов), `autorid`. Диапазоны не должны пересекаться. `wbinfo` проверяет интеграцию.

---

**Практическая работа №3: PAM и NSS для winbind**

**Задание:**
1. Настройте NSS для winbind.
2. Настройте PAM для winbind.
3. Проверьте разрешение пользователя.
4. Проверьте вход AD-пользователя.
5. Настройте создание домашних каталогов.

**Решение и пояснения:**
```bash
# /etc/nsswitch.conf: passwd: files winbind ; group: files winbind
# /etc/pam.d/common-session: pam_mkhomedir.so skel=/etc/skel umask=0022
# /etc/pam.d/common-auth: pam_winbind.so
getent passwd LAB\\user1                  # 3. Разрешение
su - 'LAB\user1'                          # 4. Вход
```
**Пояснения:**
NSS (`libnss_winbind`) позволяет системе видеть AD-пользователей, PAM (`libpam_winbind`) — аутентифицировать их. `pam_mkhomedir` создаёт домашний каталог при первом входе. Проверка — `getent` и вход.

---

**Практическая работа №4: Диагностика членства и доступ к ресурсам**

**Задание:**
1. Проверьте доверие домена.
2. Посмотрите информацию о домене.
3. Проверьте Kerberos-билеты.
4. Настройте доступ AD-группе к ресурсу.
5. Объясните типовые проблемы.

**Решение и пояснения:**
```bash
wbinfo -t                                 # 1. Доверие
wbinfo --domain-info=LAB
klist                                     # 3. Билеты
# smb.conf ресурс: valid users = @LAB\\smbgroup
sudo systemctl restart smbd
```
**Пояснения:**
`wbinfo -t` проверяет доверие, `klist` — Kerberos-билеты. Ресурсы могут разрешать доступ AD-группам. Типовые проблемы: рассинхронизация времени, неверный DNS, ошибки ID mapping, отсутствие `winbind`.
