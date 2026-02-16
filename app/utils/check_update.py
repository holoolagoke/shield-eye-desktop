import platform
import requests
import traceback
import hashlib
from PySide6.QtCore import Qt, QRunnable, QObject, Signal, QUrl
from PySide6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QDesktopServices
import os
from utils.db_crud import log_activity

source_dir = "update checker"

class UpdateSignals(QObject):
    finished = Signal(dict)
    error = Signal(str)

class UpdateChecker(QRunnable):
    def __init__(self, update_url):
        super().__init__()
        self.update_url = update_url
        self.signals = UpdateSignals()

    def run(self):
        try:
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            current_os = platform.system().lower()
            platform_data = data.get("platforms", {}).get(current_os, {})
            update_info = {
                "version": data.get("version"),
                "release_date": data.get("release_date"),
                "repo_url": data.get("repo_url"),
                "download_url": platform_data.get("download_url"),
                "hash": platform_data.get("hash")
            }
            self.signals.finished.emit(update_info)
        except Exception as e:
            log_activity("error", type(e).__name__, source_dir, str(e), traceback.format_exc(), "UpdateChecker run")
            self.signals.error.emit(str(e))

class UpdateDetailDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Available")
        self.setMinimumWidth(400)
        container = QVBoxLayout(self)

        container.addWidget(QLabel(f"<b>New Version:</b> {data['version']}"))

        hash_label = QLabel(f"<b>SHA-256 Hash:</b><br/><code style='color:#f0f0f0;'>{data['hash']}</code>")
        hash_label.setWordWrap(True)
        hash_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        container.addWidget(hash_label)

        btn_container = QHBoxLayout()
        
        repo_btn = QPushButton("Visit Repository")
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(data["repo_url"])))
        
        download_btn = QPushButton("Download from App")
        download_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Later")
        cancel_btn.clicked.connect(self.reject)

        btn_container.addWidget(repo_btn)
        btn_container.addWidget(download_btn)
        btn_container.addWidget(cancel_btn)
        container.addLayout(btn_container)

class DownloadSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

class UpdateDownloader(QRunnable):
    def __init__(self, download_url, new_update_version_hash):
        super().__init__()
        self.download_url = download_url
        self.new_update_version_hash = new_update_version_hash
        self.signals = DownloadSignals()

    def run(self):
        try:
            temp_dir = os.getenv("TEMP") if os.name == "nt" else "/tmp"
            local_filename = os.path.join(temp_dir, self.download_url.split("/")[-1])
            
            response = requests.get(self.download_url, stream=True, timeout=30)
            total_size_header = response.headers.get("content-length")
            if total_size_header is None:
                total_size = 0
                self.signals.progress.emit(-1)
            else:
                total_size = int(total_size_header)
            
            downloaded = 0
            
            with open(local_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = min(99, int(100 * downloaded / total_size))
                            self.signals.progress.emit(percent)
                        else:
                            pass
            self.signals.progress.emit(100)
            
            # Security Check: Verify Hash
            actual_hash = self.hash_file(local_filename)
            if self.new_update_version_hash and actual_hash != self.new_update_version_hash:
                raise ValueError("Hash mismatch! File might be corrupted or tampered with!")

            self.signals.finished.emit(local_filename)
        except Exception as e:
            log_activity("error", type(e).__name__, source_dir, str(e), traceback.format_exc(), "UpdateDownloader run")
            self.signals.error.emit(str(e))

    def hash_file(self, file_path):
        with open(file_path, "rb") as f:
            digest = hashlib.file_digest(f, "sha256")
        return digest.hexdigest()

