class Network:
    def __init__(self, network, net_mask, fw_name, interface='', zone=''):
        self.network = network
        self.net_mask = net_mask
        self.fw_name = fw_name
        self.interface = interface
        self.zone = zone

    def __str__(self):
        return f"{self.network}/{self.net_mask} - {self.fw_name} - {self.zone}"
