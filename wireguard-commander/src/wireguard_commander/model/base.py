import loggate
from typing import TypeVar, Type

from pydantic import BaseModel, Field, PrivateAttr
from duckdb.duckdb import DuckDBPyConnection, ParserException

T = TypeVar('T', bound='BaseDbModel')


class BaseDbModel(BaseModel):
    _TABLE: str = PrivateAttr('---')
    _SQL_SUBQUERY: str = PrivateAttr('')

    id: int
    logger: object = None
    # field(init=False, metadata={
    #     'store': False,
    #     'serializable': False
    # })

    @classmethod
    def __subclasscheck__(cls, subclass):
        print(cls.__name__)
        print(subclass.__name__)
        cls.logger = loggate.get_logger(cls.__class__.__name__)

    @classmethod
    def gets(cls: Type[T], db: DuckDBPyConnection, query: str = '1 = 1',
             *args) -> [T]:
        print(cls.logger)
        try:
            res = db.execute(
                f"SELECT f.*{cls._SQL_SUBQUERY} "
                f"FROM {cls._TABLE} f "
                f"WHERE {query}",
                args,
            ).fetchall()
        except ParserException as ex:
            cls.logger.error(
                f"SELECT f.*{cls._SQL_SUBQUERY} "
                f"FROM {cls._TABLE} f "
                f"WHERE {query}; {args}"
            )
            raise ex
        column_names = [desc[0] for desc in db.description]
        return [cls(**dict(zip(column_names, it))) for it in res]

    @classmethod
    def get(cls: Type[T], db: DuckDBPyConnection, query: str | int, *args) -> T:
        if isinstance(query, int) and len(args) == 0:
            args = [query]
            query = f'id=$1'
        res = db.execute(
            f"SELECT f.*{cls._SQL_SUBQUERY} "
            f"FROM {cls._TABLE} f "
            f"WHERE {query}",
            args,
        ).fetchone()
        column_names = [desc[0] for desc in db.description]
        if res is None:
            return None
        return cls(**dict(zip(column_names, res)))

