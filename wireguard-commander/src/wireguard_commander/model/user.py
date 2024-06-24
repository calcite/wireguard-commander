from attrs import define, field


@define(kw_only=True)
class User(object):

    username: str = field()
    display_name: str = field()
    mail: str = field()
