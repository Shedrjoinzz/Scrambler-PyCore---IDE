from PyQt5.QtWidgets import QTreeView,  QMenu, QAction, QInputDialog, QMessageBox, QApplication, QPlainTextEdit, QLabel, QLineEdit, QPushButton, QDialog, QFileSystemModel
from PyQt5.QtCore import QDir, Qt, pyqtSignal, QThread, QMimeData, QSize, QFile, QFileInfo, QTimer
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QDrag

import os
import shutil
from icon_files import CustomFileSystemModel
from custom_dialog import ConfirmDeleteDialog
import chardet
from edition import PyNote
from logicai import set_icon_on_tab_windows, create_window_message_box, create_window_dialog_box

class FileLoaderThread(QThread):
    file_loaded = pyqtSignal((str, str))  # Сигнал для передачи текста обратно в основной поток
    error_occurred = pyqtSignal(str)  # Сигнал для передачи ошибки

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, "rb") as file:
                raw_data = file.read()

                detected_encoding = chardet.detect(raw_data)
                encoding = detected_encoding.get("encoding", "utf-8") or "utf-8"
                content = raw_data.decode(encoding)

                self.file_loaded.emit(content, self.file_path)  # Передаем текст через сигнал
        except Exception as e:
            self.error_occurred.emit(str(e))  # Передаем ошибку через сигнал
        

