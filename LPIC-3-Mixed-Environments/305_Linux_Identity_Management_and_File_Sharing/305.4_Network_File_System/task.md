[Оглавление](LPIC-3-Mixed-Environmentshome.md)

**Практическая работа №1: Настройка NFSv4**

**Задание:**
1. Установите NFSv4-сервер.
2. Создайте псевдо-корень.
3. Настройте экспорт NFSv4.
4. Смонтируйте с клиента.
5. Проверьте работу.

**Решение и пояснения:**
```bash
sudo apt install -y nfs-kernel-server
sudo mkdir -p /srv/nfs4/data
# /etc/exports:
# /srv/nfs4 *(ro,fsid=0)          # псевдо-корень
# /srv/nfs4/data 192.168.1.0/24(rw,sync)
sudo exportfs -ra
# Клиент:
sudo mount -t nfs4 server:/data /mnt/nfs4
```
**Пояснения:**
NFSv4 использует единый псевдо-корень (`fsid=0`) вместо множества экспортов. Клиент монтирует `server:/path`. NFSv4 работает через один порт (2049) и поддерживает ACL и Kerberos.

---

**Практическая работа №2: ID mapping в NFSv4**

**Задание:**
1. Посмотрите конфигурацию `idmapd`.
2. Настройте домен для сопоставления.
3. Проверьте сопоставление `user@domain`.
4. Проверьте права файлов.
5. Объясните назначение ID mapping.

**Решение и пояснения:**
```bash
cat /etc/idmapd.conf
# [General] Domain = lab.local
# [Mapping] Nobody-User = nobody
sudo systemctl restart nfs-idmapd
idmapd 2>/dev/null; nfsidmap -l
```
**Пояснения:**
NFSv4 передаёт идентификаторы в виде `user@domain`. `idmapd` сопоставляет их с локальными UID/GID. Правильный домен критичен для корректных прав; иначе владельцы отображаются как `nobody`.

---

**Практическая работа №3: NFSv4 ACL**

**Задание:**
1. Создайте файл на NFSv4-ресурсе.
2. Посмотрите ACL.
3. Установите ACL для пользователя.
4. Проверьте ACL.
5. Объясните отличия NFSv4 ACL от POSIX ACL.

**Решение и пояснения:**
```bash
nfs4_getfacl /mnt/nfs4/data/file.txt
nfs4_setfacl -a A::user1@lab.local:rxtncy /mnt/nfs4/data/file.txt
nfs4_getfacl /mnt/nfs4/data/file.txt
```
**Пояснения:**
NFSv4 ACL ближе к Windows-ACL: поддерживают наследование, deny-правила и тонкие права (`r`, `w`, `x`, `d`, `a` и др.). Инструменты: `nfs4_getfacl`, `nfs4_setfacl`, `nfs4_editfacl`.

---

**Практическая работа №4: Kerberos для NFSv4**

**Задание:**
1. Настройте `sec=krb5` в экспорте.
2. Получите билет на клиенте.
3. Смонтируйте с Kerberos.
4. Проверьте доступ по билету.
5. Объясните варианты sec.

**Решение и пояснения:**
```bash
# /etc/exports: /srv/nfs4/data *(rw,sync,sec=krb5)
sudo exportfs -ra
kinit user1@LAB.LOCAL
sudo mount -t nfs4 -o sec=krb5 server:/data /mnt/nfs4
klist
```
**Пояснения:**
`sec=krb5` требует Kerberos-аутентификацию; `krb5i` добавляет целостность, `krb5p` — шифрование. Это защищает NFS от подмены и прослушивания. Требуется корректный Kerberos (SSSD/FreeIPA/AD).
