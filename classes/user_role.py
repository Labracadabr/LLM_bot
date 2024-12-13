from enum import Enum


# класс ролей юзеров - для выдачи доступов и прочего
class UserRole(Enum):
    USER_FREE = "user_free"
    USER_PREM = "user_prem"
    ADMIN = "admin"
    BANNED = "banned"

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __str__(self):
        return self.value


# test
if __name__ == '__main__':
    role = UserRole('user_premium')
    print(role, type(role))  # user_premium <enum 'UserRole'>
    print(role.value, type(role.value))  # user_premium <class 'str'>
