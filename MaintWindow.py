from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QTableWidget, QVBoxLayout, QPlainTextEdit

from Handlers.widget_links import COMMANDS

w = "[Maintenance Window]"
class MaintenanceWindow(QMainWindow):
    def __init__(self, main_window, log_to_terminal, galil):
        super().__init__()
        self.dict_values = {}
        self.current_values = []
        self.term_msg = None
        self.main_window = main_window
        self.last_term_msg = ""
        uic.loadUi("Maintenance_Window.ui", self)  # Load the .ui file
        self.setWindowTitle("Maintenance Window")

        self.showMaximized()
        # Widget creation
        self.btn_poll_settings = self.findChild(QPushButton, "btn_Poll_Settings")
        self.btn_ret_main_screen =self.findChild(QPushButton, "btn_RetMainScreen")
        self.btn_connect = self.findChild(QPushButton, "btn_Connect_to_Galil")
        self.btn_disconnect = self.findChild(QPushButton, "btn_Disconnect_Galil")

        self.txt_maint_terminal = self.findChild(QPlainTextEdit,"txt_Maint_Terminal")
        # Widget actions
        self.btn_poll_settings.clicked.connect(self.update_tbl_parameters)
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_ret_main_screen.clicked.connect(self.ret2main)



        self.log_to_terminal = log_to_terminal
        self.galil = galil
        if self.galil.is_connected():
            self.btn_disconnect.show()
            self.btn_connect.hide()
        else:
            self.btn_disconnect.hide()
            self.btn_connect.show()
        self.read_values = COMMANDS
        print(type(self.read_values))
        layout = QVBoxLayout()
        self.tbl_parameters = self.findChild(QTableWidget, "tbl_parameters")
        layout.addWidget(self.tbl_parameters)
        self.setLayout(layout)
        self.tbl_parameters.setStyleSheet("""
                    QTableWidget {
                        font-size: 14pt;
                        font-weight: bold;
                    }
                """)


    def ret2main(self):
        self.main_window.show()
        self.close()


    def connect_device(self):
        self.log_to_terminal("Connecting...")
        try:
            self.galil.dmc_connect()
            if self.galil.is_connected():
                self.btn_connect.hide()
                self.btn_disconnect.show()
                self.log_to_maint_terminal(f"{w}Connection Successful. {self.galil.get_info()}")
            else:
                self.log_to_terminal(f"{w}Failed to connect to controller", level="error")
                self.log_to_maint_terminal(f"{w}Failed to connect to controller", level="error")
                self.btn_connect.show()
                self.btn_disconnect.hide()
        except Exception as e:
            self.log_to_terminal(f"{w}Error Connecting {e}", level="error")
            self.log_to_maint_terminal(f"{w}Error Connecting {e}", level="error")
    def disconnect_device(self):
        try:
            self.galil.dmc_disconnect()

            if not self.galil.is_connected():
                self.btn_connect.show()
                self.btn_disconnect.hide()
                self.log_to_terminal(f"{w}Disconnected from Controller", level="info")
                self.log_to_maint_terminal(f"{w}Disconnected from Controller {self.galil.get_info()}")

        except Exception as e:
            self.log_to_terminal(f'{w}Disconnect failed:{e}', level="error")
            self.log_to_maint_terminal(f'{w}Disconnect failed:{e}', level="error")

    def update_maint_terminal(self):
        if self.term_msg is not None and self.last_term_msg != self.term_msg:
            try:
                self.txt_maint_terminal.appendPlainText(str(self.term_msg))
                self.last_term_msg = self.term_msg
            except Exception as e:
                self.log_to_terminal(f"{w}Terminal window update failed: {e}", level="error")
                self.log_to_maint_terminal(f"{w}Terminal window update failed: {e}", level="error")

    def log_to_maint_terminal(self, msg: str, level: str = "info"):
        # msg = msg.replace("→", "->")  # keep CP1252-safe
        self.term_msg = msg
        self.update_maint_terminal()

    def update_tbl_parameters(self):
        self.log_to_maint_terminal(f"Maintenance Window Parameters Update")

        AXES = ['X', 'Y']
        if self.galil.is_connected():


                for axis in AXES:
                    for value in self.read_values:
                        if value.startswith("_"):
                            parameter = f"{value}{axis}"
                        else:
                            parameter = f"{axis.lower()}{value}"
                        try:
                            result = self.galil.read_expr(parameter)
                            self.log_to_maint_terminal(f"Current Value: {parameter}={result}")
                            self.current_values.append(result)

                            # ✅ store parameter → result as key:value
                            self.dict_values[parameter] = result

                        except Exception as e:
                            self.log_to_maint_terminal(f"{w}Error reading {parameter} {e}", level="error")
                            self.log_to_terminal(f"{w}Error reading {parameter} {e}", level="error")

                self.populate_table()

    def populate_table(self):

        try:
            self.tbl_parameters.setRowCount(len(self.dict_values))

            for row, (param, val) in enumerate(self.dict_values.items()):
                if param.startswith("x"):
                    param = param.removeprefix("x")
                    col =2
                    x_row = 1
                elif param.endswith("X"):
                    param = param.removesuffix("X")
                    col = 2
                elif param.startswith("y"):
                    param = param.removeprefix("y")
                    col = 3
                    row = row + 1
                elif param.endswith("Y"):
                    param = param.removesuffix("Y")
                    col = 3
                    row = row + 1
                # Key goes into "Parameter" (col 2)
                self.tbl_parameters.setItem(row, col, QTableWidgetItem(str(param)))

                # Value goes into "A Axis Current Value" (col 1)
                self.tbl_parameters.setItem(row, 1, QTableWidgetItem(str(val)))

        except Exception as e:
            # Replace w with "" or remove it (looks like a leftover variable)
            self.log_to_terminal(f"Failed to update table: {e}", level="error")
            self.log_to_maint_terminal(f"Failed to update table: {e}", level="error")
