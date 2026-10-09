[Оглавление](LPIC-2home.md)

**Практическая работа №1: Включение IP-форвардинга и NAT**

**Задание:**
1. Включите пересылку IP-пакетов.
2. Сделайте параметр постоянным.
3. Настройте NAT (masquerade) для локальной сети.
4. Проверьте доступ в интернет через шлюз.
5. Объясните роль NAT.

**Решение и пояснения:**
```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-forward.conf
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE   # 3. NAT
sudo iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
```
**Пояснения:**
IP-форвардинг позволяет хосту маршрутизировать пакеты. NAT подменяет адрес источника (masquerade) для выхода в интернет. Это основа интернет-шлюза, скрывающего внутреннюю сеть.

---

**Практическая работа №2: Фильтрация пакетов**

**Задание:**
1. Заблокируйте входящий порт.
2. Разрешите SSH только из подсети.
3. Настройте политику по умолчанию DROP.
4. Сохраните правила.
5. Проверьте фильтрацию.

**Решение и пояснения:**
```bash
sudo iptables -A INPUT -p tcp --dport 23 -j DROP
sudo iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P INPUT DROP
sudo iptables-save | sudo tee /etc/iptables/rules.v4   # 4. Сохранение
```
**Пояснения:**
iptables фильтрует по протоколу, порту, адресу. Политика `DROP` по умолчанию блокирует всё, кроме разрешённого. Правило `ESTABLISHED,RELATED` разрешает ответы на исходящие соединения. `iptables-save`/`restore` сохраняют и загружают правила.

---

**Практическая работа №3: Перенаправление портов**

**Задание:**
1. Перенаправьте внешний порт на внутренний хост.
2. Настройте DNAT.
3. Проверьте перенаправление.
4. Ограничьте перенаправление по источнику.
5. Объясните сценарии использования.

**Решение и пояснения:**
```bash
# Входящий 8080 -> внутренний 80:
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 \
  -j DNAT --to-destination 192.168.1.20:80
sudo iptables -A FORWARD -p tcp -d 192.168.1.20 --dport 80 -j ACCEPT
sudo iptables -t nat -L PREROUTING -n -v
```
**Пояснения:**
DNAT перенаправляет входящие соединения на внутренний хост (port forwarding). Используется для публикации сервисов (веб, SSH) из внутренней сети. Ограничение по источнику (`-s`) повышает безопасность.

---

**Практическая работа №4: IPv6 и сохранение правил**

**Задание:**
1. Посмотрите правила для IPv6.
2. Настройте базовую фильтрацию IPv6.
3. Сохраните правила для IPv4 и IPv6.
4. Восстановите правила из файла.
5. Объясните различия iptables и ip6tables.

**Решение и пояснения:**
```bash
sudo ip6tables -L -n
sudo ip6tables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo ip6tables -P INPUT DROP
sudo ip6tables-save | sudo tee /etc/iptables/rules.v6
sudo iptables-restore < /etc/iptables/rules.v4
```
**Пояснения:**
`ip6tables` — аналог `iptables` для IPv6 (отдельные таблицы). Правила сохраняют раздельно (`rules.v4`, `rules.v6`). В новых системах на смену приходит `nftables` (`nft`), но iptables остаётся широко используемым.
