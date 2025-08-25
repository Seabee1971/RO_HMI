import time

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QBrush
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QTextEdit, QPushButton, QLineEdit, QPlainTextEdit
from PyQt6 import uic
import sys
from Handlers.WriteOutputValues import WriteWidgetOutputs as Writer
from Handlers.galil import galil


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        self.galil = galil()

        # Load uic file
        uic.loadUi("RO_HMI.ui", self)
        self.x = 0
        labels = self.findChildren(QLabel)
        # Set the window title and icon
        self.setWindowTitle("RO HMI")
        self.setWindowIcon(QIcon("icon.png"))
        self.counter = 0
        #Define Buttons

        self.btn_abort_run = self.findChild(QPushButton, "btn_Abort_Run")
        self.btn_connect = self.findChild(QPushButton, "btn_Connect_to_Galil")
        self.btn_disconnect = self.findChild(QPushButton, "btn_Disconnect_Galil")
        self.btn_end_run = self.findChild(QPushButton,"btn_End_Run")
        self.btn_exit_app = self.findChild(QPushButton,"btn_Exit")
        self.btn_pause_run = self.findChild(QPushButton,"btn_Pause_Run")
        self.btn_start_run = self.findChild(QPushButton, "btn_Start_Run")
        self.btn_trend_data = self.findChild(QPushButton, "btn_Trend_Data")

        #Define LineEdits

        self.linedit_back_distance = self.findChild(QLineEdit, "lned_Back_Distance")
        self.linedit_offset_distance = self.findChild(QLineEdit, "lned_Offset_Distance")
        self.linedit_shift_distance = self.findChild(QLineEdit, "lned_Shift_Distance")

        #Define Labels
        self.lbl_drum_rev_act = self.findChild(QLabel, "lbl_Drum_Rev_Act")
        self.lbl_drum_speed_act = self.findChild(QLabel, "lbl_Drum_Speed_Act")
        self.lbl_layer_count_act = self.findChild(QLabel, "lbl_Layer_Count_Act")
        self.lbl_sw1_grn = self.findChild(QLabel, "lbl_Sw1_Grn")
        self.lbl_sw1_red = self.findChild(QLabel, "lbl_Sw1_Red")
        self.lbl_sw2_grn = self.findChild(QLabel, "lbl_Sw2_Grn")
        self.lbl_sw2_red = self.findChild(QLabel, "lbl_Sw2_Red")

        #Define PlainTextBox Window
        self.terminal_window = self.findChild(QPlainTextEdit, "txt_Terminal_Window")
        self.terminal_window.appendPlainText("Starting program...")
        # Widget button click
        self.btn_disconnect.hide()
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_exit_app.clicked.connect(self.exit)

        # QTimer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all_widgets)
        self.timer.start(50)  # 50 milliseconds
        #  Show the App
        self.showMaximized()

    def drum_rev_act(self):
        self.x+=1
        Writer.write(self, self.lbl_drum_rev_act, value=str(self.x))
        #self.lbl_Drum_Rev_Act.setText("drum_rev_act")
    def drum_speed_act(self):
        Writer.write(self, self.lbl_drum_speed_act, "2032")

    def abort_run(self):
        # This function will be called when the button is clicked
        print("Abort Run button clicked")

    def connect_device(self):
        # This function will be called when the button is clicked

        self.terminal_window.appendPlainText("Connecting...")
        try:
            self.connected,self.galil_object = self.galil.dmc_connect()
            self.terminal_window.appendPlainText(str(self.connected))
            if self.connected == True:
                self.btn_connect.hide()

                self.btn_disconnect.setStyleSheet(self.button.green)
                self.btn_disconnect.show()
                self.terminal_window.appendPlainText(f'Connection Successful\r\n{str(self.connected)}')
                #self.btn_connect.setStyleSheet(self.button.green)
            else:
                self.btn_connect.show()
                self.btn_disconnect.hide()

        except Exception as e:
            print(e)

    def update_all_widgets(self):
        """Refresh dynamic label values."""
        self.drum_rev_act()
        self.drum_speed_act()

    def disconnect_device(self):
        self.galil.dmc_disconnect()# This function will be called when the button is clicked
        self.terminal_window.appendPlainText("Disconnected from Controller")

    def end_run(self):
        # This function will be called when the button is clicked
        self.galil.dmc_disconnect()
        print("End Run button clicked")

    def exit(self):
        self.galil.dmc_disconnect()
        self.terminal_window.appendPlainText("Disconnected from Controller\r\nHmi Shutting Down in 5 seconds")
        time.sleep(5)
        sys.exit(1)

    def pause_run(self):
        # This function will be called when the button is clicked
        print("Pause Run button clicked")

    def start_run(self):
        # This function will be called when the button is clicked
        print("Start Run button clicked")

    def stop_run(self):
        # This function will be called when the button is clicked
        print("Stop Run button clicked")

    def trend_run(self):
        # This function will be called when the button is clicked
        print("Trend Data button clicked")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    UIWindow = UI()

    app.exec()
