import os
from dataclasses import dataclass
from environs import Env
from settings import prod


@dataclass
class Config:
    project_path: str = os.path.abspath(os.path.dirname(__file__))
    BOT_TOKEN: str = None           # телеграм бот

    # LLM API
    GROQ_API_KEY: str = None
    MISTRAL_API_KEY: str = None
    OPENAI_API_KEY: str = None
    llm_limit: int = None           # лимит токенов в день
    img_limit: int = None           # лимит фото в день

    # DB
    host: str = None                # хост
    dbname: str = None              # имя базы данных
    user: str = None                # пользователь
    password: str = None            # пароль
    port: int = None                # порт

    # Payments
    PayMaster: str = None


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    BOT_TOKEN=env('BOT_TOKEN_PROD') if prod else env('BOT_TOKEN_TEST'),

    GROQ_API_KEY=env('GROQ_API_KEY'),
    MISTRAL_API_KEY=env('MISTRAL_API_KEY'),
    OPENAI_API_KEY=env('OPENAI_API_KEY'),
    llm_limit=env.int('llm_limit'),
    img_limit=env.int('img_limit'),

    host=env('host'),
    dbname=env('dbname'),
    user=env('user'),
    password=env('password'),
    port=env.int('port'),

    PayMaster=env('PayMaster') if prod else env('PayMaster_Test')
)

