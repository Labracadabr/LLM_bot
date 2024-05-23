
from datetime import datetime
from settings import prod
import psycopg2
from functools import wraps
from config import config

tables = {
    'users': 'users' if prod else 'users_test',
    # 'tasks': 'tasks' if prod else 'tasks_test',
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
def table_exists(cursor) -> bool:
    cursor.execute("select * from information_schema.tables where table_name=%s", ('mytable',))
    bool(cursor.rowcount)
    result = bool(cursor.rowcount)
    print(f'Table {tables["users"]} exists:', result)
    return result


# создать таблицу
@postgres_decorator
def create_table(cursor):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {tables['users']} (
                                user_id BIGINT PRIMARY KEY,
                                model VARCHAR(255),
                                first_start TIMESTAMP,
                                tg_username VARCHAR(255),
                                tg_fullname VARCHAR(255),
                                lang_tg VARCHAR(10),
                                lang VARCHAR(10),
                                status VARCHAR(255),
                                actions INTEGER,
                                balance INTEGER
    );"""
    res = cursor.execute(create_table_query)
    print(f"Table {tables['users']} created")


# создать запись нового юзера и вернуть их новое количество
@postgres_decorator
def new_user(cursor, user, **kwargs) -> int:
    extra_s = ", ".join(["%s" for i in range(len(kwargs))])
    fields = ", ".join([i for i in kwargs.keys()])
    values = tuple(f"'{i}'" for i in [user] + list(kwargs.values()))
    print(f'{extra_s = }')
    print(f'{fields = }')
    print(f'{values = }')

    query = f"""INSERT INTO {tables['users']} (user_id, {fields}) VALUES (%s, {extra_s});""" % values
    print(f'{query = }')
    cursor.execute(query)
    print(f"[INFO] user {user} added")

    # проверить сколько юзеров в базе стало
    cursor.execute(f"SELECT COUNT(*) FROM {tables['users']}")
    return cursor.fetchone()[0]


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
def set_user_info(cursor, user: str, key_vals: dict) -> bool:
    # создать строку запроса
    set_str = ", ".join([f"{key} = %s" for key in key_vals.keys()])
    upd_req = f"UPDATE {tables['users']} SET {set_str} WHERE user_id = %s"

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


# перевести из json в sql
@postgres_decorator
def migrate_users(cursor, data):
    flag = False
    bad_users = []
    for user in data:

        if isinstance(data[user], list):
            data[user] = data[user][0]
        # Convert the datetime object to the appropriate format for PostgreSQL
        start_date = data[user]['first_start']
        date_time_obj = datetime.strptime(start_date, '%d/%m/%Y %H:%M')
        data[user]['first_start'] = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')

        # data[user]['project'] = 'so_dev'

        key_vals = {k: v for k, v in data[user].items() if v is not None}
        # создать строку запроса
        set_str = ", ".join([key for key in key_vals.keys()])
        # создать кортеж значений
        values = (user,) + tuple(val for val in key_vals.values())
        print(f'values: {values} / user: {user}')
        try:
            cursor.execute(f"INSERT INTO {tables['users']} (user_id, {set_str}) VALUES ({', '.join('%s' for _ in values)});", values)
        except Exception as e:
            print(e)
            bad_users.append(user)
            continue

        print(f"user {user} inserted")
    print('migrate_users ok')
    print('bad:')  # ['522853308', '992863889', '5109029500', '5337342772', '901159774', '639770334', '5239029846']
    print(bad_users)

# # получить список юзеров по критериям
# @postgres_decorator
# def get_users_list(cursor, query: str) -> list:
#     cursor.execute(f"SELECT {', '.join(keys)} FROM users WHERE user_id = {user}")

if not table_exists():
    create_table()

if __name__ == '__main__':
    pass

    uuid = '13'
    # count_user = new_user(user=uuid, tg_username='biba', tg_fullname='boba', lang_tg='en', lang='fr')
    # print(f'{count_user = }')
    print(get_user_info(user=uuid))
    print(delete_user(user=uuid))
    print(get_user_info(user=uuid))

    # user_upd = {
    #     'tg_fullname': 'biba',
    #     'lang': 'tr',
    #     'lang_tg': 'ru',
    #     'tg_username': 'qwertr',
    # }
    # set_user_info(user=uuid, key_vals=user_upd)
    # #
    # attributes = get_user_info(user=uuid)
    # print(attributes)
