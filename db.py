import html
from settings import prod
import psycopg2
from functools import wraps
from config import config
from aiogram.types.message import Message
from api_integrations.api_llm import custom_markup_to_html


tables = {
    'users': 'users' if prod else 'users_test',
    'messages': 'messages' if prod else 'messages_test',
    'logs': 'logs' if prod else 'logs_test',
}


# postgres декоратор для обработки ошибок, открытия и закрытия коннекта
def postgres_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # подключение к БД
        conn = psycopg2.connect(host=config.host, dbname=config.dbname, user=config.user, password=config.password)
        conn.autocommit = True

        # исполнение sql запроса
        try:
            with conn.cursor() as cursor:
                result = func(cursor, *args, **kwargs)
                return result
        except ImportError as e:
            print("[INFO] Postgres Error:", e)

        # завершить подключение
        finally:
            conn.close() if conn else None
    return wrapper


# существует ли таблица
@postgres_decorator
def table_exists(cursor, table=None) -> bool:
    pass


# создать таблицу
@postgres_decorator
def create_users_table(cursor, table='users'):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tables[table]} (
                                user_id BIGINT PRIMARY KEY,
                                model VARCHAR(255),
                                first_start TIMESTAMP,
                                tg_username VARCHAR(255),
                                tg_fullname VARCHAR(255),
                                lang_tg VARCHAR(10),
                                lang VARCHAR(10),
                                status VARCHAR(255),
                                actions INTEGER,
                                balance INTEGER,
                                tkn_today INTEGER,
                                tkn_total INTEGER,
                                img_today INTEGER,
                                img_total INTEGER,
                                premium BOOL,
                                role VARCHAR(255)
    );"""
    cursor.execute(create_table_query)
    print(f"Table {tables['users']} created")


# создать таблицу
@postgres_decorator
def create_messages_table(cursor, table='messages'):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tables[table]} (
                                chat BIGINT,
                                msg_id BIGINT,
                                reply_to BIGINT,
                                username VARCHAR(255),
                                text TEXT,
                                unix INTEGER,
                                type VARCHAR(255),
                                bot BOOL,
                                file_id VARCHAR(255)
    );"""
    cursor.execute(create_table_query)
    print(f"Table {tables[table]} created")


# создать запись нового юзера и вернуть их новое количество
@postgres_decorator
def new_user(cursor, user, **kwargs) -> int:
    kwargs['role'] = 'free'
    extra_s = ", ".join(["%s" for i in range(len(kwargs))])
    fields = ", ".join([i for i in kwargs.keys()])
    values = tuple(f"'{i}'" for i in [user] + list(kwargs.values()))

    query = f"""INSERT INTO {tables['users']} (user_id, {fields}) VALUES (%s, {extra_s});""" % values
    print(f'{query = }')
    cursor.execute(query)
    print(f"[INFO] user {user} added")

    # проверить сколько юзеров в базе стало
    cursor.execute(f"SELECT COUNT(*) FROM {tables['users']}")
    return cursor.fetchone()[0]


# сохранить новое сообщение
@postgres_decorator
def save_msg(cursor, msg: Message):
    # внести в бд новые строки
    print(f'inserting msg {msg.message_id}, chat {msg.chat.id}')

    # словарь из Message
    data = {
        'chat': msg.chat.id,
        'msg_id': msg.message_id,
        'username': msg.from_user.username,
        'text': html.escape(msg.text) if msg.text else custom_markup_to_html(msg.caption) if msg.caption else None,
        'reply_to': msg.reply_to_message.message_id if msg.reply_to_message else 0,
        'unix': int(msg.date.timestamp()),
        'type': msg.content_type,
        'bot': msg.from_user.is_bot,
        'file_id': msg.photo[-1].file_id if msg.photo else None,
    }

    # ключи из словаря на входе
    keys = tuple(key for key in data)

    # запрос
    col_names = ', '.join(keys)
    extra_s = ", ".join(["%s" for _ in range(len(data))])
    values = tuple(f"'{i}'" for i in list(data.values()))
    query = f'INSERT INTO {tables["messages"]} ({col_names}) VALUES ({extra_s});' % values
    print(f'{query = }')
    cursor.execute(query)


