import json
import asyncpg
from fastapi import Depends, Query
from typing import TypeVar, Optional, List
from pydantic import BaseModel, Field
from asyncpg import Connection

from models import ConstrainError, ObjectNotFound
from libs.db import DBConnection


class BasePModel(BaseModel):
    id: int

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id


class CommonQueryParams(BaseModel):
    """
    This is common query class for gets method.
    """
    offset: int = Query(0, ge=0)
    limit: int = Query(0, ge=0, le=1000)
    sort_by: str = Query('f.id', regex="^[a-zA-Z0-9\\.]*$")


def query_params(params: CommonQueryParams = Depends()):
    return params.dict()


# Get Pydantic type
G = TypeVar('G', bound=BasePModel)      # Full pydantic object
C = TypeVar('C', bound=BaseModel)       # Create pydantic object
U = TypeVar('U', bound=BaseModel)      # Update pydantic object


class BaseDBModel:
    class Meta:
        db_table = 'unknow'
        sql_subquery = ''
        PYDANTIC_CLASS = BasePModel
        DEFAULT_SORT_BY: str = 'id'
        reload_after_create: bool = False

    def __init_subclass__(cls, **kwargs):
        if handler := getattr(cls.Meta, 'onchange_handler', None):
            if not callable(handler):
                handler = getattr(cls, handler)
            DBConnection.register_notification(cls.Meta.db_table, handler)
        if handler := getattr(cls.Meta, 'onstart_handler', None):
            if not callable(handler):
                handler = getattr(cls, handler)
            DBConnection.register_startup(handler)

    @staticmethod
    def get_object(cls, row):
        # for key, val in row.items():
        #     if cls.model_fields[key]
        return cls(**row)

    @classmethod
    async def get(cls, db: Connection, query: str | int | G, *args, **kwargs) -> Optional[G]:
        _cls = kwargs.pop('_cls', cls)
        _raise = kwargs.pop('_raise', False)
        _sub_sql = kwargs.pop('_sub_sql', getattr(_cls.Meta, 'sub_sql', ''))
        _sub_columns = kwargs.pop('_sub_columns', getattr(_cls.Meta, 'sub_columns', ''))
        group_by = kwargs.pop('_group_by', getattr(_cls.Meta, 'group_by', ''))
        _pydantic_class = kwargs.pop('_pydantic_class', getattr(_cls.Meta, 'PYDANTIC_CLASS', _cls.Meta.PYDANTIC_CLASS))
        _db_table = getattr(_cls.Meta, 'db_view', getattr(_cls.Meta, 'db_table', ''))
        if isinstance(query, _pydantic_class):
            return query
        if isinstance(query, int) and len(args) == 0:
            args = [query]
            query = 'f."id"=$1'
        if _sub_columns:
            _sub_columns = f', {_sub_columns}'
        _post_sql = ' '
        if group_by:
            _post_sql += f' GROUP BY {",".join(group_by)}'
        if row := await db.fetchrow(
            f'SELECT f.* {_sub_columns} FROM "{_db_table}" f {_sub_sql} WHERE {query} {_post_sql}',
            *args
        ):
            return cls.get_object(_pydantic_class, row)
        elif not _raise:
            return None
        else:
            raise ObjectNotFound(
                f'Object {_cls.__name__} not found: {query} ({args}).'
            )

    @classmethod
    async def gets(cls, db: Connection, query='1=1', *args, offset: int = 0,
                   limit: int = 0, sort_by='', **kwargs) -> List[G]:
        _cls = kwargs.pop('_cls', cls)
        _sub_sql = kwargs.pop('_sub_sql', getattr(_cls.Meta, 'sub_sql', ''))
        _sub_columns = kwargs.pop('_sub_columns', getattr(_cls.Meta, 'sub_columns', ''))
        _pydantic_class = kwargs.pop('_pydantic_class', getattr(_cls.Meta, 'PYDANTIC_CLASS', object))
        _db_table = getattr(_cls.Meta, 'db_view', getattr(_cls.Meta, 'db_table', ''))
        group_by = kwargs.pop('_group_by', getattr(_cls.Meta, 'group_by', ''))
        if not sort_by and hasattr(_cls.Meta, 'DEFAULT_SORT_BY'):
            sort_by = getattr(_cls.Meta, 'DEFAULT_SORT_BY')
        _post_sql = ' '
        if limit:
            _post_sql += f' LIMIT {limit}'
        if offset:
            _post_sql += f' OFFSET {offset}'
        if group_by:
            _post_sql += f' GROUP BY {",".join(group_by)}'
        if sort_by:
            _post_sql += f' ORDER BY {sort_by}'
        if _sub_columns:
            _sub_columns = f', {_sub_columns}'

        rows = await db.fetch(
            f'SELECT f.* {_sub_columns} FROM "{_db_table}" f {_sub_sql} '
            f'WHERE {query} {_post_sql};',
            *args
        )
        return [cls.get_object(_pydantic_class, row) for row in rows]

    @classmethod
    def json_encoder(obj):
        return obj

    @classmethod
    async def update(cls, db: Connection, obj: str | int | G, update: U, *args, **kwargs) -> G:
        _cls = kwargs.pop('_cls', cls)
        obj = await _cls.get(db, obj, *args, _raise=True)
        if hasattr(_cls, 'pre_update'):
            await _cls.pre_update(db, obj, update, **kwargs)
        columns, values = ([], [])
        fields = update.__class__.model_fields
        fields.update(update.__class__.model_computed_fields)
        for key, meta in fields.items():
            val = getattr(update, key)
            ext = getattr(meta, 'json_schema_extra', None) or {}
            if not ext.get('no_save', False) and getattr(obj, key, None) != val:
                ix = len(values) + 1
                columns.append(f'"{key}" = ${ix}')
                if isinstance(val, dict) or isinstance(val, list):
                    values.append(json.dumps(val, default=_cls.json_encoder))
                else:
                    values.append(val)
                setattr(obj, key, val)
        if not values:
            return obj
        try:
            await db.execute(
                f'UPDATE "{_cls.Meta.db_table}" SET {",".join(columns)} WHERE id = {obj.id}',
                *values
            )
        except asyncpg.exceptions.IntegrityConstraintViolationError as e:
            raise ConstrainError(str(e))
        if hasattr(_cls, 'post_update'):
            await _cls.post_update(db, obj, **kwargs)
        return obj

    @classmethod
    async def create(cls, db: Connection, create: C, **kwargs) -> G:
        _cls = kwargs.pop('_cls', cls)
        _reload_after_create = kwargs.pop('_reload_after_create',
                                          getattr(_cls.Meta, 'reload_after_create', False))
        if hasattr(_cls, 'pre_create'):
            await _cls.pre_create(db, create, **kwargs)
        columns, values, indexes = ([], [], [])
        fields = create.__class__.model_fields
        fields.update(create.__class__.model_computed_fields)
        for key, meta in fields.items():
            val = getattr(create, key)
            ext = getattr(meta, 'json_schema_extra', None) or {}
            if not ext.get('no_save', False):
                columns.append(f'"{key}"')
                if isinstance(val, dict) or isinstance(val, list):
                    values.append(json.dumps(val, default=_cls.json_encoder))
                else:
                    values.append(val)
                indexes.append(f'${len(values)}')
        try:
            row = await db.fetchrow(
                f'INSERT INTO "{_cls.Meta.db_table}"  ({",".join(columns)}) '
                f'VALUES ({",".join(indexes)}) RETURNING *;',
                *values
            )
            data = dict(**row)
            if hasattr(_cls, 'post_sql_create'):
                await _cls.post_sql_create(db, data, create, **kwargs)
        except asyncpg.exceptions.IntegrityConstraintViolationError as e:
            raise ConstrainError(str(e))
        if not _reload_after_create:
            obj = _cls.Meta.PYDANTIC_CLASS(**data)
        else:
            obj = await _cls.get(db, data['id'])
        if hasattr(_cls, 'post_create'):
            await _cls.post_create(db, obj, create, **kwargs)
        return obj

    @classmethod
    async def delete(cls, db: Connection, obj: int | G, **kwargs):
        _cls = kwargs.pop('_cls', cls)
        obj = await _cls.get(db, obj)
        if hasattr(_cls, 'pre_delete'):
            await _cls.pre_delete(db, obj, **kwargs)
        result = (await db.execute(
            f'DELETE FROM "{_cls.Meta.db_table}" WHERE id = $1;',
            obj.id
        )).startswith("DELETE ")
        if not result:
            raise ObjectNotFound(
                f'Object {_cls.__name__} not found: {obj}')
        if hasattr(_cls, 'post_delete'):
            await _cls.post_delete(db, obj, **kwargs)

    @classmethod
    def convert_object(cls, obj, toClass) -> BaseModel:
        params = {}
        for k, m in toClass.model_fields.items():
            params[k] = getattr(obj, k, m.default)
        return toClass(**params)

    @classmethod
    async def create_or_update(cls, db: Connection, create: C, keys: List[str],
                               update: U, **kwargs):
        _cls = kwargs.get('_cls', cls)
        q = list()
        vals = list()
        for ix, key in enumerate(keys):
            q.append(f'"{key}" = ${ix+1}')
            vals.append(getattr(create, key, None))
        if obj := await cls.get(db, ' AND '.join(q), *vals):
            # Update
            # print(update, issubclass(update, object))
            if issubclass(update, object):
                # U is class
                update = cls.convert_object(create, update)
            return await _cls.update(db, obj, update, **kwargs)
        return await _cls.create(db, create, **kwargs)

