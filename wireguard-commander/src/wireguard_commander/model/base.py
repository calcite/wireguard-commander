import logging

from attrs import define, field

@define(kw_only=True)
class Base(object):
    __sql_subquery__ = ''

    id: int = field(default=None)
    logger: logging.Logger = field(init=False, metadata={
        'store': False,
        'serializable': False
    })


    @classmethod
    async def gets(cls, db, query: str, *args):
        res = await db.fetch(
            f"SELECT f.*{cls.__sql_subquery__} "
            f"FROM {cls.__tablename__} f "
            f"WHERE {query}",
            *args,
        )
        if res:
            return [cls(**dict(it.items())) for it in res]
        return []

    @classmethod
    async def get(cls, db, query: str | int, *args):
        if isinstance(query, int) and len(args) == 0:
            query = f'id={query}'
        res = await db.fetchrow(
            f"SELECT f.*{cls.__sql_subquery__} "
            f"FROM {cls.__tablename__} f "
            f"WHERE {query}",
            *args,
        )
        if res:
            return cls(**dict(res.items()))
        return None

    def __attrs_post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
