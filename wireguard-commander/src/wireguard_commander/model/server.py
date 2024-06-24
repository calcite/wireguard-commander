from datetime import datetime
from attrs import define, field
from model.base import Base


@define(kw_only=True)
class Server(Base):

    worker: str = field()
    interface: str = field()
    ips: str = field()
    name: str = field()
    listen_port: int = field()
    enabled: bool = field()
    private_key: str = field()
    public_key: str = field()
    fw_mark: int = field()
    table: str = field()
    keepalive: int = field()
    endpoint: str = field()
    dns: str = field()
    mtu: int = field()
    allowed_ips: str = field()
    created_at: datetime = field()
    updated_at: datetime = field()
    pre_up: str = field()
    post_up: str = field()
    pre_down: str = field()
    post_down: str = field()
