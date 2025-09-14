from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QPushButton, QTableView, QTableWidgetItem, QTableWidget
from PyQt6 import uic

class MaintenanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Maintenance_Window.ui", self)  # Load the .ui file
        self.setWindowTitle("Maintenance Window")
        self.showMaximized()
        self.btn_ret_main_screen =self.findChild(QPushButton, "btn_RetMainScreen")
        self.tbl_parameters = self.findChild(QTableView, "tbl_parameters")

        print(self.btn_ret_main_screen)
        self.btn_ret_main_screen.clicked.connect(self.ret2main)
        self.update_tbl_parameters()
    def ret2main(self):
        self.close()

    def update_tbl_parameters(self):
        try:
            self.data = [('test1', 'test2'), ('test3', 'test4')]

            # 1. Create a model
            model = QStandardItemModel(len(self.data), len(self.data[0]))

            # Optional: Set header labels
            model.setHorizontalHeaderLabels(['Column 1', 'Column 2'])

            # 2. Populate the model with data
            for row_index, row_data in enumerate(self.data):
                for col_index, cell_data in enumerate(row_data):
                    item = QStandardItem(cell_data)
                    model.setItem(row_index, col_index, item)

            # 3. Set the model on the QTableView from your UI file
            self.tbl_parameters.setModel(model)

        except Exception as e:
            # Assuming you have this method, otherwise just use print()
            #self.log_to_terminal(f"Failed to update table: {e}", level="error")
            print(f'Error: {e}')