from attrs import define, field


@define()
class Worker(object):
    INSTANCES = {}

    name: str = field()
    hostname: str = field()
    port: int = field()
    secret: str = field()

    def __attrs_post_init__(self):
        self.__class__.INSTANCES[self.name] = self

    @classmethod
    def get(cls, name: str):
        return cls.INSTANCES.get(name)
