from netmiko import ConnectHandler

from settings import JUMP_SERVER_IP, JUMP_USER, JUMP_PASS

device = {
    'device_type': 'terminal_server',
    'ip': JUMP_SERVER_IP,
    'username': JUMP_USER,
    'password': JUMP_PASS,
    'port': 22
}


def connect_to_jump_server():
    """Disconnects from device if connected"""
    jump_connection = ConnectHandler(**device)
    print(f"### Connected to Jump Server: {jump_connection.find_prompt().upper().split()[0]} ###")
    return jump_connection


def disconnect_from_jump_server(jump_connection):
    """Disconnects from device if connected"""
    if jump_connection:
        jump_connection.disconnect()
    print("Disconnected from Jump Server")
