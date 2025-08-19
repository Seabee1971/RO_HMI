from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow,QApplication,QLabel,QTextEdit,QPushButton
from PyQt6 import uic
import sys
from LoadWidgets.button_methods import button_methods


class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()

        #Load uic file
        uic.loadUi("RO_HMI.ui",self)
        labels = self.findChildren(QLabel)

        textEdit =self.findChildren(QTextEdit)
        buttons = self.findChildren(QPushButton)
        #  Show the App
        self.showMaximized()
        self.connect_buttons(buttons)
        self.connect_labels(labels)

    def connect_buttons(self,buttons):
        for btn in buttons:
            if btn.objectName() in button_methods:
                # Call the method associated with the button
                btn.clicked.connect(getattr(self, button_methods[btn.objectName()]))
            else:
                print(btn.objectName(), "not found in button_methods")

    def connect_labels(self,labels):

        for label in labels:
            print(label.objectName())


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

        # Set the window title and icon
        self.setWindowTitle("RO HMI")
        self.setWindowIcon(QIcon("icon.png"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    UIWindow = UI()

    app.exec()



