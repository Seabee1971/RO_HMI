from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QTableWidget, QVBoxLayout

from Handlers.widget_links import READ_CONTINUOUS


class MaintenanceWindow(QMainWindow):
    def __init__(self, running, log_to_terminal, galil):
        super().__init__()
        self.connection_sts = False
        self.current_values = None
        uic.loadUi("Maintenance_Window.ui", self)  # Load the .ui file
        self.setWindowTitle("Maintenance Window")
        self.showMaximized()

        self.btn_ret_main_screen =self.findChild(QPushButton, "btn_RetMainScreen")
        self.btn_connect = self.findChild(QPushButton, "btn_Connect_to_Galil")
        self.btn_disconnect = self.findChild(QPushButton, "btn_Disconnect_Galil")
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_ret_main_screen.clicked.connect(self.ret2main)
        self.btn_disconnect.hide()
        self.btn_connect.show()
        self.running = running
        self.log_to_terminal = log_to_terminal
        self.galil = galil
        self.read_values = READ_CONTINUOUS

        layout = QVBoxLayout()
        self.tbl_parameters = self.findChild(QTableWidget, "tbl_parameters")
        layout.addWidget(self.tbl_parameters)
        self.setLayout(layout)


    def ret2main(self):
        self.close()


    def connect_device(self):
        self.log_to_terminal("Connecting...")
        try:

            connected, self.galil_object = self.galil.dmc_connect()
            if connected:
                self.connection_sts = True
                self.btn_connect.hide()
                self.btn_disconnect.show()
                self.log_to_terminal(f"Connection Successful. {connected}")
                self.update_tbl_parameters()
            else:
                self.connection_sts = False
                self.btn_connect.show()
                self.btn_disconnect.hide()
        except Exception as e:
            self.log_to_terminal(f"Error Connecting {e}", level="software_error")

    def disconnect_device(self):
        try:
            self.disconnected, self.galil_object = self.galil.dmc_disconnect()
        except Exception as e:

            self.disconnected = False
            self.log_to_terminal(f'"Disconnect failed"{e}', level="software_error")

        if self.disconnected:
            self.connection_sts = False
            self.btn_connect.show()
            self.btn_disconnect.hide()
            self.log_to_terminal("Disconnected from Controller", level= "info")

    def poll_galil(self):

        try:
            for value in self.read_values:
                self.current_values.append = self.galil.read_expr(value)  # wrapper: GCommand(f"MG {expr}")
        except Exception as e:
            self.log_to_terminal(f'Failed to update Galil Values: {e}', level="software_error")
        print(self.current_values)

    def update_tbl_parameters(self):
        try:
            self.poll_galil()
            for row_index, row_data in enumerate(self.current_values):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(cell_data)
                    # Optional: Customize item properties (e.g., text alignment)
                    # if col_index == 1: # Center align Age column
                    #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tbl_parameters.setItem(row_index, col_index, item)

        except Exception as e:
            # Assuming you have this method, otherwise just use print()
            self.log_to_terminal(f"Failed to update table: {e}", level="error")
