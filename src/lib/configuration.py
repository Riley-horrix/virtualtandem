import sys
import time

import toml

from typing import TypeVar, Generic, get_args, get_origin


class ConfigurationException(Exception):
    def __init__(self, message):
        super().__init__(message)


T = TypeVar('T')

class _TypedConfiguration(Generic[T]):
    def __init__(self, config):
        self.config = config

    def get_conf(self, obj: str, config: str, default, fail, t_str) -> T:
        if obj in self.config:
            if config in self.config[obj]:
                if get_origin(self.__orig_class__.__args__[0]) is list and type(self.config[obj][config]) == list:
                    if all(isinstance(x, get_args(self.__orig_class__.__args__[0])) for x in self.config[obj][config]):
                        return self.config[obj][config]
                    elif fail:
                        raise ConfigurationException(f"[configuration]: '{config}' in '{obj}' is not a list of floats!")
                elif type(self.config[obj][config]) == self.__orig_class__.__args__[0]:
                    return self.config[obj][config]
                elif fail:
                    raise ConfigurationException(f"[configuration]: '{config}' in '{obj}' is not a {t_str}!")
            elif fail:
                raise ConfigurationException(f"[configuration]: '{obj}' is not defined in '{config}'")
        elif fail:
            raise ConfigurationException(f"[configuration]: '{obj}' is not a valid configuration")
        else:
            return default


class Configuration:
    def __init__(self, file_path: str):
        with open(file_path) as stream:
            try:
                self.config = toml.load(stream)
            except toml.TomlDecodeError as err:
                raise ConfigurationException(f"[configuration]: {err}")

    def get_conf_num_f(self, obj: str, config: str, default: float = 0.0, fail: bool = True) -> float:
        type_config = _TypedConfiguration[float](self.config)
        return type_config.get_conf(obj, config, default, fail, "float")

    def get_conf_num(self, obj: str, config: str, default: int = 0, fail: bool = True) -> int:
        type_config = _TypedConfiguration[int](self.config)
        return type_config.get_conf(obj, config, default, fail, "int")

    def get_conf_str(self, obj: str, config: str, default: str = "", fail: bool = True) -> str:
        type_config = _TypedConfiguration[str](self.config)
        return type_config.get_conf(obj, config, default, fail, "str")

    def get_conf_list_f(self, obj: str, config: str, default: list[float] = [], fail: bool = True) -> list[float]:
        type_config = _TypedConfiguration[list[float]](self.config)
        return type_config.get_conf(obj, config, default, fail, "list of floats")

    def get_conf_list(self, obj: str, config: str, default: list[int] = [], fail: bool = True) -> list[int]:
        type_config = _TypedConfiguration[list[int]](self.config)
        return type_config.get_conf(obj, config, default, fail, "list of ints")


global_conf = Configuration("configuration.toml")


class Configurable:
    def __init__(self):
        self.conf = global_conf