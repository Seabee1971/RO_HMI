from PyQt6.QtWidgets import QLabel, QPushButton


class WriteWidgetOutputs:
    def __init__(self):
        pass

    def write(self,widget,value):
        if type(widget) == QLabel:
            widget.setText(str(value))
        # elif type(widget) == QPushButton:
        #     widget.


