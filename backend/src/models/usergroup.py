from datetime import datetime
from typing import Optional, Set
from libs.db import DBConnection, Connection
from config import get_config
from models.base import BaseDBModel, BasePModel, BaseModel, Field, Connection

KEYCLOAK_ADMIN_ROLE = get_config('KEYCLOAK_ADMIN_ROLE')


class UserGroupLite(BasePModel):
    id: int
    name: str = Field(max_length=75)
    permissions: set[str] = Field(default_factory=set)
    description: Optional[str] = Field(None, max_length=75)


class UserGroup(UserGroupLite):
    realm_role: Optional[str] = Field(None, max_length=75)
    is_default: Optional[bool] = Field(default=False)
    is_assignable: bool = Field(default=True)
    is_admin: Optional[bool] = Field(default=False)
    created_at: Optional[datetime] = Field(default=None)


class UserGroupUpdate(BaseModel):
    name: str = Field( max_length=75)
    description: Optional[str] = Field(None, max_length=75)
    realm_role: Optional[str] = Field(None, max_length=75)
    # permissions: set[str] = Field(default_factory=set(), exclude=True)


class UserGroupCreate(UserGroupUpdate):
    pass


# Database model class with asyncpg integration
class UserGroupDB(BaseDBModel):

    class Meta:
        db_table = 'usergroup'
        PYDANTIC_CLASS = UserGroup
        DEFAULT_SORT_BY: str = 'name'

    # @DBConnection.register_startup
    # @staticmethod
    # async def init(db: Connection):
    #     await db.execute(f'''
    #         INSERT INTO "usergroup" ("name", "description", "realm_role", "is_assignable", "is_admin")
    #         VALUES ('Admins', 'Application administrators', NULL, false, true)
    #         ON CONFLICT ("is_admin") DO NOTHING;

    #         INSERT INTO "usergroup" ("name", "description", "is_assignable", "is_default")
    #         VALUES ('Generic', 'Default user group', false, true)
    #         ON CONFLICT ("is_default") DO NOTHING;
    #     ''')

    @classmethod
    async def load_permissions(cls, db: Connection, usergroups: Set[UserGroup]):
        pass
        # ids = {}
        # for usergroup in usergroups:
        #     ids[usergroup.id] = usergroup
        #     if usergroup.is_default:
        #         usergroup.permissions = {'user:authenticated'}
        #     if usergroup.is_admin:
        #         usergroup.permissions = {'admin:all'}
                # return
        # rows = await db.fetch(
        #     'SELECT p.* FROM "usergroup_network_permission" p WHERE p."usergroup_id" = ANY($1::int[])',
        #     list(ids.keys())
        # )
        # for row in rows:
        #     ids[row['usergroup_id']].permissions.add(f'network:{row["network_id"]}:{row["permission"]}')
