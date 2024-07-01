
import sys
from typing import List, Dict

from loggate import setup_logging, get_logger
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from onacol import ConfigManager
from libs import LdapClient
from libs.helper import setup_db_connection
from model.server import Server
from model.user_device import UserDevice
from model.worker import Worker
from model.formaters import ServerFormater, ClientFormater

logger = get_logger('main')
app = FastAPI(
    title="Wireguard Command Server",
    description="Wireguard Command Server",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    global app
    # Load Config
    conf = ConfigManager('default_config.yaml',
                         optional_files=['config.yaml'],
                         env_var_prefix="WC")
    conf.config_from_env_vars()
    conf.config_from_cli_args(sys.argv[1:])
    conf.validate()
    app.config = conf.config

    # Setup Logging
    setup_logging(conf.config['logging'].copy_flat())

    # Load workers
    for name, worker in conf.config['workers'].items():
        logger.info(f'Loading worker "{name}"')
        Worker(name=name, **worker)

    # Setup LDAP connection
    ldap_conf = app.config['ldap']
    ldap = LdapClient(
        host=ldap_conf['host'],
        port=int(ldap_conf['port']),
        use_ssl=ldap_conf['use_ssl'],
        base_dn=ldap_conf['base_dn']
    )
    ldap.connect(ldap_conf['user'], ldap_conf['password'])
    app.ldap = ldap

    # Setup and update DB
    app.db = setup_db_connection(conf.config['database'])


@app.get('/workers', response_model=Dict[str, Worker])
def get_workers():
    workers = Worker.INSTANCES
    return workers


@app.get('/servers', response_model=List[Server])
def get_servers(request: Request):
    with request.app.db.cursor() as db:
        servers = Server.gets(db)
        return servers

@app.get('/worker/{name}', response_class=PlainTextResponse)
def get_worker_conf(name, request: Request):
    worker = Worker.get(name)
    if worker is None:
        raise HTTPException(status_code=403, detail="Worker not found.")
    # worker.get_config()
    # entries = app['ldap'].get_members_of_group('gg_BackOffice')
    #
    # for entry in entries:
    #     print(entry)
    logger.info(
        f"Getting worker configuration for {name} from {request.client.host}")
    res = ''
    with request.app.db.cursor() as db:
        for server in worker.get_servers(db):
            res += ServerFormater.get_interface(server)
            for peer in server.get_user_devices(db):
                res += '\n\n'
                res += ServerFormater.get_peer(peer)
    return res


@app.get('/client/{name}', response_class=PlainTextResponse)
def get_client_conf(name, request: Request):
    # worker.get_config()
    # entries = app['ldap'].get_members_of_group('gg_BackOffice')
    #
    # for entry in entries:
    #     print(entry)
    res = ''
    with request.app.db.cursor() as db:
        logger.info(f"Getting client configuration for {name} from {request.client.host}")
        devices = UserDevice.gets(db, 'username=$1', name)
        if devices is None:
            raise HTTPException(status_code=403, detail="Device not found.")
        for device in devices:
            server = Server.get(db, device.server_id)
            res += ClientFormater.get_interface(device, server)
            res += '\n\n'
            res += ClientFormater.get_peer(server, device)
            # server.get_next_free_ip(db)
    return res

