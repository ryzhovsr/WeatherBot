import utils  # Свой модуль с функциями

lastMessageBot = {}   # Последнее сообщения бота
city = ''   # Город, по которому будет отсылаться запрос на сайт


# Обработчик на команду /start
@utils.BOT.message_handler(commands=['start'])
def start(message):
    utils.writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id, "Clicked /start")
    utils.removeMessage(chatID=message.from_user.id, messageID=message.message_id)  # Удаляем сообщение пользователя
    global city, lastMessageBot
    lastMessageBot = utils.BOT.send_message(message.chat.id, ('Привет, {0.first_name}! 😃\n'
                                                              'Я умею прогнозировать погоду.\n'
                                                              'Просто напиши город 🏙\n'
                                                              'Или отправь свою геопозицию 🌍'
                                                              .format(message.from_user)))


# Обработчик на любое текстовое сообщение
# (func=lambda message: True) для edit_message_text
@utils.BOT.message_handler(func=lambda message: True, content_types=['text'])
def bot_message(message):
    utils.removeMessage(chatID=message.from_user.id, messageID=message.message_id)   # Удаляем сообщение пользователя
    global city, lastMessageBot

    if utils.checkKey(message):  # Проверка по ключу на получение журнала действий пользователей
        quit()

    if message.chat.type == 'private':    # Если это личное сообщение

        if message.text == 'Текущий прогноз' and city != '':
            utils.writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Clicked on the current forecast')
            weatherText = utils.currentForecast(city)

            try:
                utils.removeMessage(message.chat.id, lastMessageBot.id)   # Удаляем сообщение бота
            except:
                pass

            lastMessageBot = utils.BOT.send_message(message.from_user.id, text=weatherText,
                                                    reply_markup=utils.createMarkup())

            """ # Пока не работает
            BOT.edit_message_text(chat_id=message.chat.id, message_id=lastMessageBot.id,
                                 text=weatherText, reply_markup=createMarkup())
            """

        elif message.text == 'Прогноз на 4 дня' and city != '':
            utils.writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Clicked on the four-day forecast')
            weatherText = utils.forecastForFourDays(city)

            try:
                utils.removeMessage(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
            except:
                pass

            lastMessageBot = utils.BOT.send_message(message.from_user.id, text=weatherText,
                                                    reply_markup=utils.createMarkup())

        elif message.text == 'Выбрать другой город' and city != '':
            utils.writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Clicked to select another city')

            try:
                utils.removeMessage(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
            except:
                pass

            lastMessageBot = utils.BOT.send_message(message.chat.id, 'Напиши город 🏙\nИли отправь свою геопозицию 🌍')

        else:  # Если пользователь не ввёл текст кнопок (ввёл предположительно город)
            userText = message.json['text'].capitalize()
            utils.writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Sent a text "{0}"'.format(message.text))

            try:
                utils.removeMessage(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
            except:
                pass

            if utils.cityCheck(userText):    # Если пользователь ввёл корректное название города
                city = userText
                lastMessageBot = utils.BOT.send_message(message.chat.id, 'Вы выбрали город {0}'.format(city),
                                                        reply_markup=utils.createMarkup())
            else:
                lastMessageBot = utils.BOT.send_message(message.chat.id, 'Я не знаю городов с таким названием 😒\n'
                                                                         'Напиши другой город или '
                                                                         'отправь другую геопозицию!')


# Обработчик на геопозицию
@utils.BOT.message_handler(content_types=["location"])
def location(message):
    utils.writeUserAction(message.from_user.full_name, message.chat.username, message.from_user.id, "Sent geolocation")

    global city, lastMessageBot
    city = utils.cityDefinition(message)

    try:
        utils.removeMessage(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
    except:
        pass

    if city:    # Если город выбран
        lastMessageBot = utils.BOT.send_message(message.chat.id, 'Вы выбрали город {0}'.format(city),
                                                reply_markup=utils.createMarkup())
    else:
        lastMessageBot = utils.BOT.send_message(message.chat.id, 'Я не смог определить город по вашей метке 😒\n'
                                                                 'Напиши другой город или '
                                                                 'отправь другую геопозицию!')

    utils.removeMessage(chatID=message.from_user.id, messageID=message.message_id)  # Удаляем сообщение пользователя


utils.BOT.polling(none_stop=True)
