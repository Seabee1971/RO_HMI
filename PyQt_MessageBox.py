import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self, title="My App", width=600, height=400):
        super().__init__()
        self.msgBox = None
        self.setWindowTitle(title)
        self.setGeometry(100, 100, width, height)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI elements here. Extend this method in subclasses."""
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Example content
        label = QLabel("Hello, PyQt6 World!")
        label.setStyleSheet("font-size: 18px; padding: 10px;")

        layout.addWidget(label)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
    def msg_box(self,msg: str):
        self.msgBox = QMessageBox()
        self.msgBox.setText(msg)
        self.msgBox.setInformativeText('Test')
        self.msgBox.setStandardButtons(QMessageBox.setStandardButtons.Yes)

        ret =self.msgBox.exec()

def run_app(window_class=MainWindow, **kwargs):
    """Helper function to start the PyQt6 application."""
    app = QApplication(sys.argv)
    window = window_class(**kwargs)
    window.show()
    window.msg_box("Test")
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app(title="Reusable PyQt6 Window", width=800, height=500)
