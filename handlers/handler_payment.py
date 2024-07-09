from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from utils import *
from settings import *
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from config import config
from db import *

# Инициализация
router: Router = Router()

# prices
PRICE = types.LabeledPrice(label='Subscription 1 month', amount=220 * 100)


# команда /pay
@router.message(Command(commands=['pay']))
async def pay(msg: Message, state: FSMContext, bot: Bot, ):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text)

    language = get_user_info(user=user).get('lang')
    lexicon = load_lexicon(language)

    if prod:
        await msg.answer('Реальный платеж')
    else:
        await msg.answer('Тестовый платеж')

    await bot.send_invoice(chat_id=msg.from_user.id,
                           title='title',
                           description='description',
                           provider_token=config.PayMaster,
                           currency='RUB',
                           payload='test_invoice_payload',
                           start_parameter='one-month',
                           prices=[types.LabeledPrice(label='Subscription', amount=220 * 100)],
                           )


# обработка платежа
@router.pre_checkout_query(lambda x: True)
async def pre_checkout(msg: types.PreCheckoutQuery, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await log(logs, user, 'pre_checkout_query')

    await bot.answer_pre_checkout_query(msg.id, ok=True)


# successful payment
@router.message(F.content_type.in_(('successful_payment', )))
async def successful_payment(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await log(logs, user, "successful_payment")
    print(msg.model_dump_json(exclude_none=True, indent=2, round_trip=True))


