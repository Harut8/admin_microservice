import uuid
from typing import Union

from auth.auth import get_hashed_password
from repository.core.core import DbConnection, fetch_row_transaction, insert_row_transaction, fetch_transaction, \
    execute_delete_query
from dataclasses import dataclass
from repository.user_db_manager.user_db_interface import UserDbInterface
from asyncpg import Record


@dataclass
class UserDbManager(UserDbInterface):

    @staticmethod
    async def get_user_from_db(*, username) -> Record:
        _user_info = await fetch_row_transaction(
            """select admin_id, admin_password, admin_login from admin_table where admin_login = $1""",
            username)
        return _user_info

    @staticmethod
    async def get_user_from_db_by_uuid(uuid):
        _user_info = await fetch_row_transaction(
            """select admin_id, admin_login from admin_table where admin_id = $1""",
            uuid)
        return _user_info

    @staticmethod
    async def get_dillers():
        try:
            _dillers = await fetch_transaction(
                """select d.d_name, d.d_id from diller d order by d.d_id;"""
            )
            return _dillers
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def get_companies(admin_login, search: str):
        try:
            if search.isdigit():
                search_from = "c_inn"
            else:
                search_from = "c_name"
            _info = await fetch_transaction(
                f"""
                                    with cte as (
                                    select c_id,
                                    
                                    case
                                    when (select * from (select pt2.permission_id = 1 as tip from admin_table at2
                                        join privilege_table pt on at2.admin_privilege = pt.privilege_id
                                        join permission_table pt2 on pt2.permission_id = pt.privilege_type
                                        where at2.admin_login=$1) s where tip in (true)) then c_unique_id
                                    else 0
                                    end as c_unique_id, c_diller_id, c_name, c_contact_name, c_phone, c_email, c_inn, c_address,
                                    row_number () over(partition by c.c_diller_id order by c.c_diller_id) as numer from company c)
                                    select c_id,
                                    c_unique_id,
                                    c_diller_id,
                                    c_name,
                                    c_contact_name,
                                    c_phone,
                                    c_email,
                                    c_inn,
                                    c_address,
                                    numer, port
                                    from cte left join device_port on unique_id_cp = c_unique_id where {search_from} like $2;
                                    """,
                admin_login,
               '%'+ search+'%'
            )
            return _info
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def get_company_and_tarif_by_id(company_id):
        _info = await fetch_transaction("""
                    select distinct soat.order_id, soat.order_summ, soat.order_date pay_date,
    soat.cass_stantion_count, soat.mobile_cass_count, soat.mobile_manager_count, soat .web_manager_count,
    (select curr_name from curr_types where curr_id = soat.order_curr_type) as curr_type,
    case
    	when soat.order_state then (select ct.start_license from client_tarif ct where ct.c_t_id = soat.company_id and ct.c_t_tarif_id = soat.tarif_id_fk )
    	else null
    end start_license,
    case
    	when soat.order_state then (select ct.end_license from client_tarif ct where ct.c_t_id = soat.company_id and ct.c_t_tarif_id = soat.tarif_id_fk )
    	else null
    end end_license
    from saved_order_and_tarif soat
    left join client_tarif ct on ct.c_t_id = soat.company_id
    where soat.company_id = $1
                    """, company_id)
        return _info

    @staticmethod
    async def get_used_device_count(company_id):
        product_id_table = {
            1: 'cass_stantion_count',
            2: 'mobile_cass_count',
            3: 'web_manager_count',
            4: 'mobile_manager_count'
        }
        _devices = await fetch_transaction("""
                    with cte2 as (
                    select count(*), l.product_id_fk  from licenses l
                    where l.unique_id_cp = (select c.c_unique_id  from company c where c.c_id = $1)
                    group by l.product_id_fk order by l.product_id_fk )
                    select * from cte2;
                    """, company_id)
        return [{product_id_table[i["product_id_fk"]]: i["count"]} for i in _devices]

    @staticmethod
    async def block_tarif_for_company(order_id, admin_login):
        _permission = await fetch_row_transaction(
                """select * from check_permission($1)""",
                admin_login
                                        )
        if _permission["check_permission"] != 1:
            return
        await fetch_transaction(
                """UPDATE saved_order_and_tarif set order_state = false where order_id = $1;""", order_id)
        return 1

    @staticmethod
    async def enable_tarif_for_company(order_id, admin_login):
        _permission = await fetch_row_transaction(
            """select * from check_permission($1)""",
            admin_login
        )
        if _permission["check_permission"] != 1:
            return
        await fetch_transaction(
            """
            UPDATE saved_order_and_tarif set order_state = true where order_id = $1;
            """, order_id)
        return 1

    @staticmethod
    async def get_payments_for_view(*, order_state: tuple[bool], order_curr_type: tuple):
        _info = await fetch_transaction("""
                    select order_id,
                    c_name, c_contact_name, c_phone, c_email, c_inn, c_address,
                           order_summ,
                           cass_stantion_count,
                           mobile_cass_count,
                           mobile_manager_count,
                           web_manager_count,
                           order_curr_type,
                           order_date,
                           order_ending,
                           order_state
                    from saved_order_and_tarif soat
                    join company cp on cp.c_id = soat.company_id
                    where order_state = ANY($1::bool[])
                    and order_curr_type = ANY($2::int[])
                    order by order_date desc
                    """, order_state, order_curr_type)
        return _info

