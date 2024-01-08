import configparser    # Для парсинга файлов

config = configparser.ConfigParser()
config.read('bot.ini', encoding='utf-8')


# Возвращает строку с токеном бота
def get_bot_token():
    return str(config['set']['BOT_TOKEN'])


# Возвращает строку с API токеном сайта погоды
def get_api_token():
    return str(config['set']['API_TOKEN'])


def get_admin_id():
    return int(config['set']['ADMIN_ID'])


# Возвращает строку с секретным ключом
def get_key():
    return str(config['set']['KEY'])
