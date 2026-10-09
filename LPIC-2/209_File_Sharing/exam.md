[Оглавление](LPIC-2/home.md)

# Экзаменационные боевые задачи — Тема 209: File Sharing

Задачи приближены к реальным заданиям экзамена **202-450**.

## Задача 1. Настройка Samba-ресурса с аутентификацией

**Условие:** Настройте Samba-ресурс, доступный только членам группы, с правами на запись.

**Ожидаемый результат:** Ресурс доступен авторизованным пользователям.

**Решение и пояснения:**
```bash
sudo apt install -y samba
sudo mkdir -p /srv/samba/docs && sudo chown root:smbgroup /srv/samba/docs
sudo chmod 2770 /srv/samba/docs
# smb.conf:
# [docs] path=/srv/samba/docs valid users=@smbgroup read only=no
sudo useradd -M -s /usr/sbin/nologin smbuser
sudo smbpasswd -a smbuser
sudo testparm && sudo systemctl restart smbd
smbclient //localhost/docs -U smbuser
```
`valid users` ограничивает доступ, `read only = no` разрешает запись. Пользователей добавляют в базу Samba (`smbpasswd`). SGID на каталоге сохраняет группу новых файлов.

## Задача 2. Монтирование CIFS на клиенте

**Условие:** Смонтируйте Samba-ресурс на Linux-клиенте и настройте автомонтирование.

**Ожидаемый результат:** Ресурс смонтирован.

**Решение и пояснения:**
```bash
sudo apt install -y cifs-utils
sudo mkdir -p /mnt/smb
sudo tee /root/.smbcred >/dev/null <<'EOF'
username=smbuser
password=Passw0rd!
EOF
sudo chmod 600 /root/.smbcred
# fstab: //server/docs /mnt/smb cifs credentials=/root/.smbcred,uid=1000 0 0
sudo mount -a && findmnt /mnt/smb
```
`mount.cifs` монтирует SMB-ресурс. Учётные данные хранят в защищённом файле (`credentials=`). Опции `uid`/`gid` сопоставляют владельца для локальных пользователей.

## Задача 3. Настройка NFS-сервера

**Условие:** Экспортируйте каталог для подсети с ограничениями и смонтируйте на клиенте.

**Ожидаемый результат:** NFS-ресурс доступен.

**Решение и пояснения:**
```bash
sudo apt install -y nfs-kernel-server
sudo mkdir -p /srv/nfs/data
# /etc/exports: /srv/nfs/data 192.168.1.0/24(rw,sync,root_squash,no_subtree_check)
sudo exportfs -ra
sudo exportfs -v
# Клиент:
sudo mount -t nfs server:/srv/nfs/data /mnt/nfs
```
`/etc/exports` задаёт экспорты и опции. `exportfs -ra` применяет. `root_squash` сопоставляет root клиента `nobody` (безопасность). `sync` обеспечивает согласованность.

## Задача 4. NFSv4 с Kerberos

**Условие:** Настройте NFSv4 с аутентификацией Kerberos (`sec=krb5`).

**Ожидаемый результат:** Доступ по билету Kerberos.

**Решение и пояснения:**
```bash
# /etc/exports: /srv/nfs4 *(rw,sync,sec=krb5,fsid=0)
sudo exportfs -ra
kinit user1@LAB.LOCAL
sudo mount -t nfs4 -o sec=krb5 server:/data /mnt/nfs4
klist
```
`sec=krb5` требует Kerberos-аутентификацию, `krb5i` — целостность, `krb5p` — шифрование. NFSv4 использует псевдо-корень (`fsid=0`). Требуется корректный Kerberos (SSSD/FreeIPA/AD).

## Задача 5. Диагностика проблем файлового доступа

**Условие:** Пользователь не может открыть общий ресурс. Найдите причину.

**Ожидаемый результат:** Проблема найдена.

**Решение и пояснения:**
```bash
sudo smbstatus                       # Сессии и ресурсы Samba
sudo testparm -s
sudo tail /var/log/samba/log.smbd
showmount -e server                  # Экспорты NFS
rpcinfo -p server
getfacl /srv/samba/docs
```
Проверяют: конфигурацию (`testparm`), журналы, активные сессии (`smbstatus`), экспорты (`showmount`), права/ACL. Типовые причины: права на каталог, неверный `valid users`, firewall, отсутствие rpcbind.

## Задача 6. Ограничение и защита файловых ресурсов

**Условие:** Ограничьте доступ к Samba/NFS по хостам и настройте аудит доступа.

**Ожидаемый результат:** Доступ ограничен, аудит включён.

**Решение и пояснения:**
```bash
# smb.conf: [docs] hosts allow = 192.168.1.0/24
#   vfs objects = full_audit
#   full_audit:prefix = %u|%I|%S
sudo systemctl reload smbd
# NFS: /srv/nfs/data 192.168.1.10(rw,sync)
sudo exportfs -ra
sudo iptables -A INPUT -p tcp --dport 2049 -s 192.168.1.0/24 -j ACCEPT
```
`hosts allow` и ограничения в exports сокращают доступ. VFS `full_audit` логирует операции. Firewall дополнительно защищает порты SMB/NFS. Аудит доступа важен для расследований.
