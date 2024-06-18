
class User(object):
    def __init__(self, id, name, mail, dn):
        self.id = id
        self.name = name
        self.mail = mail
        self.dn = dn

    def __repr__(self):
        return f'<User {self.name} ({self.id})>'
