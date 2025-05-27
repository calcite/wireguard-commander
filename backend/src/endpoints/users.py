from fastapi import APIRouter, Depends, Security, status
from libs.db import Pool, db_pool, db_logger
from typing import List
from libs.keycloak import get_me
from models.base import query_params
from models.user import User, UserDB, UserUpdate

router = APIRouter(tags=["users"])
sql_logger = 'sql.users'



@router.get("/", response_model=List[User])
async def user_list(q_params: dict = Depends(query_params),
                    pool: Pool = Depends(db_pool),
                    _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire() as db, db_logger(sql_logger, db):
        users = await UserDB.gets(db, 'disabled IS NOT true', **q_params)
        return users


@router.get("/{user_id}", response_model=User)
async def user_get(user_id: int,
                   pool: Pool = Depends(db_pool),
                   _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire() as db, db_logger(sql_logger, db):
        user = await UserDB.get(db, user_id)
        return user

@router.put("/{user_id}", response_model=User)
async def user_update(user_id: int, update: UserUpdate,
                      pool: Pool = Depends(db_pool),
                      _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire() as db, db.transaction(), db_logger(sql_logger, db):
        return await UserDB.update(db, user_id, update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(user_id: int,
                      pool: Pool = Depends(db_pool),
                      _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire() as db, db.transaction(), db_logger(sql_logger, db):
        await UserDB.delete(db, user_id)


# @router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
# async def user_create(create: UserCreate,
#                       pool: Pool = Depends(db_pool),
#                       _user: User = Security(get_client)):
#     _user.test_permission('admin:all')
#     async with pool.acquire() as db:
#         return await UserDB.create(db, create)

