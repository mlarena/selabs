[Оглавление](LPIC-3-Mixed-Environments/home.md)

# Экзаменационные боевые задачи — Тема 304: Samba Client Configuration

Задачи приближены к реальным заданиям экзамена **300-300**.

## Задача 1. Аутентификация Linux-клиента в AD

**Условие:** Настройте SSSD для входа AD-пользователей на Linux-клиенте.

**Ожидаемый результат:** AD-пользователь входит в систему.

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
SSSD обеспечивает аутентификацию и кэширование для AD/LDAP/Kerberos. `sssd.conf` (права 600) задаёт домен. SSSD позволяет офлайн-вход.

## Задача 2. Монтирование CIFS-ресурса

**Условие:** Смонтируйте ресурс и настройте автомонтирование при входе пользователя.

**Ожидаемый результат:** Ресурс монтируется автоматически.

**Решение и пояснения:**
```bash
sudo apt install -y cifs-utils libpam-mount
# /etc/security/pam_mount.conf.xml:
# <volume user="*" fstype="cifs" server="server"
#   path="homes/%(USER)" mountpoint="~/smbhome" />
sudo systemctl restart sssd
ls ~/smbhome
```
`pam_mount` монтирует ресурсы при входе и размонтирует при выходе, используя учётные данные пользователя. Удобно для домашних каталогов и профилей в смешанной среде.

## Задача 3. Доступ к Windows-ресурсам

**Условие:** Подключитесь к Windows-ресурсу, скачайте файл и посмотрите ACL.

**Ожидаемый результат:** Доступ выполнен, ACL получен.

**Решение и пояснения:**
```bash
smbclient -L //winserver -U 'LAB\user1'
smbclient //winserver/docs -U 'LAB\user1' -c "ls; get file.txt"
smbget smb://winserver/docs/file.txt
getcifsacl /mnt/cifs/file.txt
smbcquotas -L //winserver/docs -U 'LAB\user1'
```
`smbclient` — интерактивный клиент, `smbget` — скачивание, `getcifsacl`/`smbcquotas` — ACL и квоты. Домен в имени пользователя (`LAB\user1`) указывает на AD-аутентификацию.

## Задача 4. Присоединение Windows-клиента (концептуально)

**Условие:** Опишите шаги присоединения Windows к Samba AD и доступ к ресурсам.

**Ожидаемый результат:** Продемонстрировано понимание процесса.

**Решение и пояснения:**
```text
1. DNS Windows -> IP AD DC
2. Параметры -> Система -> Присоединение к домену (LAB.LOCAL)
3. Учётные данные администратора домена
4. Проверка на DC: samba-tool computer list
5. Доступ: net use Z: \\server\docs /persistent:yes
6. Принтер: net use LPT1: \\server\printer
```
Windows присоединяется к AD при корректном DNS. В AD создаётся объект компьютера. Ресурсы доступны по UNC или сопоставленным дискам. Действуют доменные GPO.

## Задача 5. Диагностика членства и Kerberos

**Условие:** Пользователь не может войти с AD-учётной записью. Найдите причину.

**Ожидаемый результат:** Причина найдена.

**Решение и пояснения:**
```bash
wbinfo -t
wbinfo --domain-info=LAB
klist
kinit user1@LAB.LOCAL
getent passwd user1@lab.local
sudo journalctl -u sssd -n 50
```
Проверяют: доверие (`wbinfo -t`), билеты (`klist`), разрешение (`getent`), журналы SSSD. Типовые причины: рассинхронизация времени, неверный DNS, ошибки ID mapping, отсутствие `sssd`.

## Задача 6. Профили и перенаправление папок

**Условие:** Настройте перемещаемые профили и перенаправление папок для Windows-клиентов.

**Ожидаемый результат:** Профили хранятся на сервере.

**Решение и пояснения:**
```text
# smb.conf: logon path = \\%L\profiles\%U
#            logon home = \\%L\%U
# GPO: перенаправление Documents на \\server\users\%username%
# Проверка: gpupdate /force на клиенте
```
Перемещаемые профили доступны с любой машины, но замедляют вход. Перенаправление папок переносит только данные. Настройки задаются в GPO и `smb.conf`.
