import gclib
from logging import exception

from PyQt6.QtWidgets import QLabel, QPushButton

mg = "MG "

# Handlers/galil.py
class Galil:
    _instance = None
    _connected = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.g = gclib.py()
        self.IP_address = "169.254.154.33"

    def dmc_connect(self):
        if not Galil._connected:
            try:
                self.g.GOpen(f'{self.IP_address} --direct')
                Galil._connected = True
                return self.g
            except Exception as e:
                return self.g
        return None

    def dmc_disconnect(self):
        try:
            self.g.GClose()
            Galil._connected = False
        except Exception as e:
            return self.g

        return self.g

    def is_connected(self):
        return Galil._connected

    def read_expr(self, expr: str) -> str:
        return self.g.GCommand(f"MG {expr}").strip()


    def write_var(self, name: str, value) -> None:
          self.g.GCommand(f"{name}={value}")


    def read_input(self, variable: str) -> str:
        return self.g.GCommand(f"MG {variable}").strip()


    def write_output(self, variable: str, value: str) -> str:
        return self.g.GCommand(f"{variable}={value}")
