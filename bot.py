import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from handlers import ai, admin, user_talk_to_admin, payment, system_prompt, commands
from config import config
import settings
from utils import check_files
from schedules import run_schedule, schedule_daily_task
from aiogram.client.default import DefaultBotProperties


async def main():
    # Инициализация бота
    storage: MemoryStorage = MemoryStorage()
    bot: Bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp: Dispatcher = Dispatcher(storage=storage)
    await on_start(bot=bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(commands.router)
    dp.include_router(admin.router)
    dp.include_router(payment.router)
    dp.include_router(system_prompt.router)
    dp.include_router(user_talk_to_admin.router)
    dp.include_router(ai.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=False)  # False > бот ответит на апдейты, присланные за время откл
    await dp.start_polling(bot)


# при запуске: создать команды в меню и написать ссылку в консоль
async def on_start(bot: Bot) -> None:
    command_list = [BotCommand(command=item[0], description=item[1]) for item in settings.commands.items()]
    await bot.set_my_commands(commands=command_list)
    print('Команды созданы:', len(command_list), 'шт')

    # ссылка на бота
    bot_info = await bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}"
    print(f'{bot_link = }')

    check_files()


async def start_all():
    schedule_daily_task()
    await asyncio.gather(run_schedule(), main())


if __name__ == '__main__':
    asyncio.run(start_all())
