import loggate

from ldap3 import Server, Connection, ALL_ATTRIBUTES
from model import User

class LdapClient(object):

    def __init__(self, host, port, base_dn, use_ssl=True):
        self.logger = loggate.getLogger('ldap')
        self.server = Server(
            host=host,
            port=int(port),
            use_ssl=use_ssl,
            get_info='ALL'
        )
        self.connection = None
        self.base_dn = base_dn

    def connect(self, bind_user, bind_password):
        self.connection = Connection(
            self.server,
            user=bind_user,
            password=bind_password,
            read_only=True,
            auto_bind=True
        )
        if self.connection.bind():
            self.logger.info('Connected to LDAP server')
        else:
            self.logger.error('Failed to bind to LDAP server')
            self.connection = None
        return self.connection

    def get(self, dn: str, attributes=None) -> dict:
        if self.connection.search(
            search_base=dn,
            search_filter='(objectClass=*)',
            search_scope='BASE',
            attributes=attributes if attributes else ALL_ATTRIBUTES
        ):
            if self.connection.entries:
                self.logger.debug(f'Loading the entry {dn} from LDAP server')
                return self.connection.entries[0]
        self.logger.warning(f'Failed to load the entry {dn} from LDAP server')
        return None

    def get_members_of_group(self, group_name):
        res = []
        if self.connection.search(
            search_base=self.base_dn,
            search_filter=f'(&(objectClass=group)(cn={group_name}))',
            attributes=['member']
        ):
            for member_dn in self.connection.entries[0].member:
                data = self.get(
                    member_dn,
                    ['sAMAccountName', 'displayName', 'mail']
                )
                res.append(
                    User(
                        username=data.sAMAccountName,
                        display_name=data.displayName,
                        mail=data.mail
                    )
                )
        return res
