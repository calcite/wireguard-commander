import pathlib
import re
import sys

import duckdb
from loggate import setup_logging, get_logger
from aiohttp import web
from onacol import ConfigManager
from libs import LdapClient
from model.worker import Worker

logger = get_logger('main')

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


def setup_db_connection(app):
    db = duckdb.connect(app['config']['db']['path'])
    version = -1
    exist_table = db.sql(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_name = 'db_version'"
    ).fetchone()[0]
    if exist_table > 0:
        row = db.sql(
            "SELECT version FROM db_version ORDER BY date DESC"
        ).fetchone()
        if row:
            version = int(row[0]) + 1
    try:
        for ix in range(version, 999):
            for file in pathlib.Path('./sql').glob(f'{ix}-*.sql'):
                db.begin()
                logger.info(f"Apply SQL file {file}")
                ver = re.match(r'.*/(\d+)-[^/]+$', str(file)).group(1)
                with open(file, 'r') as fd:
                    db.sql(fd.read())
                    db.sql(
                        f"INSERT INTO db_version VALUES ({int(ver)}, DEFAULT);"
                    )
                db.commit()
        return db
    except Exception as e:
        db.rollback()
        logger.error(e)


def load_workers(app):
    for name, worker in app['config']['workers'].items():
        logger.info(f'Loading worker "{name}"')
        Worker(name=name, **worker)


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
setup_logging(app['config']['logging'].copy_flat())
load_workers(app)
app['db'] = setup_db_connection(app)
app['ldap'] = setup_ldap_connection(app)

app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)
