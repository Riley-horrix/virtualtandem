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
        
