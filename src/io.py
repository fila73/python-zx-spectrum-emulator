class IOBus:
    def __init__(self):
        """
        Z80 I/O Bus.
        Sběrnice V/V Z80.
        """
        self.devices = []

    def add_device(self, device):
        """
        Add an I/O device to the bus.
        Přidat V/V zařízení na sběrnici.
        """
        self.devices.append(device)

    def read_byte(self, port, cycles):
        """
        Read a byte from the specified port.
        Přečti bajt ze specifikovaného portu.
        
        :param port: 16-bit port address
        :param cycles: current CPU cycles for floating bus
        :return: 8-bit value
        """
        # Iterate through devices, if any responds, return value
        # Basic implementation: devices return None if they don't handle the port
        
        for device in self.devices:
            res = device.read_port(port)
            if res is not None:
                return res
                
        # If no device responded, return floating bus from ULA
        # Pokud žádné zařízení neodpovídá, vrátit plovoucí sběrnici z ULA
        for device in self.devices:
            if hasattr(device, 'get_floating_bus_value'):
                return device.get_floating_bus_value(cycles)
                
        return 0xFF

    def write_byte(self, port, value):
        """
        Write a byte to the specified port.
        Zapiš bajt na specifikovaný port.
        
        :param port: 16-bit port address
        :param value: 8-bit value
        """
        for device in self.devices:
            device.write_port(port, value)