class FileExplorer(QTreeView):
    path_files = pyqtSignal((int, str))
    ctrl_click_signal = pyqtSignal(str)
    signal_column_line = pyqtSignal(str)
    index_brak_read_file = pyqtSignal(int)
    file_deleted = pyqtSignal(str)  # Сигнал при удалении файла
    file_renamed = pyqtSignal(str, str)  # Сигнал при переименовании файла (старый путь, новый путь)


    def __init__(self, editor, progress_bar, tab_widget, open_files):
        super().__init__()
        # Настройка
        self.setTabKeyNavigation(False)
        self.setAnimated(True)  # Включаем анимацию
        self.setAcceptDrops(True)  # Включаем прием перетаскиваемых данных
        self.setDragEnabled(True)  # Разрешаем перетаскивание из QTreeView
        self.setDropIndicatorShown(True)  # Показываем индикатор перетаскивания
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self.setRootIsDecorated(True)
        self.setHeaderHidden(True)
        self.setIndentation(20) # Отступ для вложенности

        
        self.progress_bar = progress_bar
        self.editor = editor
        self.tab_widget = tab_widget
        self.open_files = open_files
        self.isSuccessReadFile = True
        
        # Отображаем только директории и файлы
        self.model = CustomFileSystemModel()        
        # setCursor(Qt.CursorShape.PointingHandCursor)
        self.model.setRootPath(QDir.rootPath())
        self.setModel(self.model)
        self.model.setReadOnly(False)
            
        self.setRootIndex(self.model.index(QDir.currentPath()))
        self.setColumnWidth(0, 250)  # Ширина колонки с именами файлов

        
        # Скрываем столбцы Size, Type и Date Modified
        self.hideColumn(1)  # Скрыть столбец "Size"
        self.hideColumn(2)  # Скрыть столбец "Type"
        self.hideColumn(3)  # Скрыть столбец "Date Modified"
 
        # Обрабатываем событие при двойном клике на файл        
        self.clicked.connect(self.open_file)
        
         # Подключаем обработчик правого клика
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        
        self.isReadFile = False

    
    def dragEnterEvent(self, event):
        """Разрешаем перетаскивание на окно приложения"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()

                # Определяем директорию назначения
                index = self.indexAt(event.pos())
                if index.isValid():
                    target_directory = self.model.filePath(index)
                    if not os.path.isdir(target_directory):
                        target_directory = os.path.dirname(target_directory)
                else:
                    target_directory = QDir.currentPath()

                if os.path.exists(file_path) and os.path.isdir(target_directory):
                    try:
                        # Перемещаем или копируем файл/папку
                        target_path = os.path.join(target_directory, os.path.basename(file_path))
                        if os.path.exists(target_path):
                            create_window_message_box(status="war",
                                                    title="Перетаскивание",
                                                    label=f"Файл или папка '{os.path.basename(file_path)}' уже существует в '{target_directory}'!")
                        else:
                            shutil.move(file_path, target_path)

                            # Обновляем модель
                            self.model.setRootPath('')
                            self.model.setRootPath(target_directory)
                            create_window_message_box(status="info",
                                          title="Info",
                                          label=f"Перемещено: {file_path} -> {target_path}")
                    except Exception as e:
                        create_window_message_box(title="Ошибка",
                                                  label=f"Ошибка при перемещении: {e}",
                                                  status="critic")
                else:
                    create_window_message_box(title="Info",
                                            label=f"Целевая директория недоступна или некорректна.",
                                            status="war")
            event.accept()
        else:
            event.ignore()

    def handle_dropped_file(self, file_path):
        """Обрабатываем перемещенный файл"""
        # Получаем текущую директорию в модели
        index = self.currentIndex()
        target_directory = self.model.filePath(index)
        
        if os.path.isdir(target_directory):
            try:
                # Перемещаем файл или папку в целевую директорию
                target_path = os.path.join(target_directory, os.path.basename(file_path))
                shutil.move(file_path, target_path)

                # Обновляем модель, чтобы отобразить перемещенный файл
                self.model.setRootPath('')
                self.model.setRootPath(target_directory)
                create_window_message_box(status="info",
                                          title="Info",
                                          label=f"Файл перемещен: {file_path} -> {target_path}")
            except Exception as e:
                create_window_message_box(status="critic",
                                          title="Ощибка",
                                          label=f"Ошибка при перемещении: {e}")
    
    # Обработка перетаскивания файлов из `QTreeView` в файловый менеджер (например, Проводник Windows)
    def start_drag(self, index):
        file_path = self.model.filePath(index)

        if os.path.exists(file_path):
            mime_data = QMimeData()
            mime_data.setText(file_path)  # Устанавливаем путь к файлу для перетаскивания
            
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(index)  # Устанавливаем точку "горячей" области, где будет отображаться курсор
            
            drag.exec_()
                
    def open_file(self, index):
        
        
        if self.isReadFile == False:
            self.isReadFile = True
            file_path = self.model.filePath(index)
            
            
            if os.path.isfile(file_path):
                res_checks = file_path.split("/")[-1].split(".")[-1]
                # print(res_checks)
                
                allowed_list_of_files = [
                                "py", "txt", "json", "js", "go"
                                "md", "css", "html", "cpp", "c"
                                ]
                
                if not res_checks in allowed_list_of_files:
                    create_window_message_box(status="war",
                                                title="Внимание файл",
                                                label=f"Не удалось открыть файл типа '<a style='color: white;'>.{res_checks}</a>'")
                    self.isReadFile = False
                    return
                
                # Проверяем, не открыт ли файл уже
                if file_path in self.open_files:
                    # Переключаемся на существующую вкладку
                    index = self.open_files[file_path]
                    self.tab_widget.setCurrentIndex(index)
                    self.isReadFile = False
                    return
                
                if self.editor.path_file != file_path:
                    # Запускаем загрузку файла в отдельном потоке
                    self.loader_thread = FileLoaderThread(file_path)
                    self.loader_thread.file_loaded.connect(self.on_file_loaded)
                    self.loader_thread.error_occurred.connect(self.on_error)
                    self.loader_thread.start()
                else:
                    self.isReadFile = False
            else:
                self.isReadFile = False


    def on_file_loaded(self, content, file_path):
        self.progress_bar.show()
        
        
        # Разделяем содержимое на части
        chunk_size = 1024 * 1  # 1 КБ за раз
        
                
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        editor = PyNote(self.tab_widget)
        editor.document().setModified(True)
        
        self.tab_widget.addTab(editor, file_path.split("/")[-1])
        new_index = self.tab_widget.count() - 1
        self.isSuccessReadFile = True

        for chunk in chunks:
            if self.tab_widget.widget(new_index) == editor:
                QApplication.processEvents()  # Обновляем GUI
                editor.insertPlainText(chunk)
            else:
                self.isSuccessReadFile = False
                self.tab_widget.widget(new_index-1).setWindowModified(False)
                break
            
        # editor.setWindowModified
        # Добавляем вкладку с редактором и индексируем при условии что не закрыт в преждевременном чтении и записи в виджет "editor"
        if self.isSuccessReadFile:
            self.tab_widget.setCurrentIndex(new_index)
            self.path_files.emit(new_index, file_path)
            icon = set_icon_on_tab_windows(file_path.split("/")[-1].split(".")[-1])
            self.tab_widget.setTabIcon(new_index, icon)
            
        self.progress_bar.hide()
        self.isReadFile = False
        
        
        
    def on_error(self, error_message):
        self.loader_thread = None
                        
                        
    def open_context_menu(self, position):
        """Создает контекстное меню для добавления нового файла"""
        index = self.indexAt(position)
        
        if not index.isValid():
            return
        
        # Определяем путь директории, куда будет добавляться файл
        path = self.model.filePath(index)
        path2 = path
        if not os.path.isdir(path):
            path2 = os.path.dirname(path)

        # Создаем контекстное меню
        menu = QMenu()
        
        new_file_action = QAction("Новый файл", self)
        new_file_action.triggered.connect(lambda: self.create_new_file(path2))
        
        new_folder_action = QAction("Новая папка", self)
        new_folder_action.triggered.connect(lambda: self.create_new_folder(path2))

        delete_item = QAction("Удалить", self)
        delete_item.triggered.connect(lambda: self.delete_items(path))

        rename_action = QAction("Переименовать", self)
        rename_action.triggered.connect(lambda: self.rename_item_in_place(position))        
        
        menu.addAction(new_file_action)
        menu.addAction(new_folder_action)
        menu.addAction(delete_item)
        menu.addAction(rename_action)
        
        # Отображаем меню
        menu.exec_(self.viewport().mapToGlobal(position))
    
    def create_new_file(self, directory):
        """Создает новый файл в указанной директории"""
        # Создаем экземпляр QInputDialog
        file_name = create_window_dialog_box(title="Создать новый файл",
                                                label="Введите имя файла:",
                                                but_name1="Создать файл",
                                                but_name2="Отмена")
        if file_name:
            file_path = os.path.join(directory, file_name)
            try:
                # Создаем файл на диске
                with open(file_path, 'w') as file:
                    file.write("")  # Пустой файл
                
                # Обновляем модель, чтобы отобразить новый файл
                self.model.setRootPath('')  # Перезагрузка модели
                self.model.setRootPath(directory)  # Возврат к нужной директории
                
                create_window_message_box(status="info",
                                        title="Файл создан",
                                        label=f"Файл '<a style='color: white;'>{file_name}</a>' успешно создан.")            
            except Exception as e:
                create_window_message_box(status="critic",
                                                title="Ошибка",
                                                label=f"Не удалось создать файл: <a style='color: white;'>{e}</a>")
    
    def rename_item_in_place(self, position):
        """Включает режим редактирования имени файла прямо в дереве"""
        # Временно разрешаем редактирование
        self.setEditTriggers(QTreeView.AllEditTriggers)
        
        index = self.indexAt(position)
        
        if not index.isValid():
            return
        
        
        # Включаем режим редактирования для текущего индекса
        self.edit(index)

        
        # self.file_renamed.emit()
        
        # print(self.currentIndex(), index, position)

        # Отключаем редактирование обратно
        # Используем QTimer, чтобы дождаться завершения редактирования
        QTimer.singleShot(100, lambda: self.setEditTriggers(QTreeView.NoEditTriggers))
        self.refresh_model()
        
    # def rename_item(self, old_path, new_name):
    #     """Переименовывает файл и отправляет сигнал."""

    #     new_path = os.path.join(os.path.dirname(old_path), new_name)

    #     try:
    #         os.rename(old_path, new_path)
    #         self.file_renamed.emit(old_path, new_path)  # Отправляем сигнал о переименовании
    #         QTimer.singleShot(100, lambda: self.setEditTriggers(QTreeView.NoEditTriggers))
    #         self.refresh_model()

    #     except Exception as e:
    #         create_window_message_box(status="critic",
    #                                 title="Ошибка",
    #                                 label=f"Ошибка при переименовании: {e}")

    def refresh_model(self):
        """Обновляет модель."""
        current_dir = self.model.filePath(self.rootIndex())
        self.model.setRootPath("")
        self.model.setRootPath(current_dir)
        
        
    def create_new_folder(self, directory):
        """Создает новую папку в указанной директории"""
        
        folder_name = create_window_dialog_box(title="Создать новую папку",
                                            label="Введите имя папки:",
                                            but_name1="Создать папку",
                                            but_name2="Отмена")

        # Показываем диалог и получаем ввод
        if folder_name:
            folder_path = os.path.join(directory, folder_name)
            try:
                # Создаем папку на диске
                os.makedirs(folder_path)
                
                # Обновляем модель, чтобы отобразить новую папку
                self.model.setRootPath('')  # Перезагрузка модели на корневой путь
                self.model.setRootPath(directory)  # Возврат к нужной директории
                
                create_window_message_box(status="info",
                                            title="Папка создана",
                                            label=f"Папка '<a style='color: white;'>{folder_name}</a>' успешно создана.")
                
            except Exception as e:
                create_window_message_box(status="critic",
                                        title="Ошибка",
                                        label=f"Не удалось создать папку: <a style='color: white;'>{e}</a>")
                                    
    def delete_items(self, path):
        """Удаляет файл или папку с подтверждением."""
        dialog = ConfirmDeleteDialog(f"Вы действительно хотите удалить '<a style='color: white;'>{os.path.basename(path)}</a>'?")
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    self.file_deleted.emit(path)

                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    
                    self.file_deleted.emit(path)
                    
                # Обновляем модель
                parent_dir = os.path.dirname(path)
                self.model.setRootPath("")
                self.model.setRootPath(parent_dir)
                create_window_message_box(status="info",
                                        title="Удалено",
                                        label=f"'<a style='color: white;'>{os.path.basename(path)}</a>' успешно удалено.")
            except Exception as e:
                create_window_message_box(status="critic",
                                        title="Ошибка",
                                        label=f"Не удалось удалить: <a style='color: white;'>{e}</a>")

    