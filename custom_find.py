from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QTextCursor, QTextDocument

class TextSearchAndReplaceHandler:
    def __init__(self, editor: QPlainTextEdit):
        self.editor = editor  # QPlainTextEdit
        self.search_term = ""
        self.replace_term = ""

    def set_search_term(self, term: str):
        """Устанавливает текст для поиска."""
        self.search_term = term

    def set_replace_term(self, term: str):
        """Устанавливает текст для замены."""
        self.replace_term = term

    def find_next(self):
        """Ищет следующее совпадение текста."""
        if not self.search_term:
            return

        # Перемещаем курсор в начало перед началом поиска
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)

        # Ищем следующее совпадение
        if not self.editor.find(self.search_term):
            # Если не нашли, начинаем с начала
            self.editor.moveCursor(QTextCursor.Start)
            self.editor.find(self.search_term)

        # return self.search_term.count(self.search_term)
    
    def find_previous(self):
        """Ищет предыдущее совпадение текста."""
        if not self.search_term:
            return

        # Перемещаем курсор в конец перед началом поиска
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Ищем предыдущее совпадение
        if not self.editor.find(self.search_term, QTextDocument.FindBackward):
            # Если не нашли, начинаем с конца
            self.editor.moveCursor(QTextCursor.End)
            self.editor.find(self.search_term, QTextDocument.FindBackward)

    def replace_current(self):
        """Заменяет текущее выделенное совпадение с использованием Undo/Redo."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.search_term:
            # Сохраняем текущее состояние в Undo/Redo стеке
            self.editor.setUndoRedoEnabled(True)  # Включаем поддержку Undo/Redo
            cursor.insertText(self.replace_term)

    def replace_all(self):
        """Заменяет все вхождения текста с поддержкой Undo/Redo."""
        cursor = self.editor.textCursor()

        # Перемещаем курсор в начало перед началом замены всех вхождений
        cursor.movePosition(QTextCursor.Start)
        self.editor.setTextCursor(cursor)  # Устанавливаем курсор в начало

        replacement_count = 0

        # Блокируем историю изменений во время массовой замены
        self.editor.setUndoRedoEnabled(True)

        while self.editor.find(self.search_term):
            cursor = self.editor.textCursor()
            cursor.insertText(self.replace_term)
            replacement_count += 1

        return replacement_count
