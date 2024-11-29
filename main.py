# Стандартные библиотеки
import sys
import os
import subprocess

# Библиотеки сторонних разработчиков
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QLineEdit, QProgressBar, QSplitter, QMenuBar, QFileDialog,
                            QAction, QTabWidget, QMessageBox)
from PyQt5.QtGui import QIcon, QKeyEvent, QFont, QDesktopServices
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl

# Локальные модули и файлы
import resources
from style import css_style, menu_bar_status, progress_bar, menu_bar_style, tab_widget_styles
from edition import PyNote
from file_explorer import FileExplorer
from logicai import set_icon_on_tab_windows, create_window_message_box
from cprofile_code import profile_user_code
from terminal import Terminal


class CommandThread(QThread):
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(
            self.command,
            shell=True,
            stdin=subprocess.PIPE,  # Включаем стандартный ввод
            stdout=subprocess.PIPE,  # Включаем стандартный вывод
            stderr=subprocess.PIPE,  # Включаем стандартный вывод ошибок
            text=True  # Работаем с текстом вместо байтов
        )

        while True:
            output = process.stdout.readline(100)  # Читаем по одному символу
            if output:
                self.output_received.emit(output)  # Отображаем вывод в вашем виджете
            if 'Y/n' in output or 'Y | n' in output:  # Проверяем запрос подтверждения
                process.stdin.write('Y\n')  # Отправляем подтверждение
                process.stdin.flush()  # Обязательно сбрасываем буфер
            if process.poll() is not None:  # Если процесс завершился
                break
        
        # Завершаем чтение и добавляем ошибки, если есть
        errors = process.stderr.read()

        if errors:
            self.error_received.emit(errors)


