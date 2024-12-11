import asyncio
import json
import base64
from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
import os
from settings import *
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, FSInputFile, User
from aiogram import Bot
from datetime import datetime
from config import config

# Инициализация бота
TKN = config.BOT_TOKEN
bot_func: Bot = Bot(token=TKN)


# Фильтр, проверяющий доступ юзера
class Access(BaseFilter):
    # фильтр принимает список со строками id
    def __init__(self, access: list[str]) -> None:
        self.access = access

    # вернуть True если юзер в списке
    async def __call__(self, message: Message) -> bool:
        user_id_str = str(message.from_user.id)
        return user_id_str in self.access


# Фильтр, проверяющий принадлежность текста сообщения к списку
class InList(BaseFilter):
    # фильтр принимает список со словами
    def __init__(self, array: list[str]) -> None:
        self.array = array

    async def __call__(self, message: Message) -> bool:
        return message.text in self.array


# Состояния FSM, в которых будет находиться бот в разные моменты взаимодействия с юзером
class FSM(StatesGroup):
    msg_to_admin = State()            # ожидание сообщения админу
    system_prompt = State()            # ожидание системного промпта


# запись логов в tsv, консоль и тг канал
async def log(file, key, item):
    t = str(datetime.now()).split('.')[0]
    log_text = '\t'.join((t, str(key), repr(item)))

    # сохранить в tsv
    try:
        with open(file, 'a', encoding='utf-8') as f:
            print(log_text, file=f)
    except Exception as e:
        log_text += f'\n🔴Ошибка записи в tsv:\n{e}'

    # дублировать логи в консоль
    print(log_text)
    # дублировать логи в тг-канал
    # if log_channel_id:
    #     try:
    #         await bot_func.send_message(chat_id=log_channel_id, text=log_text.replace(t, ''))
    #     except Exception as e:
    #         print('channel error', e)


# айди из текста
def id_from_text(text: str) -> str:
    user_id = ''
    for word in text.split():
        if word.lower().startswith('id'):
            for symbol in word:
                if symbol.isnumeric():
                    user_id += symbol
            break
    return user_id


# написать имя и ссылку на юзера, даже если он без username
def contact_user(user: User) -> str:
    tg_url = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
    text = f'{tg_url} id{user.id} @{user.username}'
    return text


# получить значение
def get_context(filename: str, key: str):
    path = f'{users_data}/{filename}.json'
    if os.path.exists(path):
        # прочитать бд
        with open(path, 'r', encoding='utf-8') as f:
            user_data: dict = json.load(f)
    else:
        user_data: dict = {}
    value = user_data.get(key)
    return value


# задать значение
def set_context(filename: str, key: str, val):
    path = f'{users_data}/{filename}.json'

    if os.path.exists(path):
        # прочитать бд
        with open(path, 'r', encoding='utf-8') as f:
            user_data: dict = json.load(f)
    else:
        user_data: dict = {}
    old_val = user_data.get(key)

    # сохр изменение
    user_data[key] = val
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)
    print(filename, f'edited {key = }')
    # print(user, f'{key}: {old_val} => {val}')


# удалить контекст и перезаписать системное сообщение
def delete_context(context_filename: str, user_data: dict, stream=True):
    from api_integrations.api_llm import system_message
    language = user_data.get('lang')
    sys_prompt = user_data.get('sys_prompt')

    # o-1 не поддерживает system_message
    model = user_data.get('model')
    if model == 'o-1':
        conversation_history = []
        stream = False
    else:
        conversation_history = [system_message(language, extra=sys_prompt)]

    set_context(context_filename, 'messages', conversation_history)
    if stream:
        set_context(context_filename, 'stream', True)


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


# сохранить json в удобно читаемый вид
def save_json(data: dict, filename: str):
    if not filename.endswith('.json'):
        filename += '.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(filename, 'saved')


# скачать файл из телеграм
async def bot_download(file_id: str, msg: Message, bot: Bot, path) -> None:
    # todo user id + lexicon
    delete = await msg.answer(text='Loading...')
    await bot.download(file=file_id, destination=path)
    await bot.delete_message(chat_id=msg.from_user.id, message_id=delete.message_id)


# закодировать фото для отправки запроса
def encode_image(image_path: str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

