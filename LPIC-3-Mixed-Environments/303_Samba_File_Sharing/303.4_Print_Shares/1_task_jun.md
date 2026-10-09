[Оглавление](?file=LPIC-3-Mixed-Environments%2Fhome.md)

**Практическая работа №1: Печать в Samba и CUPS**

**Задание:**
1. Установите CUPS и Samba.
2. Включите поддержку печати в Samba.
3. Проверьте интеграцию с CUPS.
4. Посмотрите ресурсы печати.
5. Объясните поток печати.

**Решение и пояснения:**
```bash
sudo apt install -y cups samba
# smb.conf global: printing = cups ; printcap name = cups ; load printers = yes
sudo systemctl restart smbd cups
smbclient -L localhost -N | grep -i print
```
**Пояснения:**
Samba интегрируется с CUPS для печати: Windows-клиенты печатают через SMB, задание передаётся в CUPS. `printing = cups` задаёт систему печати, `load printers = yes` публикует принтеры.

---

**Практическая работа №2: Ресурс печати**

**Задание:**
1. Настройте ресурс `[printers]`.
2. Настройте ресурс `[print$]` для драйверов.
3. Проверьте доступ к ресурсу печати.
4. Отправьте задание на печать через SMB.
5. Объясните назначение `[print$]`.

**Решение и пояснения:**
```bash
# smb.conf:
# [printers] comment=All Printers path=/var/spool/samba printable=yes browseable=no
# [print$] path=/var/lib/samba/printers browseable=yes read only=yes
sudo systemctl reload smbd
smbclient //localhost/printers -U user1 -c "print /tmp/file.txt"
```
**Пояснения:**
`[printers]` — динамический ресурс для всех принтеров CUPS. `[print$]` хранит драйверы Windows. `printable = yes` делает ресурс принтером. Задания буферизуются в `/var/spool/samba/`.

---

**Практическая работа №3: Драйверы печати Windows**

**Задание:**
1. Опишите загрузку драйверов через «Add Print Driver Wizard».
2. Настройте архитектуру драйверов.
3. Проверьте список драйверов через `rpcclient`.
4. Задайте принтер по умолчанию.
5. Объясните необходимость драйверов.

**Решение и пояснения:**
```bash
# smb.conf: [print$] path=/var/lib/samba/printers write list=@admins
# spoolss: architecture = Windows x64
rpcclient -U administrator%pass //localhost -c "enumdrivers"
rpcclient -U administrator%pass //localhost -c "enumprinters"
```
**Пояснения:**
Windows-клиентам нужны драйверы принтера. Их загружают в `[print$]` (через мастер или `rpcclient`/`net`). `spoolss: architecture` задаёт целевую архитектуру. Это позволяет автоматическую установку драйверов у клиентов.

---

**Практическая работа №4: Диагностика печати**

**Задание:**
1. Проверьте очередь печати CUPS.
2. Посмотрите журнал Samba по печати.
3. Проверьте права `SePrintOperatorPrivilege`.
4. Управляйте заданиями через `rpcclient`.
5. Объясните типовые проблемы.

**Решение и пояснения:**
```bash
lpstat -o
sudo grep -i print /var/log/samba/log.smbd | tail
rpcclient -U admin%pass //localhost -c "enumjobs"
rpcclient -U admin%pass //localhost -c "setdriver" 2>/dev/null
```
**Пояснения:**
Печать диагностируют через CUPS (`lpstat`, `/var/log/cups/`) и логи Samba. Право `SePrintOperatorPrivilege` позволяет управлять драйверами/очередью. Типовые проблемы: неверные драйверы, права на `[print$]`, недоступность CUPS, `spoolssd`.
