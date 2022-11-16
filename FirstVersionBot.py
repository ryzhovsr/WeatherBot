import requests
import telebot
import datetime
import os
from geopy.geocoders import Nominatim
from telebot import types

APIKey = "6f69386c33961b4b134327a55abe3ce4"  # Токен с сайта погоды для доступа к данным
botToken = "5629716671:AAFp2lUokDCQbs4yGO8_57hXBT857ruH2Vg"

bot = telebot.TeleBot(botToken)
city = ""   # Город, по которому будет отсылаться запрос на сайт
MONTHS = {1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля", 5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа",
          9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"}

# Для path к журналу действий пользователей
if os.name == 'nt':
    userdir = os.path.join(os.getcwd(), 'UsersActions\\')
else:
    userdir = os.path.join(os.getcwd(), 'UsersActions/')


# Обработчик на команду \start
@bot.message_handler(commands=['start'])
def getTextMessages(message):
    print("user entered /start")    # Для отладки
    writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id, "pressed \start")
    text = ("Привет, {0.first_name}! 😊\n"
            "Я умею прогнозировать погоду!\n"
            "Просто напиши мне название города 🏙\n"
            "Или отправь свою геопозицию 🌍".format(message.from_user))
    bot.send_message(chat_id=message.from_user.id, text=text)
    removeMessage(userID=message.from_user.id, messageID=message.message_id)


# Обработчик на любое текстовое сообщение
@bot.message_handler(content_types=['text'])
def anyMessage(message):
    print("User sent text")     # Для отладки

    if message.from_user.id == 1654897577 and message.json['text'] == '0805':
        file = open(userdir + 'journal.txt', 'rb')
        bot.send_document(message.from_user.id, file)
        file.close()

    else:
        writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id, "sent a message")
        chatID = message.chat.id
        global city
        city = message.json['text'].capitalize()
        sendMenu(chatID)
        removeMessage(userID=message.from_user.id, messageID=message.message_id)


# Обработчик меню
@bot.callback_query_handler(func=lambda call: True)
def callbackWorker(call):
    menu = {1: 'Выбранный город: ' + '{0}'.format(city), 2: 'Погода сейчас', 3: 'Прогноз на 4 дня'}
    keyList = {}

    for i in range(1, menu.__len__() + 1):
        vars()['key_0_' + str(i)] = types.InlineKeyboardButton(text=str(menu[i]), callback_data='pressed_0_' + str(i))
        keyList[i] = eval('key_0_' + str(i))

    keyboard = types.InlineKeyboardMarkup(keyboard=None, row_width=1)

    for i in range(1, keyList.__len__() + 1):
        keyboard.add(keyList[i])

    chat_id = call.from_user.id

    if 'pressed_0_' in call.data:

        if call.data == 'pressed_0_1':  # Кнопка для показа селектирующего города
            pass

        if call.data == 'pressed_0_2':  # Прогноз на текущее время
            writeUserAction(call.from_user.full_name, call.from_user.username,
                            call.from_user.id, "pressed forecast now")
            weatherText = weatherNow(city)
            bot.send_message(chat_id, text=weatherText, reply_markup=keyboard)

        if call.data == 'pressed_0_3':  # Прогноз на 4 дня
            writeUserAction(call.from_user.full_name, call.from_user.username,
                            call.from_user.id, "pressed forecast for 4 days")
            weatherText = weatherForFourDays(city)
            bot.send_message(chat_id, text=weatherText, reply_markup=keyboard)


# Обработчик на геопозицию
@bot.message_handler(content_types=["location"])
def location(message):
    print("User submitted location")    # Для отладки
    writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id, "sent geolocation")
    chatID = message.chat.id
    latitude = str(message.location.latitude)
    longitude = str(message.location.longitude)
    geolocator = Nominatim(user_agent="my_request")
    global city

    if 'village' in geolocator.reverse(latitude + ', ' + longitude).raw['address'].keys():
        city = geolocator.reverse(latitude + ', ' + longitude).raw['address']['village']
    elif 'town' in geolocator.reverse(latitude + ', ' + longitude).raw['address'].keys():
        city = geolocator.reverse(latitude + ', ' + longitude).raw['address']['town']
    else:
        bot.send_message(chat_id=message.from_user.id, text="По отправленной геопозиции не удалось определить город 😢\n"
                                                            "Попробуйте ещё раз!")
        return

    sendMenu(chatID)
    removeMessage(userID=message.from_user.id, messageID=message.message_id)


# Удаляет сообщение из чата
def removeMessage(userID, messageID):
    bot.delete_message(chat_id=userID, message_id=messageID)


