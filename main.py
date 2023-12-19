from jump_server_connection import connect_to_jump_server, disconnect_from_jump_server
from network_objekt import Network
from router_connection import *
from firewall_connection import *

jump_connection = connect_to_jump_server()
evi_connection = connect_to_evi(jump_connection)

with open('ip_list.txt', 'r') as f:
    ip_list = f.read().splitlines()
    print('Collecting routes from EVI')
    for ip in ip_list:
        print('!', end="")
        ip = ip.split('/')[0]
        command = f'display ip routing-table vpn-instance bcn-core {ip}'
        output = send_commands_to_evi(evi_connection, command)
        net = output.splitlines()[-1].split()[0]
        network, net_mask = net.split('/')
        interface = output.splitlines()[-1].split()[5]
        if interface in fw_mapping:
            if any(obj.network == network for obj in behind_fw_networks_list):
                continue
            network = Network(network, net_mask, fw_mapping[interface])
            behind_fw_networks_list.append(network)
        else:
            interface = 'BCN'
            network = Network(network, net_mask, interface)
            bcn_networks_list.append(network)
    print('')
disconnect_from_evi(evi_connection)
disconnect_from_jump_server(jump_connection)
jump_connection = connect_to_jump_server()

pa_connection = connect_to_palo_alto(jump_connection)
print('Collecting info from PA')
for net in behind_fw_networks_list:
    command = f'test routing fib-lookup virtual-router {net.fw_name} ip {net.network}'
    output = send_commands_to_pa(pa_connection, command, r"---------", wait=2)
    if 'ae1.2221' in output:
        zone = "NSX-T-Default"
        interface = 'ae1.2221'
    else:
        interface = output.strip().splitlines()[6].split()[1]
        vlan = interface[4:]
        zone_command = f"show zone-protection | match {vlan}"
        zone_output = send_commands_to_pa(pa_connection, zone_command, r"Zone", wait=2).strip()
        zone = zone_output.split()[1]
    net.interface = interface
    net.zone = zone

print()
print('#' * 30)
print()
sorted_behind_fw_networks_list = sorted(behind_fw_networks_list, key=lambda x: x.network)
for net in sorted_behind_fw_networks_list:
    print(net)

print()
sorted_bcn_networks_list = sorted(bcn_networks_list, key=lambda x: x.network)
for net in sorted_bcn_networks_list:
    print(net)

print()
print('#' * 30)
print()

disconnect_from_pa(pa_connection)
disconnect_from_jump_server(jump_connection)
