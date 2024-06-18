import sys

from aiohttp import web
from onacol import ConfigManager
from libs import LdapClient


async def handle(request):
    entries = app['ldap'].get_members_of_group('gg_BackOffice')

    for entry in entries:
        print(entry)

    return web.Response(text=f"Hello, world  {request.app['config']['log_level']}")


def setup_config():
    conf = ConfigManager('default_config.yaml',
                         optional_files=['config.yaml'],
                         env_var_prefix="WC")
    conf.config_from_env_vars()
    conf.config_from_cli_args(sys.argv[1:])
    conf.validate()
    return conf.config


def setup_ldap_connection(app) -> LdapClient:
    ldap_conf = app['config']['ldap']
    ldap = LdapClient(
        host=ldap_conf['host'],
        port=int(ldap_conf['port']),
        use_ssl=ldap_conf['use_ssl'],
        base_dn=ldap_conf['base_dn']
    )
    ldap.connect(ldap_conf['user'], ldap_conf['password'])
    return ldap


app = web.Application()
app['config'] = setup_config()
app['ldap'] = setup_ldap_connection(app)

app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)
