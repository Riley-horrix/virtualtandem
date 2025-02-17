from typing import Any
import hardware.hardwareInterface as hw

def bounded(value, min, max) -> bool:
    return value > min and value < max

def bound(value, min_val: Any, max_val: Any) -> Any:
    return min(max(value, min_val), max_val)


def config_port_to_hw(motor):
    match motor:
        case "PORT_A":
            return hw.MOTOR_PORTS.PORT_A
        case "PORT_B":
            return hw.MOTOR_PORTS.PORT_B
        case "PORT_C":
            return hw.MOTOR_PORTS.PORT_C
        case "PORT_D":
            return hw.MOTOR_PORTS.PORT_D
        
class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for line, name in enumerate(names.split('\n')):
            if name.find(",") >= 0:
                # strip out the spaces
                while(name.find(" ") != -1):
                    name = name[:name.find(" ")] + name[(name.find(" ") + 1):]

                # strip out the commas
                while(name.find(",") != -1):
                    name = name[:name.find(",")] + name[(name.find(",") + 1):]

                # if the value was specified
                if(name.find("=") != -1):
                    number = int(float(name[(name.find("=") + 1):]))
                    name = name[:name.find("=")]

                # optionally print to confirm that it's working correctly
                #print "%40s has a value of %d" % (name, number)

                setattr(self, name, number)
                number = number + 1