# Password-bot task for VK

Воспользоваться ботом можно по ссылке: http://t.me/zqwy_password_bot

Серверная часть бота расположена в инфраструктуре VK Cloud
Доступ по SSH к серверной части бота в сообщение.

Технологии которые используются **Python3.9 + библоитека Telebot; Docker compose + Tarantool с replicas**

Исходный код Python лежит в репозитории.

_Что реализовано?_
- Бот отправляет статический текст
- Бот удалять сообщение с паролем через промежуток времение в запросах /set и /get
- Бот проверяет наличие нехватки аргументов в запросе для тестирование вот /set /set 1 set 1 1
- Бот отправлят читает данные - функция /get
- Бот читает данные при помощи функции /set
- Бот удаляет данные при помощи функции /del
- Бот проверяет UUID пользователя отправителя
- Бот при команде /set проверяет наличие сервиса


Что не реализовано и какие проблемы?
- Пользователь не имеет отдельное полноценное пространство для своих сервисов, но имеет отдельныое пространства для UUID. Соотвественно пользователь с другим UUID не сможет увидеть пароль сервиса другого UUID, но не сможет создать сервис с таким же названием сервиса.

Команды и как они работают:

/help - получение списка команд

/set [сервис][логин][пароль] - прикрепить логин и пароль к сервису

/get [сервис] - получить пароль по названию сервиса

/del [сервис] - удалить пароль по названию сервиса

**Как поднять локально базу?**

Для этого необхоидимо установить Docker и Docker compose
Используем этот compose
```
version: '2'

services:
  tarantool1:
    image: tarantool/tarantool:1.10.2
    environment:
      TARANTOOL_REPLICATION: "tarantool1,tarantool2"
    networks:
      - mynet
    ports:
      - "3301:3301"

  tarantool2:
    image: tarantool/tarantool:1.10.2
    environment:
      TARANTOOL_REPLICATION: "tarantool1,tarantool2"
    networks:
      - mynet
    ports:
      - "3302:3301"

networks:
  mynet:
    driver: bridge
```
```
docker compose up -d
```
Обращаемся в главной реплике
```docker exec -it root-tarantool1-1 console```

######
Создаём базу
######
```
data = box.schema.space.create('data')
```
```
data:format({
{name = 'id', type = 'unsigned'},
{name = 'uuid', type = 'unsigned'},
{name = 'service_name', type = 'string'},
{name = 'user_login', type = 'string'},
{name = 'user_password', type = 'string'}
})
```
```
box.space.space-name:create_index('index-name')
```
```
data:create_index('primary', {
type = 'tree',
parts = {'id'}
})
```
```
data:create_index('secondary', {
type = 'tree',
parts = {'service_name'}
})
```
