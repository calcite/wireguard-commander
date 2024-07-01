import ipaddress
from datetime import datetime
from duckdb.duckdb import DuckDBPyConnection

from model.base import BaseDbModel
from model.user_device import UserDevice


class Server(BaseDbModel):
    __tablename__ : str = 'server'

    worker: str
    interface: str
    cidr: str
    name: str
    listen_port: int
    enabled: bool
    private_key: str
    public_key: str
    fw_mark: int
    table: str
    keep_alived: int
    endpoint: str
    dns: str
    mtu: int
    allow_ips: str
    created_at: datetime
    updated_at: datetime
    pre_up: str
    post_up: str
    pre_down: str
    post_down: str
    domain_group: str

    def get_user_devices(self, db: DuckDBPyConnection):
        return UserDevice.gets(db, 'server_id=$1', self.id)

    def get_next_free_ip(self, db: DuckDBPyConnection):
        user_devices = self.get_user_devices(db)
        net = ipaddress.IPv4Network(self.cidr, strict=False)
        ips = {str(ip) for ip in net}
        # Eliminate gateway ip
        ips.remove(str(ipaddress.ip_interface(self.cidr).ip))
        # Eliminate broadcast
        ips.remove(str(net.broadcast_address))
        # Eliminate network address
        ips.remove(str(net.network_address))
        for user_device in user_devices:
            # Eliminate registered ips
            ips.remove(user_device.ip)
        if not ips:
            raise Exception(f'No available ip in {self.cidr}.')
        return ips.pop()
