
---

**Практическая работа №1: Управление службами и мониторинг демонов**

**Задание:**
1. Запустите и остановите службы Samba.
2. Проверьте статус демонов.
3. Посмотрите активные сессии.
4. Отправьте сообщение демону через `smbcontrol`.
5. Объясните назначение smbcontrol.

**Решение и пояснения:**
```bash
sudo systemctl stop smbd nmbd winbind
sudo systemctl start smbd nmbd winbind
systemctl status smbd
sudo smbstatus                          # 3. Сессии
sudo smbcontrol smbd reload-config      # 4. Перезагрузка конфигурации
sudo smbcontrol smbd debug 5            # 4. Изменение уровня логов
```
**Пояснения:**
`smbstatus` показывает подключения, блокировки и используемые ресурсы. `smbcontrol` отправляет сообщения демонам (reload-config, debug, shutdown). Это удобно для управления без перезапуска.

---

**Практическая работа №2: Резервное копирование TDB-файлов**

**Задание:**
1. Найдите TDB-файлы Samba.
2. Определите назначение `secrets.tdb`, `registry.tdb`.
3. Сделайте резервную копию TDB.
4. Восстановите TDB.
5. Объясните риски повреждения TDB.

**Решение и пояснения:**
```bash
ls /var/lib/samba/private/*.tdb
sudo tdbbackup /var/lib/samba/private/secrets.tdb   # 3. Бэкап
# Файл создаётся как secrets.tdb.bak
sudo tdbrestore /var/lib/samba/private/secrets.tdb  # 4. Восстановление
```
**Пояснения:**
TDB — формат баз данных Samba. `secrets.tdb` хранит секреты домена, `registry.tdb` — реестр. `tdbbackup`/`tdbrestore` делают согласованные копии. Повреждение TDB ломает аутентификацию и конфигурацию.

---

**Практическая работа №3: Резервное копирование контроллера домена AD**

**Задание:**
1. Выполните онлайн-бэкап AD DC.
2. Посмотрите созданный архив.
3. Опишите стратегию восстановления.
4. Учтите влияние виртуализации.
5. Объясните роль VM Generation ID.

**Решение и пояснения:**
```bash
sudo samba-tool domain backup online --targetdir=/backup/samba --server=dc1.lab
ls -lh /backup/samba/
# Офлайн-бэкап: samba-tool domain backup offline
```
**Пояснения:**
`samba-tool domain backup online` делает бэкап работающего DC, `offline` — остановленного. Восстановление включает sysvol и базу. При виртуализации важно учитывать снапшоты и VM Generation ID, чтобы избежать рассинхронизации AD.

---

**Практическая работа №4: Восстановление и обслуживание**

**Задание:**
1. Проверьте целостность базы AD.
2. Найдите устаревшие объекты.
3. Перезапустите службы после обслуживания.
4. Проверьте репликацию (если есть).
5. Объясните регулярные задачи обслуживания.

**Решение и пояснения:**
```bash
sudo samba-tool dbcheck --cross-ncs
sudo samba-tool dbcheck --fix
sudo systemctl restart samba-ad-dc
sudo samba-tool drs showrepl
```
**Пояснения:**
`samba-tool dbcheck` проверяет и исправляет базу AD. `drs showrepl` показывает состояние репликации. Регулярное обслуживание: бэкапы, проверка БД, мониторинг репликации, обновление Samba.
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
find /var/backups/samba -maxdepth 1 -mtime +7 -exec rm -rf {} \;
SCRIPT
sudo chmod +x /usr/local/bin/samba_backup.sh
# crontab -e: 0 2 * * * /usr/local/bin/samba_backup.sh
```
**Пояснения:**
Резервное копирование TDB-файлов критично для AD DC.
