[Оглавление](LPIC-3-Securityhome.md)

**Практическая работа №1: Шифрование раздела через LUKS**

**Задание:**
1. Установите `cryptsetup`.
2. Создайте и отформатируйте LUKS-устройство.
3. Откройте устройство.
4. Создайте ФС и смонтируйте.
5. Закройте устройство.

**Решение и пояснения:**
```bash
sudo apt install -y cryptsetup
sudo dd if=/dev/zero of=/tmp/crypt.img bs=1M count=200
sudo cryptsetup luksFormat /tmp/crypt.img          # 2. Форматирование LUKS
sudo cryptsetup luksOpen /tmp/crypt.img cryptvol   # 3. Открытие
sudo mkfs.ext4 /dev/mapper/cryptvol
sudo mount /dev/mapper/cryptvol /mnt
sudo umount /mnt && sudo cryptsetup luksClose cryptvol   # 5. Закрытие
```
**Пояснения:**
LUKS — стандарт шифрования блочных устройств в Linux. `luksFormat` создаёт заголовок с мастер-ключом, защищённым паролем. `luksOpen` создаёт отображение в `/dev/mapper`. Без ключа данные нечитаемы.

---

**Практическая работа №2: Управление ключами LUKS**

**Задание:**
1. Посмотрите заголовок LUKS.
2. Добавьте второй ключ (пароль).
3. Проверьте слоты ключей.
4. Удалите ключ.
5. Объясните назначение нескольких слотов.

**Решение и пояснения:**
```bash
sudo cryptsetup luksDump /tmp/crypt.img            # 1. Заголовок
sudo cryptsetup luksAddKey /tmp/crypt.img          # 2. Добавление ключа
sudo cryptsetup luksDump /tmp/crypt.img | grep -i slot
sudo cryptsetup luksRemoveKey /tmp/crypt.img       # 4. Удаление
sudo cryptsetup luksHeaderBackup /tmp/crypt.img --header-backup-file /backup/luks-header.img
```
**Пояснения:**
LUKS поддерживает до 8 слотов ключей: разные пароли или keyfiles. Это позволяет менять пароль без перешифрования. Резервную копию заголовка (`luksHeaderBackup`) хранят отдельно — её потеря означает потерю данных.

---

**Практическая работа №3: Автомонтирование и keyfile**

**Задание:**
1. Создайте keyfile.
2. Добавьте keyfile как ключ LUKS.
3. Настройте `/etc/crypttab`.
4. Настройте `/etc/fstab`.
5. Проверьте открытие при загрузке (концептуально).

**Решение и пояснения:**
```bash
sudo dd if=/dev/urandom of=/root/crypt.key bs=512 count=4
sudo chmod 600 /root/crypt.key
sudo cryptsetup luksAddKey /tmp/crypt.img /root/crypt.key   # 2. Keyfile
# /etc/crypttab: cryptvol /tmp/crypt.img /root/crypt.key luks
# /etc/fstab: /dev/mapper/cryptvol /mnt ext4 defaults 0 2
sudo cryptdisks_start cryptvol
```
**Пояснения:**
Keyfile позволяет открывать устройство без ввода пароля (например, для серверов). `/etc/crypttab` описывает шифрованные устройства, `/etc/fstab` — их монтирование. Keyfile хранят с правами 600.

---

**Практическая работа №4: Шифрование домашнего каталога и swap**

**Задание:**
1. Опишите варианты шифрования домашних каталогов.
2. Опишите `eCryptfs`.
3. Опишите шифрование swap.
4. Проверьте статус шифрования домашнего каталога.
5. Объясните риски незашифрованного swap.

**Решение и пояснения:**
```bash
# eCryptfs: ecryptfs-verify / ecryptfs-mount-private
ls -la ~/.Private 2>/dev/null
# Шифрование swap через LUKS: crypttab + fstab с /dev/mapper/swap
sudo swapon --show
cat /etc/crypttab
```
**Пояснения:**
Домашние каталоги шифруют через eCryptfs (per-file) или LUKS (весь раздел). Swap нужно шифровать: туда могут попасть пароли и ключи из памяти. `crypttab` с записью для swap и случайным ключом решает проблему.

---

**Практическая работа №5: dm-crypt, целостность и производительность**

**Задание:**
1. Посмотрите параметры dm-crypt.
2. Опишите режимы (plain, LUKS, tcrypt).
3. Проверьте производительность шифрования.
4. Опишите dm-integrity.
5. Объясните влияние на производительность.

**Решение и пояснения:**
```bash
sudo dmsetup ls
sudo dmsetup status
sudo cryptsetup benchmark                      # 3. Бенчмарк
sudo cryptsetup luksDump /tmp/crypt.img | grep -iE "cipher|mode|hash"
```
**Пояснения:**
dm-crypt — подсистема ядра для прозрачного шифрования. Режимы: `plain` (без заголовка), `LUKS` (с заголовком), `tcrypt` (TrueCrypt/VeraCrypt). dm-integrity добавляет защиту целостности. AES-NI ускоряет шифрование на современных CPU.
