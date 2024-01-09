from jump_server_connection import connect_to_jump_server, disconnect_from_jump_server
from network_objekt import Network
from router_connection import *
from firewall_connection import *

bcn_networks_list = []
bcn_directly_connected_list = []
sap_networks_list = []
pa_networks_list = []
vsx_firewall_list = []

jump_connection = connect_to_jump_server()
evi_connection = connect_to_evi(jump_connection)


with open('ip_list.txt', 'r') as f:
    """ Reading IP list file """
    ip_list = f.read().splitlines()
    print('Collecting routes from EVI')

    for ip in ip_list:
        """ Sending commands for each IP Route """
        print('!', end="")
        host_subnet = ip.split('/')
        ip = host_subnet[0]
        host_mask = '32'
        if len(host_subnet) == 2:
            host_mask = host_subnet[1]

        command = f'display ip routing-table vpn-instance bcn-core {ip}'
        output = send_commands_to_evi(evi_connection, command).splitlines()
        subnet = output[-1].split()[0]
        network, net_mask = subnet.split('/')
        interface = output[-1].split()[5]
        directly_connected = output[-1].split()[1]

        if interface in pa_fw_mapping:
            network_obj = Network(ip, host_mask, network, net_mask, pa_fw_mapping[interface])
            pa_networks_list.append(network_obj)

        elif interface in sap_fw_mapping:
            # if not any(obj.network == network for obj in sap_networks_list):
            network_obj = Network(ip, host_mask, network, net_mask, zone=sap_fw_mapping[interface])
            sap_networks_list.append(network_obj)

        elif directly_connected == "Direct":
            network_obj = Network(ip, host_mask, network, net_mask, zone="BCN", interface='Directly Connected')
            vsx_firewall_list.append(network_obj)
        else:
            network_obj = Network(ip, host_mask, network, net_mask, zone='BCN')
            bcn_networks_list.append(network_obj)
    print('')

disconnect_from_evi(evi_connection)
disconnect_from_jump_server(jump_connection)


# sending commands to PA if objects in pa_networks_list
if pa_networks_list:
    jump_connection = connect_to_jump_server()
    pa_connection = connect_to_palo_alto(jump_connection)
    print('Collecting info from PA')

    for subnet in pa_networks_list:
        """ Finding zones """
        print('!', end="")
        command = f'test routing fib-lookup virtual-router {subnet.fw_name} ip {subnet.host}'

        output = send_commands_to_pa(pa_connection, command, r"---------", wait=2)
        if 'via' in output:
            interface = output.strip().splitlines()[6].split()[3][:-1]
        elif 'to host' in output:
            interface = output.strip().splitlines()[6].split()[3]
        else:
            interface = output.strip().splitlines()[6].split()[1][:-1]

        command = f"show interface {interface} | match Zone:"
        output = send_commands_to_pa(pa_connection, command, string=r"virtual system:", wait=0.2)
        zone = output.split()[1][:-1]
        subnet.interface = interface
        subnet.zone = zone

        command = f"show interface {interface} | match address:"
        output = send_commands_to_pa(pa_connection, command, string=r"Interface IP address:", wait=0.2)
        result = output.split()[3]
        gw, mask = result.split('/')
        subnet.network = gw
        subnet.net_mask = mask

    print()
    disconnect_from_pa(pa_connection)
    disconnect_from_jump_server(jump_connection)


print()
print('#' * 50, end='\n')

if pa_networks_list:
    sorted_pa_networks_list = sorted(pa_networks_list, key=lambda x: x.network)

    for subnet in sorted_pa_networks_list:
        print(subnet)

if bcn_networks_list:
    sorted_bcn_networks_list = sorted(bcn_networks_list, key=lambda x: x.network)

    for subnet in sorted_bcn_networks_list:
        print(f"{subnet.host}/{subnet.host_mask} - {subnet.network}/{net_mask} - {subnet.zone}")

if sap_networks_list:
    sorted_sap_networks_list = sorted(sap_networks_list, key=lambda x: x.network)

    for subnet in sorted_sap_networks_list:
        print(f'{subnet.host}/{subnet.host_mask} - {subnet.network}/{net_mask} - {subnet.zone}')

if vsx_firewall_list:
    sorted_vsx_firewall_list = sorted(vsx_firewall_list, key=lambda x: x.network)
    for subnet in sorted_vsx_firewall_list:
        print(f"{subnet.host}/{subnet.host_mask} - {subnet.network}/{net_mask} - {subnet.zone} - {subnet.interface}")


print()
print('#' * 50, end='\n')



