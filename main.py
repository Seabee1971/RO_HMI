import sys
import time
from datetime import datetime

from PyQt6.QtCore import QTimer, QObject, QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QPlainTextEdit, QMessageBox
)
from PyQt6 import uic


from Handlers.galil import Galil          # Ensure Galil has read_expr() and write_var()
from Handlers.error_logging import (      # Assumes these are configured at import
    software_logger, process_error_logger, process_info_logger
)
from MaintWindow import MaintenanceWindow

class UI(QMainWindow):
    """Red Oktober HMI – UI logic only; Galil I/O via wrapper; logging centralized."""

    def __init__(self):
        super().__init__()

        # --- State ---
        self.galil = Galil()
        self.galil_object = None
        self.connection_sts = False
        self.disconnected = False

        self.term_msg = None
        self.last_term_msg = ""

        # RPM calc state (if you enable speed later)
        self._rpm_last_rev = 0.0
        self._rpm_last_time = time.perf_counter()

        # Loggers
        self.software_error_log = software_logger
        self.process_error_log = process_error_logger
        self.process_info_log = process_info_logger
        self.process_info_log.info("Software Started...")

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

        self.linedit_back_distance   = self.findChild(QLineEdit, "lned_Back_Distance")
        self.linedit_shift_distance  = self.findChild(QLineEdit, "lned_Shift_Distance")
        self.linedit_offset_distance = self.findChild(QLineEdit, "lned_Offset_Distance")

        self.lbl_drum_rev_act    = self.findChild(QLabel, "lbl_Drum_Rev_Act")
        self.lbl_drum_speed_act  = self.findChild(QLabel, "lbl_Drum_Speed_Act")
        self.lbl_layer_count_act = self.findChild(QLabel, "lbl_Layer_Count_Act")

        self.lbl_sw1_grn = self.findChild(QLabel, "lbl_Sw1_Grn")
        self.lbl_sw1_red = self.findChild(QLabel, "lbl_Sw1_Red")
        self.lbl_sw2_grn = self.findChild(QLabel, "lbl_Sw2_Grn")
        self.lbl_sw2_red = self.findChild(QLabel, "lbl_Sw2_Red")

        self.terminal_window = self.findChild(QPlainTextEdit, "txt_Terminal_Window")
        self.terminal_window.setReadOnly(True)

        # Initial indicator state
        if self.lbl_sw1_grn and self.lbl_sw1_red:
            self.lbl_sw1_grn.setVisible(False)
            self.lbl_sw1_red.setVisible(True)
        if self.lbl_sw2_grn and self.lbl_sw2_red:
            self.lbl_sw2_grn.setVisible(False)
            self.lbl_sw2_red.setVisible(True)

        # --- Bindings registry (one source of truth) ---
        # kind: "lineedit" (two-way) | "label" (device→UI) | "bool_pair" (device→two labels)
        # read_expr: expression usable by MG (e.g., "@IN[6]", "_TPX"). None if not polled.
        # write_var: Galil variable name for "var=value". None if read-only.
        # coerce: device text -> python value. fmt: python value -> display text.
        self.BINDINGS = [
            # Two-way numeric inputs
            dict(object="lned_Back_Distance",   kind="lineedit", read_expr=None, write_var="back",
                 coerce=float, fmt=lambda v: f"{v:g}"),
            dict(object="lned_Shift_Distance",  kind="lineedit", read_expr=None, write_var="shift",
                 coerce=float, fmt=lambda v: f"{v:g}"),
            dict(object="lned_Offset_Distance", kind="lineedit", read_expr=None, write_var="offset",
                 coerce=float, fmt=lambda v: f"{v:g}"),

            # Device → UI labels (examples; adjust to your actual variables)
            dict(object="lbl_Drum_Rev_Act",   kind="label", read_expr="rev",  write_var=None,
                 coerce=lambda s: float(s), fmt=lambda v: f"{v:.0f}"),
            dict(object="lbl_Drum_Speed_Act", kind="label", read_expr="_TDX", write_var=None,
                 coerce=lambda s: float(s), fmt=lambda v: f"{v:.2f}"),
            # dict(object="lbl_Layer_Count_Act", kind="label", read_expr="_TPY", write_var=None,
            #      coerce=lambda s: float(s), fmt=lambda v: f"{v:.0f}"),

            # Boolean LED pairs (using @IN[] that return 0.0000 / 1.0000)
            dict(object=("lbl_Sw1_Grn", "lbl_Sw1_Red"), kind="bool_pair", read_expr="@IN[6]", write_var=None,
                 coerce=lambda s: float(s) >= 0.5, fmt=None),
            dict(object=("lbl_Sw2_Grn", "lbl_Sw2_Red"), kind="bool_pair", read_expr="@IN[8]", write_var=None,
                 coerce=lambda s: float(s) >= 0.5, fmt=None),
        ]
        # Audio system
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        #Load the Sound File
        self.player.setSource(QUrl.fromLocalFile("SubDiving.mp3"))

        # Resolve widgets & hook editors
        self._bindings = []
        for b in self.BINDINGS:
            obj = b["object"]
            if b["kind"] == "bool_pair":
                grn = self.findChild(QLabel, obj[0])
                red = self.findChild(QLabel, obj[1])
                if grn is None or red is None:
                    continue
                entry = dict(b, widget=(grn, red))
            else:
                w = self.findChild(QObject, obj)
                if w is None:
                    continue
                entry = dict(b, widget=w)
                if b["kind"] == "lineedit" and b["write_var"] and isinstance(w, QLineEdit):
                    # capture entry to avoid late-binding in lambda
                    w.editingFinished.connect(lambda e=entry: self._on_lineedit_commit(e))
            self._bindings.append(entry)

        # --- Click handlers ---
        self.btn_abort_run.clicked.connect(self.abort_run)
        self.btn_start_run.clicked.connect(self.start_run)
        self.btn_end_run.clicked.connect(self.end_run)
        self.btn_connect.clicked.connect(self.connect_device)
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_exit_app.clicked.connect(self.exit_program)
        self.btn_pause_run.clicked.connect(self.pause_run)
        self.btn_maint_scrn.clicked.connect(self.openMaintenanceWindow)
        self.btn_disconnect.hide()
        self.maintenance_window= None
        # --- Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all_widgets)
        self.timer.start(50)

        self.showMaximized()

    def openMaintenanceWindow(self):
        if self.maintenance_window is None:
            self.maintenance_window = MaintenanceWindow()
        self.maintenance_window.show()



    # ---------- Helpers ----------
    def parse_number(self, text: str):
        text = str(text).strip()
        if text == "":
            return False, None, "empty"
        try:
            return True, float(text), None
        except ValueError:
            return False, text, "not_numeric"

    def log_to_terminal(self, msg: str, level: str = "info"):
        if not isinstance(msg, str):
            msg = str(msg)
        msg = msg.replace("→", "->")  # keep CP1252-safe
        self.term_msg = msg
        self.update_terminal_window()
        if level == "error":
            self.process_error_log.error(msg)
        else:
            self.process_info_log.info(msg)

    # ---------- Button slots ----------
    def abort_run(self):
        self.log_to_terminal("Abort Run button clicked")

    def start_run(self):
        vals = self.read_galil_inputs_from_ui()  # {'back': .., 'shift': .., 'offset': ..}
        if all(v is not None and isinstance(v, (int, float)) for v in vals.values()):
            self.log_to_terminal(f"Start Run with {vals}")
            # TODO: start your run logic here
        else:
            self.log_to_terminal("Please set back, shift, and offset, then try again", level="error")

    def end_run(self):
        reply = QMessageBox.question(
            self, "Confirm End", "Are you sure you want to end run?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.log_to_terminal("End Run confirmed")
        else:
            self.log_to_terminal("End Run cancelled")

    def pause_run(self):
        self.log_to_terminal("Pause Run button clicked")

    def connect_device(self):
        self.log_to_terminal("Connecting...")
        try:
            self.player.play()
            connected, self.galil_object = self.galil.dmc_connect()
            if connected:
                QMessageBox.information(self, "Reminder", "Position Oiler in Forward\rPosition Against Drum")
                self.connection_sts = True
                self.btn_connect.hide()
                self.btn_disconnect.show()
                self.btn_start_run.setEnabled(True)
                self.log_to_terminal(f"Connection Successful. {connected}")

                # Push initial values from the three lineedits (if present)
                vals = self.read_galil_inputs_from_ui()
                for var in ("back", "shift", "offset"):
                    v = vals.get(var)
                    if v is None:
                        continue
                    try:
                        # wrapper: name=value
                        self.galil.write_var(var, v)
                    except Exception as e:
                        self.software_error_log.exception(f"Failed sending {var}={v}")
                        self.log_to_terminal(f"Error sending {var}={v}: {e}", level="error")
            else:
                self.connection_sts = False
                self.btn_connect.show()
                self.btn_disconnect.hide()
        except Exception:
            self.software_error_log.exception("Error Connecting")
            self.log_to_terminal("Error Connecting (see software log for details)", level="error")

    def disconnect_device(self):
        try:
            self.disconnected, self.galil_object = self.galil.dmc_disconnect()
        except Exception:
            self.disconnected = False
            self.software_error_log.exception("Disconnect failed")

        if self.disconnected:
            self.connection_sts = False
            self.btn_connect.show()
            self.btn_disconnect.hide()
            self.log_to_terminal("Disconnected from Controller")

    def exit_program(self):
        try:
            self.disconnect_device()
            if self.connection_sts:
                return
            self.log_to_terminal("Program Exiting.")
            QTimer.singleShot(2000, QApplication.instance().quit)
        except Exception as e:
            self.software_error_log.exception("Exit Program Exception")
            self.log_to_terminal(f"Exit Program Exception: {e}", level="error")

    # ---------- Generic write handler (UI → device) ----------
    def _on_lineedit_commit(self, entry: dict):
        w: QLineEdit = entry["widget"]
        write_var = entry["write_var"]
        coerce = entry["coerce"]

        text = w.text().strip()
        if text == "":
            self.log_to_terminal(f"{write_var} left blank; not sent")
            return

        try:
            val = coerce(text)
        except Exception as e:
            self.log_to_terminal(f"Invalid input for {write_var}: {text} ({e})", level="error")
            return

        if self.connection_sts and self.galil_object:
            try:
                self.galil.write_var(write_var, val)
                echoed = self.galil.read_expr(write_var)  # MG var
                self.log_to_terminal(f"{write_var} changed -> {val} (read back {echoed})")
            except Exception:
                self.software_error_log.exception(f"{write_var} write failed")
                self.log_to_terminal(f"{write_var} write failed (see software log)", level="error")
        else:
            self.log_to_terminal(f"{write_var} changed (not connected) -> {val}")

    # ---------- UI <-> dict helpers ----------
    def read_galil_inputs_from_ui(self) -> dict:
        """Return dict of {'back': value/None, ...} using BINDINGS for lineedits."""
        values = {}
        for e in self._bindings:
            if e["kind"] != "lineedit":
                continue
            w: QLineEdit = e["widget"]
            ok, value, _ = self.parse_number(w.text())
            values[e["write_var"]] = value if ok else None
        return values

    def write_galil_values_to_ui(self, galil_values: dict) -> None:
        """Write values back into mapped lineedits."""
        for e in self._bindings:
            if e["kind"] != "lineedit":
                continue
            w: QLineEdit = e["widget"]
            var = e["write_var"]
            if var in galil_values:
                v = galil_values[var]
                w.setText("" if v is None else e["fmt"](v))

    # ---------- Polling (device → UI) ----------
    def poll_bindings(self):
        if not (self.connection_sts and self.galil_object):
            return

        for e in self._bindings:
            expr = e.get("read_expr")
            if not expr:
                continue

            try:
                raw = self.galil.read_expr(expr)   # wrapper: GCommand(f"MG {expr}")
                val = e["coerce"](raw)

                kind = e["kind"]
                if kind == "label":
                    lbl: QLabel = e["widget"]
                    lbl.setText(e["fmt"](val))

                elif kind == "lineedit":
                    # if you want to reflect device changes into the field, uncomment:
                    # w: QLineEdit = e["widget"]
                    # w.setText(e["fmt"](val))
                    pass

                elif kind == "bool_pair":
                    grn, red = e["widget"]
                    is_on = bool(val)
                    grn.setVisible(is_on)
                    red.setVisible(not is_on)

            except Exception:
                # Don't spam; log stack once per problematic expr
                self.software_error_log.exception(f"Poll failed for {expr}")

    # ---------- Terminal + periodic update ----------
    def update_terminal_window(self):
        if self.term_msg is not None and self.last_term_msg != self.term_msg:
            try:
                self.terminal_window.appendPlainText(str(self.term_msg))
                self.last_term_msg = self.term_msg
            except Exception:
                self.software_error_log.exception("Terminal window update failed")

    def update_all_widgets(self):
        self.update_terminal_window()
        self.poll_bindings()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    UIWindow = UI()
    app.exec()
