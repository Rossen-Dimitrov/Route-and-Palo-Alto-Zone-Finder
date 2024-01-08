import time
from netmiko import redispatch
from settings import TACACS_PASS, FW_IP


def connect_to_palo_alto(pa_connection):
    try:
        pa_connection.write_channel(FW_IP)
        time.sleep(3)
        jump_server_output = pa_connection.read_channel()
        if 'The authenticity of host' in jump_server_output:
            pa_connection.write_channel('yes\n')

        if 'Password' in jump_server_output:
            pa_connection.write_channel(TACACS_PASS)
        redispatch(pa_connection, device_type='paloalto_panos')
        print(f"Connected to: {pa_connection.find_prompt()}")
        return pa_connection

    except:
        print(f"Connection !!! FILED !!!"
              f"\nPlease check password in settings.py or "
              f"\nconnectivity to FW {FW_IP}")
        exit()


def send_commands_to_pa(pa_connection, command, string=None, wait=2):
    """sending commands to current connection"""
    output = pa_connection.send_command(command, expect_string=string)
    time.sleep(wait)
    # if string not in output:
    #     output = pa_connection.send_command(command, expect_string=string)
    #     time.sleep(wait)
    print('!', end='')
    return output


def disconnect_from_pa(pa_connection):
    if pa_connection:
        pa_connection.disconnect()
    print("Disconnected from PA")
