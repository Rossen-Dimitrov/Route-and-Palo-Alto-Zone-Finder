import time
from netmiko import redispatch
from settings import TACACS_PASS, EVI_ROUTER

bcn_networks_list = []
behind_fw_networks_list = []

fw_mapping = {
    'Vlan891': 'MSVX-NSX-T-Default',
    'Vlan892': 'MSVX-NSX-T-DMZ',
    'Vlan894': 'vmpchbi01',
    'Vlan895': 'vmpcsdcn01',
    'Vlan896': 'Infra',
    'Vlan900': 'Sap01'
}


def connect_to_evi(evi_connection):
    evi_connection.write_channel(EVI_ROUTER)
    time.sleep(1)
    jump_server_output = evi_connection.read_channel()
    if 'The authenticity of host' in jump_server_output:
        evi_connection.write_channel('yes\n')

    if 'password' in jump_server_output:
        evi_connection.write_channel(TACACS_PASS)
    redispatch(evi_connection, device_type='hp_comware')
    print(f"Connected to: {evi_connection.find_prompt()}")
    return evi_connection


def send_commands_to_evi(evi_connection, command):
    """sending commands to current connection"""
    output = evi_connection.send_command(command)
    return output


def disconnect_from_evi(evi_connection):
    """Disconnects from device if connected"""
    if evi_connection:
        evi_connection.disconnect()
    print("Disconnected from EVI Router")


