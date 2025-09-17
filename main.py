import os
import sys
import time

from PyQt6.QtCore import QTimer, QObject, QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (QMainWindow, QApplication, QLabel, QPushButton, QPlainTextEdit, QMessageBox,
                             QDoubleSpinBox)
from PyQt6 import uic

from Handlers.widget_links import WIDGET_LINKS
from Handlers.galil import Galil
from Handlers.error_logging import (process_error_logger, process_info_logger)
import threading
from MaintWindow import MaintenanceWindow


class UI(QMainWindow):
    """Red Oktober HMI – UI logic only; Galil I/O via wrapper; logging centralized."""

    def __init__(self):
        super().__init__()

        # --- State ---
        self.running = False


        self.disconnected = False

        self.term_msg = None
        self.last_term_msg = ""

        # RPM calc state (if you enable speed later)
        self._rpm_last_rev = 0.0
        self._rpm_last_time = time.perf_counter()


        # Loggers
        self.process_error_log = process_error_logger
        self.process_info_log = process_info_logger
        self.process_info_log.info("Software Started...")

        self.galil = Galil(self.log_to_terminal)
        # --- Load UI ---
        uic.loadUi("RO_HMI.ui", self)
        self.setWindowTitle("Red Oktober")

        # --- Widgets (you can still keep direct references if you like) ---
        self.btn_abort_run   = self.findChild(QPushButton, "btn_Abort_Run")
        self.btn_connect     = self.findChild(QPushButton, "btn_Connect_to_Galil")
        self.btn_disconnect  = self.findChild(QPushButton, "btn_Disconnect_Galil")
        self.btn_end_run     = self.findChild(QPushButton, "btn_End_Run")
        self.btn_exit_app    = self.findChild(QPushButton, "btn_Exit")
        self.btn_pause_run   = self.findChild(QPushButton, "btn_Pause_Run")
        self.btn_start_run   = self.findChild(QPushButton, "btn_Start_Run")
        self.btn_trend_data  = self.findChild(QPushButton, "btn_Trend_Data")
        self.btn_maint_scrn  = self.findChild(QPushButton, "btn_maint_screen")

        self.dsb_Back_Distance   = self.findChild(QDoubleSpinBox, "dsb_Back_Distance")
        self.dsb_Shift_Distance = self.findChild(QDoubleSpinBox, "dsb_Shift_Distance")
        self.dsb_Offset_Distance = self.findChild(QDoubleSpinBox, "dsb_Offset_Distance")

        self.lbl_drum_rev_act    = self.findChild(QLabel, "lbl_Drum_Rev_Act")
        self.lbl_drum_speed_act  = self.findChild(QLabel, "lbl_Drum_Speed_Act")
        self.lbl_layer_count_act = self.findChild(QLabel, "lbl_Layer_Count_Act")
        self.lbl_Sw1_Off = self.findChild(QLabel, "lbl_Sw1_Off")
        self.lbl_Sw2_Off = self.findChild(QLabel,"lbl_Sw2_Off")
        self.lbl_Sw1_On = self.findChild(QLabel, "lbl_Sw1_On")
        self.lbl_Sw2_On = self.findChild(QLabel,"lbl_Sw2_On")
        self.lbl_Sw1_On.setVisible(False)
        self.lbl_Sw2_On.setVisible(False)
        self.lbl_Sw1_Off.setVisible(True)
        self.lbl_Sw2_Off.setVisible(True)

        self.terminal_window = self.findChild(QPlainTextEdit, "txt_Terminal_Window")
        self.terminal_window.setReadOnly(True)


        self.WIDGET_LINKS = WIDGET_LINKS
        # Audio system
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        #Load the Sound File
        self.player.setSource(QUrl.fromLocalFile("SubDiving.mp3"))

        # Resolve widgets & hook editors
        self._widget_links = []
        for widget in self.WIDGET_LINKS:
            obj = widget["object"]
            if widget["widget_type"] == "bool_pair":
                sw_on = self.findChild(QLabel, obj[0])
                sw_off = self.findChild(QLabel, obj[1])
                if sw_on is None or sw_off is None:
                    continue
                entry = dict(widget, widget=(sw_on, sw_off))
            else:
                current_widget = self.findChild(QObject, obj)
                if current_widget is None:
                    continue
                entry = dict(widget, widget=current_widget)
                if widget["widget_type"] == "doublespinbox" and widget["write_var"] and isinstance(current_widget, QDoubleSpinBox):
                    # capture entry to avoid late-binding in lambda
                    current_widget.editingFinished.connect(lambda e=entry: self._on_doublespin_commit(e))
            self._widget_links.append(entry)

        # --- Click handlers ---
        self.btn_abort_run.clicked.connect(self.abort_run)
        self.btn_start_run.clicked.connect(self.start_run)
        self.btn_end_run.clicked.connect(self.end_run)
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_exit_app.clicked.connect(self.exit_program)
        self.btn_pause_run.clicked.connect(self.launch_hunt)
        self.btn_maint_scrn.clicked.connect(self.open_maintenance_window)
        self.btn_disconnect.hide()
        self.maintenance_window= None

        # --- Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all_widgets)
        self.timer.start(50)

        self.showMaximized()
    def _on_doublespin_commit(self, entry: dict):
        w: QDoubleSpinBox = entry["widget"]
        write_var = entry["write_var"]
        convert_value = entry["convert_value"]

        text = w.text().strip()
        if text == "":
            self.log_to_terminal(f"{write_var} left blank; not sent")
            return

        try:
            text = text.removesuffix(' mm')
            val = convert_value(text)
        except Exception as e:
            self.log_to_terminal(f"Invalid input for {write_var}: {text} ({e})", level="error")
            return

        if self.galil.is_connected()  :
            try:
                self.galil.write_var(write_var, val)
                echoed = self.galil.read_expr(write_var)  # MG var
                self.log_to_terminal(f"{write_var} changed -> {val} (read back {echoed})")
            except Exception:
                self.log_to_terminal(f"{write_var} write failed (see software log)", level="error")
        else:
            self.log_to_terminal(f"{write_var} No Connection Failure to write-> {val}")


    def abort_run(self):
        self.galil.write_var("ST",1)
        self.log_to_terminal("Abort Run button clicked")

    def launch_hunt(self):
        self.log_to_terminal("Launching Hunt for Red Oktober...")
        import hunt_for_red_oktober.hunt as hunt
        threading.Thread(target=hunt, daemon=True).start()

    def connect_device(self):
        self.log_to_terminal("Connecting...")
        try:
            #self.player.play()
            self.galil.dmc_connect()
            if self.galil.is_connected():
                self.btn_connect.hide()
                self.btn_disconnect.show()
                self.btn_start_run.setEnabled(True)
                self.log_to_terminal(f"Connection Successful. {self.galil.get_info()}")
                self.log_to_terminal(f"Move Oiler to start position(Closest to the Drum)")

                # Push initial values from the three doublespinboxs (if present)
                vals = self.read_galil_inputs_from_ui()
                for var in ("back", "shift", "offset"):
                    v = vals.get(var)
                    if v is None:
                        continue
                    try:
                        # wrapper: name=value
                        self.galil.write_var(var, v)
                    except Exception as e:
                        self.log_to_terminal(f"Error sending {var}={v}: {e}", level="error")
            else:
                self.btn_connect.show()
                self.btn_disconnect.hide()
        except Exception as e:
            self.log_to_terminal(f"Error Connecting {e}", level="error")

    def disconnect_device(self):
        try:
           self.galil.dmc_disconnect()

        except Exception as e:

            self.log_to_terminal(f'"Disconnect failed" {e}',"error")

        if not self.galil.is_connected():
            self.btn_connect.show()
            self.btn_disconnect.hide()
            self.log_to_terminal("Disconnected from Controller")
    def end_run(self):
        try:
            end_box = QMessageBox()
            end_box.setText("Are you sure you want to end the run?")
            end_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            ret = end_box.exec()
            if ret == QMessageBox.StandardButton.Yes:
                self.log_to_terminal("End Run confirmed")
                if self.galil.is_connected():
                    self.galil.write_var("start",0)
            else:
                self.log_to_terminal("End Run cancelled")
        except Exception as e:
            self.log_to_terminal(f'"Error End Run" {e}', level="error")

    def exit_program(self):
        exit_box = QMessageBox()
        exit_box.setText("Are you sure you want to exit program?")
        exit_box.setStandardButtons(QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        ret = exit_box.exec()

        if ret == QMessageBox.StandardButton.Yes:
            try:
                self.disconnect_device()
                if self.galil.is_connected():
                    return
                self.log_to_terminal("Program Exiting.")
                QTimer.singleShot(2000, QApplication.instance().quit)
            except Exception as e:
                self.log_to_terminal(f"Exit Program Exception: {e}", level="error")


    def log_to_terminal(self, msg: str, level: str = "info"):

        msg = msg.replace("→", "->")  # keep CP1252-safe
        self.term_msg = msg
        self.update_terminal_window()
        if level == "error":
            self.process_error_log.error(msg)
        else:
            self.process_info_log.info(msg)

    def open_maintenance_window(self):
        if self.maintenance_window is None:
            self.maintenance_window = MaintenanceWindow(self, self.log_to_terminal, self.galil)
        self.hide()
        self.maintenance_window.show()

    def parse_number(self, text: str):
        text = str(text).removesuffix(' mm')
        if text == "":
            return False, None, "empty"
        try:
            return True, float(text), None
        except ValueError:
            return False, text, "not_numeric"
    def pause_run(self):
        self.log_to_terminal("Pause Run button clicked")
        self.launch_hunt()

    def poll_widget_links(self):
        if not (self.galil.is_connected()):
            return

        for e in self._widget_links:
            expr = e.get("read_expr")
            if not expr:
                continue

            try:
                raw = self.galil.read_expr(expr)   # wrapper: GCommand(f"MG {expr}")
                val = e["convert_value"](raw)

                widget_type = e["widget_type"]
                if widget_type == "label":
                    lbl: QLabel = e["widget"]
                    lbl.setText(e["fmt"](val))

                elif widget_type == "D":
                    # if you want to reflect device changes into the field, uncomment:
                    current_widget: QDoubleSpinBox = e["widget"]
                    current_widget.setText(e["fmt"](val))
                    pass

                elif widget_type == "bool_pair":
                    grn, red = e["widget"]
                    is_on = bool(val)
                    grn.setVisible(is_on)
                    red.setVisible(not is_on)

            except Exception as e:
                # Don't spam; log stack once per problematic expr
                self.log_to_terminal(f"Poll failed for {expr} Error: {e}")

    def read_galil_inputs_from_ui(self) -> dict:
        """Return dict of {'back': value/None, ...} using BINDINGS for doublespinboxs."""
        values = {}
        for e in self._widget_links:
            if e["widget_type"] != "doublespinbox":
                continue
            w: QDoubleSpinBox = e["widget"]
            ok, value, _ = self.parse_number(w.text())
            values[e["write_var"]] = value if ok else None
        return values

    def start_run(self):
        try:
            ok,vals = self._check_start_params()
            print(ok,vals)

            if ok:
                self.log_to_terminal(f'Back,Shift,Offset = {vals}')
                self.log_to_terminal(f"Start Run with {vals}")
                self.galil.write_var("start", 1)
            else:
                self.log_to_terminal(f"Please set {vals} then try again", level="info")
        except Exception as e:
            self.log_to_terminal(f"Failed to start run: {e}", level="error")



    def update_all_widgets(self):
        self.update_terminal_window()
        if self.galil.is_connected():
            self.btn_connect.hide()
            self.btn_disconnect.show()
            self.poll_widget_links()



    def update_terminal_window(self):
        if self.term_msg is not None and self.last_term_msg != self.term_msg:
            try:
                self.terminal_window.appendPlainText(str(self.term_msg))
                self.last_term_msg = self.term_msg
            except Exception as e:
                self.log_to_terminal(f"Terminal window update failed: {e}", level="error")


    def write_galil_values_to_ui(self, galil_values: dict) -> None:
        """Write values back into mapped doublespinboxs."""
        for e in self._widget_links:
            if e["widget_type"] != "doublespinbox":
                continue
            w: QDoubleSpinBox = e["widget"]
            var = e["write_var"]
            if var in galil_values:
                v = galil_values[var]
                w.setText("" if v is None else e["fmt"](v))

    def _check_start_params(self):
        try:
            vals = self.read_galil_inputs_from_ui()  # {'back': .., 'shift': .., 'offset': ..}

            for v in vals.items():
                if v[1] > 0.0:
                    pass
                else:
                    return False,v
            return True,v

        except Exception as e:
            self.log_to_terminal(f"Failed to start run: {e}", level="error")
            return False



if __name__ == "__main__":
    os.environ["QT_QPA_PLATFORM"] = "windows"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    UIWindow = UI()
    app.exec()
