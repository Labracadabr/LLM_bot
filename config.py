from dataclasses import dataclass
from environs import Env
from settings import prod


@dataclass
class Config:
    BOT_TOKEN: str = None           # телеграм бот
    GROQ_API_KEY: str = None

    host: str = None                # хост
    dbname: str = None              # имя базы данных
    user: str = None                # пользователь
    password: str = None            # пароль
    port: int = None                # порт

    llm_limit: int = None     # лимит генераций в день


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    BOT_TOKEN=env('BOT_TOKEN_PROD') if prod else env('BOT_TOKEN_TEST'),
    GROQ_API_KEY=env('GROQ_API_KEY'),

    host=env('host'),
    dbname=env('dbname'),
    user=env('user'),
    password=env('password'),
    port=env.int('port'),

    llm_limit=env.int('llm_limit'),
)

