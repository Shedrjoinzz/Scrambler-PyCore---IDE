from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class ConfirmDeleteDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #282C34;
                color: #ABB2BF;
                font-size: 14px;
                border: 1px solid #61AFEF;
            }
            QLabel {
                font-size: 12px;
                color: #61AFEF;
            }
            QPushButton {
                background-color: #61AFEF;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #528CC8;
            }
            QPushButton:pressed {
                background-color: #3B6DA0;
            }
        """)

        self.setFixedSize(400, 100)

        layout = QVBoxLayout(self)
        self.message_label = QLabel(message, self)
        layout.addWidget(self.message_label)

        button_layout = QVBoxLayout()

        self.yes_button = QPushButton("Да", self)
        self.yes_button.clicked.connect(self.accept)
        button_layout.addWidget(self.yes_button)

        self.no_button = QPushButton("Нет", self)
        self.no_button.clicked.connect(self.reject)
        button_layout.addWidget(self.no_button)

        layout.addLayout(button_layout)