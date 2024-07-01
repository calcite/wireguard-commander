from model.server import Server
from model.user_device import UserDevice


class ClientFormater(object):

    @staticmethod
    def get_interface(user_device: UserDevice, server: Server):
        lines = ['[Interface]']
        lines.append(f'PrivateKey = {user_device.private_key}')
        lines.append(f'Address = {user_device.ip}')
        if server.dns:
            lines.append(f'DNS = {server.dns}')
        if server.mtu:
            lines.append(f'MTU = {server.mtu}')
        return '\n'.join(lines)

    @staticmethod
    def get_peer(peer: Server, user_device: UserDevice):
        lines = ['[Peer]']
        lines.append(f'PublicKey = {peer.public_key}')
        lines.append(f'AllowedIPs = {peer.allow_ips}')
        lines.append(f'Endpoint = {peer.endpoint}')
        if peer.keep_alived:
            lines.append(f'PersistentKeepalive = {peer.keep_alived}')
        if user_device.preshared_key:
            lines.append(f'PresharedKey = {user_device.preshared_key}')
        return '\n'.join(lines)
