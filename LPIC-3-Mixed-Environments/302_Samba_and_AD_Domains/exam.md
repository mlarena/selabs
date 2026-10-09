[Оглавление](?file=LPIC-3-Mixed-Environments%2Fhome.md)

# Экзаменационные боевые задачи — Тема 302: Samba and Active Directory Domains

Задачи приближены к реальным заданиям экзамена **300-300**.

## Задача 1. Создание домена AD

**Условие:** Разверните новый домен Samba AD с DNS и проверьте его состояние.

**Ожидаемый результат:** Домен создан и работает.

**Решение и пояснения:**
```bash
sudo apt install -y samba smbclient winbind krb5-user
sudo systemctl stop smbd nmbd winbind && sudo systemctl disable smbd nmbd winbind
hostname -f
sudo samba-tool domain provision --use-rfc2307 --realm=LAB.LOCAL --domain=LAB \
  --adminpass='Passw0rd!' --server-role=dc
sudo systemctl enable --now samba-ad-dc
sudo samba-tool domain level show
```
`domain provision` создаёт домен (DNS, Kerberos, LDAP, SYSVOL). Требуется FQDN и разрешаемый DNS. Служба — `samba-ad-dc`. Проверка — `domain level show`.

## Задача 2. Настройка DNS домена

**Условие:** Добавьте A-запись в доменную зону и проверьте разрешение.

**Ожидаемый результат:** Имя разрешается.

**Решение и пояснения:**
```bash
sudo samba-tool dns add 127.0.0.1 lab.local host1 A 192.168.1.50
dig @127.0.0.1 host1.lab.local
dig @127.0.0.1 _ldap._tcp.lab.local SRV
# Форвардер: smb.conf: dns forwarder = 8.8.8.8
sudo systemctl restart samba-ad-dc
```
AD требует DNS с SRV-записями служб. `samba-tool dns` управляет зонами и записями. `dns forwarder` задаёт сервер для внешних имён. Клиенты должны использовать DNS DC.

## Задача 3. Управление пользователями AD

**Условие:** Создайте пользователя и группу, добавьте пользователя в группу, задайте политику паролей.

**Ожидаемый результат:** Пользователь и группа настроены.

**Решение и пояснения:**
```bash
sudo samba-tool user create user1 'Passw0rd!' --given-name=User --surname=One
sudo samba-tool group add devs
sudo samba-tool group addmembers devs user1
sudo samba-tool domain passwordsettings set --min-pwd-length=10 --complexity=on
sudo samba-tool user list
```
`samba-tool user`/`group` управляют объектами AD. Политика паролей задаётся `domain passwordsettings`. Пользователи хранятся в LDAP (`CN=Users`).

## Задача 4. Присоединение member server к домену

**Условие:** Присоедините Linux-сервер к AD как member server с winbind.

**Ожидаемый результат:** Сервер в домене, AD-пользователи видны.

**Решение и пояснения:**
```bash
# /etc/resolv.conf -> DNS DC
sudo apt install -y samba winbind libnss-winbind libpam-winbind krb5-user
sudo net ads join -U administrator
sudo net ads testjoin
# smb.conf: security=ads ; realm ; idmap config LAB : backend=rid
sudo systemctl restart smbd winbind
wbinfo -u ; wbinfo -t
```
`net ads join` присоединяет к домену (нужны DNS и точное время). winbind обеспечивает разрешение и аутентификацию AD-пользователей. `wbinfo` проверяет интеграцию.

## Задача 5. Настройка ID mapping и входа

**Условие:** Настройте сопоставление идентификаторов и вход AD-пользователя.

**Ожидаемый результат:** AD-пользователь входит в систему.

**Решение и пояснения:**
```bash
# smb.conf: idmap config LAB : backend = rid ; range = 10000-999999
# /etc/nsswitch.conf: passwd: files winbind
# /etc/pam.d/common-session: pam_mkhomedir.so
sudo systemctl restart winbind
getent passwd 'LAB\user1'
su - 'LAB\user1'
```
ID mapping сопоставляет SID AD с Unix UID/GID (backend `rid` детерминирован). NSS/PAM позволяют системе видеть и аутентифицировать AD-пользователей. `pam_mkhomedir` создаёт каталог.

## Задача 6. Репликация и FSMO

**Условие:** Присоедините второй DC и передайте ему FSMO-роль.

**Ожидаемый результат:** Репликация работает, роль передана.

**Решение и пояснения:**
```bash
# На втором сервере:
sudo samba-tool domain join LAB.LOCAL DC -U administrator --password='Passw0rd!'
sudo samba-tool drs showrepl
sudo samba-tool fsmo show
sudo samba-tool fsmo transfer --role=rid --url=ldap://dc2.lab.local
```
Несколько DC дают отказоустойчивость. `drs showrepl` показывает репликацию, `fsmo transfer` передаёт роль. FSMO-роли — уникальные операции домена.
