from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTableView, QPushButton, QTextEdit,
    QSplitter, QMessageBox
)
from collections import Counter
from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from gui.widgets.card import *
from utils.db_crud import *
from gui.widgets.log_table import AlertTableModel
from utils.dialog_win import *

class Notifications(QWidget):
    refresh_database = Signal()
    def __init__(self, alert_logs):
        super().__init__()
        self.setAutoFillBackground(True)
        self.alert_logs = alert_logs
        self.filtered_alerts = alert_logs

        self.setWindowTitle("Notifications")
        self.main_layout = QVBoxLayout(self) 

        self.summary_ui()
        self.table_and_detail_ui()
        self.css_styles()
        
    # summary
    def summary_ui(self):
        container = QHBoxLayout()

        stats = Counter(x for l in (self.alert_logs or []) for x in (l["level"], l["status"]))
        self.info_alert_count = str(stats.get("info", 0))
        self.warn_alert_count = str(stats.get("warn", 0))
        self.error_alert_count = str(stats.get("error", 0))
        self.critical_alert_count = str(stats.get("critical", 0))
        self.total_alert_count = str(len(self.alert_logs or []))
        self.read_alert_count = str(stats.get("read", 0))
        self.unread_alert_count = str(stats.get("unread", 0))

        # Log Level Card
        log_level_container = QVBoxLayout()

        self.info_card = SmallSummaryCard("Info", self.info_alert_count, "#2563eb")
        self.warn_card = SmallSummaryCard("Warn", self.warn_alert_count, "#f59e0b")
        self.error_card = SmallSummaryCard("Error", self.error_alert_count, "#F84E4E")
        self.critical_card = SmallSummaryCard("Critical", self.critical_alert_count, "#dc2626")
        log_level_container.addWidget(self.info_card)
        log_level_container.addWidget(self.warn_card)
        log_level_container.addWidget(self.error_card)
        log_level_container.addWidget(self.critical_card)

        # Button
        btn_container = QVBoxLayout()
        btn_container.setContentsMargins(30, 0, 0, 0)
        self.read_alert_btn = QPushButton("Mark as read")
        self.read_alert_btn.setObjectName("readAlertBtn")
        self.read_alert_btn.clicked.connect(self.read_alert_btn_clicked)
        btn_container.addWidget(self.read_alert_btn)

        self.read_all_alert_btn = QPushButton("Read all")
        self.read_all_alert_btn.setObjectName("readAllAlertBtn")
        self.read_all_alert_btn.clicked.connect(self.read_all_btn_clicked)
        btn_container.addWidget(self.read_all_alert_btn)

        self.delete_alert_btn = QPushButton("Delete alert")
        self.delete_alert_btn.setObjectName("deleteAlertBtn")
        self.delete_alert_btn.clicked.connect(self.delete_alert_btn_clicked)
        btn_container.addWidget(self.delete_alert_btn)

        self.delete_all_alerts_btn = QPushButton("Delete all")
        self.delete_all_alerts_btn.setObjectName("deleteAllAlertBtn")
        self.delete_all_alerts_btn.clicked.connect(self.delete_all_alert_btn_clicked)
        btn_container.addWidget(self.delete_all_alerts_btn)

        # summary card
        self.total_card = SummaryCard("Total alerts", self.total_alert_count, "#0ea5a0")
        self.read_card = SummaryCard("Read", self.read_alert_count, "#0ea5a0")
        self.unread_card = SummaryCard("Unread", self.unread_alert_count, "#0ea5a0")
        container.addWidget(self.total_card)
        container.addWidget(self.read_card)
        container.addWidget(self.unread_card)
        container.addLayout(log_level_container)
        container.addLayout(btn_container)

        container.addStretch(1)
        self.main_layout.addLayout(container)

    # table & pane
    def filter_alerts(self, text):
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterFixedString(text)

    def table_and_detail_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search alerts...")
        self.search_box.textChanged.connect(self.filter_alerts)

        self.table = QTableView()
        self.model = AlertTableModel(self.filtered_alerts)
        
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        
        self.table.setModel(self.proxy)
        self.table.clicked.connect(self.inspect_alerts)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)

        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        splitter.setSizes([700, 300])

        self.layout().addWidget(splitter)
        self.layout().addWidget(self.search_box)

    def inspect_alerts(self, selected_alerts):
        source_index = self.proxy.mapToSource(selected_alerts)
        alert = self.filtered_alerts[source_index.row()]
        alert_dict = dict(alert)
        formatted = "\n\n".join(f">> {k}: {v if v is not None else ''}" for k, v in alert_dict.items())
        self.detail.setText(formatted)
        self.alert_id = alert_dict["id"]

    def read_alert_btn_clicked(self):
        if self.alert_logs:
            id = self.alert_id
            result = mark_alert_as_read(id)
            if result:
                self.refresh_database.emit()
                QMessageBox.information(self, "Successful", "Alert marked as read")
            return
        QMessageBox.warning(self, "Error", "No alert selected")

    def read_all_btn_clicked(self):
        if self.alert_logs:
            result = mark_all_alert()
            if result:
                self.refresh_database.emit()
                QMessageBox.information(self, "Successful", "All alert marked as read")
            return
        QMessageBox.warning(self, "Error", "No alert detected")

    def delete_alert_btn_clicked(self):
        if self.alert_logs:
            id = self.alert_id
            title = "Delete Alert"
            message = f"Are you sure you want to delete alert {id}"
            dialog = ConfirmDialog(title, message, self)
            if dialog.exec() == QDialog.Accepted:
                result = delete_alert(id)
                if result:
                    self.refresh_database.emit()
                    QMessageBox.information(self, "Successful", f"Alert {id} deleted")
            return
        QMessageBox.warning(self, "Error", "No alert selected")
        
    def delete_all_alert_btn_clicked(self):
        if self.alert_logs:
            title = "Delete All Alert"
            message = f"Are you sure you want to delete all alerts"
            dialog = ConfirmDialog(title, message, self)
            if dialog.exec() == QDialog.Accepted:
                result = delete_all_alerts()
                if result:
                    self.refresh_database.emit()
                    QMessageBox.information(self, "Successful", f"All alerts deleted")
            return
        QMessageBox.warning(self, "Error", "No alert detected")
    
    def update_data(self, new_alerts):
        self.alert_logs = new_alerts
        self.filtered_alerts = new_alerts
        self.model.refresh_alerts_ui(self.filtered_alerts)
        self.refresh_ui(self.alert_logs)
    
    def refresh_ui(self, new_alert_logs=None):
        self.new_alert_logs = new_alert_logs if new_alert_logs is not None else []
        stats = Counter(x for l in (self.new_alert_logs or []) for x in (l["level"], l["status"]))
        self.info_card.update_smallsummarycard_value(stats.get("info", 0))
        self.warn_card.update_smallsummarycard_value(stats.get("warn", 0))
        self.error_card.update_smallsummarycard_value(stats.get("info", 0))
        self.critical_card.update_smallsummarycard_value(stats.get("info", 0))
        self.total_card.update_summarycard_value(len(self.new_alert_logs or []))
        self.read_card.update_summarycard_value(stats.get("read", 0))
        self.unread_card.update_summarycard_value(stats.get("unread", 0))
    
    # style
    def css_styles(self):
        self.setStyleSheet("""
        QWidget {
            color: #cbd5e1;
            font-size: 13px;
        }
        QTableView {
            gridline-color: #123047;
            background-color: #061323;
        }
        QHeaderView::section {
            background-color: #081428;
            padding: 4px;
            border: 1px solid #123047;
        }
        QPushButton {
            color: white;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
            min-width: 100px;
            max-width: 100px;
        }
        QPushButton#readAlertBtn {
            background-color: #a5ec72;
            border: 1px solid #94d665; 
        }
        QPushButton#readAllAlertBtn {
            background-color: #a3bd52;
            border: 1px solid #94d665; 
        }
        QPushButton#deleteAlertBtn {
            background-color: #FA0000;
            border: 1px solid #CC0808; 
        }
        QPushButton#deleteAllAlertBtn {
            background-color: #FF0828;
            border: 1px solid #CC0808; 
        }
        """)
