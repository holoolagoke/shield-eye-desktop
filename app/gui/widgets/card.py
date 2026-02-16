from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

class SummaryCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 2px;
            }}
        """)

        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        self.value_label = QLabel(str(value))

        title_label.setStyleSheet("color: white; font-size: 14px;")
        self.value_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        self.setFixedWidth(200)
        self.setLayout(layout)

    def update_summarycard_value(self, new_value):
        self.value_label.setText(str(new_value))

class DetailCard(QFrame):
    def __init__(self, line1, line2, line3, line4, line5, color):
        super().__init__()
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 2px;
                color: white;
                font-size: 14px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        line1_label = QLabel(line1)
        line2_label = QLabel(line2)
        line3_label = QLabel(line3)
        line4_label = QLabel(line4)
        line5_label = QLabel(line5)

        line1_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        line2_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        line3_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        line4_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        line5_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        layout.addWidget(line1_label)
        layout.addWidget(line2_label)
        layout.addWidget(line3_label)
        layout.addWidget(line4_label)
        layout.addWidget(line5_label)
        self.setFixedWidth(700)
        self.setLayout(layout)

class SmallSummaryCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setObjectName("SmallSummaryCard")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 2px;
            }}
        """)

        flexLayout = QHBoxLayout(self)
        title_label = QLabel(title)
        self.value_label = QLabel(str(value))
        title_label.setStyleSheet("color: white; font-size: 10px;")
        self.value_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        flexLayout.addWidget(title_label)
        flexLayout.addWidget(self.value_label)
        self.setFixedHeight(40)
        self.setFixedWidth(200)
        self.setLayout(flexLayout)
    
    def update_smallsummarycard_value(self, new_value):
        self.value_label.setText(str(new_value))