class MainWindow(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.progress_bar = QProgressBar(minimum=0, maximum=0, textVisible=False)

        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(menu_bar_status)
        
        self.progress_bar.setObjectName("GreenProgressBar")
        self.progress_bar.setStyleSheet(progress_bar)
        self.progress_bar.hide()
                
        self.status_bar.addWidget(self.progress_bar)
        
        self.setup_ui()
        self.create_menu()
        # Подключаем сигналы
        self.file_explorer.file_deleted.connect(self.close_tab_by_path)
        self.file_explorer.file_renamed.connect(self.rename_tab_by_path)
        
    def create_menu(self):
        """Создаем меню для открытия файлов."""
        menu = self.menuBar()

        file_menu = menu.addMenu("Файл")
        open_file = QAction("Открыть файл", self)
        open_file.triggered.connect(self.open_file)
        file_menu.addAction(open_file)

        open_folder = QAction("Открыть папку", self)
        open_folder.triggered.connect(self.openFolder)
        file_menu.addAction(open_folder)

        save_file = QAction("Сохранить файл", self)
        save_file.triggered.connect(self.savePyFile)
        file_menu.addAction(save_file)
        
        save_file_as = QAction("Сохранить файл как", self)
        save_file_as.triggered.connect(self.save_file_as)
        file_menu.addAction(save_file_as)
        
        
        run_menu = menu.addMenu("Запуск")        
        run_test_code = QAction("Запустить Анализ", self)
        run_test_code.triggered.connect(self.run_analysis)
        run_menu.addAction(run_test_code)
        
        run_test_code_Scalene = QAction("Запустить Анализ - Scalene", self)
        run_test_code_Scalene.triggered.connect(self.run_analysis_scalene)
        run_menu.addAction(run_test_code_Scalene)

        terminal_menu = menu.addMenu("Терминал")
        terminal_open = QAction("Открыть", self)
        terminal_open.triggered.connect(self.set_terminal_show)
        terminal_menu.addAction(terminal_open)
        
        terminal_clear = QAction("Очистить", self)
        terminal_clear.triggered.connect(self.terminal.clear)
        terminal_menu.addAction(terminal_clear)

        terminal_hide = QAction("Скрыть", self)
        terminal_hide.triggered.connect(self.set_terminal_hide)
        terminal_menu.addAction(terminal_hide)

    def set_terminal_hide(self):
        self.terminal.hide()
        self.line_commands.hide()
            
    def set_terminal_show(self):
        self.terminal.show()
        self.line_commands.show()
            
            
    def rename_tab_by_path(self, old_path, new_path):
        """Обновляет вкладку, если файл переименован."""
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            if hasattr(widget, "file_path") and widget.file_path == old_path:
                widget.file_path = new_path  # Обновляем путь в редакторе
                self.tab_widget.setTabText(index, os.path.basename(new_path))  # Обновляем заголовок вкладки
                break

            
    def open_file(self):
        """Открывает файл и создает вкладку для него."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.py)")
        if file_path:
            # Проверяем, не открыт ли файл уже
            if file_path in self.open_files:
                # Переключаемся на существующую вкладку
                index = self.open_files[file_path]
                self.tab_widget.setCurrentIndex(index)
                return

            # Открываем файл и читаем его содержимое
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                create_window_message_box(status="critic",
                                          title="Ощибка",
                                          label=f"Не удалось открыть файл {e}")
                return

            # Создаем новую вкладку
            editor = PyNote()
            editor.path_file = file_path
            editor.setPlainText(content)
            self.tab_widget.addTab(editor, os.path.basename(file_path))
            
            # Сохраняем информацию о файле
            tab_index = self.tab_widget.count() - 1
            self.new_dict_path_files(tab_index, file_path)

            self.tab_widget.setCurrentIndex(tab_index)
        
                                
    def run_analysis_scalene(self):
        current_index = self.tab_widget.currentIndex()
        old_file_path = next((key for key, val in self.open_files.items() if val == current_index), None)
        
        command = f'scalene "{old_file_path}"'

        try:
            # Запускаем файл
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            self.terminal.insertPlainText(f">>> {e}\n")

        
    def save_file_as(self):
        """Сохраняет текущую вкладку как новый файл."""
        current_index = self.tab_widget.currentIndex()
        if current_index == -1:
            create_window_message_box(status="war",
                                      title="Ощибка",
                                      label="Нет открытых вкладок")
            return
        
        
        old_file_path = next((key for key, val in self.open_files.items() if val == current_index), None)
        
        # Выбор пути сохранения
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл как", "", "Все файлы (*)")

        if file_path:
            current_editor = self.tab_widget.widget(current_index)

            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(current_editor.toPlainText())
                    
                # Обновляем путь в словаре и имя вкладки
                self.tab_widget.setTabText(current_index, os.path.basename(file_path))
                icon = set_icon_on_tab_windows(file_path.split("/")[-1].split(".")[-1])
                self.tab_widget.setTabIcon(current_index, icon)

                self.open_files.pop(old_file_path)
                self.open_files[file_path] = current_index
                
                
                create_window_message_box(status="info",
                                    title="Сохранение",
                                    label="Файл успешно сохранен!")

            except Exception as e:
                create_window_message_box(status="critic",
                                    title="Ощибка",
                                    label="Не удалось сохранить файл")

                self.terminal.insertPlainText(f">>> {e}\n")


        
    def savePyFile(self):
        """Сохраняет текущую вкладку."""
        current_index = self.tab_widget.currentIndex()

        # Проверяем, есть ли путь к файлу
        if current_index == -1:
            create_window_message_box(status="war",
                                    title="Ощибка",
                                    label="Нет открытых вкладок")            
            return

        file_path = next((key for key, val in self.open_files.items() if val == current_index), None)

        widget_editor = self.tab_widget.widget(current_index)
        
        if file_path != '' and file_path != "New File":

            with open(file_path, "w", encoding="utf-8") as Pyfile:
                Pyfile.write(widget_editor.toPlainText())
                
            self.tab_widget.setTabText(current_index, os.path.basename(file_path))
            
            widget_editor.document().setModified(False)

        elif file_path == '' or file_path == "New File":
            self.save_file_as()
    
        
    def setup_ui(self):
        # Создаем QTabWidget для вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_widget.setStyleSheet(tab_widget_styles)
        self.tab_widget.adjustSize()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        # Словарь для хранения открытых файлов
        self.open_files = {}
        
        # Создаем меню
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName("menu_bar_action")
        self.menubar.setStyleSheet(menu_bar_style)

        contacts = self.menubar.addMenu("Контакты")

        self.statusBar().setStyleSheet("color: white;")
        telegram_support_action = QAction("Telegram", self)
        telegram_support_action.setStatusTip("Ссылка")
        telegram_support_action.triggered.connect(self.open_telegram)
        contacts.addAction(telegram_support_action)
        
        telegram_projects_action = QAction("Проекты и Разработки", self)
        telegram_projects_action.setStatusTip("Ссылка")
        telegram_projects_action.triggered.connect(self.open_telegram_projects)
        contacts.addAction(telegram_projects_action)

        github_projects_action = QAction("GitHub", self)
        github_projects_action.setStatusTip("Ссылка")
        github_projects_action.triggered.connect(self.open_github_projects)
        contacts.addAction(github_projects_action)

        self.setMenuBar(self.menubar)

        # Window Setup
        self.setWindowTitle("Scrambler PyCore - 1.0.1v")


        self.setWindowIcon(QIcon(":img/logo.png"))
        self.setStyleSheet("background-color: #181818;")
        
        self.setGeometry(400, 100, 1200, 800)
        
        
        self.editor = PyNote(self.tab_widget)
        
        self.tab_widget.addTab(self.editor, "Welcome")
        new_index = self.tab_widget.count() - 1
                        
        self.tab_widget.setCurrentIndex(new_index)
        self.new_dict_path_files(new_index, "New File")
        
        # Создаем панель файлов и редактор кода
        self.file_explorer = FileExplorer(self.editor, self.progress_bar, self.tab_widget, self.open_files)
        self.file_explorer.setStyleSheet(css_style)
        self.file_explorer.path_files.connect(self.new_dict_path_files)
        
        
        self.terminal = Terminal()
        self.terminal.hide()

        
        self.line_commands = QLineEdit()
        self.line_commands.hide()
        self.line_commands.setObjectName("terminal_commands_line")
        self.line_commands.setStyleSheet(css_style)
        self.line_commands.setFixedHeight(50)
        self.line_commands.setFont(QFont("Arial"))
        self.line_commands.setPlaceholderText("cmd:")

        # Подключаем сигнал returnPressed к функции
        self.line_commands.returnPressed.connect(self.handle_enter)
        
        # Разделяем окно на две части: панель файлов и редактор
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_explorer)
        splitter.addWidget(self.tab_widget)
        splitter.setSizes([80, 320, 100])  # Устанавливаем начальные размеры панелей

        # Создаем главный сплиттер, который содержит верхний и терминал
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(splitter)  # Добавляем верхний сплиттер
        main_splitter.addWidget(self.line_commands)
        main_splitter.addWidget(self.terminal)  # Добавляем терминал внизу
        main_splitter.setSizes([300, 10, 100])  # Устанавливаем начальные размеры для вертикальных областей

        # Настраиваем главное окно
        container = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(main_splitter)        
        container.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(container)
        self.resize(800, 600)

    def handle_enter(self):
        command = self.line_commands.text()
        if not command:
            self.terminal.appendPlainText(">>> Ошибка: команда не введена")
            return

        # Запуск команды в отдельном потоке
        self.threads = CommandThread(command)
        self.threads.output_received.connect(self.display_output)
        self.threads.error_received.connect(self.display_error)
        self.threads.start()
        self.line_commands.clear()

    def display_output(self, text):
        self.terminal.appendPlainText(text)

    def display_error(self, text):
        self.terminal.appendPlainText(text)
    
        
    def run_analysis(self):
        """Выполняет анализ введенного кода."""
        
        widget = self.tab_widget.currentWidget()
        
        user_code = widget.toPlainText()
        if not user_code.strip():
            self.terminal.appendPlainText(f">>> Введите код для анализа.")
            return

        # Профилируем код
        profile_code = profile_user_code(user_code)
        for key, value in profile_code.items():
            info_terminal = f">>> {key} | {value}\n"
            self.terminal.insertPlainText(info_terminal)
        
    def new_dict_path_files(self, new_index, path_file):
        self.open_files[path_file] = new_index
        
    def update_dict_path_files(self, new_index, path_file):
        self.open_files[path_file] = new_index              
        
    def close_tab(self, index):
        """Закрывает вкладку."""
        # Удаляем информацию о файле
        for file_path, tab_index in list(self.open_files.items()):
            if tab_index == index:
                del self.open_files[file_path]
                break
        

        self.tab_widget.removeTab(index)

        # Обновляем индексы в словаре
        for file_path, tab_index in self.open_files.items():
            if tab_index > index:
                self.open_files[file_path] = tab_index - 1

        
    def close_tab_by_path(self, file_path):
        # print("file_path", file_path)
        """Закрывает вкладку, если файл удален."""
        current_index = self.tab_widget.currentIndex()

        if current_index == -1:
            return
        
        """Закрывает вкладку."""
        try:
            self.tab_widget.removeTab(self.open_files[file_path])
        except KeyError:
            pass

        # Удаляем информацию о файле
        for file_path, tab_index in list(self.open_files.items()):
            if self.open_files[file_path]:
                del self.open_files[file_path]
                break

        # Обновляем индексы в словаре
        for file_path, tab_index in self.open_files.items():
            if tab_index > len(self.open_files):
                self.open_files[file_path] = tab_index - 1
        
        
    def rename_tab_by_path(self, old_path, new_path):
        """Обновляет вкладку, если файл переименован."""
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            if hasattr(widget, "file_path") and widget.file_path == old_path:
                widget.file_path = new_path  # Обновляем путь в редакторе
                self.tab_widget.setTabText(index, os.path.basename(new_path))  # Обновляем заголовок вкладки
                break
            

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event.key() == Qt.Key_O and event.modifiers() & Qt.ControlModifier:
            self.openFolder()
        if event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.savePyFile()
        if event.key() == Qt.Key_R and event.modifiers() & Qt.ControlModifier:
            self.execute_program()
        
        if event.key() == 126:
            self.set_terminal_show()
                
        return super().keyPressEvent(event)

    def execute_program(self):
        current_index = self.tab_widget.currentIndex()

        if current_index == -1:
            create_window_message_box(status="war",
                                    title="Ощибка",
                                    label="Нет открытых вкладок")
            
            return
        
        file_path = next((key for key, val in self.open_files.items() if val == current_index), None)
        
        if file_path == '' or file_path == "New File":
            return self.save_file_as()
        
        # Используем кавычки вокруг пути, чтобы избежать проблем с пробелами
        command = f'python "{file_path}"'

        try:
            # Запускаем файл
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            self.terminal.insertPlainText(f">>> {e}\n")

            
        
        
    def openFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку")

        if folder_path:
            # Теперь нужно обновить QTreeView с новым путём
            self.show_directory_in_explorer(folder_path)
    
    def show_directory_in_explorer(self, directory):
        """Загружает содержимое выбранной директории в QTreeView"""
        self.file_explorer.setRootIndex(self.file_explorer.model.setRootPath(directory))
    
    def open_telegram(self):
        url = QUrl("https://t.me/ProgramsCreator")
        QDesktopServices.openUrl(url)
    
    def open_telegram_projects(self):
        url = QUrl("https://t.me/ProgramsCreatorRu")
        QDesktopServices.openUrl(url)
        
    def open_github_projects(self):
        url = QUrl("https://www.github.com/shedrjoinzz")
        QDesktopServices.openUrl(url)
    
        

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())
