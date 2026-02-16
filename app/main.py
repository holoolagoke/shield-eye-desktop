#! usr/bin/env python3

import os
import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPalette, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget,
    QStackedWidget, QMessageBox
)
from gui.dashboard_page import Dashboard
from gui.about_page import About
from gui.notifications_page import Notifications
from gui.preference_page import Preferences
from utils.db_crud import *

basedir = os.path.dirname(__file__)
icon_path = os.path.join(basedir, "assets", "icons", "logo.png")
bg_img_path = os.path.join(basedir, "assets", "themes", "background.png")

def load_event_logs():
    data = fetch_log()
    return data

def load_alert_logs():
    data = fetch_alert_log()
    return data

def load_prefs_settings():
    data = fetch_prefs_settings()
    return data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_db = init_db()
        self.init_db
        

        self.setStyleSheet("""
            QStackedWidget, .Dashboard, .Notifications, .Preferences, .About {
                background-color: #07102a; /* Use your specific theme color here */
            }
            QPushButton {
                background-color: #2b5797;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                min-width: 200px;
                max-width: 200px;
            }
            QPushButton:hover {
                background-color: #3e79db;
            }
            QPushButton:pressed {
                background-color: #1e3a63;
            }
        """)

        container = QWidget()
        layout = QVBoxLayout()
        btn_container = QHBoxLayout()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.currentChanged.connect(self.on_page_changed)

        self.event_logs = load_event_logs()
        self.dashboard = Dashboard(self.event_logs)
        self.alert_logs = load_alert_logs()
        self.notifications = Notifications(self.alert_logs)
        self.prefs_sets = load_prefs_settings()
        self.preferences = Preferences(self.prefs_sets)
        self.about = About()

        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.notifications)
        self.stacked_widget.addWidget(self.preferences)
        self.stacked_widget.addWidget(self.about)

        dashboard_button = QPushButton("Dashboard")
        dashboard_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard))
        btn_container.addWidget(dashboard_button)

        alert_button = QPushButton("Alerts")
        alert_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.notifications))
        btn_container.addWidget(alert_button)

        prefs_button = QPushButton("Prefereces")
        prefs_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.preferences))
        btn_container.addWidget(prefs_button)
        
        about_button = QPushButton("About")
        about_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.about))
        btn_container.addWidget(about_button)

        layout.addLayout(btn_container)
        layout.addWidget(self.stacked_widget)

        container.setLayout(layout)
        self.setCentralWidget(container)
        self.set_background()
        self.dashboard.refresh_database.connect(self.refresh_all_data)
        self.notifications.refresh_database.connect(self.refresh_all_data)
        self.preferences.refresh_database.connect(self.refresh_all_data)

        QTimer.singleShot(100, self.delayed_sql_check)

    def delayed_sql_check(self):
        result = verify_sql_version()
        if isinstance(result, str):
            QMessageBox.critical(self, "Error", result)

    def refresh_all_data(self):
        try:
            self.event_logs = load_event_logs()
            self.alert_logs = load_alert_logs()
            self.prefs_sets = load_prefs_settings()

            self.dashboard.update_data(self.event_logs)
            self.notifications.update_data(self.alert_logs)
            self.preferences.update_prefs(self.prefs_sets)
        except Exception as e:
            log_activity("error", type(e).__name__, source_dir, f" File: {str(e)}", traceback.format_exc(), "refresh_all_data func")
            QMessageBox.critical(self, "Error", f"Erorr: {str(e)}")
            return
        
    #! override by QStackedWidget css
    def set_background(self):
        img = QPixmap(bg_img_path)
        scaled_img = img.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(scaled_img))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def on_page_changed(self, index):
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            widget.setVisible(i == index)
        self.stacked_widget.update()


app = QApplication(sys.argv)
app.setFont(QFont("Segoe UI", 10))
win = MainWindow()
win.setWindowIcon(QIcon(icon_path))
win.setWindowTitle("ShieldEye (log analyzer) Desktop")
win.resize(1280, 720)
win.showMaximized()
win.show()
sys.exit(app.exec())                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
