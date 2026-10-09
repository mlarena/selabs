[Оглавление](LPIC-3-Mixed-Environments/home.md)

# Экзаменационные боевые задачи — Тема 305: Linux Identity Management and File Sharing

Задачи приближены к реальным заданиям экзамена **300-300**.

## Задача 1. Установка FreeIPA

**Условие:** Разверните сервер FreeIPA с DNS и проверьте службы.

**Ожидаемый результат:** FreeIPA работает, admin входит.

**Решение и пояснения:**
```bash
sudo apt install -y freeipa-server
sudo hostnamectl set-hostname ipa.lab.local
sudo ipa-server-install --domain=lab.local --realm=LAB.LOCAL \
  --ds-password='DirPass1!' --admin-password='AdminPass1!' --setup-dns --forwarder=8.8.8.8
sudo ipactl status
kinit admin
```
FreeIPA объединяет LDAP, Kerberos, DNS, CA, SSSD. `ipa-server-install` разворачивает сервер, `ipactl` управляет службами. Требуется FQDN и точное время.

## Задача 2. Управление сущностями FreeIPA

**Условие:** Создайте пользователя, группу, хост и сервис с keytab.

**Ожидаемый результат:** Сущности созданы.

**Решение и пояснения:**
```bash
kinit admin
ipa user-add user1 --first=User --last=One --password
ipa group-add devs && ipa group-add-member devs --users=user1
ipa host-add client2.lab.local --ip-address=192.168.1.60
ipa service-add HTTP/client2.lab.local
ipa-getkeytab -p HTTP/client2.lab.local -k /tmp/http.keytab
klist -k /tmp/http.keytab
```
`ipa user/group/host/service` управляют объектами. Keytab содержит ключи сервиса для Kerberos-аутентификации. HBAC и sudo-правила централизуют доступ.

## Задача 3. Присоединение клиента к FreeIPA

**Условие:** Присоедините Linux-клиент к FreeIPA и проверьте вход.

**Ожидаемый результат:** Клиент в домене, вход работает.

**Решение и пояснения:**
```bash
sudo apt install -y freeipa-client
sudo ipa-client-install --domain=lab.local --server=ipa.lab.local --mkhomedir
getent passwd admin
su - admin
```
`ipa-client-install` настраивает Kerberos, SSSD, NSS/PAM, DNS. Клиент входит в домен и получает единый вход. `--mkhomedir` создаёт домашние каталоги.

## Задача 4. Доверие FreeIPA с AD

**Условие:** Настройте cross-forest trust между FreeIPA и AD.

**Ожидаемый результат:** Пользователи AD имеют доступ к Linux.

**Решение и пояснения:**
```bash
sudo apt install -y freeipa-server-trust-ad
sudo ipa-adtrust-install --admin-password='AdminPass1!'
ipa trust-add ad.local --type=ad --admin=Administrator --password
ipa trust-show ad.local
ipa trust-fetch-domains ad.local
```
Cross-forest trust позволяет AD и FreeIPA сосуществовать, обеспечивая доступ через Kerberos. `trust-add` создаёт доверие, `trust-fetch-domains` подтягивает домены. PAC передаёт группы/SID.

## Задача 5. Настройка NFSv4

**Условие:** Настройте NFSv4 с псевдо-корнем и смонтируйте на клиенте.

**Ожидаемый результат:** NFSv4-ресурс доступен.

**Решение и пояснения:**
```bash
sudo apt install -y nfs-kernel-server
sudo mkdir -p /srv/nfs4/data
# /etc/exports:
# /srv/nfs4 *(ro,fsid=0)
# /srv/nfs4/data 192.168.1.0/24(rw,sync)
sudo exportfs -ra
# Клиент:
sudo mount -t nfs4 server:/data /mnt/nfs4
```
NFSv4 использует единый псевдо-корень (`fsid=0`) и один порт (2049). Поддерживает ACL и Kerberos. Клиент монтирует `server:/path`.

## Задача 6. Резервное копирование FreeIPA

**Условие:** Сделайте резервную копию FreeIPA и опишите восстановление.

**Ожидаемый результат:** Бэкап создан.

**Решение и пояснения:**
```bash
sudo ipa-backup
ls -lh /var/lib/ipa/backup/
sudo ipa-backup --data --online
# Восстановление: sudo ipa-restore <backup_dir>
```
`ipa-backup` создаёт копии конфигурации, данных LDAP и CA. Бэкап CA критичен для сертификатов. Восстановление — `ipa-restore`. Регулярные бэкапы обязательны.
