import utils  # Свой модуль с функциями

lastMessageBot = {}   # Последнее сообщения бота
city = ''   # Город, по которому будет отсылаться запрос на сайт


# Обработчик на команду /start
@utils.BOT.message_handler(commands=['start'])
def start(message):
    utils.write_user_action(message.from_user.full_name, message.chat.username, message.from_user.id, "Clicked /start")
    utils.remove_message(chat_id=message.from_user.id, message_id=message.message_id)  # Удаляем сообщение пользователя
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
    utils.remove_message(chat_id=message.from_user.id, message_id=message.message_id)   # Удаляем сообщение пользователя
    global city, lastMessageBot

    if utils.check_key(message):  # Проверка по ключу на получение журнала действий пользователей
        quit()

    if message.chat.type == 'private':    # Если это личное сообщение

        if message.text == 'Текущий прогноз' and city != '':
            utils.write_user_action(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Clicked on the current forecast')
            weather_text = utils.current_forecast(city)

            try:
                utils.remove_message(message.chat.id, lastMessageBot.id)   # Удаляем сообщение бота
            except:
                pass

            lastMessageBot = utils.BOT.send_message(message.from_user.id, text=weather_text,
                                                    reply_markup=utils.create_markup())

            """ # Пока не работает
            BOT.edit_message_text(chat_id=message.chat.id, message_id=lastMessageBot.id,
                                 text=weatherText, reply_markup=createMarkup())
            """

        elif message.text == 'Прогноз на 4 дня' and city != '':
            utils.write_user_action(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Clicked on the four-day forecast')
            weather_text = utils.forecast_for_four_days(city)

            try:
                utils.remove_message(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
            except:
                pass

            lastMessageBot = utils.BOT.send_message(message.from_user.id, text=weather_text,
                                                    reply_markup=utils.create_markup())

        elif message.text == 'Выбрать другой город' and city != '':
            utils.write_user_action(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Clicked to select another city')

            try:
                utils.remove_message(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
            except:
                pass

            lastMessageBot = utils.BOT.send_message(message.chat.id, 'Напиши город 🏙\nИли отправь свою геопозицию 🌍')

        else:  # Если пользователь не ввёл текст кнопок (ввёл предположительно город)
            user_text = message.json['text'].capitalize()
            utils.write_user_action(message.from_user.full_name, message.chat.username, message.from_user.id,
                                  'Sent a text "{0}"'.format(message.text))

            try:
                utils.remove_message(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
            except:
                pass

            if utils.city_check(user_text):    # Если пользователь ввёл корректное название города
                city = user_text
                lastMessageBot = utils.BOT.send_message(message.chat.id, 'Вы выбрали город {0}'.format(city),
                                                        reply_markup=utils.create_markup())
            else:
                lastMessageBot = utils.BOT.send_message(message.chat.id, 'Я не знаю городов с таким названием 😒\n'
                                                                         'Напиши другой город или '
                                                                         'отправь другую геопозицию!')


# Обработчик на геопозицию
@utils.BOT.message_handler(content_types=["location"])
def location(message):
    utils.write_user_action(message.from_user.full_name, message.chat.username, message.from_user.id, "Sent geolocation")

    global city, lastMessageBot
    city = utils.city_definition(message)

    try:
        utils.remove_message(message.chat.id, lastMessageBot.id)  # Удаляем сообщение бота
    except:
        pass

    if city:    # Если город выбран
        lastMessageBot = utils.BOT.send_message(message.chat.id, 'Вы выбрали город {0}'.format(city),
                                                reply_markup=utils.create_markup())
    else:
        lastMessageBot = utils.BOT.send_message(message.chat.id, 'Я не смог определить город по вашей метке 😒\n'
                                                                 'Напиши другой город или '
                                                                 'отправь другую геопозицию!')

    utils.remove_message(chat_id=message.from_user.id, message_id=message.message_id)  # Удаляем сообщение пользователя


utils.BOT.polling(none_stop=True)
