from PyQt6.QtGui import QIcon, QBrush
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QTextEdit, QPushButton, QLineEdit
from PyQt6 import uic
import sys
from WidgetHandlers.WriteOutputValues import WriteWidgetOutputs as Writer
from WidgetHandlers.galil import galil

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        self.galil = galil

        # Load uic file
        uic.loadUi("RO_HMI.ui", self)
        self.x = 0
        labels = self.findChildren(QLabel)
        # Set the window title and icon
        self.setWindowTitle("RO HMI")
        self.setWindowIcon(QIcon("icon.png"))

        #Define Buttons

        self.btn_abort_run = self.findChild(QPushButton, "btn_Abort_Run")
        self.btn_connect = self.findChild(QPushButton, "btn_Connect_to_Galil")
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

        # Widget button click

        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_exit_app.clicked.connect(self.exit)
        #  Show the App
        self.showMaximized()

    def drum_rev_act(self):
        self.x+=1
        Writer.write(self, self.lbl_drum_rev_act, value=str(self.x))
        #self.lbl_Drum_Rev_Act.setText("drum_rev_act")
    def drum_speed_act(self):
        Writer.write(self, self.lbl_Drum_Speed_Act, "2032")

    def abort_run(self):
        # This function will be called when the button is clicked
        print("Abort Run button clicked")

    def connect_device(self):
        # This function will be called when the button is clicked
        print(dir(self.btn_connect))
        self.btn_connect.setStyleSheet("background-color: green;")

    def disconnect_device(self):
        # This function will be called when the button is clicked
        print("Disconnect button clicked")

    def end_run(self):
        # This function will be called when the button is clicked
        print("End Run button clicked")

    def exit(self):
        sys.exit(1)

    def pause_run(self):
        # This function will be called when the button is clicked
        print("Pause Run button clicked")

    def on_button_clicked(self, button: QPushButton):
        print(f"Button {button.objectName()} clicked")

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
