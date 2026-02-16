import os
from PySide6.QtCore import QThreadPool, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QProgressDialog
)
from gui.widgets.card import DetailCard
from utils.db_crud import *
from utils.check_update import *

source_dir = "about page"
APP_VERSION = "1.0.0"
GITHUB_UPDATE_URL = "https://raw.githubusercontent.com/holoolagoke/shield-eye-desktop/refs/heads/master/version.json"

class About(QWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setWindowTitle("About")
        self.main_layout = QVBoxLayout(self) 
        self.page_ui()

    def page_ui(self):
        container = QVBoxLayout()
        group_container = QHBoxLayout()

        app_name_label = "App Name: ShieldEye (log analyzer) Desktop"
        app_version_label =f"Version: {APP_VERSION}"
        developer_label = "Developer: Holo Olagoke"
        github_url_label = "Github: https://github.com/holoolagoke"
        website_label = "Website: https://www.holoolagoke.com"

        container.addWidget(DetailCard(app_name_label, app_version_label, developer_label, github_url_label, website_label, "#0ea5a0"))

        self.check_update_button = QPushButton("Check update")
        self.check_update_button.clicked.connect(self.start_update_check)
        self.threadpool = QThreadPool.globalInstance()

        self.live_webpage_button = QPushButton("Webpage version")
        self.live_webpage_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.shieldeye.holoolagoke.com")))

        group_container.addWidget(self.check_update_button)
        group_container.addWidget(self.live_webpage_button)
        group_container.addSpacing(20)
        container.addLayout(group_container)

        container.addStretch(1)
        self.main_layout.addLayout(container)

    def start_update_check(self):
        self.check_update_button.setEnabled(False)
        self.check_update_button.setText("Checking...")
        
        checker = UpdateChecker(GITHUB_UPDATE_URL)
        checker.signals.finished.connect(self.on_update_found)
        checker.signals.error.connect(self.on_update_error)
        
        self.threadpool.start(checker)

    @Slot(dict)
    def on_update_found(self, data):
        self.check_update_button.setEnabled(True)
        self.check_update_button.setText("Check update")
        if data["version"] <= APP_VERSION:
            QMessageBox.information(None, "Updated", "ShieldEye app is updated")
            return
        dialog = UpdateDetailDialog(data, self)
        if dialog.exec() == QDialog.Accepted:
            self.start_file_download(data)

    @Slot(str)
    def on_update_error(self, message):
        self.check_update_button.setEnabled(True)
        self.check_update_button.setText("Check update")
        QMessageBox.warning(None, "Update Error", f"Failed: {message}")

    def start_file_download(self, data):
        self.progress_bar = QProgressDialog("Downloading update...", "Cancel", 0, 100, self)
        self.progress_bar.setAutoClose(True)
        self.progress_bar.show()

        uploader = UpdateDownloader(data["download_url"], data["hash"])
        uploader.signals.progress.connect(self.progress_bar.setValue)
        uploader.signals.error.connect(lambda err: QMessageBox.critical(None, "Error", str(err)))
        uploader.signals.finished.connect(self.execute_installer)
        
        self.threadpool.start(uploader)

    def execute_installer(self, file_path):
        if self.progress_bar:
            self.progress_bar.setValue(100)
            self.progress_bar.close()
        # Windows
        if os.name == "nt":
            QMessageBox.information(None, "New version downloaded", f"Install the latest downloaded version at {file_path}")
        # Linux / macOS
        else:
            os.chmod(file_path, 0o755)
            QMessageBox.information(None, "New version downloaded", f"Run: 'sudo apt install {file_path}")

