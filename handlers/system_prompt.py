from aiogram import Router
from aiogram.filters import Command, StateFilter
from utils import *
from settings import *
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import db

router: Router = Router()


# команда /system
@router.message(Command(commands=['system']))
async def system(msg: Message, state: FSMContext):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = db.get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['system'])
    await state.set_state(FSM.system_prompt)


# команда /cancel
@router.message(Command(commands=['cancel']), StateFilter(FSM.system_prompt))
async def cancel(msg: Message, bot: Bot, state: FSMContext):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # удалить промпт
    db.set_user_info(user=user, key_vals={'sys_prompt': ''})

    # уведомить
    language = db.get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await bot.delete_message(chat_id=user, message_id=msg.message_id)
    await bot.edit_message_text(chat_id=user, message_id=msg.message_id-1, text=lexicon['cancel'])
    await state.clear()


# юзер задал системный промпт
@router.message(StateFilter(FSM.system_prompt))
async def system_ok(msg: Message, bot: Bot, state: FSMContext):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)
    system_prompt = msg.text

    # сохранить в бд
    db.set_user_info(user, key_vals={'sys_prompt': system_prompt})

    # уведомить юзера
    language = db.get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await bot.delete_message(chat_id=user, message_id=msg.message_id)
    await bot.edit_message_text(chat_id=user, message_id=msg.message_id-1,
                                text=lexicon['system_ok']+system_prompt, parse_mode='HTML')
    await state.clear()

