from pprint import pprint
from aiogram import Router, Bot, F

from filters import CustomFilter
from classes.user_role import UserRole
from utils import *
import db

router: Router = Router()


# админ ответил на сообщение
@router.message(Access(admins), F.reply_to_message)
async def reply_to_msg(msg: Message, bot: Bot):
    db.save_msg(msg)
    admin = str(msg.from_user.id)
    # ответ админа
    admin_response = str(msg.text)
    # сообщение, на которое отвечает админ
    orig = msg.reply_to_message
    # user = вытащить id из текста сообщения
    user = id_from_text(orig.text)

    # ответ юзеру
    language = db.get_user_info(user=user, keys=['lang']).get('lang')
    lexicon = load_lexicon(language)
    text = f"{lexicon['msg_from_admin']}\n\n<i>{admin_response}</i>"

    # если админ тупит
    if not user:
        await bot.send_message(orig.chat.id, 'На это сообщение не надо отвечать')
        await log(logs, admin, 'adm_reply fail')
        return

    # если админ отвечает на сообщение юзера
    elif user:
        await log(logs, user, f'adm_reply: {admin_response}')
        # отпр ответ юзеру и всем админам
        for i in [user]+admins:
            ans = await bot.send_message(chat_id=i, text=text, parse_mode='HTML')
            db.save_msg(ans)


# админ что-то пишет
@router.message(Access(admins), lambda msg: msg.text and msg.text.startswith('!'))
async def adm_msg(msg: Message, bot: Bot):
    db.save_msg(msg)
    admin = str(msg.from_user.id)
    txt = msg.text

    if False:
        pass
    else:
        await msg.answer('Команда не распознана')
        await log(logs, admin, f'wrong_command: \n{txt}')

