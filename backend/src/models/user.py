
from loggate import get_logger
from pydantic import Field, computed_field
from datetime import datetime
from typing import List, Optional, Set

from models import Forbidden
from config import get_config
from libs.helpers import get_yaml
from models.base import BaseDBModel, BasePModel, BaseModel, Connection, C, G

PERMISSIONS = get_config('PERMISSION_DEFINITIONS', wrapper=get_yaml)
KEYCLOAK_ADMIN_ROLE = get_config('KEYCLOAK_ADMIN_ROLE')

logger = get_logger('user')


class User(BasePModel):
    id: int
    name: str
    email: str
    created_at: Optional[datetime]
    last_logged_at: Optional[datetime]
    last_realm_roles: Optional[str]
    permissions: Set[str] = Field(default_factory=set)
    disabled: Optional[bool] = Field(None)

    @computed_field
    def is_admin(self) -> bool:
        return bool(self.last_realm_roles and
                    KEYCLOAK_ADMIN_ROLE in self.last_realm_roles)

    def can(self, permission: str|None = None) -> bool:
        if 'admin:all' in self.permissions:
            return True
        return permission in self.permissions

    def test_permission(self, permission: str|None = None):
        # if not permission:
        #     permission = str(inspect.stack()[1].function).replace('_', ':')
        if not self.can(permission):
            logger.error(f'User {self.name} does not have permission {permission}')
            raise Forbidden(
                f'You do not have permission "{permission}" '
                f'to perform this operation.'
            )


class UserInternalUpdate(BaseModel):
    last_logged_at: datetime
    disabled: Optional[bool] = Field(None)


class UserUpdate(BaseModel):
    name: str = Field(max_length=75)
    email: str = Field(max_length=50)


class UserCreate(UserUpdate):
    pass

# Database model class with asyncpg integration
class UserDB(BaseDBModel):
    class Meta:
        db_table = 'user'
        PYDANTIC_CLASS = User
        DEFAULT_SORT_BY: str = 'name'

    @classmethod
    async def load_assigns(cls, db: Connection, user: User,
                           realm_roles: List[str] = None,
                           load_permissions: bool = False):
        pass
        # user.member_of_static = set(await UserGroupDB.gets(
        #     db, 'ugu."user_id"=$1', user.id,
        #     _sub_sql='LEFT JOIN "usergroup_user" ugu '
        #              'ON f."id" = ugu."usergroup_id"'
        # ))
        # if not realm_roles:
        #     realm_roles = user.last_realm_roles.split(',') if user.last_realm_roles else []
        # user.member_of_dynamic = set(await UserGroupDB.gets(
        #     db,
        #     'f."realm_role" = ANY($1::text[]) OR f."is_default" = true',
        #     realm_roles
        # ))
        # if load_permissions:
        #     user_groups = user.member_of_static | user.member_of_dynamic
        #     await UserGroupDB.load_permissions(db, user_groups)
        #     for ug in user_groups:
        #         user.permissions.update(ug.permissions)
