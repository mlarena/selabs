[Оглавление](LPIC-3-Mixed-Environments/home.md)

**Практическая работа №1: Настройка доверия с AD**

**Задание:**
1. Установите компоненты доверия.
2. Настройте разрешение имён.
3. Установите доверие с AD.
4. Проверьте доверие.
5. Объясните назначение cross-forest trust.

**Решение и пояснения:**
```bash
sudo apt install -y freeipa-server-trust-ad
sudo ipa-adtrust-install --admin-password='AdminPass1!'
ipa trust-add ad.local --type=ad --admin=Administrator --password
ipa trust-show ad.local
```
**Пояснения:**
FreeIPA может доверять AD через Kerberos cross-realm trust. Пользователи AD получают доступ к ресурсам Linux. `ipa-adtrust-install` добавляет необходимые сервисы, `trust-add` создаёт доверие.

---

**Практическая работа №2: ID ranges и внешние группы**

**Задание:**
1. Посмотрите ID ranges.
2. Создайте ID range для AD-домена.
3. Добавьте внешнюю группу.
4. Добавьте AD-пользователя в группу.
5. Проверьте доступ.

**Решение и пояснения:**
```bash
ipa idrange-find
ipa idrange-add ad.local_idrange --base-id=200000 --range-size=200000 \
  --rid-base=1000000 --dom-ad.local --dom-sid=S-1-5-21-...
ipa group-add external_admins --external
ipa group-add-member external_admins --external='AD.LOCAL\Domain Admins'
```
**Пояснения:**
ID range задаёт диапазон POSIX-идентификаторов для пользователей AD. Внешние (non-POSIX) группы позволяют включать AD-группы в правила FreeIPA (например, sudo/HBAC).

---

**Практическая работа №3: Проверка и диагностика доверия**

**Задание:**
1. Проверьте состояние доверия.
2. Получите билет из доверенного домена.
3. Проверьте разрешение AD-пользователя.
4. Посмотрите журналы SSSD.
5. Объясните типовые проблемы.

**Решение и пояснения:**
```bash
ipa trust-show ad.local
kinit aduser@AD.LOCAL
klist
getent passwd aduser@ad.local
sudo journalctl -u sssd -n 50
```
**Пояснения:**
Доверие проверяют `trust-show`, получением билета из доверенного домена и `getent`. Проблемы: DNS, время, PAC, ID ranges, несовпадение SID. Диагностика — журналы SSSD.

---

**Практическая работа №4: Репликация и интеграция (awareness)**

**Задание:**
1. Опишите репликационную интеграцию FreeIPA/AD.
2. Опишите PAC.
3. Сравните trust и репликацию.
4. Оцените ограничения.
5. Предложите стратегию интеграции.

**Решение / Описание:**
```text
# Trust (cross-forest): AD и FreeIPA сосуществуют, доступ через Kerberos trust.
# Replication-based: данные AD копируются в FreeIPA (реже, ограничено).
# PAC (Privilege Attribute Certificate): содержит группы/SID AD.
# Проверка: ipa trust-fetch-domains ad.local
```
**Пояснения:**
Cross-forest trust — предпочтительный способ интеграции: домены остаются независимыми, доступ обеспечивается через Kerberos. PAC передаёт идентификацию и группы пользователя AD. Репликационная интеграция ограничена и используется редко.
