[Оглавление](https://gitflic.ru/project/ml/selabs/blobhome.md)

**Практическая работа №1: Шифрование съемного носителя (USB) с LUKS**

**Задание:**    
1. Определите имя устройства USB-накопителя (например, /dev/sdb1).    
2. Создайте зашифрованный контейнер LUKS на USB-носителе.    
3. Отформатируйте зашифрованный раздел в файловую систему ext4.    
4. Смонтируйте зашифрованный раздел и создайте тестовый файл.    
5. Размонтируйте и проверьте, что данные недоступны без пароля.    
6. Снова смонтируйте, введя пароль, и проверьте доступ к файлу.    

**Решение и пояснения:**
```bash
lsblk                                 # 1. Определение устройства USB
sudo cryptsetup luksFormat /dev/sdb1  # 2. Создание LUKS контейнера (введите YES, пароль)
sudo cryptsetup open /dev/sdb1 usb_crypt  # 3. Открытие контейнера (введите пароль)
sudo mkfs.ext4 /dev/mapper/usb_crypt  # 3. Форматирование
sudo mount /dev/mapper/usb_crypt /mnt # 4. Монтирование
sudo touch /mnt/test.txt             # 4. Тестовый файл
sudo umount /mnt && sudo cryptsetup close usb_crypt  # 5. Закрытие
sudo mount /dev/sdb1 /mnt 2>&1       # 5. Попытка монтирования без расшифровки (должна быть ошибка)
sudo cryptsetup open /dev/sdb1 usb_crypt && sudo mount /dev/mapper/usb_crypt /mnt  # 6. Доступ с паролем
```

**Пояснения:**     
`cryptsetup` управляет LUKS шифрованием.     
`luksFormat` создает зашифрованный контейнер.     
`open` открывает его с паролем, создавая устройство-маппер `/dev/mapper/usb_crypt`.     
Без открытия контейнера данные недоступны.

---

**Практическая работа №2: Создание зашифрованного файлового контейнера**    

**Задание:**    
1. Создайте файл-контейнер размером 100MB для хранения зашифрованных данных.    
2. Настройте LUKS шифрование на этом файле-контейнере.    
3. Создайте файловую систему внутри контейнера.    
4. Смонтируйте контейнер и добавьте в него файлы.    
5. Автоматизируйте монтирование через /etc/fstab (с паролем при загрузке).    
6. Проверьте целостность зашифрованных данных.    

**Решение и пояснения:**
```bash
dd if=/dev/zero of=~/encrypted_container.bin bs=1M count=100  # 1. Создание файла-контейнера
sudo losetup -f ~/encrypted_container.bin                    # 1. Связывание с loop-устройством
sudo cryptsetup luksFormat /dev/loop0                         # 2. Шифрование LUKS
sudo cryptsetup open /dev/loop0 container_crypt               # 3. Открытие контейнера
sudo mkfs.ext4 /dev/mapper/container_crypt                    # 3. Файловая система
sudo mount /dev/mapper/container_crypt /mnt                   # 4. Монтирование
sudo touch /mnt/secret_file.txt                               # 4. Добавление файла
# 5. Для /etc/fstab: /dev/mapper/container_crypt /mnt ext4 defaults 0 2
sudo cryptsetup luksDump /dev/loop0                           # 6. Проверка заголовка LUKS
```
**Пояснения:**     
Файл-контейнер имитирует диск.     
`losetup` связывает файл с устройством `/dev/loopX`.     
Пароль требуется при каждом открытии (`cryptsetup open`).     
`luksDump` показывает информацию о контейнере без пароля.         
Полезно для портативных зашифрованных данных.    

---

**Практическая работа №3: Работа с ключевыми файлами вместо паролей**    

**Задание:**    
1. Создайте ключевой файл со случайными данными.    
2. Добавьте ключевой файл как способ разблокировки LUKS-раздела.    
3. Настройте автоматическое монтирование при загрузке с помощью ключевого файла.    
4. Смонтируйте раздел с использованием ключевого файла.    
5. Удалите пароль, оставив только ключевой файл для доступа.    
6. Проверьте, что монтирование с паролем больше не работает.    

**Решение и пояснения:**    
```bash
sudo dd if=/dev/urandom of=/root/keyfile bs=4096 count=1  # 1. Создание ключевого файла
sudo chmod 0400 /root/keyfile                             # 1. Защита файла
sudo cryptsetup luksAddKey /dev/sdb1 /root/keyfile        # 2. Добавление ключа в LUKS
# 3. В /etc/crypttab: usb_crypt /dev/sdb1 /root/keyfile luks
sudo cryptsetup open --key-file /root/keyfile /dev/sdb1 usb_crypt  # 4. Открытие ключом
sudo mount /dev/mapper/usb_crypt /mnt                      # 4. Монтирование
sudo cryptsetup luksRemoveKey /dev/sdb1                    # 5. Удаление пароля (спросит оставшийся ключ)
sudo cryptsetup open /dev/sdb1 test                       # 6. Попытка без ключа (должна запросить пароль)
```
**Пояснения:**     
Ключевые файлы удобны для автоматизации.     
`luksAddKey` добавляет новый ключ, `luksRemoveKey` удаляет.     
`/etc/crypttab` настраивает автоматическое открытие при загрузке.     
Ключевой файл должен быть хорошо защищен (права 0400).    

---

**Практическая работа №4: Резервное копирование и восстановление заголовков LUKS**    

**Задание:**    
1. Создайте резервную копию заголовка LUKS раздела.    
2. Проверьте целостность резервной копии.    
3. Имитируйте повреждение заголовка LUKS (осторожно!).    
4. Восстановите заголовок из резервной копии.    
5. Убедитесь, что данные доступны после восстановления.    
6. Создайте скрипт для регулярного резервного копирования заголовков.    

**Решение и пояснения:**
```bash
sudo cryptsetup luksHeaderBackup /dev/sdb1 --header-backup-file ~/luks_header_backup.img  # 1. Резервная копия
sudo cryptsetup luksDump ~/luks_header_backup.img  # 2. Проверка резервной копии
# 3. Имитация повреждения (ТОЛЬКО НА ТЕСТОВОМ УСТРОЙСТВЕ!):
# sudo dd if=/dev/zero of=/dev/sdb1 bs=512 count=4096
sudo cryptsetup luksHeaderRestore /dev/sdb1 --header-backup-file ~/luks_header_backup.img  # 4. Восстановление
sudo cryptsetup open /dev/sdb1 test && echo "Восстановление успешно"  # 5. Проверка доступа
# 6. Скрипт backup_luks_headers.sh:
#!/bin/bash
for dev in /dev/sd*1; do
  sudo cryptsetup luksHeaderBackup $dev --header-backup-file /backup/$(basename $dev).img
done
```
**Пояснения:**     
Заголовок LUKS содержит мастер-ключ и метаданные.     
Без него данные теряются навсегда.     
`luksHeaderBackup` создает резервную копию.     
`luksHeaderRestore` восстанавливает. 


**Критически важно:**     
Резервные копии должны храниться отдельно от зашифрованных данных и быть защищены.    


[Оглавление](https://gitflic.ru/project/ml/selabs/blobhome.md)