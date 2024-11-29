from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

class StyledMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QMessageBox {
                background-color: #282C34;
                color: #ABB2BF;
                font-size: 14px;
                border: 1px solid #61AFEF;
            }
            
            QLabel {
                color: #61AFEF;
                background-color: none;
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
