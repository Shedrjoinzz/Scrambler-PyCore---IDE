from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from custom_messages import StyledMessageBox
from style import dialog_flow_style
import resources

def set_icon_on_tab_windows(extension):
    # иконки для файлов
    dict_list_type_files = {
        "py": QIcon(":img/python.png"),
        "txt": QIcon(":img/align-left.png"),
        "md": QIcon(":img/markdown.png"),
        "css": QIcon(":img/tag.png"),
        "html": QIcon(":img/html-code.png"),
        "cpp": QIcon(":img/cpp.png"),
        "go": QIcon(":img/golang.png"),
        "json": QIcon(":img/json.png"),
        "js": QIcon(":img/js.png"),
    }

    try:
        return dict_list_type_files[extension]
    except KeyError:
        # для остальных типов файлов
        return QIcon(":img/unknown.png")


def create_window_message_box(status, title, label):
    # создание кастомного окна сообщений 
    msg_box = StyledMessageBox()
    status_message_dict = {
        "info": QMessageBox.Information,
        "critic": QMessageBox.Critical,
        "war": QMessageBox.Warning,
    }

    msg_box.setIcon(status_message_dict[status])
    msg_box.setWindowTitle(title)
    msg_box.setText(label)
    msg_box.exec_()
    
def create_window_dialog_box(title, label, but_name1, but_name2):
    input_dialog = QInputDialog()
    input_dialog.setWindowFlags(Qt.FramelessWindowHint)
    input_dialog.resize(600, 400)
    input_dialog.setStyleSheet(dialog_flow_style)
    input_dialog.setWindowTitle(title)
    input_dialog.setLabelText(label)
    input_dialog.setOkButtonText(but_name1)
    input_dialog.setCancelButtonText(but_name2)
    
    line_edit = input_dialog.findChild(QLineEdit)
    if line_edit:
        line_edit.setMaxLength(60)  # Устанавливаем максимальное количество символов
        
    # Показываем диалог и получаем ввод
    if input_dialog.exec_() == QInputDialog.Accepted:
        folder_name = input_dialog.textValue()
        return folder_name