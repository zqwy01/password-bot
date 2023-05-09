import telebot, time, tarantool

#Подключаем БД
connection = tarantool.connect("localhost", 3301)
data = connection.space('data')

#Подключаем API токен нашего бота
Bot = telebot.TeleBot('6227984046:AAFUfE81Iw_NrT8bbEb-mX-l7DwUsCalDc0')

print('Bot Loaded')

#Функция /get и /del
def text_decode(service_name, uuid, func):
    print('decode')
    with open('file.txt', 'w') as output:
        output.write(str(data.select(service_name, index=1)))

    f = open('file.txt', 'r')
    if f.read() == '':
        answer = False
        print('пусто')
    else:
        answer = True

    if answer == False:
        return ('Сервис не найден')
    else:
        lines = open('file.txt', 'r').readlines()
        with open('file.txt', 'w') as fp:
            for line in lines:
                line = line[2:]
                fp.write(line)

        with open('file.txt') as input:
            array = input.read().split(sep=',')

        if (int(array[1].strip(" "))) == uuid:
            if func == True:
                data.delete(service_name, index=1)
                return ('Пароль удалён')
            else:
                return(array[4].strip("' ']")+' - вот ваш пароль\n' + array[3].strip("' '") + ' - вот ваш логин')
        else:
            return ('Сервис не найден')
#Функция /set
def insert_db(uuid, service_name, login, password):
    #Запись counter в файл
    f = open('counter.txt', 'r')
    a = f.read()
    f.close()

    f = open('counter.txt').readlines()
    f.pop(0)

    f = open('counter.txt', 'w+')
    f.write(str(int(a) + 1))
    f.close()

    print('decode')
    with open('file.txt', 'w') as output:
        output.write(str(data.select(service_name, index=1)))

    f = open('file.txt', 'r')
    if f.read() == '':
        f = open('counter.txt', 'r')
        data.insert((int(f.read()), uuid, service_name, login, password))
        f.close()
        return (True)
    else:
        return (False)

#Подключим декоратор для чтение текста пользователя
@Bot.message_handler(content_types=['text'])
def get_text_messages(message):
    #Создание команд для взаимодействие с ботом
    if message.text == "/start":
        Bot.send_message(message.from_user.id, "Привет, я Бот который умеет хранить твои пароли. Чтобы подробнее узнать о командах напиши /help.")
    elif message.text == "/help":
        Bot.send_message(message.from_user.id, "/set [сервис][логин][пароль] - прикрепить логин и пароль к сервису\n/get [сервис] - получить пароль по названию сервиса\n/del [сервис] - удалить пароль по названию сервиса")
    elif message.text.split(' ', 1)[0] == "/set":
        #Разделяем сообщение для работы с ним
        msg = message.text.split()
        if len(msg) >= 2:
            if len(msg) >= 3:
                if len(msg) == 4:
                    if insert_db(message.from_user.id, msg[1], msg[2], msg[3]) == True:
                        Bot.send_message(message.from_user.id, "Ваш пароль сохранен.\nВаше сообщение будет удаленно через 5 секунд")
                        time.sleep(5)
                        Bot.delete_message(message.chat.id, message.message_id)
                    else:
                        Bot.send_message(message.from_user.id, "Уже существует такой сервис")
                elif len(msg) <= 4:
                    Bot.send_message(message.from_user.id, "Вы забыли ввести пароль")
                else:
                    Bot.send_message(message.from_user.id, "Вы ввели слишком много аргументов")
            else:
                Bot.send_message(message.from_user.id, "Вы забыли ввести логин и пароль")
        else:
            Bot.send_message(message.from_user.id, "Вы забыли написать название сервиса, логин и пароль")
    elif message.text.split(' ', 1)[0] == "/get":
        msg = message.text.split()
        if len(msg) >= 2:
            Bot.send_message(message.from_user.id, text_decode(msg[1], message.from_user.id, False))
            Bot.send_message(message.from_user.id, "Я удалю сообщение с паролем через 5 секунд")
            time.sleep(5)
            Bot.delete_message(message.chat.id, message.message_id+1)
        else:
            Bot.send_message(message.from_user.id, "Вы забыли ввести название сервиса")
    elif message.text.split(' ', 1)[0] == "/del":
        msg = message.text.split()
        if len(msg) >= 2:
            print('del')
            Bot.send_message(message.from_user.id, text_decode(msg[1], message.from_user.id, True))
        else:
            Bot.send_message(message.from_user.id, "Вы забыли ввести название сервиса")
    else:
        Bot.send_message(message.from_user.id, "Неизвестная команда, напишите /help")


#Скажем боту постоянно проверять наличие новых сообщений
Bot.polling(none_stop=True, interval=0)



##### Как работает БД
#База данных проверят по телеграм ID пользователя и ищет его пароль

#Использование инструментов
#Python3.11, библиотеки telebot и tarantool.
#Docker - для развёртки приложение бд.
#Tarantool - БД

###### Документация TO-DO list
# - Бот отправляет статический текст
# - Бот удалять сообщение с паролем через промежуток времение в запросах /set и /get
# - Бот проверяет наличие нехватки аргументов в запросе для тестирование вот /set /set 1 set 1 1
# - Бот отправлят читает данные - функция /get
# - Бот читает данные при помощи функции /set
# - Бот удаляет данные при помощи функции /del
# - Бот проверяет UUID пользователя отправителя
# - Бот при команде /set проверяет наличие сервиса

# - Бот не имеет отдельные пространства для сервисов, но имеет отдельныое пространства для UUID. Соотвественно UUID не сможет увидеть пароль сервиса другого UUID, но не сможет создать сервис с таким же названием.