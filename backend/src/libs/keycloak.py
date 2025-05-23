import jwt
import urllib3
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from config import get_config
from logging import getLogger

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


async def get_me(token: str = Depends(oauth2_scheme)) -> dict:
    """
    :raise jose.exceptions.ExpiredSignatureError
    :param token:
    :return: dict
    :raise ExpiredSignatureError
    """
    res = jwt.decode(
        token,
        f"-----BEGIN PUBLIC KEY-----\n"
        f"{KEYCLOAK_SECRET_KEY}\n"
        f"-----END PUBLIC KEY-----",
        algorithms=KEYCLOAK_ALGORITHM,
        options={"verify_signature": True, "verify_aud": False, "exp": True}
    )
    res_roles = res.get('resource_access', {}).get(KEYCLOAK_CLIENT_ID, {}).get('roles', [])
    permitions = []
    if WG_COMMAND_ADMIN_ROLE in res_roles:
        permitions.append('admin:all')
    return {
        'name': res.get('name'),
        'email': res.get('email'),
        'preferred_username': res.get('preferred_username'),
        'given_name': res.get('given_name'),
        'family_name': res.get('family_name'),
        'realm_access': res.get('realm_access', {}).get('roles', []),
        'resource_access': res_roles,
        'permissions': permitions
    }