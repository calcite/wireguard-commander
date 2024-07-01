from datetime import datetime
from pydantic import Field
from model.base import BaseDbModel


class UserDevice(BaseDbModel):
    __tablename__: str = 'user_device'

    username: str
    mail: str
    ip: str
    server_id: int
    private_key: str
    public_key: str
    preshared_key: str
    created_at: datetime
    updated_at: datetime
    enabled: bool = Field(True)
