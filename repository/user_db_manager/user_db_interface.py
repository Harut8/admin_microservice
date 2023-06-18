import uuid
from abc import abstractmethod, ABCMeta
from typing import Union
from asyncpg import Record



class UserDbInterface(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    async def get_user_from_db(username) -> Record:
        ...

