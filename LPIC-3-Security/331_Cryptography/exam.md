[Оглавление](LPIC-3-Security/home.md)

# Экзаменационные боевые задачи — Тема 331: Cryptography

Задачи приближены к реальным заданиям экзамена **303-300**.

## Задача 1. Развёртывание PKI

**Условие:** Создайте корневой CA, промежуточный CA и выпустите серверный сертификат с SAN.

**Ожидаемый результат:** Цепочка сертификатов проверяется.

**Решение и пояснения:**
```bash
openssl genrsa -out root.key 4096
openssl req -x509 -new -nodes -key root.key -days 3650 -subj "/CN=Lab Root CA" -out root.crt
openssl genrsa -out int.key 4096
openssl req -new -key int.key -subj "/CN=Lab Int CA" -out int.csr
openssl x509 -req -in int.csr -CA root.crt -CAkey root.key -CAcreateserial -days 1825 \
  -extfile <(echo "basicConstraints=critical,CA:TRUE") -out int.crt
openssl verify -CAfile root.crt -untrusted int.crt web.crt
```
Иерархия PKI: корневой CA → промежуточный → конечные сертификаты. Корневой ключ хранят офлайн. `basicConstraints CA:TRUE` помечает CA. `verify` проверяет цепочку.

## Задача 2. Сертификаты для шифрования и подписи

**Условие:** Зашифруйте файл открытым ключом, создайте и проверьте цифровую подпись.

**Ожидаемый результат:** Шифрование и подпись работают.

**Решение и пояснения:**
```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out key.pem
openssl pkey -in key.pem -pubout -out pub.pem
openssl pkeyutl -encrypt -pubin -inkey pub.pem -in secret.bin -out secret.enc
openssl pkeyutl -decrypt -inkey key.pem -in secret.enc -out secret.out
openssl dgst -sha256 -sign key.pem -out file.sig file.txt
openssl dgst -sha256 -verify pub.pem -signature file.sig file.txt
```
Асимметричное шифрование медленное — на практике гибридное (сессионный ключ + AES). Подпись подтверждает целостность и авторство: любое изменение файла делает её недействительной.

## Задача 3. Шифрование диска (LUKS)

**Условие:** Создайте зашифрованный контейнер, настройте второй ключ и резервную копию заголовка.

**Ожидаемый результат:** Зашифрованный том работает.

**Решение и пояснения:**
```bash
sudo cryptsetup luksFormat /tmp/vol.img
sudo cryptsetup luksAddKey /tmp/vol.img
sudo cryptsetup luksDump /tmp/vol.img
sudo cryptsetup luksOpen /tmp/vol.img cryptvol
sudo mkfs.ext4 /dev/mapper/cryptvol
sudo cryptsetup luksHeaderBackup /tmp/vol.img --header-backup-file /backup/luks-header.img
sudo cryptsetup luksClose cryptvol
```
LUKS шифрует блочное устройство. Несколько слотов ключей позволяют менять пароль без перешифрования. Резервная копия заголовка критична — без неё данные не восстановить.

## Задача 4. Шифрованные файловые системы и swap

**Условие:** Настройте автомонтирование зашифрованного раздела и шифрование swap.

**Ожидаемый результат:** Шифрование применяется при загрузке.

**Решение и пояснения:**
```bash
sudo dd if=/dev/urandom of=/root/crypt.key bs=512 count=4 && sudo chmod 600 /root/crypt.key
sudo cryptsetup luksAddKey /dev/sdb1 /root/crypt.key
# /etc/crypttab:
# cryptdata UUID=<uuid> /root/crypt.key luks
# cryptswap /dev/sdb2 /dev/urandom swap,cipher=aes-xts-plain64
# /etc/fstab: /dev/mapper/cryptdata /mnt/crypt ext4 defaults 0 2
sudo cryptdisks_start cryptdata
```
Keyfile позволяет открывать раздел без пароля. crypttab автоматизирует открытие, swap шифруется случайным ключом (данные памяти не попадут на диск).

## Задача 5. DNSSEC и защищённый DNS

**Условие:** Подпишите зону DNSSEC и проверьте валидацию.

**Ожидаемый результат:** Зона подписана, подписи проверяются.

**Решение и пояснения:**
```bash
dnssec-keygen -a ECDSAP256SHA256 -n ZONE lab.local
dnssec-keygen -a ECDSAP256SHA256 -f KSK -n ZONE lab.local
dnssec-signzone -o lab.local -k Klab.local.+013+*.key db.lab.local
# named.conf: file "db.lab.local.signed";
sudo rndc reload
dig +dnssec lab.local @localhost | grep -i rrsig
```
ZSK подписывает записи, KSK — DNSKEY. `dnssec-signzone` создаёт подписанную зону. Валидация идёт по цепочке DS от корня. DoT/DoH дополнительно шифруют транспорт DNS.
