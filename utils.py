import requests     # Для запросов к сайту
import telebot      # Для инициализации и работы с ботом
import datetime     # Для получения текущего времени
import os           # Для получения пути к журналу действий пользователей
from telebot import types   # Для клавиш в меню бота
from geopy.geocoders import Nominatim
# Свой модуль с функциями для чтения конфигурации файла
from configReader import get_bot_token, get_api_token, get_admin_id, get_key


# Constants
BOT_TOKEN = get_bot_token()
API_TOKEN = get_api_token()
BOT = telebot.TeleBot(BOT_TOKEN)
MONTHS = {1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля", 5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа",
          9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"}

# Получаем правильный путь к журналу действий пользователей в зависимости от ОС
if os.name == 'nt':
    journalDir = os.path.join(os.getcwd(), 'UsersActions\\')
else:
    journalDir = os.path.join(os.getcwd(), 'UsersActions/')


# Делает проверку на запросы к сайту погоды с заданным городом (если название города корректное - вернёт True)
def city_check(selected_city):
    query = requests.get('http://api.openweathermap.org/data/2.5/forecast',
                         params={'q': selected_city, 'units': 'metric', 'lang': 'ru', 'APPID': API_TOKEN})
    return query.reason != 'Not Found'


# Удаляет сообщение из чата
def remove_message(chat_id, message_id):
    BOT.delete_message(chat_id=chat_id, message_id=message_id)


# Возвращает текст прогноза погоды на данный момент
def current_forecast(selected_city):
    data = requests.get('http://api.openweathermap.org/data/2.5/find',
                        params={'q': selected_city, 'units': 'metric',
                                'lang': 'ru', 'APPID': API_TOKEN}).json()['list'][0]

    output_text = str(round(data['main']['temp'])) + '° '
    weather = str(data['weather'][0]['description']).capitalize()
    output_text += add_emoji_weather(weather)
    pressure = round(data['main']['pressure'] * 750.06 / 1000)  # Переводи из мБар в мм. рт. ст.
    output_text += 'Давление ' + str(pressure) + ' мм '
    output_text += 'Влажность ' + str(data['main']['humidity']) + ' %\n'
    output_text += 'Ветер ' + str(round(data['wind']['speed'])) + ' м/с \n\n'
    return output_text


# Определяет погоду на 4 дня
def forecast_for_four_days(selected_city):
    data = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                        params={'q': selected_city, 'units': 'metric', 'lang': 'ru', 'APPID': API_TOKEN}).json()

    right_days = {}
    counter = 0

    now = datetime.datetime.now()

    # Цил для нахождения утра/обеда/вечера первых четырёх дней
    for inf in data['list']:
        if str(now.day) == inf['dt_txt'][8:10]:
            continue
        if inf['dt_txt'][11:] == '09:00:00' or inf['dt_txt'][11:] == '12:00:00' or inf['dt_txt'][11:] == '18:00:00':
            right_days[counter] = inf
            counter += 1
        if counter == 12:
            break

    counter = 3     # Чтобы начать с утра
    output_text = ""

    for key in right_days:
        if counter == 3:    # Для отметки нового дня
            output_text += right_days[key]['dt_txt'][8:10] + " " + MONTHS[int(right_days[key]['dt_txt'][5:7])] + '\n'
            counter = 0

        if key == 0 or key == 3 or key == 6 or key == 9:
            output_text += "Утром      "
        elif key == 1 or key == 4 or key == 7 or key == 10:
            output_text += "Днём        "
        elif key == 2 or key == 5 or key == 8 or key == 11:
            output_text += "Вечером  "

        output_text += str(round(right_days[key]['main']['temp'])) + "° "
        weather = right_days[key]['weather'][0]['description'].capitalize()
        output_text += add_emoji_weather(weather)

        counter += 1

        if key == 2 or key == 5 or key == 8 or key == 11:
            output_text += "\n"

    return output_text


# Создаёт меню с кнопками
def create_markup():
    item1 = types.KeyboardButton('Текущий прогноз')
    item2 = types.KeyboardButton('Прогноз на 4 дня')
    item3 = types.KeyboardButton('Выбрать другой город')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(item1, item2, row_width=2)
    markup.add(item3)
    return markup


# Добавляет к погоде соответствующий смайлик
def add_emoji_weather(weather):
    match weather:
        case 'Ясно': return '☀ ' + weather + '\n'
        case 'Пасмурно': return '☁ ' + weather + '\n'
        case 'Дождь': return '🌧 ' + weather + '\n'
        case 'Облачно с прояснениями': return '🌦 ' + 'Обл. с прояснениями' + '\n'
        case 'Переменная облачность': return '🌥 ' + 'Переменная обл.' + '\n'
        case 'Небольшой дождь': return '🌧 ' + weather + '\n'
        case 'Небольшая облачность': return '🌤 ' + 'Небольшая обл.' + '\n'
        case 'Небольшой снег': return '🌨 ' + weather + '\n'
        case 'Снег': return '🌨 ' + weather + '\n'
        case _: return weather + '\n'   # Default


# Записывает в журнал все действия пользователей
def write_user_action(name, username, id_user, text=""):
    time_now = str(datetime.datetime.now())[:-7]

    if username is None:
        username = ''
    import codecs

    with codecs.open(journalDir + 'journal.txt', 'a', encoding='utf-8') as f:   # a - ключ добавления в файл
        f.write(time_now + ' | ' + username + ' ' + name + " (ID " + str(id_user) + ") | " + text + "\n")


def check_key(message):
    if message.from_user.id == get_admin_id() and message.json['text'] == get_key():
        file = open(journalDir + 'journal.txt', 'rb')
        BOT.send_document(message.from_user.id, file)
        file.close()
        return True
    return False


# Определяет город по геопозиции
def city_definition(message):
    latitude = str(message.location.latitude)
    longitude = str(message.location.longitude)
    geolocator = Nominatim(user_agent="my_request")

    if 'village' in geolocator.reverse(latitude + ', ' + longitude).raw['address'].keys():
        return geolocator.reverse(latitude + ', ' + longitude).raw['address']['village']
    elif 'town' in geolocator.reverse(latitude + ', ' + longitude).raw['address'].keys():
        return geolocator.reverse(latitude + ', ' + longitude).raw['address']['town']
    else:   # Если не получилось определить город, возвратим пустую строку
        return ''
