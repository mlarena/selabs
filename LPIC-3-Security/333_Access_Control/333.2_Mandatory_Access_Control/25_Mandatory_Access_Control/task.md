[Оглавление](home.md)     

**Практическая работа №1: Установка и базовая настройка SELinux**     

**Задание:**     
1. Проверьте, установлен ли SELinux в системе.     
2. Установите SELinux и необходимые утилиты.     
3. Проверьте текущий режим работы SELinux.     
4. Измените режим работы на permissive.     
5. Временно переключите режим в enforcing и обратно.     
6. Настройте SELinux для работы в enforcing режиме после перезагрузки.     

**Решение и пояснения:**
```bash
getenforce 2>/dev/null || echo "SELinux не установлен"  # 1. Проверка
sudo apt install selinux-basics selinux-policy-default auditd -y  # 2. Установка
sudo selinux-activate  # Активация SELinux
getenforce  # 3. Проверка режима (вероятно Disabled)
sudo setenforce Permissive  # 4. Временное переключение в permissive
sudo setenforce Enforcing   # 5. Временное переключение в enforcing
sudo setenforce Permissive  # Возврат в permissive
sudo nano /etc/selinux/config  # 6. Измените SELINUX=enforcing и SELINUXTYPE=default
```

**Пояснения:**      
Debian по умолчанию не использует SELinux (используется AppArmor).      
`getenforce` показывает режим: Disabled/Enforcing/Permissive.      
`setenforce` меняет режим временно (до перезагрузки).             
`/etc/selinux/config` настраивает постоянный режим.       
Permissive режим логирует нарушения, но не блокирует.      
      
---

**Практическая работа №2: Работа с контекстами файлов и процессов**      

**Задание:**      
1. Проверьте контекст безопасности вашего домашнего каталога.      
2. Измените контекст файла на `user_home_t`.      
3. Восстановите контекст по умолчанию для файла.      
4. Проверьте контекст запущенного процесса (например, `sshd`).      
5. Создайте файл и проверьте его унаследованный контекст.      
6. Измените контекст рекурсивно для каталога.      

**Решение и пояснения:**
```bash
ls -Z ~/  # 1. Просмотр контекстов файлов (если SELinux активен)
touch testfile
chcon -t user_home_t testfile  # 2. Изменение контекста файла
ls -Z testfile  # Проверка
restorecon testfile  # 3. Восстановление контекста по умолчанию
ps -eZ | grep sshd  # 4. Контекст процесса sshd
mkdir testdir && touch testdir/file.txt
ls -Zd testdir && ls -Z testdir/file.txt  # 5. Унаследованный контекст
chcon -R -t httpd_sys_content_t testdir/  # 6. Рекурсивное изменение контекста
```
**Пояснения:** 
`ls -Z` показывает контекст безопасности.       
`chcon` изменяет контекст.       
`restorecon` восстанавливает контекст по умолчанию из политики.       
Процессы также имеют контексты, которые определяют их права.       
Контекст обычно включает: пользователь, роль, тип и уровень.      

---

**Практическая работа №3: Анализ и устранение нарушений**      

**Задание:**      
1. Просмотрите логи SELinux на наличие нарушений.      
2. Создайте ситуацию с нарушением (попробуйте запустить веб-сервер в неположенном каталоге).      
3. Найдите соответствующую запись в логах.      
4. Используйте `audit2why` для анализа нарушения.      
5. Используйте `audit2allow` для создания модуля разрешения.      
6. Примените созданный модуль.      

**Решение и поясния:**
```bash
sudo tail -20 /var/log/audit/audit.log  # 1. Просмотр логов (или /var/log/syslog)
# 2. Создадим нарушение (пример):
sudo mkdir /wrong_web
sudo chcon -R -t httpd_sys_content_t /wrong_web/
sudo systemctl start apache2  # Если Apache пытается получить доступ
sudo grep "denied" /var/log/audit/audit.log | tail -5  # 3. Поиск нарушений
sudo grep "denied" /var/log/audit/audit.log | audit2why  # 4. Объяснение нарушения
sudo grep "denied" /var/log/audit/audit.log | audit2allow -M mymodule  # 5. Создание модуля
sudo semodule -i mymodule.pp  # 6. Установка модуля
```
**Пояснения:**       
Логи SELinux находятся в `/var/log/audit/audit.log` или `/var/log/syslog`.       
`audit2why` объясняет, почему доступ был запрещен.       
`audit2allow` создает политику для разрешения обнаруженных нарушений.       
Модули — безопасный способ добавлять исключения в политику SELinux.      


---

**Практическая работа №4: Управление портами и логинами**      

**Задание:**      
1. Просмотрите привязанные к портам контексты SELinux.      
2. Измените контекст порта 8080 на `http_port_t`.      
3. Проверьте контексты логинов пользователей.      
4. Настройте контекст по умолчанию для пользователя.      
5. Создайте ограничение доступа по уровню (MLS).      
6. Переведите SELinux в режим MLS и проверьте работу.      

**Решение и пояснения:**      
```bash
sudo semanage port -l | grep http  # 1. Просмотр портов для http
sudo semanage port -a -t http_port_t -p tcp 8080  # 2. Добавление порта 8080 для http
sudo semanage login -l  # 3. Контексты логинов
sudo semanage login -a -s user_u -r s0 user1  # 4. Назначение контекста пользователю
# 5. Для MLS требуется специальная политика и настройка
# 6. В /etc/selinux/config установите SELINUXTYPE=mls и перезагрузитесь
getenforce  # Проверка после перезагрузки
```
**Пояснения:**       
`semanage` управляет политикой SELinux.       
Порт 8080 по умолчанию не разрешен для веб-серверов в SELinux.       
Контексты логинов связывают пользователей Linux с пользователями SELinux.       
MLS (Multi-Level Security) добавляет уровни безопасности (например, секретность).       
Требует перезагрузки для применения.      

[Оглавление](home.md)     