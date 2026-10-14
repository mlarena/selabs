import os, glob, sys

BASE = r"C:\_selabs\selabs"

# Content for task 5 in LPIC-3-Mixed-Environments
TASKS_MIXED = {
    "301_Samba_Basics/301.1_Samba_Concepts/task.md": """
---

**Практическая работа №5: Диагностика и мониторинг Samba**

**Задание:**
1. Запустите `smbclient -L localhost -U%` и проанализируйте вывод.
2. Используйте `testparm -sv` для проверки всей конфигурации.
3. Проверьте открытые порты: `ss -tlnp | grep -E '445|139'`.
4. Посмотрите активные подключения: `smbstatus`.
5. Составьте отчёт о состоянии сервера.

**Решение и пояснения:**
```bash
smbclient -L localhost -U%
testparm -sv 2>&1 | grep -E "server role|security|interfaces"
ss -tlnp | grep -E "445|139"
smbstatus
```
**Пояснения:**
`testparm -sv` показывает ВСЕ параметры. `smbstatus` выводит PID, UID, IP клиентов, открытые файлы.
""",
    "301_Samba_Basics/301.2_Samba_Configuration/task.md": """
---

**Практическая работа №5: Безопасность через include-файлы**

**Задание:**
1. Создайте `/etc/samba/conf.d/security.conf`.
2. Подключите через `include = /etc/samba/conf.d/security.conf`.
3. Задайте `restrict anonymous = 2`, `server min protocol = SMB3_11`.
4. Проверьте конфигурацию и примените.

**Решение и пояснения:**
```bash
sudo mkdir -p /etc/samba/conf.d
sudo tee /etc/samba/conf.d/security.conf <<'EOF'
restrict anonymous = 2
map to guest = never
server min protocol = SMB3_11
server signing = required
EOF
testparm -sv | grep -E "restrict anonymous|server min protocol"
sudo systemctl restart smbd
```
**Пояснения:**
`include` позволяет модульно управлять конфигурацией. `restrict anonymous = 2` запрещает анонимный доступ.
""",
    "301_Samba_Basics/301.3_Samba_Maintenance/task.md": """
---

**Практическая работа №5: Автоматизация обслуживания**

**Задание:**
1. Напишите скрипт резервного копирования `smb.conf` и TDB-файлов.
2. Настройте cron-задачу на ежедневное выполнение в 02:00.
3. Настройте ротацию логов через logrotate.
4. Проверьте работу скрипта.

**Решение и пояснения:**
```bash
sudo tee /usr/local/bin/samba_backup.sh <<'SCRIPT'
#!/bin/bash
BACKUP_DIR="/var/backups/samba/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"
cp /etc/samba/smb.conf "$BACKUP_DIR/"
cp /var/lib/samba/*.tdb "$BACKUP_DIR/" 2>/dev/null
find /var/backups/samba -maxdepth 1 -mtime +7 -exec rm -rf {} \\;
SCRIPT
sudo chmod +x /usr/local/bin/samba_backup.sh
# crontab -e: 0 2 * * * /usr/local/bin/samba_backup.sh
```
**Пояснения:**
Резервное копирование TDB-файлов критично для AD DC.
""",
    "301_Samba_Basics/301.4_Troubleshooting_Samba/task.md": """
---

**Практическая работа №5: Мониторинг производительности**

**Задание:**
1. Используйте `smbstatus -p` для просмотра процессов Samba.
2. Проверьте задержку SMB-запросов через `ss -ti`.
3. Проанализируйте нагрузку на диск.
4. Составьте рекомендации по оптимизации.

**Решение и пояснения:**
```bash
smbstatus -p
ss -ti dst :445
iostat -x 1 5
sudo perf top -p $(pgrep smbd | head -1)
```
**Пояснения:**
`smbstatus -p` показывает CPU-загрузку каждого процесса. `ss -ti` показывает RTT, retransmits.
""",
    "302_Samba_and_AD_Domains/302.1_AD_Domain_Controller/task.md": """
---

**Практическая работа №5: Восстановление AD DC из бэкапа**

**Задание:**
1. Остановите службы Samba AD DC.
2. Проверьте целостность базы `samba-tool dbcheck`.
3. Восстановите из резервной копии.
4. Запустите службы и проверьте аутентификацию.
5. Синхронизируйте с другими DC.

**Решение и пояснения:**
```bash
sudo systemctl stop samba-ad-dc
sudo cp /var/lib/samba/private/sam.ldb /var/lib/samba/private/sam.ldb.bak
sudo samba-tool dbcheck --cross-ncs
sudo samba-tool domain backup restore --file=/var/backups/ad-2024-01-01.tar.bz2 --target-dir=/var/lib/samba/private/
sudo systemctl start samba-ad-dc
kinit administrator@LAB.EXAMPLE.COM && klist
samba-tool drs showrepl
```
**Пояснения:**
`samba-tool dbcheck` находит и исправляет повреждения в LDAP-базе AD.
""",
    "302_Samba_and_AD_Domains/302.2_AD_Name_Resolution/task.md": """
---

**Практическая работа №5: DNS-форвардинг и DNSSEC**

**Задание:**
1. Настройте DNS-форвардинг на `8.8.8.8`.
2. Настройте обратную зону для подсети AD.
3. Проверьте рекурсивные запросы через `dig`.
4. Включите DNSSEC валидацию.

**Решение и пояснения:**
```bash
# /etc/samba/smb.conf [global]: dns forwarder = 8.8.8.8
sudo systemctl restart samba-ad-dc
dig @localhost external.lab A +short
dig @localhost -x 192.168.1.10 +short
delv lab.example.com A +cd
```
**Пояснения:**
`dns forwarder` перенаправляет внешние запросы. `delv` валидирует DNSSEC-цепочки.
""",
    "302_Samba_and_AD_Domains/302.3_AD_User_Management/task.md": """
---

**Практическая работа №5: Массовое управление пользователями AD**

**Задание:**
1. Создайте пользователей из CSV через `samba-tool user create`.
2. Добавьте в группу через `samba-tool group addmembers`.
3. Установите срок действия пароля 90 дней.
4. Экспортируйте список пользователей.

**Решение и пояснения:**
```bash
while IFS=, read -r user pass name; do
    samba-tool user create "$user" "$pass" --given-name="$name"
done < users.csv
samba-tool group addmembers Developers "$(awk -F, '{print $1}' users.csv | paste -sd,)"
samba-tool domain passwordsettings set --max-password-age=90
samba-tool user list > users_list.txt
```
**Пояснения:**
`samba-tool` позволяет скриптовать все операции AD.
""",
    "302_Samba_and_AD_Domains/302.4_Domain_Membership/task.md": """
---

**Практическая работа №5: Настройка gMSA**

**Задание:**
1. На клиенте настройте sssd для работы с gMSA.
2. Настройте службу для использования gMSA.
3. Проверьте автоматическую ротацию пароля.

**Решение и пояснения:**
```bash
sudo apt install -y libnss-sss libpam-sss adcli realmd
sudo realm join LAB.EXAMPLE.COM -U administrator
sudo systemctl restart sssd
id sqlsvc@lab.example.com
```
**Пояснения:**
gMSA — учётная запись службы с автоматически ротируемым паролем в AD.
""",
    "302_Samba_and_AD_Domains/302.5_Local_User_Management/task.md": """
---

**Практическая работа №5: Аудит неактивных пользователей**

**Задание:**
1. Найдите неактивные пользователи (>90 дней без входа).
2. Экспортируйте отчёт.
3. Автоматически отключите неактивные аккаунты.

**Решение и пояснения:**
```bash
samba-tool user list | while read -r u; do
    last=$(samba-tool user show "$u" 2>/dev/null | grep -i lastLogon | awk '{print $2}')
    if [ -z "$last" ] || [ "$last" = "1601" ]; then
        echo "INACTIVE: $u"
    fi
done > inactive_users.txt
for u in $(cat inactive_users.txt); do
    samba-tool user disable "$u"
done
```
**Пояснения:**
`lastLogon` хранится как Windows FILETIME. Значение `1601` означает «никогда не входил».
""",
    "303_Samba_File_Sharing/303.1_CIFS_File_Shares/task.md": """
---

**Практическая работа №5: Аудит доступа к CIFS-ресурсам**

**Задание:**
1. Включите `full_audit` VFS-модуль для ресурса `data`.
2. Смоделируйте действия пользователей и проверьте логи.
3. Настройте алерт при массовом удалении файлов.

**Решение и пояснения:**
```bash
# smb.conf в [data]:
# vfs objects = full_audit
# full_audit:prefix = "AUDIT|%U|%I|%m"
# full_audit:success = open write unlink rename mkdir rmdir
# full_audit:facility = local7
sudo journalctl -t AUDIT --since "5 min ago"
grep -c "unlink" /var/log/samba/log.smbd | awk '$1>50 {print "ALERT: mass delete"}'
```
**Пояснения:**
`full_audit` логирует операции с файлами: кто, откуда, что сделал.
""",
    "303_Samba_File_Sharing/303.2_Permissions_and_ACLs/task.md": """
---

**Практическая работа №5: Скрипт массового управления ACL**

**Задание:**
1. Напишите скрипт применения стандартного набора ACL.
2. Установите default ACL для наследования.
3. Проверьте результат через `getfacl`.

**Решение и пояснения:**
```bash
sudo tee /usr/local/bin/set_acl.sh <<'SCRIPT'
#!/bin/bash
DIR="$1"
chmod 750 "$DIR"
setfacl -m u::rwx,g::rx,o::--- "$DIR"
setfacl -m u:audit:rx "$DIR"
setfacl -d -m u::rwx,g::rx,o::--- "$DIR"
getfacl "$DIR"
SCRIPT
sudo chmod +x /usr/local/bin/set_acl.sh
sudo /usr/local/bin/set_acl.sh /srv/samba/projects
```
**Пояснения:**
`setfacl -m` устанавливает ACL, `-d` — default ACL (наследуется новыми файлами).
""",
    "303_Samba_File_Sharing/303.3_DFS_Shares/task.md": """
---

**Практическая работа №5: Проверка DFS-ссылок**

**Задание:**
1. Проверьте доступ через `smbclient`.
2. Протестируйте перенаправление при отказе сервера.

**Решение и пояснения:**
```bash
smbclient //dc1.lab.example.com/DFS -U user1%pass1 -c "ls"
smbclient //dc1.lab.example.com/DFS/Data -U user1%pass1 -c "ls"
```
**Пояснения:**
DFS предоставляет единое пространство имён для файлов на разных серверах.
""",
    "303_Samba_File_Sharing/303.4_Print_Shares/task.md": """
---

**Практическая работа №5: Мониторинг очереди печати**

**Задание:**
1. Просмотрите очередь через `lpstat`.
2. Проверьте логи CUPS при ошибке.
3. Настройте алерт при зависании очереди.

**Решение и пояснения:**
```bash
lpstat -t
lp -d printer1 -n 3 test.ps
sudo tail -50 /var/log/cups/error_log
lpstat -o | awk '$4=="processing-stopped" {print "STUCK:", $1}'
```
**Пояснения:**
`lpstat -t` показывает все очереди и задания.
""",
    "304_Samba_Client_Configuration/304.1_Authentication_Clients/task.md": """
---

**Практическая работа №5: Kerberos-конфигурация на клиенте**

**Задание:**
1. Настройте `/etc/krb5.conf` для домена LAB.EXAMPLE.COM.
2. Получите TGT через `kinit`.
3. Проверьте билет `klist`.

**Решение и пояснения:**
```bash
sudo tee /etc/krb5.conf <<'EOF'
[libdefaults]
    default_realm = LAB.EXAMPLE.COM
    dns_lookup_kdc = true
[realms]
    LAB.EXAMPLE.COM = {
        kdc = dc1.lab.example.com
    }
EOF
kinit user1@LAB.EXAMPLE.COM
klist
```
**Пояснения:**
`dns_lookup_kdc = true` позволяет находить KDC через DNS SRV-записи AD.
""",
    "304_Samba_Client_Configuration/304.2_CIFS_Clients/task.md": """
---

**Практическая работа №5: Mount CIFS с шифрованием**

**Задание:**
1. Смонтируйте CIFS-ресурс с `seal`.
2. Используйте `cred` файл.
3. Настройте `nofail` в fstab.

**Решение и пояснения:**
```bash
sudo tee /etc/samba/creds.txt <<'EOF'
username=user1
password=pass1
EOF
sudo chmod 600 /etc/samba/creds.txt
sudo mount -t cifs //dc1/lab /mnt/lab \\
  -o credentials=/etc/samba/creds.txt,seal,uid=1001,gid=1001,nofail
```
**Пояснения:**
`seal` включает шифрование SMB3 (AES-128-CCM).
""",
    "304_Samba_Client_Configuration/304.3_Windows_Clients/task.md": """
---

**Практическая работа №5: GPO для Windows-клиентов**

**Задание:**
1. Создайте GPO через `samba-tool gpo`.
2. Проверьте применение политики.

**Решение и пояснения:**
```bash
samba-tool gpo listall
samba-tool gpo create --name "MapDrive" --link "OU=Workstations,DC=lab,DC=example,DC=com"
samba-tool gpo show "MapDrive"
```
**Пояснения:**
GPO применяются через механизм SYSVOL/Netlogon.
""",
    "305_Linux_Identity_Management_and_File_Sharing/305.1_FreeIPA_Installation/task.md": """
---

**Практическая работа №5: Резервное копирование FreeIPA**

**Задание:**
1. Выполните дамп базы через `ipa-backup`.
2. Смоделируйте восстановление.
3. Настройте ежедневное резервное копирование.

**Решение и пояснения:**
```bash
sudo ipa-backup --ds-only
ls -la /var/lib/ipa/backup/
sudo ipa-restore /var/lib/ipa/backup/ipabkp2024-01-01.tar.gz --no-restore-ds
sudo ipactl status
# crontab: 0 3 * * * /usr/sbin/ipa-backup --quiet --no-logs
```
**Пояснения:**
`ipa-backup` создаёт полный дамп LDAP (DS) и KDC.
""",
    "305_Linux_Identity_Management_and_File_Sharing/305.2_FreeIPA_Entities/task.md": """
---

**Практическая работа №5: Правила sudo в FreeIPA**

**Задание:**
1. Создайте sudo-правило для группы `sysadmins`.
2. Ограничьте хостами из `production`.
3. Проверьте на клиенте.

**Решение и пояснения:**
```bash
ipa sudorule-add admins --desc="Full access for sysadmins"
ipa sudorule-add-option admins --sudooption '!authenticate'
ipa sudorule-add-user admins --groups=sysadmins
ipa sudorule-add-host admins --hostgroups=production
ipa sudorule-enable admins
sudo -l
```
**Пояснения:**
FreeIPA хранит sudo-правила в LDAP, клиенты получают их через sssd.
""",
    "305_Linux_Identity_Management_and_File_Sharing/305.3_FreeIPA_AD_Integration/task.md": """
---

**Практическая работа №5: Диагностика доверия FreeIPA и AD**

**Задание:**
1. Проверьте статус доверия через `ipa trust-show`.
2. Проверьте DNS SRV-записи.
3. Выполните `net rpc testjoin`.

**Решение и пояснения:**
```bash
ipa trust-show lab.example.com --all
dig +short _ldap._tcp.lab.example.com SRV
net rpc testjoin -S dc1.lab.example.com
sudo journalctl -u sssd --since "10 min ago" | grep -i "trust"
```
**Пояснения:**
DNS SRV-записи критичны для поиска KDC.
""",
    "305_Linux_Identity_Management_and_File_Sharing/305.4_Network_File_System/task.md": """
---

**Практическая работа №5: Мониторинг NFS**

**Задание:**
1. Просмотрите активные NFS-монтирования.
2. Проверьте экспорт через `showmount -e`.
3. Проанализируйте производительность через `nfsstat`.

**Решение и пояснения:**
```bash
mount -t nfs4 | grep -v "^proc"
showmount -e nfs-server.lab.example.com
nfsstat -s
nfsstat -c
```
**Пояснения:**
`nfsstat` показывает счётчики RPC и NFS-операций.
""",
}


