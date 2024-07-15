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
async def start_command(msg: Message, bot: Bot, state: FSMContext):
    db.save_msg(msg)
    await state.clear()
    user = msg.from_user
    msg_time = msg.date.strftime('%Y-%m-%d %H:%M:%S')
    user_id = str(user.id)
    # логи
    await log(logs, user_id, f'/start {msg_time}, {user.full_name}, @{user.username}, {user.language_code}')

    # чтение БД
    user_data = db.get_user_info(user=user_id)

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
    await msg.answer(text=lexicon['start'] + lexicon['help'])


# команда /status
@router.message(Command(commands=['status']))
async def status(msg: Message):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # read db
    user_data = db.get_user_info(user=user)
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
async def model_cmd(msg: Message):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    # какая модель уже выбрана
    user_data = db.get_user_info(user=user)
    model_now = user_data.get('model')

    # показать кнопки с выбором LLM
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['model'].format(model_now), reply_markup=keyboards.keyboard_llm)


# юзер выбрал модель
@router.message(InList(llm_list))
async def model_set(msg: Message):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)
    model = msg.text.lower()

    # сохранить
    db.set_user_info(user, key_vals={'model': model})

    # уведомить
    language = db.get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['model_ok'].format(model) + lexicon['delete_context'], reply_markup=None)


# команда /help
@router.message(Command(commands=['help']))
async def help_(msg: Message):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = db.get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['help'], reply_markup=None)


# команда /language
@router.message(Command(commands=['language']))
async def lang(msg: Message):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    await msg.answer('Выберите язык / Choose language', reply_markup=keyboards.keyboard_lang)
    await log(logs, user, msg.text)


# юзер выбрал язык
@router.callback_query(lambda x: x.data in available_languages)
async def lng(msg: CallbackQuery, bot: Bot):
    db.save_msg(msg)
    user = str(msg.from_user.id)
    language = msg.data

    # сохранить значение
    db.set_user_info(user=user, key_vals={'lang': language})
    # language = get_user_info(user=user, key='lang').get('lang')
    lexicon = load_lexicon(language)

    # удалить контекст и перезаписать системное сообщение
    delete_context(user, db.get_user_info(user=user))

    # уведомить о смене
    await bot.send_message(chat_id=user, text=lexicon["lang_ok"].format(language.upper()) + lexicon['delete_context'])
    await log(logs, user, f'language: {language}')


# команда delete_context
@router.message(or_f(Command('delete_context')))
async def delete_context_(msg: Message):
    db.save_msg(msg)
    await log(logs, msg.from_user.id, msg.text)
    user = str(msg.from_user.id)
    user_data = db.get_user_info(user=user)
    language = user_data.get('lang')

    # удалить контекст и перезаписать системное сообщение
    delete_context(user, user_data)

    # ответ
    lexicon = load_lexicon(language)
    await msg.answer(text=lexicon['delete_context'], reply_markup=None)


# юзер что-то пишет
@router.message(F.content_type.in_({'text'}))
async def usr_txt1(msg: Message, bot: Bot):
    db.save_msg(msg)
    user = str(msg.from_user.id)

    # read user data
    user_data = db.get_user_info(user=user)
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    tkn_today = user_data['tkn_today'] if user_data['tkn_today'] else 0
    tkn_total = user_data['tkn_total'] if user_data['tkn_total'] else 0
    model = user_data.get('model')

    # не превышен ли лимит
    if user not in admins and tkn_today > config.llm_limit:
        ans = await msg.answer(text=lexicon['limit'])
        db.save_msg(ans)
        return

    # работа с текстом
    context_path = f'{user}'
    prompt = msg.html_text
    new_msg = user_message(prompt)

    await log(logs, user, f'#q: {prompt}')
    await bot.send_chat_action(chat_id=user, action='typing')

    # добавить новое сообщение в контекст
    conversation_history: list = get_context(context_path, 'messages')
    conversation_history += [new_msg]
    set_context(context_path, 'messages', conversation_history)

    # LLM api stream request
    first_msg = None
    last_msg = None
    full_answer = ''
    for batch in stream(conversation=conversation_history, model=llm_list.get(model), batch_size=20):
        full_answer += batch
        answer_html = custom_markup_to_html(full_answer)
        try:
            # первый батч отправить новым сообщением
            if not first_msg:
                first_msg = await msg.answer(answer_html)
            # остальные батчи добавлять редактированием первого сообщения
            else:
                last_msg = await bot.edit_message_text(answer_html, user, first_msg.message_id)

        # если сообщение не изменено
        except aiogram.exceptions.TelegramBadRequest:
            pass

    # сохранить ответ LLM в контекст этого юзера
    db.save_msg(last_msg)

    new_msg = {"role": "assistant", "content": full_answer}
    conversation_history += [new_msg]
    set_context(context_path, 'messages', conversation_history)

    # обновить usage - посчитать токены всего контекста "вручную", тк в стриме нет инфо о usage
    usage = sum(count_tokens(txt.get('content')) for txt in conversation_history)
    print(f'{usage = }')
    upd_dict = {
        'tkn_today': usage + tkn_today,
        'tkn_total': usage + tkn_total,
    }
    db.set_user_info(user, key_vals=upd_dict)
    await log(logs, user, f'#a: {full_answer}')


# юзер отправил фото
@router.message(F.content_type.in_({'photo'}))
async def usr_img1(msg: Message, bot: Bot):
    db.save_msg(msg)
    user = str(msg.from_user.id)

    # read user data
    user_data = db.get_user_info(user=user)
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    tkn_today = user_data['tkn_today'] if user_data['tkn_today'] else 0
    tkn_total = user_data['tkn_total'] if user_data['tkn_total'] else 0
    model = user_data.get('model')

    # выбрана ли visual модель
    if model != 'gpt-4o':
        ans = await msg.answer(text=lexicon['not_visual'], reply_markup=keyboards.keyboard_llm)
        db.save_msg(ans)
        return

    # не превышен ли лимит
    if user not in admins and tkn_today > config.llm_limit:
        ans = await msg.answer(text=lexicon['limit'])
        db.save_msg(ans)
        return

    # скачать фото
    photo_save_path = f'{users_data}/{user}_input.jpg'
    await bot_download(msg, bot, path=photo_save_path)

    # очистить контекст и создать системный промпт (фото обрабатываются вне основного контекста для экономии)
    context_path = f'{user}_img'
    delete_context(context_path, user_data, stream=False)

    # словарь сообщения к отправке
    prompt = msg.caption
    new_msg = user_message(prompt, encode_image(photo_save_path))
    await log(logs, user, f'#qf: {prompt} #file_id: {msg.photo[-1].file_id}')

    # добавить новое сообщение в контекст
    conversation_history: list = get_context(context_path, 'messages')
    conversation_history += [new_msg]
    set_context(context_path, 'messages', conversation_history)

    # LLM api request
    await bot.send_chat_action(chat_id=user, action='typing')
    response = await send_chat_request(conversation=conversation_history, model=llm_list.get(model))
    if response.get('status_code') != 200:  # error handling
        await msg.answer(str(response))
        await log(logs, user, str(response))
        return

    # обновить usage
    usage = response.get('usage').get('total_tokens')
    upd_dict = {
        'tkn_today': usage + tkn_today,
        'tkn_total': usage + tkn_total,
    }
    db.set_user_info(user, key_vals=upd_dict)

    # ответить юзеру
    answer = response.get('choices')[0]['message']['content']
    answer_html = custom_markup_to_html(answer)
    ans = await msg.answer(answer_html)
    db.save_msg(ans)
    await log(logs, user, f'#a: {answer_html}')

