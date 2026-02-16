import traceback
import json
from datetime import datetime
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel,
    QMessageBox, QCheckBox
)
from utils.db_crud import *
from utils.check_update import *

source_dir = "Preferences page"

class Preferences(QWidget):
    refresh_database = Signal()
    def __init__(self, prefs_sets):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setWindowTitle("Preferences")
        self.main_layout = QVBoxLayout(self)
        self.update_prefs(prefs_sets)
        self.page_ui()

    def page_ui(self):
        container = QVBoxLayout()
        alert_prefs_container = QVBoxLayout()
        flex_container = QHBoxLayout()

        self.alert_prefs_label = QLabel("Create alert for: ")
        self.alert_prefs_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.warn_check = QCheckBox("Warn event")
        self.error_check = QCheckBox("Error event")
        self.critical_check = QCheckBox("Critical event")
        self.save_prefs_btn = QPushButton("Save")
        self.save_prefs_btn.clicked.connect(self.prefs_btn_clicked)

        self.status_label = QLabel("Status: Ready to Import")
        self.status_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.btn_upload = QPushButton("Upload Logs")
        self.btn_upload.clicked.connect(self.process_json)

        alert_prefs_container.addWidget(self.alert_prefs_label)
        alert_prefs_container.addWidget(self.error_check)
        alert_prefs_container.addWidget(self.critical_check)
        alert_prefs_container.addWidget(self.warn_check)
        alert_prefs_container.addWidget(self.save_prefs_btn)
        alert_prefs_container.addSpacing(20)

        flex_container.addWidget(self.btn_upload)
        flex_container.addWidget(self.status_label)

        container.addLayout(alert_prefs_container)
        container.addLayout(flex_container)

        container.addStretch(1)
        self.main_layout.addLayout(container)
    
    def prefs_btn_clicked(self):
        id = str(uuid.uuid4())
        timestamp = datetime.now()
        warn_e_check = "warn" if self.warn_check.isChecked() else ""
        error_e_check = "error" if self.error_check.isChecked() else ""
        critical_e_check = "critical" if self.critical_check.isChecked() else ""

        result = fetch_prefs_settings()
        
        if result:
            result = update_prefs_settings(warn_e_check, error_e_check, critical_e_check)
        else:
            result = save_prefs_settings(id, timestamp, warn_e_check, error_e_check, critical_e_check)
        
        if result:
            QMessageBox.information(self, "Success", "User preference setting updated")
        
    def process_json(self):
        self.status_label.setText("Uploading...")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Log File", "", "JSON Files (*.json)")
        if not file_path: return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            logs = data if isinstance(data, list) else [data]
            all_records = []
            
            for entry in logs:
                try:
                    log_data = (
                        entry["_id"],
                        entry["timestamp"]["$date"],
                        entry["level"],
                        entry["category"],
                        entry["event_type"],
                        entry["source"],
                        entry["message"],
                        entry["stack"],
                        json.dumps(entry["tags"]),
                        entry["app"]["name"],
                        entry["app"]["version"],
                        entry["user"]["id"],
                        entry["user"]["ip"],
                        entry["user"]["method"],
                        entry["user"]["endpoint"],
                        entry["user"]["status"],
                        entry["user"]["user_agent"]
                    )
                    all_records.append(log_data)
                except KeyError as e:
                    log_activity("error", type(e).__name__, source_dir, f"Rejected: Missing key {str(e)}", traceback.format_exc(), "process_json loop")
                    QMessageBox.warning(self, "Warn", f"Rejected: Missing key {str(e)}.")
                    self.status_label.setText(f"Rejected: Missing key {str(e)}")
                    return
            if all_records:
                result = append_log(all_records)
                if result:
                    QMessageBox.information(self, "Success", f"Appended {len(all_records)} records.")
                    self.status_label.setText(f"Success: Appended {len(all_records)} records.")
                    self.refresh_database.emit()
                    if self.prefs_sets:
                        self.scan_for_alert(data)
                    return
        except Exception as e:
            log_activity("error", type(e).__name__, source_dir, f"Invalid File: {str(e)}", traceback.format_exc(), "process_json func")
            QMessageBox.critical(self, "Error", f"Invalid File: {str(e)}")
            return

    def scan_for_alert(self, data):
        if self.prefs_sets:
            check_list = {str(k).lower().strip() for k in self.prefs_sets if str(k).strip()}
        else:
            check_list = set()

        try:
            alerts = data if isinstance(data, list) else [data]
            all_alert = []
            
            for entry in alerts:
                level = entry.get("level")
                if not level:
                    continue
                    
                if level.lower() in check_list:
                    try:
                        alert_data = (
                            str(uuid.uuid4()),
                            datetime.now(),
                            entry["level"],
                            entry["category"],
                            entry["event_type"],
                            entry["message"],
                            entry["_id"],
                            "unread"
                        )
                        all_alert.append(alert_data)
                    except KeyError as e:
                        log_activity("error", type(e).__name__, source_dir, f"Rejected: Missing key {str(e)}", traceback.format_exc(), "scan_for_alert loop")
                        QMessageBox.warning(self, "Warn", f"Rejected: Missing key {str(e)}.")
                        self.status_label.setText(f"Rejected: Missing key {str(e)}")
                        return
            if all_alert:
                result = create_alert(all_alert)
                if result:
                    QMessageBox.information(self, "Success", f"{len(all_alert)} alert(s) created.")
                    self.status_label.setText(f"Success: {len(all_alert)} alert(s) created.")
                    self.refresh_database.emit()
                return
        except Exception as e:
            log_activity("error", type(e).__name__, source_dir, f"Invalid Format: {str(e)}", traceback.format_exc(), "scan_for_alert func")
            QMessageBox.critical(self, "Error", f"Invalid Format: {str(e)}")
            return
    
    def update_prefs(self, new_prefs_sets):
        self.prefs_sets = new_prefs_sets