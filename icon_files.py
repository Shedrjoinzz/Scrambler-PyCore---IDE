from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QIcon, QStandardItemModel
import os
import resources


class CustomFileSystemModel(QFileSystemModel):
    def data(self, index, role):        

        if role == Qt.DecorationRole:
            file_path = self.filePath(index)
            if os.path.isdir(file_path):
                # Значок для папок
                return QIcon(":img/folder-code.png")
            else:
                # Определение значка по расширению файла
                _, extension = os.path.splitext(file_path)
                extension = extension.lower()
                if extension == ".py":
                    return QIcon(":img/python.png")
                                
                elif extension in ".txt":
                    return QIcon(":img/align-left.png")                

                elif extension == ".pyc":
                    return QIcon(":img/pyc.ico")

                elif extension == ".ico":
                    return QIcon(":img/star.png")

                elif extension == ".json":
                    return QIcon(":img/json.png")

                elif extension == ".js":
                    return QIcon(":img/js.png")

                elif extension in [".jpg", ".jpeg", ".png", ".gif"]:
                    return QIcon(":img/image-gallery.png")

                elif extension == ".md":
                    return QIcon(":img/markdown.png")

                elif extension == ".css":
                    return QIcon(":img/tag.png")
                
                elif extension == ".html":
                    return QIcon(":img/html-code.png")
                
                elif extension == ".cpp":
                    return QIcon(":img/cpp.png")
                
                elif extension == ".c":
                    return QIcon(":img/c.png")
                
                elif extension == ".go":
                    return QIcon(":img/golang.png")
                
                else:
                    # Значок по умолчанию для остальных типов файлов
                    return QIcon(":img/unknown.png")
                

        # Используем стандартное поведение для других ролей
        return super().data(index, role)