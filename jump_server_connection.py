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
    try:
        jump_connection = ConnectHandler(**device)
        print(f"### Connected to Jump Server: {jump_connection.find_prompt().upper().split()[0]} ###")
    except:
        print(f"Connection !!! FILED !!!"
              f"\nPlease check password in settings.py or "
              f"\nconnectivity to JUMP SERVER {JUMP_SERVER_IP}")
        exit()

    return jump_connection


def disconnect_from_jump_server(jump_connection):
    """Disconnects from device if connected"""
    if jump_connection:
        jump_connection.disconnect()
    print("Disconnected from Jump Server")
