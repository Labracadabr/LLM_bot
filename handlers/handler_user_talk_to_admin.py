import aiogram.exceptions
from aiogram import Router, Bot, F, types
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, or_f
from utils import *
import keyboards
from settings import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, URLInputFile
from config import config
from db import *
from api_integratoins.api_groq import send_chat_request, system_preset, custom_markup_to_html

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
    await bot.edit_message_text(chat_id=user, message_id=msg.message_id-1, text=lexicon['cancel'])


# сообщение админу
@router.message(StateFilter(FSM.msg_to_admin))
async def to_admin(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # отправить админу
    msg_to_admin = f'📩 Сообщение от {contact_user(msg.from_user)}:\n{msg.text}'
    for ad in admins:
        await bot.send_message(text=msg_to_admin, chat_id=ad, parse_mode='HTML')

    # уведомить юзера
    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await bot.edit_message_text(chat_id=user, message_id=msg.message_id-1, text=lexicon['admin_sent'])
    await state.clear()
