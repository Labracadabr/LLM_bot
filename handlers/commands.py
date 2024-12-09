import aiogram.exceptions
from aiogram import Router, F
from aiogram.filters import Command, CommandStart, or_f
from utils import *
import keyboards
from settings import *
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import db
from api_integrations.api_llm import *

router: Router = Router()


# команда /start
@router.message(CommandStart())
async def start_command(msg: Message, bot: Bot, state: FSMContext, user_data: dict):
    db.save_msg(msg)
    await state.clear()
    user = msg.from_user
    msg_time = msg.date.strftime('%Y-%m-%d %H:%M:%S')
    user_id = str(user.id)
    # логи
    await log(logs, user_id, f'/start {msg_time}, {user.full_name}, @{user.username}, {user.language_code}')

    # создать учетную запись юзера, если её еще нет
    if not user_data:
        # сохранить язык приложения tg
        language = str(user.language_code).lower()

        # запись в бд
        count_user = db.new_user(user=user_id, first_start=msg_time, tg_username=user.username, model='llama3-70b',
                              tg_fullname=user.full_name, lang_tg=user.language_code, lang=language)

        # создать первое системное сообщение для чата с LLM
        set_context(user_id, 'messages', [system_message(language)])

        # сообщить админу о новом юзере
        alert = f'➕ user {count_user} {contact_user(user=user)}'
        for i in admins:
            await bot.send_message(text=alert, chat_id=i, disable_notification=True)

    # если юзер уже в БД и просто снова нажал старт
    else:
        # взять язык из памяти
        language = user_data.get('lang')
        print(user_id, 'start_again')

    # приветствие
    lexicon = load_lexicon(language)
    text = lexicon['start'] + lexicon['help']

    # имитация стрима генерации
    first_msg = None
    last_msg = None
    full_answer = ''
    for batch in imitate_stream(text):
        full_answer += batch
        answer_html = custom_markup_to_html(full_answer)
        try:
            # первый батч отправить новым сообщением
            if not first_msg:
                first_msg = await msg.answer(answer_html)
            # остальные батчи добавлять редактированием первого сообщения
            else:
                last_msg = await bot.edit_message_text(answer_html, user_id, first_msg.message_id)

        # если сообщение не изменено
        except aiogram.exceptions.TelegramBadRequest:
            pass

    # сохранить
    db.save_msg(last_msg)


# команда /status
@router.message(Command(commands=['status']))
async def status(msg: Message, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # read db
    tkn_today = user_data['tkn_today'] if user_data['tkn_today'] else 0
    tkn_total = user_data['tkn_total'] if user_data['tkn_total'] else 0

    # answer
    language = db.get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)

    # more info for admin
    if user in admins:
        bot_tkn_today = sum([int(i[0]) for i in db.get_col(col_name='tkn_today', ) if i[0] is not None])
        bot_tkn_total = sum([int(i[0]) for i in db.get_col(col_name='tkn_total', ) if i[0] is not None])
        await msg.answer(text=lexicon['status_adm'].format(tkn_today, bot_tkn_today, tkn_total, bot_tkn_total))
    else:
        await msg.answer(text=lexicon['status'].format(tkn_today, config.llm_limit, tkn_total))


# команда /model
@router.message(Command(commands=['model']))
async def model_cmd(msg: Message, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # какая модель уже выбрана
    model_now = user_data.get('model')

    # показать кнопки с выбором LLM
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['model'].format(model_now), reply_markup=keyboards.keyboard_llm)


# юзер выбрал модель
@router.message(InList(llm_list))
async def model_set(msg: Message, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)
    model = msg.text.lower()

    # сохранить
    db.set_user_info(user, key_vals={'model': model})

    # уведомить
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['model_ok'].format(model) + lexicon['delete_context'], reply_markup=None)


# команда /help
@router.message(Command(commands=['help']))
async def help_(msg: Message, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['help'], reply_markup=None)


# команда /language
@router.message(Command(commands=['language']))
async def lang(msg: Message, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await msg.answer('Выберите язык / Choose language', reply_markup=keyboards.keyboard_lang)
    await log(logs, user, msg.text)


# юзер выбрал язык
@router.callback_query(lambda x: x.data in available_languages)
async def lng(msg: CallbackQuery, bot: Bot, user_data: dict):
    user = str(msg.from_user.id)
    language = msg.data

    # сохранить значение
    db.set_user_info(user=user, key_vals={'lang': language})
    # language = get_user_info(user=user, key='lang').get('lang')
    lexicon = load_lexicon(language)

    # удалить контекст и перезаписать системное сообщение
    delete_context(user, db.get_user_info(user=user))

    # уведомить о смене
    ans = await bot.send_message(chat_id=user, text=lexicon["lang_ok"].format(language.upper()) + lexicon['delete_context'])
    await log(logs, user, f'language: {language}')
    db.save_msg(ans)


# команда delete_context
@router.message(or_f(Command('delete_context')))
async def delete_context_(msg: Message, user_data: dict):
    db.save_msg(msg)
    await log(logs, msg.from_user.id, msg.text)
    user = str(msg.from_user.id)
    language = user_data.get('lang')

    # удалить контекст и перезаписать системное сообщение
    delete_context(user, user_data)

    # ответ
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['delete_context'], reply_markup=None)

