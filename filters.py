from aiogram.filters import Filter
from aiogram.types import Message
from tgbot.roles import UserRole


# Фильтр, проверяющий доступ юзера
class CustomFilter(Filter):
    def __init__(self, access: list or UserRole):
        self.required_roles = access if isinstance(access, list) else [access]

    async def __call__(self, message: Message, **data) -> bool:
        user_data = data['user_data']
        role = UserRole(user_data.get('role'))
        approved: bool = user_data.get('role_approved')
        return role in self.required_roles and approved

