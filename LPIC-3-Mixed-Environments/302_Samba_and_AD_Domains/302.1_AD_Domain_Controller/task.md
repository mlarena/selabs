[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Подготовка и установка AD DC**

**Задание:**
1. Установите пакет `samba` (AD DC).
2. Остановите конфликтующие службы.
3. Проверьте разрешение имени хоста.
4. Создайте новый домен AD.
5. Проверьте состояние домена.

**Решение и пояснения:**
```bash
sudo apt install -y samba smbclient winbind krb5-user
sudo systemctl stop smbd nmbd winbind
sudo systemctl disable smbd nmbd winbind
hostname -f                                   # 3. FQDN должен разрешаться
sudo samba-tool domain provision --use-rfc2307 --realm=LAB.LOCAL \
  --domain=LAB --adminpass='Passw0rd!' --server-role=dc
sudo systemctl enable --now samba-ad-dc
sudo samba-tool domain level show              # 5. Уровень домена
```
**Пояснения:**
Samba AD DC создаётся командой `domain provision`. Требуется корректный FQDN, разрешаемый DNS, и пароль администратора. Служба — `samba-ad-dc`. Домен получает DNS, Kerberos, LDAP и SYSVOL.

---

**Практическая работа №2: Присоединение второго DC и репликация**

**Задание:**
1. Подготовьте второй сервер.
2. Присоедините его как дополнительный DC.
3. Проверьте репликацию.
4. Посмотрите список DC.
5. Объясните назначение нескольких DC.

**Решение и пояснения:**
```bash
# На втором сервере:
sudo samba-tool domain join LAB.LOCAL DC -U administrator --password='Passw0rd!'
sudo samba-tool drs showrepl                 # 3. Репликация
sudo samba-tool domain demote                # Понижение (при необходимости)
```
**Пояснения:**
Несколько DC обеспечивают отказоустойчивость и распределение нагрузки. `domain join ... DC` присоединяет реплику, `drs showrepl` показывает репликацию, `domain demote` понижает DC перед удалением.

---

**Практическая работа №3: FSMO-роли и сайты**

**Задание:**
1. Посмотрите владельцев FSMO-ролей.
2. Передайте FSMO-роль другому DC.
3. Посмотрите список сайтов.
4. Создайте сайт и подсеть.
5. Объясните влияние FSMO на отказоустойчивость.

**Решение и пояснения:**
```bash
sudo samba-tool fsmo show                    # 1. Владельцы ролей
sudo samba-tool fsmo transfer --role=rid --url=ldap://dc2.lab   # 2. Передача
sudo samba-tool sites list                   # 3. Сайты
sudo samba-tool sites create Site2
sudo samba-tool sites subnet create Site2 192.168.2.0/24
```
**Пояснения:**
FSMO-роли (Schema Master, Domain Naming, RID, PDC Emulator, Infrastructure) — уникальные операции. При отказе владельца роли возникают проблемы, поэтому роли можно передавать/захватывать. Сайты описывают топологию сети для репликации.

---

**Практическая работа №4: Уровни домена, доверия и SYSVOL**

**Задание:**
1. Посмотрите функциональные уровни домена и леса.
2. Повысьте функциональный уровень.
3. Настройте доверие между доменами (концептуально).
4. Проверьте SYSVOL.
5. Объясните назначение SYSVOL.

**Решение и пояснения:**
```bash
sudo samba-tool domain level show
sudo samba-tool domain level raise --domain-level=2008_R2 --forest-level=2008_R2
sudo samba-tool domain trust create OTHER.LOCAL --type=external
ls /var/lib/samba/sysvol/
```
**Пояснения:**
Функциональные уровни определяют доступные возможности AD. Доверия (trust) связывают домены/леса для аутентификации. SYSVOL (`/var/lib/samba/sysvol`) хранит GPO и скрипты, реплицируемые между DC.
