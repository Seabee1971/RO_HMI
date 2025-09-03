import time

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QPlainTextEdit, QMessageBox
from PyQt6 import uic
import sys
from Handlers.galil import Galil
from Handlers.error_logging import *

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        self._rpm_last_rev = None
        self.disconnected = None
        self._rpm_last_time = None
        self.rpm = None
        self.previous_rev_count = 0
        self.galil_object = None
        self.term_msg = None
        self.last_term_msg = ""
        self.galil = Galil()
        self.connection_sts = False
        _ = datetime.now()
        self.software_error_log = software_logger
        self.process_error_log = process_error_logger
        self.process_info_log = process_info_logger
        self.process_info_log.info(f'Software Started...')
            # Load .ui
        uic.loadUi("RO_HMI.ui", self)

        # Map widget objectName ----> Galil variable
        self.ui_to_galil = {
            "lned_Back_Distance":  "back",
            "lned_Shift_Distance": "shift",
            "lned_Offset_Distance":"offset",
        }
        # Hook per-field updates
        for widget_name, galil_name in self.ui_to_galil.items():
            widget = self.findChild(QLineEdit, widget_name)
            if widget:
                widget.editingFinished.connect(
                    lambda gname=galil_name, w=widget: self.on_lineedit_changed(gname, w)
                )

        # Window title
        self.setWindowTitle("Red Oktober")

        # Buttons
        self.btn_abort_run   = self.findChild(QPushButton, "btn_Abort_Run")
        self.btn_connect     = self.findChild(QPushButton, "btn_Connect_to_Galil")
        self.btn_disconnect  = self.findChild(QPushButton, "btn_Disconnect_Galil")
        self.btn_end_run     = self.findChild(QPushButton, "btn_End_Run")
        self.btn_exit_app    = self.findChild(QPushButton, "btn_Exit")
        self.btn_pause_run   = self.findChild(QPushButton, "btn_Pause_Run")
        self.btn_start_run   = self.findChild(QPushButton, "btn_Start_Run")
        self.btn_trend_data  = self.findChild(QPushButton, "btn_Trend_Data")

        # LineEdits
        self.linedit_back_distance   = self.findChild(QLineEdit, "lned_Back_Distance")
        self.linedit_offset_distance = self.findChild(QLineEdit, "lned_Offset_Distance")
        self.linedit_shift_distance  = self.findChild(QLineEdit, "lned_Shift_Distance")

        # Labels
        self.lbl_drum_rev_act    = self.findChild(QLabel, "lbl_Drum_Rev_Act")
        self.lbl_drum_speed_act  = self.findChild(QLabel, "lbl_Drum_Speed_Act")
        self.lbl_layer_count_act = self.findChild(QLabel, "lbl_Layer_Count_Act")
        self.lbl_sw1_grn         = self.findChild(QLabel, "lbl_Sw1_Grn")
        self.lbl_sw1_red = self.findChild(QLabel, "lbl_Sw1_Red")
        self.lbl_sw2_grn = self.findChild(QLabel, "lbl_Sw2_Grn")
        self.lbl_sw2_red = self.findChild(QLabel, "lbl_Sw2_Red")

        # Terminal
        self.terminal_window = self.findChild(QPlainTextEdit, "txt_Terminal_Window")
        self.terminal_window.setReadOnly(True)

        # Click handlers
        self.btn_abort_run.clicked.connect(self.abort_run)
        self.btn_start_run.clicked.connect(self.start_run)
        self.btn_end_run.clicked.connect(self.end_run)
        self.btn_disconnect.hide()
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_exit_app.clicked.connect(self.exit_program)
        self.btn_pause_run.clicked.connect(self.pause_run)
        # (hook Trend if/when you implement it)
        # self.btn_trend_data.clicked.connect(self.trend_run)

        # QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all_widgets)
        self.timer.start(50)

        self.showMaximized()

    # ---------- Button slots ----------
    def abort_run(self):
        self.term_msg = "Abort Run button clicked"
        

    def start_run(self):
        input_values =[]
        vals = self.read_galil_inputs_from_ui()  # {'back': .., 'shift': .., 'offset': ..}
        # vals is a dict like {"back": 42.0, "shift": 10.0, "offset": 5.0}

        if all(v is not None and isinstance(v, (int, float)) for v in vals.values()):
            self.term_msg = f"Start Run with {vals}"

        else:
            self.term_msg = f'Unable to Run...\r\nPlease Set the back, shift and offset and try again'
            self.update_terminal_window()


    def end_run(self):
        self.term_msg = "End Run button clicked"

    def pause_run(self):
        self.term_msg = "Pause Run button clicked"

    def connect_device(self):
        self.term_msg = "Connecting..."
        try:
            connected, self.galil_object = self.galil.dmc_connect()

            if connected:
                self.connection_sts = True
                self.btn_connect.hide()
                self.btn_disconnect.show()
                self.term_msg = f'Connection Successful\r\n{str(connected)}'
                self.process_info_log.info(self.term_msg)
                self.btn_start_run.setEnabled(True)

                # --- NEW: read UI and push to Galil on connect ---
                vals = self.read_galil_inputs_from_ui()  # {'back': ..., 'shift': ..., 'offset': ...}

                assignments = []
                for var in ("back", "shift", "offset"):
                    value = vals.get(var, None)
                    if value is None:
                        continue  # skip empty fields
                    assignments.append(f"{var}={value}")

                if assignments:
                    cmd = ";".join(assignments) + ";"  # Galil likes ';' between/after commands
                    try:
                        self.galil_object.GCommand(cmd)
                        self.term_msg = f"{self.term_msg}\nSent: {cmd}"
                        self.process_info_log.info(self.term_msg)
                    except Exception as e:
                        self.term_msg = f"{self.term_msg}\nError sending values: {e}"
                        self.process_info_log.info(self.term_msg)
                        self.software_error_log.error(self.term_msg)
                # -------------------------------------------------

            else:
                self.connection_sts = False
                self.btn_connect.show()
                self.btn_disconnect.hide()

        except Exception as e:
            self.term_msg = f"Error Connecting: {e}"
            # self.update_terminal_window()
            self.software_error_log.exception("Error Connecting")

    def disconnect_device(self):
        self.disconnected, self.galil_object = self.galil.dmc_disconnect()
        if self.disconnected:
            self.term_msg = "Disconnected from Controller"
            self.update_terminal_window()
            self.connection_sts = False
            self.process_info_log.info(self.term_msg)
            self.btn_connect.show()
            self.btn_disconnect.hide()

    def exit_program(self):
        try:
            self.disconnect_device()
            if not self.connection_sts:
                self.term_msg = "Disconnected from Controller.."
                #self.update_terminal_window()
                time.sleep(1)
                self.term_msg = "Program Exiting."
                # self.update_terminal_window()
                self.process_info_log.info(self.term_msg)
                QTimer.singleShot(200, QApplication.instance().quit)

        except Exception as e:
            self.software_error_log.error(f'Shit Anthony must have fucked this up! {e}')



    # ---------- Simple label demos (keep if you use them) ----------
    def drum_rev_act(self):
        # Example write via your galil wrapper
        try:
            cmd = "REV"
            rev_count = float(self.galil.read_input(cmd))
            # if rev_count > self.previous_rev_count:
            #     self.lbl_drum_rev_act.setText(str(rev_count))
            #     self.previous_rev_count = rev_count
            #     #self.rpm = self.update_drum_speed(rev_count)

        except Exception as e:
            if self.last_term_msg != e:
                self.term_msg = f'drum_rev_act exception = {e}'
                self.software_error_log.error(self.term_msg)
                # self.update_terminal_window()
                self.last_term_msg = self.term_msg

    def drum_speed_act(self):
        try:
            self.lbl_drum_speed_act.setText(self.rpm)
        except Exception as e:
            self.term_msg = f"Error: Drum Speed Act {str(e)}"
            self.software_error_log.error(self.term_msg)
            # self.update_terminal_window()

    # ---------- QLineEdit utilities ----------
    def on_lineedit_changed(self, galil_name: str, widget: QLineEdit) -> None:
        text_value = widget.text().strip()
        if text_value == "":
            value = None
        else:
            try:
                value = float(text_value)
            except ValueError as e:
                value = text_value
                self.term_msg = f"Input is not a float value: {str(e)}"
                self.process_info_log(self.term_msg)
                # self.update_terminal_window()

        # send live if connected
        if self.connection_sts and hasattr(self, "galil_object") and self.galil_object:
            try:
                if value is not None:
                    self.galil_object.GCommand(f"{galil_name}={value}")
                    echoed = self.galil_object.GCommand(f"MG {galil_name}").strip()
                    self.term_msg = f"{galil_name} changed ----> {value} (read back {echoed})"
                    self.process_info_log.info(self.term_msg)
                else:
                    self.term_msg = f"{galil_name} left blank; not sent"
                    self.process_info_log.info(self.term_msg)
            except Exception as e:
                self.term_msg = f"{galil_name} write failed: {e}"
                self.software_error_log.error(self.term_msg)
                # self.update_terminal_window()
        else:
            # not connected yet—just log the change
            self.term_msg = f"{galil_name} changed ----> {value}"
            self.process_info_log.info(self.term_msg)

    def read_galil_inputs_from_ui(self) -> dict:
        """Return {'back': val, 'shift': val, 'offset': val} from QLineEdits."""
        values = {}
        for widget_name, galil_name in self.ui_to_galil.items():
            widget = self.findChild(QLineEdit, widget_name)
            if not widget:
                continue
            text_value = widget.text().strip()
            if text_value == "":
                values[galil_name] = None
            else:
                try:
                    values[galil_name] = float(text_value)
                except ValueError:
                    values[galil_name] = text_value
                    self.term_msg = f"Input is not a float value: {text_value}"
                    self.software_error_log.error(self.term_msg)
                    # self.update_terminal_window()
        return values

    def write_galil_values_to_ui(self, galil_values: dict) -> None:
        """Write {'back': val, ...} into the mapped QLineEdits."""
        for widget_name, galil_name in self.ui_to_galil.items():
            if galil_name not in galil_values:
                continue
            widget = self.findChild(QLineEdit, widget_name)
            if widget:
                value = galil_values[galil_name]
                widget.setText("" if value is None else str(value))

    # ---------- Terminal + periodic update ----------
    def update_terminal_window(self):
        if self.term_msg is not None and self.last_term_msg != self.term_msg:
            try:
                self.terminal_window.appendPlainText(str(self.term_msg))
                self.last_term_msg = self.term_msg
            except Exception as e:
                self.term_msg = f"Terminal window update failed: {e}"
                self.software_error_log.error(self.term_msg)

    def update_all_widgets(self):
        self.update_terminal_window()
        if self.connection_sts:
            self.drum_rev_act()
            self.drum_speed_act()

    def update_drum_speed(self, current_rev: float) -> float:
        if self._rpm_last_time is None:
            self._rpm_last_time = time.perf_counter()
            delta_t = self._rpm_last_time
            delta_rev = current_rev - self._rpm_last_rev
            now = 0
        else:
            now = time.perf_counter()
            delta_t = now - self._rpm_last_time
            delta_rev = current_rev - self._rpm_last_rev
            rpm = 0.0


        if delta_t > 0:
            revs_per_sec = delta_rev / delta_t
            rpm = revs_per_sec * 60.0

        # persist state for next tick
        self._rpm_last_rev = current_rev
        self._rpm_last_time = now

        # push to UI (rename label if you have a dedicated RPM label)
        try:
            self.lbl_drum_speed_act.setText(f"{rpm:.2f}")
        except Exception as e:
            self.term_msg = f"SHIT DAMN FUCK Unable to update drum speed: {e}"
            self.software_error_log.error(self.term_msg)

        return rpm


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    UIWindow = UI()
    app.exec()
