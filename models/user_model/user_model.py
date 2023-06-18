import datetime
import re
import uuid
from enum import Enum
from typing import Union, Any
from pydantic import BaseModel, Field, validator, ValidationError, validate_email


class UserInfo(BaseModel):
    """DATA CLASS USED FOR RETURNING INFO AFTER CHECKING PASSWORD
       WITH THIS WE CREATE TOKENS"""
    admin_id: Union[str, uuid.UUID]
    admin_password: str
    admin_login: str


class Language(Enum):
    ru = 'ru'
    en = 'en'
    hy = 'hy'


class PaymentListEnum(Enum):
    type_card_buyed = 'bycard'
    type_transfer_buyed = 'bytransfer'
    type_all = 'allbuyed'
    type_in_order = 'inorder'


class PaymentListView(BaseModel):
    order_id: uuid.UUID
    order_summ: int
    cass_stantion_count: int
    mobile_cass_count: int
    mobile_manager_count: int
    web_manager_count: int
    order_curr_type: int
    order_date: datetime.datetime
    order_ending: datetime.datetime
    c_name: str
    c_contact_name: str
    c_phone: str
    c_email: str
    c_inn: str
    c_address: str
