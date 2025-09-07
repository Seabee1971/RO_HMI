from PyQt6.QtWidgets import QMainWindow, QPushButton
from PyQt6 import uic

class MaintenanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Maintenance_Window.ui", self)  # Load the .ui file
        self.setWindowTitle("Maintenance Window")
        self.showMaximized()
        self.btn_ret_main_screen =self.findChild(QPushButton, "btn_RetMainScreen")



        print(self.btn_ret_main_screen)
        self.btn_ret_main_screen.clicked.connect(self.ret2main)
    def ret2main(self):
        self.close()

