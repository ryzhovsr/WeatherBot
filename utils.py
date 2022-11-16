import requests     # Для запросов к сайту
import telebot      # Для инициализации и работы с ботом
import datetime     # Для получения текущего времени
import os           # Для получения пути к журналу действий пользователей
from telebot import types   # Для клавиш в менюшке бота
from geopy.geocoders import Nominatim
# Свой модуль с функциями для чтения конфг. файла
from configReader import getBotToken, getApiToken, getAdminID, getKey


# Constants
BOT_TOKEN = getBotToken()
API_TOKEN = getApiToken()
BOT = telebot.TeleBot(BOT_TOKEN)
MONTHS = {1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля", 5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа",
          9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"}

# Получаем правильный путь к журналу действий пользователей в зависимости от ОС
if os.name == 'nt':
    journalDir = os.path.join(os.getcwd(), 'UsersActions\\')
else:
    journalDir = os.path.join(os.getcwd(), 'UsersActions/')


# Делает проверку на запросы к сайту погоды с заданным городом (eсли название города корректное - вернёт True)
def cityCheck(selectedCity):
    query = requests.get('http://api.openweathermap.org/data/2.5/forecast',
                         params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': API_TOKEN})
    return query.reason != 'Not Found'


# Удаляет сообщение из чата
def removeMessage(chatID, messageID):
    BOT.delete_message(chat_id=chatID, message_id=messageID)


# Возвращает текст прогноза погоды на данный момент
def currentForecast(selectedCity):
    data = requests.get('http://api.openweathermap.org/data/2.5/find',
                        params={'q': selectedCity, 'units': 'metric',
                                'lang': 'ru', 'APPID': API_TOKEN}).json()['list'][0]

    outputText = str(round(data['main']['temp'])) + '° '
    weather = str(data['weather'][0]['description']).capitalize()
    outputText += addEmojiWeather(weather)
    pressure = round(data['main']['pressure'] * 750.06 / 1000)  # Переводи из мБар в мм. рт. ст.
    outputText += 'Давление ' + str(pressure) + ' мм '
    outputText += 'Влажность ' + str(data['main']['humidity']) + ' %\n'
    outputText += 'Ветер ' + str(round(data['wind']['speed'])) + ' м/с \n\n'
    return outputText


# Определяет погоду на 4 дня
def forecastForFourDays(selectedCity):
    data = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                        params={'q': selectedCity, 'units': 'metric', 'lang': 'ru', 'APPID': API_TOKEN}).json()

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
    outputText = ""

    for key in rightDays:
        if counter == 3:    # Для отметки нового дня
            outputText += rightDays[key]['dt_txt'][8:10] + " " + MONTHS[int(rightDays[key]['dt_txt'][5:7])] + '\n'
            counter = 0

        if key == 0 or key == 3 or key == 6 or key == 9:
            outputText += "Утром      "
        elif key == 1 or key == 4 or key == 7 or key == 10:
            outputText += "Днём        "
        elif key == 2 or key == 5 or key == 8 or key == 11:
            outputText += "Вечером  "

        outputText += str(round(rightDays[key]['main']['temp'])) + "° "
        weather = rightDays[key]['weather'][0]['description'].capitalize()
        outputText += addEmojiWeather(weather)

        counter += 1

        if key == 2 or key == 5 or key == 8 or key == 11:
            outputText += "\n"

    return outputText


# Создаёт меню с кнопками
def createMarkup():
    item1 = types.KeyboardButton('Текущий прогноз')
    item2 = types.KeyboardButton('Прогноз на 4 дня')
    item3 = types.KeyboardButton('Выбрать другой город')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(item1, item2, row_width=2)
    markup.add(item3)
    return markup


# Добавляет к погоде соответствующий смайлик
def addEmojiWeather(weather):
    match weather:
        case 'Ясно': return '☀ ' + weather + '\n'
        case 'Пасмурно': return '☁ ' + weather + '\n'
        case 'Дождь': return '🌧 ' + weather + '\n'
        case 'Облачно с прояснениями': return '🌦 ' + 'Обл. с прояс-ми' + '\n'
        case 'Переменная облачность': return '🌥 ' + 'Переменная обл.' + '\n'
        case 'Небольшой дождь': return '🌧 ' + weather + '\n'
        case 'Небольшая облачность': return '🌤 ' + 'Небольшая обл.' + '\n'
        case 'Небольшой снег': return '🌨 ' + weather + '\n'
        case 'Снег': return '🌨 ' + weather + '\n'
        case _: return weather + '\n'   # Default


# Записывает в журнал все действия пользователей
def writeUserAction(name, username, idUser, text=""):
    timeNow = str(datetime.datetime.now())[:-7]

    if username is None:
        username = ''
    import codecs

    with codecs.open(journalDir + 'journal.txt', 'a', encoding='utf-8') as f:   # 'a' - ключ добавления в файл
        f.write(timeNow + ' | ' + username + ' ' + name + " (ID " + str(idUser) + ") | " + text + "\n")


def checkKey(message):
    if message.from_user.id == getAdminID() and message.json['text'] == getKey():
        file = open(journalDir + 'journal.txt', 'rb')
        BOT.send_document(message.from_user.id, file)
        file.close()
        return True
    return False


# Определяет город по геопозиции
def cityDefinition(message):
    latitude = str(message.location.latitude)
    longitude = str(message.location.longitude)
    geolocator = Nominatim(user_agent="my_request")

    if 'village' in geolocator.reverse(latitude + ', ' + longitude).raw['address'].keys():
        return geolocator.reverse(latitude + ', ' + longitude).raw['address']['village']
    elif 'town' in geolocator.reverse(latitude + ', ' + longitude).raw['address'].keys():
        return geolocator.reverse(latitude + ', ' + longitude).raw['address']['town']
    else:   # Если не получилось определить город, возвратим пустую строку
        return ''
