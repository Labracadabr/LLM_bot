import time
import schedule
import asyncio
from db import set_col
from datetime import datetime


# корректировка по часовому поясу. например если на устройстве gmt+3, то превратить 22 в '01'
def gmt_shift(hour: int) -> str:
    gmt = int(-(time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) / 60 / 60)  # часовой пояс компа
    hour = str((hour + gmt) % 24).zfill(2)
    return hour


# ежедневная задача
async def daily_task():
    print("Running daily_task")
    # обнулить дневной учет токенов
    set_col(key='tkn_today', val=0)


# внести задачу в расписание: раз в сутки, часы указаны в gmt 0
def schedule_daily_task():
    schedule.every().day.at(f"{gmt_shift(0)}:00").do(asyncio.create_task, daily_task())


# каждые s секунд проверять, не настало ли время
async def run_schedule():
    s = 3
    while True:
        schedule.run_pending()
        await asyncio.sleep(s)

