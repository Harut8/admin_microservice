import datetime
import uuid
from datetime import timedelta
from typing import Union

from pydantic import BaseModel


class UserView(BaseModel):
    """DATA CLASS FOR CREATING MODEL IN GET_CURRENT_USER FUNCTION"""
    admin_id: Union[str, uuid.UUID]
    admin_login: str


class PayloadToken(BaseModel):
    exp: datetime.datetime
    sub: Union[str, uuid.UUID]
