import uuid

from auth.auth import decode_token
from uuid import UUID
from repository.user_db_manager.user_db_manager import UserDbManager
from models.user_model.user_model import UserInfo, PaymentListEnum, PaymentListView
from typing import Union

from service.redis_client.redis_client import RedisClient
from service.user_service_manager.user_service_interface import UserServiceInterface
from service.url_token_generators.token_creator import create_token_for_email_verify, generate_url_for_email_verify
from mailing.verify_mailing.send_account_verify_link import send_email_verify_link
from mailing.verify_mailing.send_account_recovery_code import send_account_recovery_code
from asyncpg import Record


language_dict = {
        "ru": 1,
        "en": 2,
        "hy": 3
    }


class UserServiceManager(UserServiceInterface):

    @staticmethod
    async def get_user_from_db(*, username) -> Union[UserInfo, None]:
        try:
            user_info = await UserDbManager.get_user_from_db(username=username)
            if user_info:
                return UserInfo(**user_info)
            return
        except Exception as e:
            raise e

    @staticmethod
    async def get_companies(admin_id, search):
        _dillers = await UserDbManager.get_dillers()
        _companies = await UserDbManager.get_companies(admin_login=admin_id, search=search)
        return_data = {i["d_id"]: [] for i in _dillers}
        if _companies and _dillers:
            for i in _companies:
                return_data[i["c_diller_id"]] += [i.items()]
            for i in _dillers:
                return_data[i["d_name"]] = return_data.pop(i["d_id"])
        elif _dillers:
            return_data = {i["d_name"]: [] for i in _dillers}
        else:
            return
        return return_data

    @staticmethod
    async def get_company_and_tarif_by_id(company_id):
        _company_and_tarif_ = await UserDbManager.get_company_and_tarif_by_id(company_id)
        _devices = await UserDbManager.get_used_device_count(company_id)
        if _company_and_tarif_ or _devices:
            return {"tarifes": _company_and_tarif_, "used_device": _devices}

    @staticmethod
    async def block_tarif_for_company(order_id, admin_login):
        _is_blocked = await UserDbManager.block_tarif_for_company(order_id, admin_login)
        if _is_blocked:
            return True
        return

    @staticmethod
    async def enable_tarif_for_company(order_id, admin_login):
        _is_enable = await UserDbManager.enable_tarif_for_company(order_id, admin_login)
        if _is_enable:
            return True
        return

    @classmethod
    def __create_list_of_payment(cls, info_):
        return [
            PaymentListView(
                order_id=i["order_id"],
                order_summ=i["order_summ"],
                cass_stantion_count=i["cass_stantion_count"],
                mobile_cass_count=i["mobile_cass_count"],
                mobile_manager_count=i["mobile_manager_count"],
                web_manager_count=i["web_manager_count"],
                order_curr_type=i["order_curr_type"],
                order_date=i["order_date"],
                order_ending=i["order_ending"],
                c_name=i["c_name"],
                c_contact_name=i["c_contact_name"],
                c_phone=i["c_phone"],
                c_email=i["c_email"],
                c_inn=i["c_inn"],
                c_address=i["c_address"],
            )
            for i in info_
        ]

    @staticmethod
    async def get_payment_list(type_of_payment: PaymentListEnum):
        match type_of_payment:
            case type_of_payment.type_transfer_buyed:
                info_ = await UserDbManager.get_payments_for_view(
                    order_state=(True, False),
                    order_curr_type=(0,)
                )
                if info_ is not None:
                    return UserServiceManager.__create_list_of_payment(info_)
                return
            case type_of_payment.type_card_buyed:
                info_ = await UserDbManager.get_payments_for_view(
                    order_state=(True, False),
                    order_curr_type=(1,)
                )
                if info_ is not None:
                    return UserServiceManager.__create_list_of_payment(info_)
                return
            case type_of_payment.type_in_order:
                info_ = await UserDbManager.get_payments_for_view(
                    order_state=(False,),
                    order_curr_type=(0, 1)
                )
                if info_ is not None:
                    return UserServiceManager.__create_list_of_payment(info_)
                return
            case type_of_payment.type_all:
                info_ = await UserDbManager.get_payments_for_view(
                    order_state=(True, False),
                    order_curr_type=(0, 1, 2)
                )
                if info_ is not None:
                    return UserServiceManager.__create_list_of_payment(info_)
                return
            case _:
                return