from typing import ClassVar, Dict

from pydantic import BaseModel, Field, PrivateAttr
from duckdb.duckdb import DuckDBPyConnection

from model.server import Server


class Worker(BaseModel):
    INSTANCES: ClassVar[Dict[str, 'Worker']] = {}

    name: str
    hostname: str
    port: int
    secret: str

    def __init__(self, /, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__class__.INSTANCES[self.name] = self

    @classmethod
    def get(cls, name: str):
        return cls.INSTANCES.get(name)

    @classmethod
    def gets(cls):
        return cls.INSTANCES.copy()

    def get_servers(self, db: DuckDBPyConnection):
        return Server.gets(db, 'worker=$1', self.name)

