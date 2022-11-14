import configparser    # Для парсинга файлов

config = configparser.ConfigParser()
config.read('bot.ini', encoding='utf-8')


# Возвращает строку с токеном бота
def getBotToken():
    return str(config['set']['BOT_TOKEN'])


# Возвращает строку с API токеном сайта погоды
def getApiToken():
    return str(config['set']['API_TOKEN'])


def getAdminID():
    return int(config['set']['ADMIN_ID'])


# Возвращает строку с секретным ключом
def getKey():
    return str(config['set']['KEY'])
