import hardware.hardwareInterface as hw
import toml
import sys

def getHardware(is_virtual) -> hw.HardwareInterface:
    if is_virtual:
        import hardware.virtualInterface as vi
        return vi.VirtualInterface()
    else:
        import hardware.physicalInterface as pi
        return pi.PhysicalInterface()

class Robot:
    def __init__(self, config_path):
        self.config_path = config_path
        with open(config_path) as stream:
            try:
                self.config = toml.load(stream)
                print(self.config["robot"])
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)

        self.hw = getHardware(self.config["virtual"])
