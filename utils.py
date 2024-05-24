import json
from pprint import pprint
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
    msg_to_admin = State()            # Состояние ожидания сообщения админу


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
def get_pers_json(user: str, key: str):
    path = f'{users_data}/{user}.json'
    if os.path.exists(path):
        # прочитать бд
        with open(path, 'r', encoding='utf-8') as f:
            user_data: dict = json.load(f)
    else:
        user_data: dict = {}
    value = user_data.get(key)
    return value


# задать значение
def set_pers_json(user: str, key: str, val):
    path = f'{users_data}/{user}.json'

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
    print(user, f'{key}: {old_val} => {val}')
