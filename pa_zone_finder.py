from jump_server_connection import connect_to_jump_server, disconnect_from_jump_server
from network_objekt import Network
from router_connection import *
from firewall_connection import *

bcn_networks_list = []
sap_networks_list = []
pa_networks_list = []

jump_connection = connect_to_jump_server()
evi_connection = connect_to_evi(jump_connection)


with open('ip_list.txt', 'r') as f:
    """ Reading IP list file """
    ip_list = f.read().splitlines()
    print('Collecting routes from EVI')

    for ip in ip_list:
        """ Sending commands for each IP Route """
        print('!', end="")
        ip_mask = ip.split('/')
        ip, host_mask = ip_mask[0],  ip_mask[1],
        command = f'display ip routing-table vpn-instance bcn-core {ip}'
        output = send_commands_to_evi(evi_connection, command)
        net = output.splitlines()[-1].split()[0]
        network, net_mask = net.split('/')
        interface = output.splitlines()[-1].split()[5]

        if interface in pa_fw_mapping:
            network_obj = Network(ip, host_mask, network, net_mask, pa_fw_mapping[interface])
            pa_networks_list.append(network_obj)

        elif interface in sap_fw_mapping:
            # if not any(obj.network == network for obj in sap_networks_list):
            network_obj = Network(ip, host_mask, network, net_mask, zone=sap_fw_mapping[interface])
            sap_networks_list.append(network_obj)

        else:
            network_obj = Network(ip, host_mask, network, net_mask, zone='BCN')
            bcn_networks_list.append(network_obj)
    print('')

disconnect_from_evi(evi_connection)
disconnect_from_jump_server(jump_connection)
jump_connection = connect_to_jump_server()

# sending commands to PA
pa_connection = connect_to_palo_alto(jump_connection)
print('Collecting info from PA')

for net in pa_networks_list:
    """ Finding zones """
    command = f'test routing fib-lookup virtual-router {net.fw_name} ip {net.ip}'
    # print(command)
    output = send_commands_to_pa(pa_connection, command, r"---------", wait=2)
    if 'via' in output:
        interface = output.strip().splitlines()[6].split()[3][:-1]
    else:
        interface = output.strip().splitlines()[6].split()[1][:-1]

    zone_command = f"show interface {interface} | match Zone:"
    # print(zone_command)
    zone_output = send_commands_to_pa(pa_connection, zone_command, string=r"virtual system:", wait=0.2)
    zone = zone_output.split()[1]
    net.interface = interface
    net.zone = zone

print()
print('#' * 50, end='\n')

sorted_pa_networks_list = sorted(pa_networks_list, key=lambda x: x.network)

for net in sorted_pa_networks_list:
    print(net)

sorted_bcn_networks_list = sorted(bcn_networks_list, key=lambda x: x.network)

for net in sorted_bcn_networks_list:
    print(f"{net.ip}/{net.host_mask} - {net.network}/{net_mask} - {net.zone}")

sorted_sap_networks_list = sorted(sap_networks_list, key=lambda x: x.network)

for net in sorted_sap_networks_list:
    print(f'{net.ip}/{net.host_mask} - {net.network}/{net_mask} - {net.zone}')

print()
print('#' * 50, end='\n')

disconnect_from_pa(pa_connection)
disconnect_from_jump_server(jump_connection)
