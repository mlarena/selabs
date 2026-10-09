
защита ssh входа
вход по ключу
вход по паролю
мониторнг попыток подключений


### Установка специализированных утилит:
```bash
# GoAccess - веб-аналитика логов
sudo apt install goaccess

# Анализ auth.log
sudo goaccess /var/log/auth.log --log-format=COMBINED

# DenyHosts для автоматического анализа
sudo apt install denyhosts
```
