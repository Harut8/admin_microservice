import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from fastapi.security import OAuth2PasswordRequestForm

from models.user_model.user_model import PaymentListEnum
from service.user_service_manager.user_service_manager import UserServiceManager
from starlette import status
from starlette.responses import RedirectResponse
from auth.auth import \
    get_current_user,\
    verify_password,\
    check_refresh_token,\
    create_access_token,\
    create_refresh_token,\
    get_hashed_password


admin_router = APIRouter(tags=["ADMIN API"], prefix="/admin")


@admin_router.get('/ping')
async def user_ping():
    return {"status": "ADMIN PINGING"}


@admin_router.post("/signin")
async def user_login(user_info: OAuth2PasswordRequestForm = Depends()):
    user = await UserServiceManager.get_user_from_db(username=user_info.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    hashed_pass = user.admin_password
    if not verify_password(user_info.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user.admin_id),
        "refresh_token": create_refresh_token(user.admin_id),
    }


@admin_router.get('/company')
async def get_companies(
        q: Annotated[str, Query( regex=r'^[a-zA-Z0-9]*$')] = '',
        admin_login=Depends(get_current_user)):
    info_ = await UserServiceManager.get_companies(admin_id=admin_login.admin_login, search=q)
    if info_:
        return info_
    raise HTTPException(status_code=400, detail='ERROR', headers={'status': 'ERROR'})


@admin_router.get('/company/{company_id}')
async def get_company_and_tarif(company_id: uuid.UUID, admin_login=Depends(get_current_user)):
    _user_tariff_and_device = await UserServiceManager.get_company_and_tarif_by_id(company_id)
    if _user_tariff_and_device:
        return _user_tariff_and_device
    elif _user_tariff_and_device is None:
        return {}
    raise HTTPException(status_code=400, detail='ERROR', headers={'status': 'ERROR'})


@admin_router.post('/company/tariff/block/{order_id}')
async def block_tarif_for_company(order_id: uuid.UUID, admin_login=Depends(get_current_user)):
    _is_block = await UserServiceManager.block_tarif_for_company(order_id, admin_login.admin_login)
    if _is_block:
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail='ERROR', headers={'status': 'ERROR'})


@admin_router.post('/company/tarif/enable/{order_id}')
async def enable_tarif_for_company(order_id: uuid.UUID, admin_login=Depends(get_current_user)):
    _is_enable = await UserServiceManager.enable_tarif_for_company(order_id, admin_login.admin_login)
    if _is_enable:
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail='ERROR', headers={'status': 'ERROR'})


@admin_router.get('/payment-list')
async def get_payment_list(type_of_payment: PaymentListEnum, admin_login=Depends(get_current_user)):
    info_ = await UserServiceManager.get_payment_list(type_of_payment)
    if info_ is not None:
        return info_
    raise HTTPException(status_code=404, detail='ERROR', headers={'status': 'GET PAYMENT ERROR'})