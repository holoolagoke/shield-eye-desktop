from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from gui.widgets.card import *

class LogTableModel(QAbstractTableModel):
    HEADERS = ["Level", "Category", "Source", "Event Type", "Log ID", "Message", "Stack", "Timestamp", "User ID", "IP", "Method", "Endpoint", "Status", "User Agent", "Tags", "App", "Version"]

    def __init__(self, event_logs=None):
        super().__init__()
        self.event_logs = event_logs if event_logs is not None else []

    def rowCount(self, parent=QModelIndex()):
        return len(self.event_logs)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        log = self.event_logs[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            return str([
                log["level"],
                log["category"],
                log["source"],
                log["event_type"],
                log["id"],
                log["message"],
                log["stack"],
                log["timestamp"],
                log["user_id"],
                log["user_ip"],
                log["user_method"],
                log["user_endpoint"],
                log["user_status"],
                log["user_agent"],
                log["tags"],
                log["app_name"],
                log["app_version"]
            ][col])
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
    
    def refresh_event_log_ui(self, new_event_logs=None):
        self.beginResetModel()
        self.event_logs = new_event_logs if new_event_logs is not None else []
        self.endResetModel()

class AlertTableModel(QAbstractTableModel):
    HEADERS = ["Alert_Id", "Level", "Category", "Event Type", "Log ID", "Message", "Timestamp", "Status"]

    def __init__(self, alert_logs=None):
        super().__init__()
        self.alert_logs = alert_logs if alert_logs is not None else []

    def rowCount(self, parent=QModelIndex()):
        return len(self.alert_logs)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        log = self.alert_logs[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return str([
                log["id"],
                log["level"],
                log["category"],
                log["event_type"],
                log["log_id"],
                log["message"],
                log["timestamp"],
                log["status"]
            ][col])
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]

    def refresh_alerts_ui(self, new_alert_logs=None):
        self.beginResetModel()
        self.alert_logs = new_alert_logs if new_alert_logs is not None else []
        self.endResetModel()