from datetime import datetime

from attrs import define, field

from model.base import Base


@define(kw_only=True)
class UserDevice(Base):

    username: str = field()
    mail: str = field()
    server_id: int = field()
    private_key: str = field()
    public_key: str = field()
    preshared_key: str = field()
    created_at: datetime = field()
    updated_at: datetime = field()
    enabled: bool = field(default=True)
