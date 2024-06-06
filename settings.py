prod = True
# prod = False
print(f'{prod = }')

# список языков UI бота
available_languages = ('ru', 'en')

# словарь моделей {frontend name: backend name}
llm_list = {
    'llama3-70b': 'llama3-70b-8192',
    # 'llama3-8b': 'llama3-8b-8192',
    'mixtral-8x7b': 'mixtral-8x7b-32768',
    'codestral': 'codestral-latest',
}

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
