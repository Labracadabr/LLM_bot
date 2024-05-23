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
from api_integratoins.api_groq import send_chat_request, system_preset

# Инициализация бота
TKN = config.BOT_TOKEN
router: Router = Router()
storage: MemoryStorage = MemoryStorage()


# команда /start
@router.message(CommandStart())
async def start_command(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user = message.from_user
    msg_time = message.date.strftime('%Y-%m-%d %H:%M:%S')
    user_id = str(user.id)
    await log(logs, user_id, f'start {contact_user(user=user)}')

    # чтение БД
    user_data = get_user_info(user=user_id)

    # язык
    # если это не первый старт - взять язык из памяти
    if user_data:
        language = user_data.get('lang')

    # если первый - использовать язык приложения
    else:
        language = str(message.from_user.language_code).lower()
        print(f'{language = }')
        system_message = {
            "role": "system",
            "content": system_preset.format(language)
        }
        set_pers_json(user_id, 'messages', [system_message])
    lexicon = load_lexicon(language)

    # приветствие
    await message.answer(text=lexicon['start'])

    # создать учетную запись юзера, если её еще нет
    if not user_data:
        await log(logs, user_id, f'adding user {user_id}')
        user = message.from_user
        count_user = new_user(user=user_id, first_start=msg_time, tg_username=user.username,
                              tg_fullname=user.full_name, lang_tg=user.language_code, lang=user.language_code)

        # сообщить админу, кто стартанул бота
        alert = f'➕ user {count_user} {contact_user(user=user)}'
        for i in admins:
            await bot.send_message(text=alert, chat_id=i, disable_notification=True, parse_mode='HTML')

        # логи
        await log(logs, user_id, f'{msg_time}, {user.full_name}, @{user.username}, {user.language_code}')

    # если юзер уже в БД и просто снова нажал старт
    else:
        await log(logs, user.id, f'start_again')


# команда /status
@router.message(Command(commands=['status']))
async def lang(msg: Message):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['status'])


# команда /model
@router.message(Command(commands=['model']))
async def lang(msg: Message):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['model'], reply_markup=keyboards.keyboard_llm)


# юзер выбрал модель
@router.message(InList(llm_list))
async def lang(msg: Message):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)
    model = msg.text.lower()
    print(f'{model = }')

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['model_ok'].format(model), reply_markup=None)


# команда /help
@router.message(Command(commands=['help']))
async def lang(msg: Message):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['help'])


# команда /language
@router.message(Command(commands=['language']))
async def lang(msg: Message):
    user = str(msg.from_user.id)
    await msg.answer('Выберите язык / Choose language', reply_markup=keyboards.keyboard_lang)
    await log(logs, user, msg.text)


# юзер выбрал язык
@router.callback_query(lambda x: x.data in available_languages)
async def lng(msg: CallbackQuery, bot: Bot):
    user = str(msg.from_user.id)
    language = msg.data

    # сохранить значение
    set_user_info(user=user, key_vals={'lang': language})
    # language = get_user_info(user=user, key='lang').get('lang')
    lexicon = load_lexicon(language)

    # уведомить о смене
    await bot.send_message(chat_id=user, text=lexicon["lang_ok"].format(language.upper()))
    await log(logs, user, f'language: {language}')


# команда delete_context > спросить языки
@router.message(or_f(Command('delete_context')))
async def delete_context(msg: Message, state: FSMContext):
    await log(logs, msg.from_user.id, msg.text)
    user = str(msg.from_user.id)
    language = get_user_info(user=user).get('lang')

    # удалить контекст
    system_message = {
        "role": "system",
        "content": system_preset.format(language)
    }
    set_pers_json(user, 'messages', [system_message])

    # ответ
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['delete_context'])


# юзер нажал какую-то кнопку
@router.callback_query(F.data == "какая-то кнопка", StateFilter(FSM.policy))
async def privacy_ok(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user = str(callback.from_user.id)
    await log(logs, user, 'button_ok')
    language = get_user_info(user=user, keys=['lang']).get('lang')
    lexicon = load_lexicon(language)

    await bot.send_message(chat_id=user, text='ok')
    await state.clear()


# юзер что-то пишет
@router.message(F.content_type.in_({'text'}))
async def usr_txt1(msg: Message, bot: Bot):
    user = str(msg.from_user.id)
    await log(logs, user, f'#q: {msg.text}')
    await bot.send_chat_action(chat_id=user, action='typing')

    # read disk
    conversation_history: list = get_pers_json(user, 'messages')
    new_msg = {"role": "user", "content": msg.html_text}
    print(f'{new_msg = }')
    conversation_history += [new_msg]
    set_pers_json(user, 'messages', conversation_history)

    # LLM api
    response = send_chat_request(conversation=conversation_history)
    answer = response.get('choices')[0]['message']['content']

    # result
    await log(logs, user, f'#a: {answer}')
    await msg.answer(answer, parse_mode='MarkdownV2')

