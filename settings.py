import os
prod = True
# prod = False
print(f'{prod = }')

# список языков UI бота
available_languages = ('ru', 'en')

# спи
llm_list = [
    'llama3-70b-8192',
    'llama3-8b-8192',
    'mixtral-8x7b-32768',
]

# команды бота
commands = {
    "/start": "Запуск бота",
    "/delete_context": "Удалить контекст беседы",
    "/model": "Выбрать нейросеть",
    "/help": "Помощь",
    "/language": "Сменить язык",
}

# Список id админов
dima = "992863889"
admins: list[str] = [dima]

# где хранятся данные
logs = 'logs.tsv'  # тсв с логами
users_data = 'users_data'  # папка с данными юзеров


# выбор языка. на входе языковой код (по дефолту en), на выходе словарь с лексикой этого языка
def load_lexicon(language: str) -> dict[str:str]:
    if language not in available_languages:
        language = 'en'
    lexicon_module = __import__(f'lexic.{language}', fromlist=[''])
    return lexicon_module.lexicon


def check_missing_keys(languages):
    lexic_keys_sets = []
    for lang in languages:
        lexic_keys_sets.append(set(load_lexicon(language=lang).keys()))

    # find the set with missing keys
    alert = 'Отсутствует лексика в языке:'
    for i, keys in enumerate(lexic_keys_sets):
        missing_keys = lexic_keys_sets[i-1] - keys
        if missing_keys:
            alert += f'\n{languages[i]}: {missing_keys}'

    if '\n' in alert:
        return alert
    return None


# проверить все ли на месте
def check_files():
    os.makedirs(users_data, exist_ok=True)
    file_list = [logs]
    for file in file_list:
        if not os.path.isfile(file):
            if file.endswith('json'):
                with open(file, 'w', encoding='utf-8') as f:
                    print('Отсутствующий файл создан:', file)
                    print('{}', file=f)
            elif file.endswith('sv'):
                with open(file, 'w', encoding='utf-8') as f:
                    print('Отсутствующий файл создан:', file)
                    print('\t'.join(('Time', 'User', 'Action')), file=f)

            elif 'tasks' in file:
                print()
                exit(f"Ошибка! Отсутствует файл с заданиями {file}")

    missing_keys = check_missing_keys(languages=available_languages)
    print(missing_keys if missing_keys else 'OK')


check_files()