# Отправляет меню
def sendMenu(chatID):
    global city
    menu = {1: 'Выбранный город: ' + '{0}'.format(city), 2: 'Погода сейчас', 3: 'Прогноз на 4 дня'}
    keyList = {}

    for i in range(1, menu.__len__() + 1):
        vars()['key_0_' + str(i)] = types.InlineKeyboardButton(text=str(menu[i]), callback_data='pressed_0_' + str(i))
        keyList[i] = eval('key_0_' + str(i))

    keyboard = types.InlineKeyboardMarkup(keyboard=None, row_width=1)

    for i in range(1, keyList.__len__() + 1):
        keyboard.add(keyList[i])

    if checkCity(city):
        bot.send_message(chat_id=chatID, text="Город есть в базе данных.", reply_markup=keyboard)
    else:
        bot.send_message(chat_id=chatID, text="Данного города нет в базе данных.")


# Определяет текущую погоду
def weatherNow(selectedCity):
    print("User click on weatherNow")
    res = requests.get("http://api.openweathermap.org/data/2.5/find",
                       params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': APIKey})
    data = res.json()['list'][0]

    output = str(round(data['main']['temp'])) + "° "
    weather = str(data['weather'][0]['description']).capitalize()
    output += weatherDetection(weather)
    pressure = round(data['main']['pressure'] * 750.06 / 1000)  # Переводи из мБар в мм. рт. ст
    output += "Давление " + str(pressure) + " мм "
    output += "Влажность " + str(data['main']['humidity']) + " %\n"
    output += "Ветер " + str(round(data['wind']['speed'])) + " м/с \n\n"

    return output


"""
def forecastForTomorrow(selectedCity):
    print("User click on weatherForFiveDays")
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                       params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': APIKey})
    now = datetime.datetime.now()
    now = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    data = res.json()
    output = ""
"""


# Определяет погоду на 4 дня
def weatherForFourDays(selectedCity):
    print("User click on weatherForFiveDays")
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                       params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': APIKey})
    data = res.json()

    rightDays = {}
    counter = 0

    now = datetime.datetime.now()

    # Цил для нахождения утра/обеда/вечера первых четырёх дней
    for inf in data['list']:
        if str(now.day) == inf['dt_txt'][8:10]:
            continue
        if inf['dt_txt'][11:] == '09:00:00' or inf['dt_txt'][11:] == '12:00:00' or inf['dt_txt'][11:] == '18:00:00':
            rightDays[counter] = inf
            counter += 1
        if counter == 12:
            break

    counter = 3     # Чтобы начать с утра
    output = ""

    for key in rightDays:
        if counter == 3:    # Для отметки нового дня
            output += rightDays[key]['dt_txt'][8:10] + " " + MONTHS[int(rightDays[key]['dt_txt'][5:7])] + '\n'
            counter = 0

        if key == 0 or key == 3 or key == 6 or key == 9:
            output += "Утром      "
        elif key == 1 or key == 4 or key == 7 or key == 10:
            output += "Днём        "
        elif key == 2 or key == 5 or key == 8 or key == 11:
            output += "Вечером  "

        output += str(round(rightDays[key]['main']['temp'])) + "° "
        weather = rightDays[key]['weather'][0]['description'].capitalize()
        output += weatherDetection(weather)

        counter += 1

        if key == 2 or key == 5 or key == 8 or key == 11:
            output += "\n"

    return output


"""
def weatherForFiveDays(selectedCity):
    print("User click on weatherForFiveDays")
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                       params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': APIKey})
    data = res.json()
    output = ""
    
    for inf in data['list']:
        if(inf['dt_txt'][11:] == '09:00:00'):
            print("x")

    counter = 0
    while counter < len(data['list']):
        date = data['list'][counter]['dt_txt'][5:-3]  # Слайсим год и секунды вывода даты
        output += date[3:5] + " " + MONTHS[int(date[0:2])] + " " + date[6:] + ": "
        output += str(round(data['list'][counter]['main']['temp'])) + " °C\n"
        weather = data['list'][counter]['weather'][0]['description'].capitalize()
        output += weatherDetection(weather)
        counter += 4
    return output
"""


# Добавляет к погоде смайлик
def weatherDetection(weather):
    match weather:
        case "Ясно": return "☀ " + weather + "\n"
        case "Пасмурно": return "☁ " + weather + "\n"
        case "Дождь": return "🌧 " + weather + "\n"
        case "Облачно с прояснениями": return "🌦 " + "Обл. с прояснениями" + "\n"
        case "Переменная облачность": return "🌥 " + "Переменная обл." + "\n"
        case "Небольшой дождь": return "🌧 " + weather + "\n"
        case "Небольшая облачность": return "🌤 " + "Небольшая обл." + "\n"
        case "Небольшой снег": return "🌨 " + weather + "\n"
        # Default
        case _: return weather + "\n"


# Делает проверку на существования города в базе данных сайта
def checkCity(selectedCity):
    res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                       params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': APIKey})
    if res.reason == 'Not Found':
        return False
    else:
        return True


# Записывает в журнал все действия пользователей
def writeUserAction(name, username, idUser, text=""):
    time = str(datetime.datetime.now())[:-7]
    with open(userdir + 'journal.txt', 'a') as f:
        f.write(time + ' ' + username + ' ' + name + " (ID " + str(idUser) + ") " + text + "\n")


bot.polling(none_stop=True, interval=0)
