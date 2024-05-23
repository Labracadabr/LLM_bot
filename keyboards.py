from aiogram.types import InlineKeyboardButton as Button, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from settings import llm_list

# языки
lang_rus = Button(text='🇷🇺 Русский', callback_data='ru')
lang_eng = Button(text='🇬🇧 English', callback_data='en')
# lang_ind = Button(text='🇮🇩 Indonesia', callback_data='id')

# LLM модели
llm_btns = [KeyboardButton(text=model, callback_data=model) for model in llm_list]

# списки кнопок
vars_copy = vars().copy()
lang_btn_list = list([vars_copy[i]] for i in vars_copy if i.startswith('lang'))

# клавиатуры из таких кнопок
keyboard_lang = InlineKeyboardMarkup(inline_keyboard=lang_btn_list, resize_keyboard=True)
keyboard_llm = ReplyKeyboardMarkup(keyboard=[llm_btns], resize_keyboard=True)