# получить словарь значений юзера. если юзер не найден - вернет None
@postgres_decorator
def get_user_info(cursor, user: str, keys: list = None) -> dict:
    # если искомые keys не указаны, то запросить все
    if not keys:
        cursor.execute(f"SELECT * FROM {tables['users']} WHERE user_id = %s", (user,))
    else:
        cursor.execute(f"SELECT {', '.join(keys)} FROM {tables['users']} WHERE user_id = %s", (user,))

    row = cursor.fetchone()
    if not row:
        print(f'User {user} not found')
        return None

    return {desc[0]: value for desc, value in zip(cursor.description, row)}


# задать словарем значения юзеру
@postgres_decorator
def set_user_info(cursor, user: str, key_vals: dict, table='users') -> bool:
    # создать строку запроса
    set_str = ", ".join([f"{key} = %s" for key in key_vals.keys()])
    upd_req = f"UPDATE {tables[table]} SET {set_str} WHERE user_id = %s"

    # создать кортеж значений
    values = tuple(val for val in key_vals.values()) + (user,)
    print(f'upd_req: {upd_req} / values: {values} / user: {user}')
    cursor.execute(upd_req, values)
    print(f'User {user} updated')
    return True


# удалить юзера из БД
@postgres_decorator
def delete_user(cursor, user: str):
    cursor.execute(f"DELETE FROM {tables['users']} WHERE user_id = %s", (user,))
    print(f"user {user} DELETED")


@postgres_decorator
def drop_table(cursor, table, ):
    query = f'DROP TABLE {table};'
    print(f'{query = }')

    cursor.execute(query)
    print(f'table {table} deleted')


# задать одно значение на всю колонку
@postgres_decorator
def set_col(cursor, key: str, val: str) -> None:
    # создать строку запроса
    upd_req = f"UPDATE {tables['users']} SET {key} = %s"
    # создать кортеж значений
    values = (val, )
    print(f'upd_req: {upd_req} / values: {values} / col: {key}')
    cursor.execute(upd_req, values)
    print(f'column {key} updated')


# добавить новую колонку
@postgres_decorator
def add_col(cursor, col_name, data_type, table='users') -> None:
    query = f"ALTER TABLE {tables[table]} ADD COLUMN {col_name} {data_type}"
    cursor.execute(query)
    print(f'added {col_name = }')


# данные со всей колонки
@postgres_decorator
def get_col(cursor, col_name, table='users') -> list[tuple]:
    query = f"SELECT {col_name} FROM {tables[table]}"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# на входе список колонок, на выходе список словарей, где словарь = ряд таблицы, ключи = колонки
@postgres_decorator
def get_cols(cursor, cols: list, table, where: dict = None) -> list[dict]:
    # запрос
    col_names = ', '.join(cols)
    query = f'SELECT {col_names} FROM {table}'

    # если указано where, то вернуть один словарь, где значение колонки совпадает значению словаря where
    if where:
        column, value = next(iter(where.items()))
        query += f" WHERE {column} = '{value}';"
    else:
        query += ';'
    print(f'{query = }')

    # ответ
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f'got {len(rows)} rows')

    # превратить в список словарей
    output = []
    for row in rows:
        output.append({cols[i]: row[i] for i in range(len(cols))})

    return output


# задать словарем значения одной существующей строке
@postgres_decorator
def set_row(cursor, where: dict, data_dict: dict, table) -> bool:
    assert len(where) == 1
    row_id = list(where)[0]

    # создать строку запроса
    set_str = ", ".join([f"{key} = %s" for key in data_dict.keys()])
    upd_req = f"UPDATE {table} SET {set_str} WHERE {row_id} = %s"

    # создать кортеж значений
    values = tuple(val for val in data_dict.values()) + (where[row_id],)
    cursor.execute(upd_req, values)
    print(f'row {where} updated')
    return True


if __name__ == '__main__':
    pass

    # drop_table(tables['messages'])
    create_messages_table()
