[Оглавление](LPIC-3-Mixed-Environmentshome.md)

**Практическая работа №1: Настройка SSSD для AD**

**Задание:**
1. Установите SSSD и необходимые пакеты.
2. Настройте `sssd.conf` для AD.
3. Включите службу.
4. Проверьте разрешение пользователей.
5. Проверьте вход AD-пользователя.

**Решение и пояснения:**
```bash
sudo apt install -y sssd sssd-tools realmd adcli krb5-user
sudo tee /etc/sssd/sssd.conf >/dev/null <<'EOF'
[sssd]
domains = lab.local
services = nss, pam
[domain/lab.local]
id_provider = ad
auth_provider = ad
access_provider = ad
EOF
sudo chmod 600 /etc/sssd/sssd.conf
sudo systemctl enable --now sssd
getent passwd user1@lab.local
```
**Пояснения:**
SSSD — демон аутентификации и кэширования, поддерживает AD, LDAP, Kerberos, IPA. Файл `sssd.conf` (права 600) задаёт домены и провайдеры. SSSD кэширует данные для офлайн-входа.

---

**Практическая работа №2: NSS и PAM с SSSD**

**Задание:**
1. Настройте NSS для SSSD.
2. Настройте PAM для SSSD.
3. Настройте создание домашних каталогов.
4. Проверьте вход.
5. Объясните цепочку NSS/PAM.

**Решение и пояснения:**
```bash
# /etc/nsswitch.conf: passwd: files sss ; group: files sss
# /etc/pam.d/common-session: pam_mkhomedir.so skel=/etc/skel umask=0022
# /etc/pam.d/common-auth: pam_sss.so
sudo authselect select sssd 2>/dev/null || sudo pam-auth-update --enable mkhomedir
su - user1@lab.local
```
**Пояснения:**
NSS (`nss_sss`) даёт системе доступ к пользователям из SSSD, PAM (`pam_sss`) аутентифицирует их. `pam_mkhomedir` создаёт каталог. `realm`/`authselect`/`pam-auth-update` помогают настроить цепочки.

---

**Практическая работа №3: Kerberos-билеты**

**Задание:**
1. Проверьте конфигурацию Kerberos.
2. Получите билет через `kinit`.
3. Посмотрите билеты.
4. Уничтожьте билеты.
5. Объясните назначение билетов.

**Решение и пояснения:**
```bash
cat /etc/krb5.conf
kinit user1@LAB.LOCAL                    # 2. Получение билета
klist                                    # 3. Список билетов
kdestroy                                 # 4. Уничтожение
```
**Пояснения:**
Kerberos выдаёт билеты (TGT) после аутентификации. `kinit` получает билет, `klist` показывает, `kdestroy` удаляет. Билеты используются для доступа к сервисам без повторного ввода пароля (SSO).

---

**Практическая работа №4: Политики паролей и блокировка**

**Задание:**
1. Настройте сложность паролей через PAM.
2. Настройте срок действия паролей.
3. Настройте блокировку после неудач.
4. Проверьте применение.
5. Объясните взаимодействие SSSD и PAM.

**Решение и пояснения:**
```bash
# /etc/pam.d/common-password: pam_pwquality.so minlen=12
# /etc/security/faillock.conf: deny=5 unlock_time=900
chage -l user1
faillock --user user1
```
**Пояснения:**
Политики паролей и блокировки задают на уровне PAM (`pam_pwquality`, `pam_faillock`) и/или домена AD. SSSD передаёт часть настроек. Согласованность политик важна, чтобы локальные и доменные правила не конфликтовали.
