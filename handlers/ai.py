import aiogram.exceptions
from aiogram import Router, F
from utils import *
from settings import *
from aiogram.types import CallbackQuery, Message
import db
from api_integrations.api_llm import *

router: Router = Router()


# юзер что-то пишет
@router.message(F.content_type.in_({'text'}))
async def usr_txt1(msg: Message, bot: Bot, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)

    # read user data
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

    # send message normally
    if model in not_streamable:
        await bot.send_chat_action(action='typing', chat_id=user)
        response: dict = await send_chat_request(conversation_history, model=llm_list.get(model))
        full_answer = custom_markup_to_html(response.get('choices')[0]['message']['content'])
        last_msg = await msg.answer(full_answer)

    # LLM api stream request
    else:
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
async def usr_img1(msg: Message, bot: Bot, user_data: dict):
    db.save_msg(msg)
    user = str(msg.from_user.id)

    # read user data
    language = user_data.get('lang')
    lexicon = load_lexicon(language)
    tkn_today = user_data['tkn_today'] if user_data['tkn_today'] else 0
    tkn_total = user_data['tkn_total'] if user_data['tkn_total'] else 0

    # не превышен ли лимит
    if user not in admins and tkn_today > config.llm_limit:
        ans = await msg.answer(text=lexicon['limit'])
        db.save_msg(ans)
        return

    # если сообщение без текста
    if not msg.caption:
        ans = await msg.answer(text=lexicon['caption'])
        db.save_msg(ans)
        return

    # скачать фото
    photo_save_path = f'{users_data}/{user}_input.jpg'
    file_id = msg.photo[-1].file_id
    await bot_download(file_id, msg, bot, path=photo_save_path)

    # очистить контекст и создать системный промпт (фото обрабатываются вне основного контекста для экономии)
    context_filename = f'{user}_img'
    delete_context(context_filename, user_data, stream=False)

    # словарь сообщения к отправке
    prompt = msg.caption
    new_msg = user_message(prompt, encode_image(photo_save_path))
    await log(logs, user, f'#qf: {prompt} #file_id: {msg.photo[-1].file_id}')

    # добавить новое сообщение в контекст
    conversation_history: list = get_context(context_filename, 'messages')
    conversation_history += [new_msg]
    set_context(context_filename, 'messages', conversation_history)

    # LLM api request - для фоток модель gpt-4o-mini
    await bot.send_chat_action(chat_id=user, action='typing')
    response: dict = await send_chat_request(conversation=conversation_history, model='gpt-4o-mini')

    # error handling
    if response.get('status_code') != 200:
        ans = await msg.answer(json.dumps(response, indent=2))
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


# юзер отправил войс
@router.message(F.content_type.in_({'voice'}))
async def usr_voice(msg: Message, bot: Bot, user_data: dict):
    # db.save_msg(msg)
    user = str(msg.from_user.id)
    await bot.send_chat_action(chat_id=user, action='typing')
    language = user_data.get('lang')

    # скачать звук
    file_save_path = f'{users_data}/{user}_input.m4a'
    file_id = msg.voice.file_id
    await bot.download(file=file_id, destination=file_save_path)

    # STT api request
    response: dict = transcribe_audio(file_save_path, language)

    # error handling
    if response.get('error') or response.get('status_code') != 200:
        ans = await msg.answer(json.dumps(response, indent=2))
        await log(logs, user, str(response))
        return

    # обновить usage
    pass

    # ответить юзеру
    answer = response.get('text')
    answer_html = custom_markup_to_html(answer)
    ans = await msg.answer(answer_html)
    # db.save_msg(ans)
    await log(logs, user, f'#va: {answer_html}')

