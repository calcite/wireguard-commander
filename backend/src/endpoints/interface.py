from typing import List
import loggate
from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel

from config import get_config
from libs.helpers import get_yaml
from models.base import query_params
from models.user import User
from libs.keycloak import get_me
from models.interface import InterfaceDB, Interface, InterfaceUpdate, InterfaceCreate
from libs.db import db_pool, DBPool

router = APIRouter(tags=["interface"])
sql_logger = 'sql.interface'
logger = loggate.getLogger('Interface')
PERMISSION_DEFINITIONS = get_config('PERMISSION_DEFINITIONS')
permissions = get_yaml(PERMISSION_DEFINITIONS)['permissions']['network']


@router.get("/permissions")
async def permissions_list(_user: User = Security(get_me)):
    _user.test_permission('admin:all')
    return permissions


@router.get("/", response_model=List[Interface])
async def gets(q_params: dict = Depends(query_params),
               pool: DBPool = Depends(db_pool),
               _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        return await InterfaceDB.gets(db,  **q_params)


@router.get("/{interface_id}", response_model=Interface)
async def get(interface_id: int,
              pool: DBPool = Depends(db_pool),
              _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        return await InterfaceDB.get(db, interface_id)


@router.put("/{interface_id}", response_model=Interface)
async def update(interface_id: int,
                 update: InterfaceUpdate,
                 pool: DBPool = Depends(db_pool),
                 _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        res =  await InterfaceDB.update(db, interface_id, update)
        print('A'*80)
        print(res)
        return res


@router.delete("/{interface_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(interface_id: int,
                 pool: DBPool = Depends(db_pool),
                 _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        await InterfaceDB.delete(db, interface_id)


@router.post("/", response_model=Interface,
             status_code=status.HTTP_201_CREATED)
async def create(create: InterfaceCreate,
                 pool: DBPool = Depends(db_pool),
                 _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        return await InterfaceDB.create(db, create)


class FreeIp(BaseModel):
    ip: str


@router.get("/{interface_id}/free_ip", response_model=FreeIp)
async def get_free_ip(interface_id: int,
                      pool: DBPool = Depends(db_pool),
                      _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        iface = await InterfaceDB.get(db, interface_id)
        return FreeIp(
            ip=str((await InterfaceDB.get_free_ips(db, iface)).pop(0))
        )
