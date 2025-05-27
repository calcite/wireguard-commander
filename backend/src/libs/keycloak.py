from datetime import datetime
import jwt
import urllib3
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from config import get_config
from logging import getLogger
from libs.db import Pool, db_pool, db_logger
from models.user import User, UserDB, UserCreate, UserInternalUpdate

logger = getLogger('keycloak')

urllib3.disable_warnings()

KEYCLOAK_URL = get_config('KEYCLOAK_URL')
KEYCLOAK_REALM = get_config('KEYCLOAK_REALM')
KEYCLOAK_CLIENT_ID = get_config('KEYCLOAK_CLIENT_ID')
KEYCLOAK_ALGORITHM = get_config('KEYCLOAK_ALGORITHM').split(' ')
KEYCLOAK_SECRET_KEY = get_config('KEYCLOAK_SECRET_KEY')
WG_COMMAND_ADMIN_ROLE = get_config('KEYCLOAK_REALM_ADMIN_ROLE')

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl=f'{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}'
             f'/protocol/openid-connect/token',
    authorizationUrl=f'{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}'
                     f'/protocol/openid-connect/auth',
    # scopes={
    #      'email': 'Grants read access to a user\'s email addresses.'
    #  }
)


def download_keycloak_cert():
    req_url = f'{KEYCLOAK_URL}realms/{KEYCLOAK_REALM}'
    logger.warning('Missing KEYCLOAK_SECRET_KEY in config. '
                   'It will be downloaded from %s', req_url)
    import requests
    res = requests.get(req_url, verify=False)
    res.raise_for_status()
    data = res.json()
    return data.get('public_key')


def keycloak_init():
    global KEYCLOAK_SECRET_KEY
    if not KEYCLOAK_SECRET_KEY:
        KEYCLOAK_SECRET_KEY = download_keycloak_cert()


async def get_me(token: str = Depends(oauth2_scheme),
                 pool: Pool = Depends(db_pool)) -> User:
    if not token or token == 'undefined':
        raise jwt.ExpiredSignatureError()
    payload = jwt.decode(
        token,
        f"-----BEGIN PUBLIC KEY-----\n"
        f"{KEYCLOAK_SECRET_KEY}\n"
        f"-----END PUBLIC KEY-----",
        algorithms=KEYCLOAK_ALGORITHM,
        options={"verify_signature": True, "verify_aud": False, "exp": True}
    )
    res_roles = payload.get('resource_access', {}).get(KEYCLOAK_CLIENT_ID, {}).get('roles', [])
    permitions = []
    if WG_COMMAND_ADMIN_ROLE in res_roles:
        permitions.append('admin:all')
    async with pool.acquire() as db, db_logger('sql.keycloak', db):
        async with db.transaction():
            user = await UserDB.get(db, 'email=$1', payload['email'])
            if user is None:
                user_c = UserCreate(
                    email=payload['email'],
                    name=payload['name']
                )
                user = await UserDB.create(db, user_c)
        await UserDB.load_assigns(db, user, realm_roles, load_permissions=True)
        await UserDB.update(db, user, UserInternalUpdate(
            last_logged_at=datetime.now(),
            disabled=None
        ))
    return user