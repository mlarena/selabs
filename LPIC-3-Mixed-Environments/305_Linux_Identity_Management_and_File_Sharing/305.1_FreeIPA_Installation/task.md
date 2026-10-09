[Оглавление](?file=LPIC-3-Mixed-Environments%2Fhome.md)

**Практическая работа №1: Установка FreeIPA-сервера**

**Задание:**
1. Подготовьте хост (FQDN, время, DNS).
2. Установите пакеты FreeIPA.
3. Запустите `ipa-server-install`.
4. Проверьте работу служб.
5. Войдите как admin.

**Решение и пояснения:**
```bash
sudo apt install -y freeipa-server
sudo hostnamectl set-hostname ipa.lab.local
sudo ipa-server-install --domain=lab.local --realm=LAB.LOCAL \
  --ds-password='DirPass1!' --admin-password='AdminPass1!' --setup-dns --forwarder=8.8.8.8
sudo ipactl status                       # 4. Статус служб
kinit admin                              # 5. Вход
```
**Пояснения:**
FreeIPA объединяет LDAP (389 DS), Kerberos, DNS, CA, SSSD. `ipa-server-install` разворачивает сервер. `ipactl` управляет всеми службами. Требуется корректный FQDN и синхронизация времени.

---

**Практическая работа №2: Репликация FreeIPA**

**Задание:**
1. Опишите топологию репликации.
2. Установите реплику.
3. Проверьте состояние репликации.
4. Проверьте отказоустойчивость.
5. Объясните назначение нескольких серверов.

**Решение и пояснения:**
```bash
sudo ipa-replica-install --setup-ca --setup-dns
ipa topologysegment-find realm     # 3. Топология
ipa-replica-manage list            # 3. Список реплик
ipa-replica-manage status ipa2.lab.local
```
**Пояснения:**
FreeIPA реплицирует данные (LDAP, Kerberos, CA, DNS) между серверами. Топология (ring) определяет связи. Репликация обеспечивает отказоустойчивость и распределение нагрузки.

---

**Практическая работа №3: Присоединение клиента к FreeIPA**

**Задание:**
1. Установите клиент FreeIPA.
2. Присоедините клиент к домену.
3. Проверьте разрешение пользователей.
4. Проверьте вход пользователя.
5. Объясните, что настраивает ipa-client-install.

**Решение и пояснения:**
```bash
sudo apt install -y freeipa-client
sudo ipa-client-install --domain=lab.local --server=ipa.lab.local --mkhomedir
getent passwd admin                     # 3. Проверка
su - admin                              # 4. Вход
```
**Пояснения:**
`ipa-client-install` настраивает Kerberos, SSSD, NSS/PAM, сертификаты и DNS. Клиент входит в домен и получает единый вход. `--mkhomedir` создаёт домашние каталоги.

---

**Практическая работа №4: Резервное копирование FreeIPA**

**Задание:**
1. Создайте резервную копию FreeIPA.
2. Посмотрите созданный архив.
3. Опишите стратегию восстановления.
4. Проверьте целостность.
5. Объясните важность бэкапа CA.

**Решение и пояснения:**
```bash
sudo ipa-backup                          # 1. Бэкап
ls -lh /var/lib/ipa/backup/
sudo ipa-backup --data --online
```
**Пояснения:**
`ipa-backup` создаёт резервные копии конфигурации, данных LDAP и CA. Бэкап CA критичен: без него нельзя выпускать/проверять сертификаты. Восстановление — `ipa-restore`. Регулярные бэкапы обязательны.
