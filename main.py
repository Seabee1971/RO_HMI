from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow,QApplication,QLabel,QTextEdit,QPushButton
from PyQt6 import uic
import sys

class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()
        # Dynamically assigned button methods
        button_methods = {
            "btn_Abort_Run": self.abort_run,
            "btn_Start_Run": self.start_run,
            "btn_Stop_Run": self.stop_run,
            "btn_Exit": self.close,
            "btn_Connect_to_Galil": self.connect_device,
            "btn_Disconnect": self.disconnect_device,
            "btn_Pause_Run": self.pause_run,
            "btn_End_Run": self.end_run,
            "btn_Trend_Data":self.trend_run
        }

        #Load uic file
        uic.loadUi("RO_HMI.ui",self)
        label = self.findChildren(QLabel)
        textEdit =self.findChildren(QTextEdit)
        buttons = self.findChildren(QPushButton)
        #  Show the App
        self.showMaximized()
        for btn in buttons:
            print(btn.objectName())
            if btn.objectName() in button_methods:
                # Call the method associated with the button

                btn.clicked.connect(button_methods[btn.objectName()])
            else:
                print(btn.objectName(), "not found in button_methods")



            #self.show()

    def abort_run(self):
        # This function will be called when the button is clicked
        print("Abort Run button clicked")

    def connect_device(self):
        # This function will be called when the button is clicked
        print("Connect button clicked")
    def disconnect_device(self):
        # This function will be called when the button is clicked
        print("Disconnect button clicked")
    def end_run(self):
        # This function will be called when the button is clicked
        print("End Run button clicked")
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

        # Set the window title and icon
        self.setWindowTitle("RO HMI")
        self.setWindowIcon(QIcon("icon.png"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    UIWindow = UI()
    app.exec()



