from typing import Dict, Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

import db

# middleware для запроса данных юзера из БД перед выполнением фильтров
class MiddlewareRequestDB(BaseMiddleware):
    async def __call__(self, handler: Callable, event: Message, data: Dict) -> Any:
        # запрос в бд
        user_id = str(event.from_user.id)
        user_data = db.get_user_info(user=user_id)

        # вписать в data
        data['user_data'] = user_data
        return await handler(event, data)

