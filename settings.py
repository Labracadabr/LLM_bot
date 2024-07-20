prod = True
# prod = False
print(f'{prod = }')

# список языков UI бота
available_languages = ('ru', 'en')

# словарь моделей {frontend name: backend name}
llm_list = {
    'mixtral-8x7b': 'mixtral-8x7b-32768',
    'llama3-70b': 'llama3-70b-8192',
    # 'gpt-4o': 'gpt-4o',
    # 'gpt-4o-mini': 'gpt-4o-mini',
    'codestral': 'codestral-latest',
    # 'llama3-8b': 'llama3-8b-8192',
    # 'gpt-3.5': 'gpt-3.5-turbo',
}
default_llm = 'llama3-70b'

# команды бота
commands = {
    "/delete_context": "Удалить контекст беседы",
    "/language": "Сменить язык",
    "/system": "Задать системный промпт",
    "/model": "Выбрать нейросеть",
    "/status": "Мои траты",
    "/help": "Помощь",
    "/admin": "Отправить сообщение администратору",
}

# Список id админов
dima = "992863889"
admins: list[str] = [dima]

# где хранятся данные
logs = 'logs.tsv'  # тсв с логами
users_data = 'users_data'  # папка с данными юзеров
