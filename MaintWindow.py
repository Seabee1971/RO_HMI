from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QTableWidget, QVBoxLayout

from Handlers.widget_links import READ_CONTINUOUS


class MaintenanceWindow(QMainWindow):
    def __init__(self, running, log_to_terminal, galil):
        super().__init__()
        self.current_values = None
        uic.loadUi("Maintenance_Window.ui", self)  # Load the .ui file
        self.setWindowTitle("Maintenance Window")
        self.showMaximized()

        self.btn_ret_main_screen =self.findChild(QPushButton, "btn_RetMainScreen")
        self.btn_connect = self.findChild(QPushButton, "btn_Connect_to_Galil")
        self.btn_disconnect = self.findChild(QPushButton, "btn_Disconnect_Galil")
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_ret_main_screen.clicked.connect(self.ret2main)


        self.running = running
        self.log_to_terminal = log_to_terminal
        self.galil = galil
        if self.galil.is_connected():
            self.btn_disconnect.show()
            self.btn_connect.hide()
        else:
            self.btn_disconnect.hide()
            self.btn_connect.show()
        self.read_values = READ_CONTINUOUS

        layout = QVBoxLayout()
        self.tbl_parameters = self.findChild(QTableWidget, "tbl_parameters")
        layout.addWidget(self.tbl_parameters)
        self.setLayout(layout)


    def ret2main(self):
        self.connection_sts = self.galil.is_connected()
        self.close()


    def connect_device(self):
        self.log_to_terminal("Connecting...")
        try:

            self.galil.dmc_connect()
            if self.galil.is_connected():
                self.btn_connect.hide()
                self.btn_disconnect.show()
                self.log_to_terminal(f"Connection Successful. {self.galil.GInfo()}")

            else:
                self.btn_connect.show()
                self.btn_disconnect.hide()
        except Exception as e:
            self.log_to_terminal(f"Error Connecting {e}", level="error")

    def disconnect_device(self):
        try:
            self.galil.dmc_disconnect()

            if not self.galil.is_connected():
                self.btn_connect.show()
                self.btn_disconnect.hide()
                self.log_to_terminal("Disconnected from Controller", level="info")

        except Exception as e:
            self.log_to_terminal(f'"Disconnect failed"{e}', level="error")



    def poll_galil(self):

        try:
            if self.galil.is_connected():

                self.btn_disconnect.show()
                self.btn_connect.hide()
                for value in self.read_values:
                    self.current_values.append = self.galil.read_expr(value)  # wrapper: GCommand(f"MG {expr}")
            else:
                self.btn_disconnect.hide()
                self.btn_connect.show()

        except Exception as e:
            self.log_to_terminal(f'Failed to update Galil Values: {e}', level="error")


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
