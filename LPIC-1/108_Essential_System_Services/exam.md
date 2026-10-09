[Оглавление](LPIC-1/home.md)

# Экзаменационные боевые задачи — Тема 108: Essential System Services

Задачи приближены к реальным заданиям экзамена **102-500**.

## Задача 1. Синхронизация системного времени

**Условие:** Настройте синхронизацию времени через NTP/chrony и проверьте статус.

**Ожидаемый результат:** Время синхронизируется.

**Решение и пояснения:**
```bash
sudo apt install -y chrony
sudo systemctl enable --now chrony
chronyc sources
chronyc tracking
timedatectl
```
chrony — современная замена ntpd. `chronyc sources` показывает источники времени, `tracking` — точность синхронизации. Точное время критично для Kerberos, логов, TLS.

## Задача 2. Настройка логирования

**Условие:** Настройте rsyslog для отдельного лога приложения и ротацию логов.

**Ожидаемый результат:** Логи пишутся и ротируются.

**Решение и пояснения:**
```bash
# /etc/rsyslog.d/50-myapp.conf:
# if $programname == 'myapp' then /var/log/myapp.log
# & stop
sudo systemctl restart rsyslog
# /etc/logrotate.d/myapp:
# /var/log/myapp.log { daily rotate 7 compress missingok notifempty }
sudo logrotate -f /etc/logrotate.d/myapp
```
rsyslog маршрутизирует сообщения по правилам. logrotate управляет ротацией (ежедневно, 7 копий, сжатие). Ротация предотвращает переполнение диска логами.

## Задача 3. Просмотр журналов systemd

**Условие:** Найдите ошибки за текущую загрузку, логи конкретной службы и сообщения за последний час.

**Ожидаемый результат:** Нужные записи найдены.

**Решение и пояснения:**
```bash
journalctl -b -p err            # Ошибки текущей загрузки
journalctl -u ssh --since "1 hour ago"
journalctl -f                   # Реальное время
journalctl --disk-usage
sudo journalctl --vacuum-size=500M
```
`journalctl` — журнал systemd. `-b` — загрузка, `-u` — служба, `-p` — приоритет, `--since` — период. `--vacuum-size` ограничивает размер журнала.

## Задача 4. Основы MTA и отправка почты

**Условие:** Настройте отправку системной почты и отправьте тестовое письмо локальному пользователю.

**Ожидаемый результат:** Письмо доставлено в локальный ящик.

**Решение и пояснения:**
```bash
sudo apt install -y postfix mailutils
echo "test" | mail -s "Тема" root
mailq                # Очередь
cat /var/mail/root   # Локальный ящик
# Алиасы: /etc/aliases -> root: admin ; sudo newaliases
```
MTA (Postfix) доставляет почту. `mail`/`mailx` отправляет, `/var/mail/<user>` — локальный ящик. Алиасы перенаправляют почту. Логи — в `/var/log/mail.log`.

## Задача 5. Управление печатью

**Условие:** Установите CUPS, добавьте принтер и отправьте задание на печать.

**Ожидаемый результат:** Принтер настроен, задание отправлено.

**Решение и пояснения:**
```bash
sudo apt install -y cups
sudo systemctl enable --now cups
lpstat -p -d                    # Принтеры и принтер по умолчанию
lpoptions -d printer1
lp -d printer1 /etc/hosts       # Печать файла
lpq ; lprm <job_id>             # Очередь и отмена
```
CUPS управляет печатью. `lpstat` показывает принтеры, `lp`/`lpr` отправляют задания, `lpq`/`lprm` управляют очередью. Веб-интерфейс — `http://localhost:631`.
