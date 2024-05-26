from aiogram import Router
from aiogram.filters import Command, StateFilter
from utils import *
from settings import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from config import config
from db import *

# Инициализация бота
TKN = config.BOT_TOKEN
router: Router = Router()
storage: MemoryStorage = MemoryStorage()


# команда /admin
@router.message(Command(commands=['admin']))
async def admin(msg: Message, state: FSMContext):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['admin'])
    await state.set_state(FSM.msg_to_admin)


# команда /cancel
@router.message(Command(commands=['cancel']), StateFilter(FSM.msg_to_admin))
async def cancel(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await bot.delete_message(chat_id=user, message_id=msg.message_id)
    await bot.edit_message_text(chat_id=user, message_id=msg.message_id-1, text=lexicon['cancel'])
    await state.clear()


# сообщение админу
@router.message(StateFilter(FSM.msg_to_admin))
async def to_admin(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # отправить админу
    user_txt = f"<i>{msg.text}</i>"
    msg_to_admin = f'📩 Сообщение от {contact_user(msg.from_user)}:\n{user_txt}'
    for ad in admins:
        await bot.send_message(text=msg_to_admin, chat_id=ad, parse_mode='HTML')

    # уведомить юзера
    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await bot.delete_message(chat_id=user, message_id=msg.message_id)
    await bot.edit_message_text(chat_id=user, message_id=msg.message_id-1,
                                text=lexicon['admin_sent']+user_txt, parse_mode='HTML')
    await state.clear()

