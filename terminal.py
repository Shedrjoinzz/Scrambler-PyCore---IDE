from PyQt5.QtWidgets import QPlainTextEdit
from style import css_style


class Terminal(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setObjectName("terminal")
        self.setReadOnly(True)
        self.setStyleSheet(css_style)