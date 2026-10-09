[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Демоны и компоненты Samba**

**Задание:**
1. Установите Samba 4.
2. Определите назначение демонов `smbd`, `nmbd`, `winbindd`.
3. Посмотрите статус служб.
4. Определите используемые порты SMB/CIFS.
5. Объясните разницу Samba 3 и Samba 4.

**Решение и пояснения:**
```bash
sudo apt install -y samba winbind
systemctl status smbd nmbd winbind
ss -tlnp | grep -E "445|139"
smbd -V                                   # Версия
```
**Пояснения:**
`smbd` — файловые и печатные ресурсы (порт 445/139), `nmbd` — разрешение имён NetBIOS (137-138), `winbindd` — интеграция с AD и сопоставление пользователей. Samba 4 умеет работать контроллером домена AD, Samba 3 — только файловый сервер в домене.

---

**Практическая работа №2: Протоколы и порты SMB/CIFS и AD**

**Задание:**
1. Перечислите порты, используемые SMB/CIFS.
2. Перечислите порты, используемые AD (DNS, Kerberos, LDAP).
3. Определите, какие протоколы SMB включены.
4. Ограничьте минимальную версию SMB.
5. Объясните различия версий SMB 1/2/3.

**Решение и пояснения:**
```bash
# smb.conf: server min protocol = SMB2_10
sudo systemctl restart smbd
testparm -sv | grep -i "protocol"
```
**Пояснения:**
SMB/CIFS: 445 (SMB), 139 (NetBIOS). AD использует DNS (53), Kerberos (88), LDAP (389/636), NTP (123), RPC (135). SMB1 устарел и небезопасен; SMB2/3 быстрее и безопаснее (шифрование, подписи).

---

**Практическая работа №3: Режимы работы и роли сервера**

**Задание:**
1. Посмотрите текущую роль сервера.
2. Перечислите возможные роли Samba.
3. Измените роль на standalone.
4. Проверьте режим безопасности.
5. Объясните, чем `server role` отличается от `security`.

**Решение и пояснения:**
```bash
testparm -sv | grep -E "server role|security"
# smb.conf: server role = standalone server ; security = user
sudo systemctl restart smbd
smbclient -L localhost -N
```
**Пояснения:**
`server role` задаёт архитектурную роль (`standalone`, `member server`, `classic primary domain controller`, `active directory domain controller`). `security` — способ аутентификации (`user`, `ads`, `domain`). В Samba 4 роль AD DC сама определяет security.

---

**Практическая работа №4: VFS-модули и кластеризация (awareness)**

**Задание:**
1. Посмотрите доступные VFS-модули.
2. Подключите модуль аудита.
3. Проверьте применение модуля.
4. Опишите назначение CTDB.
5. Объясните, зачем Samba VFS.

**Решение и пояснения:**
```bash
ls /usr/lib/x86_64-linux-gnu/samba/vfs/ | head
# smb.conf в ресурсе: vfs objects = full_audit
testparm -sv | grep -i "vfs objects"
```
**Пояснения:**
VFS-модули расширяют функции Samba (аудит, снапшоты, карантин, антивирус). `full_audit` логирует доступ к файлам. CTDB обеспечивает кластеризацию и высокую доступность Samba/AD на нескольких узлах.