def fix_file(filepath, base_path, tasks_dict):
    rel_path = os.path.relpath(filepath, base_path).replace("\\", "/")
    if rel_path not in tasks_dict:
        return False
    task5 = tasks_dict[rel_path]
    with open(filepath, encoding="utf-8-sig") as f:
        content = f.read()
    # Remove wrongly inserted task5 at beginning (before [Оглавление])
    # Pattern: starts with optional BOM, then ---, then task5 placeholder
    lines = content.split('\n')
    new_lines = []
    skip = False
    for i, line in enumerate(lines):
        if line.startswith('\ufeff') or line == '':
            if i == 0:
                continue  # skip BOM
        if 'Практическая работа №5' in line and 'Расширенное применение' in line:
            skip = True
            continue
        if skip:
            if line.strip() == '---' or (line.strip().startswith('**Практическая работа №') and '№1' in line):
                skip = False
                new_lines.append(line)
            continue
        new_lines.append(line)
    content = '\n'.join(new_lines)
    # Remove generic "## Задача 5" at end if present
    if '## Задача 5:' in content:
        idx = content.find('\n\n---\n\n## Задача 5:')
        if idx > 0:
            content = content[:idx]
    # Remove old task5 if present
    if 'Практическая работа №5:' in content and 'Расширенное применение' not in content:
        # Already has a proper task5, skip
        return False
    if 'Практическая работа №5:' in content and 'Расширенное применение' in content:
        # Remove old placeholder
        idx = content.find('\n\n---\n\n**Практическая работа №5:')
        if idx > 0:
            content = content[:idx]
    # Add proper task5 before [Оглавление] if present, else at end
    if '[Оглавление]' in content:
        content = content.replace('[Оглавление]', task5 + '\n[Оглавление]', 1)
    else:
        content = content.rstrip() + task5
    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(content)
    return True


def main():
    mixed_base = os.path.join(BASE, "LPIC-3-Mixed-Environments")
    changed = 0
    for dirpath, _, filenames in os.walk(mixed_base):
        for fn in filenames:
            if fn == "task.md":
                fp = os.path.join(dirpath, fn)
                if fix_file(fp, mixed_base, TASKS_MIXED):
                    changed += 1
                    print(f"OK  {os.path.relpath(fp, BASE)}")
    print(f"Total: {changed} files fixed")


if __name__ == "__main__":
    main()