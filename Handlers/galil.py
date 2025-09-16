import gclib

_mg = "MG "

# Handlers/galil.py
class Galil:
    _instance = None
    _connected = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def _init(self,log_to_terminal):
        self.g = gclib.py()
        self.IP_address = "169.254.154.33"
        self.log_to_terminal = log_to_terminal
    def dmc_connect(self):
        if not Galil._connected:
            try:

                self.g.GOpen(f'{self.IP_address} --direct')
                Galil._connected = True
            except Exception as e:
                self.log_to_terminal(f"Connecting to {self.IP_address} failed: {e}","error")


    def dmc_disconnect(self):
        try:
            self.g.GClose()
            Galil._connected = False
        except Exception as e:
            self.log_to_terminal(f"Disconnecting from {self.IP_address} failed: {e}","error")




    def get_info(self) -> str:
        try:
            return self.g.GInfo()
        except Exception as e:
            return f"Error getting GInfo: {e}"

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
