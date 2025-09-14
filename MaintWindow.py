from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt6 import uic

class MaintenanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Maintenance_Window.ui", self)  # Load the .ui file
        self.setWindowTitle("Maintenance Window")
        self.showMaximized()
        self.btn_ret_main_screen = self.findChild(QPushButton, "btn_RetMainScreen")
        self.tbl_parameters = self.findChild(QTableWidget, "tbl_parameters")

        print(self.btn_ret_main_screen)
        self.btn_ret_main_screen.clicked.connect(self.ret2main)
        self.update_tbl_parameters()
    def ret2main(self):
        self.close()

    def update_tbl_parameters(self):
        self.data = [("test1", "test2"), ("test3", "test4")]

        self.tbl_parameters.setRowCount(len(self.data))
        self.tbl_parameters.setColumnCount(len(self.data[0]))
        self.tbl_parameters.setHorizontalHeaderLabels(["Column 1", "Column 2"])

        for row_index, row_data in enumerate(self.data):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.tbl_parameters.setItem(row_index, col_index, item)
