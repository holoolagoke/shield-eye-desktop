from PySide6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLabel, QHBoxLayout

class ConfirmDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Action Confirmation")
        self.setMinimumWidth(400)
        container = QVBoxLayout(self)

        container.addWidget(QLabel(title))

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        container.addWidget(msg_label)

        btn_layout = QHBoxLayout()
        
        confirm_btn = QPushButton("Yes")
        confirm_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("No")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        container.addLayout(btn_layout)