from model.server import Server
from model.user_device import UserDevice


class ServerFormater(object):

    @staticmethod
    def get_interface(server: Server):
        lines = ['[Interface]']
        lines.append(f'ListenPort = {server.listen_port}')
        lines.append(f'PrivateKey = {server.private_key}')
        if server.cidr:
            lines.append(f'Address = {server.cidr}')
        if server.fw_mark:
            lines.append(f'PrivateKey = {server.private_key}')
        if server.fw_mark:
            lines.append(f'FwMark = {server.table}')
        if server.table:
            lines.append(f'Table = {server.table}')
        if server.pre_up:
            lines.append(f'PreUp = {server.pre_up}')
        if server.pre_down:
            lines.append(f'PreDown = {server.pre_down}')
        if server.post_up:
            lines.append(f'PostUp = {server.post_up}')
        if server.post_down:
            lines.append(f'PostDown = {server.post_down}')
        return '\n'.join(lines)

    @staticmethod
    def get_peer(peer: UserDevice):
        lines = [f'# {peer.username}' ,'[Peer]']
        lines.append(f'PublicKey = {peer.public_key}')
        lines.append(f'AllowedIPs = {peer.ip}/32')
        if peer.preshared_key:
            lines.append(f'PresharedKey = {peer.preshared_key}')
        return '\n'.join(lines)
