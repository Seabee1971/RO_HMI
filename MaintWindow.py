from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QTableWidget, QVBoxLayout, QPlainTextEdit

from Handlers.widget_links import COMMANDS

w = "[Maintenance Window]"
class MaintenanceWindow(QMainWindow):
    def __init__(self, main_window, log_to_terminal, galil):
        super().__init__()
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
                self.log_to_terminal(f"{w}Connection Successful. {self.galil.get_info()}")

            else:
                self.btn_connect.show()
                self.btn_disconnect.hide()
        except Exception as e:
            self.log_to_terminal(f"{w}Error Connecting {e}", level="error")

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
        msg = msg.replace("→", "->")  # keep CP1252-safe
        self.term_msg = msg
        self.update_maint_terminal()

    def update_tbl_parameters(self):
        try:
            raise RuntimeError("TEST: simulated failure for logger")
        except Exception as e:
            self.log_to_maint_terminal(f"{w}Error updating Maintenance Window: {e}", level="error")

        try:
            AXES = ['A','B']
            if self.galil.is_connected():
                for axis in AXES:
                    for value in self.read_values:
                        self.current_values.append(self.galil.read_expr(f'{value}{axis}'))


            for row_index, row_data in enumerate(self.current_values):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(cell_data)
                    # Optional: Customize item properties (e.g., text alignment)
                    # if col_index == 1: # Center align Age column
                    #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_parameters.setItem(row_index, col_index, item)

        except Exception as e:
            # Assuming you have this method, otherwise just use print()
            self.log_to_terminal(f"{w}Failed to update table: {e}", level="error")
            self.log_to_maint_terminal(f"{w}Failed to update table: {e}", level="error")
