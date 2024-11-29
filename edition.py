import sys
import os
import re

from PyQt5.QtWidgets import (QApplication, QWidget,  QPlainTextEdit, QTextEdit, QFileDialog,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout, QSplitter)

from PyQt5.QtCore import (Qt, QRect, pyqtSignal)

from PyQt5.QtGui import (QColor, QPainter,  QPalette,QPixmap,
                         QTextFormat, QFont, QIcon, QTextCursor,  QTextCharFormat)



import subprocess

from syntax import SyntaxHighlighter
from lineblock import QLineNumberArea
from style import css_style, css_numeration_plain
from custom_find import TextSearchAndReplaceHandler

import chardet
import resources

class PyNote(QPlainTextEdit):
    # ctrl_click_signal = pyqtSignal(str)
    new_path_files = pyqtSignal(str)
    
    def __init__(self, tab_widgets):
        super().__init__()

        self.tab_width = 4  # Ширина одного уровня отступов (в пробелах)
        self.css = css_style
        self.style_numeration_plain = css_numeration_plain
        self.tool_width, self.tool_heigth = 600, 100
        
        self.tab_widgets = tab_widgets
        
        self.setMouseTracking(True)  # Включаем отслеживание движения мыши
        
        self.setStyleSheet(self.css)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.lineNumberArea = QLineNumberArea(self)
        self.lineNumberArea.setObjectName("lineNumberArea")
        self.lineNumberArea.setStyleSheet(self.style_numeration_plain)

        self.setTabStopWidth(self.fontMetrics().width(' ') * 12)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        font = QFont("Consolas")  # Указываем семейство шрифта и размер
        self.setFont(font)

        self.syntax_document = SyntaxHighlighter(self.document())

        self.path_file = ''

        self.installEventFilter(self)

        self.isFind = False
        self.fix_ident = 0

        boxvlayout = QVBoxLayout()

        self.plane = QWidget()
        self.plane.setFixedSize(360, 60)
        self.plane.setObjectName("plane_match")
        self.plane.setStyleSheet(self.css)
        self.plane.hide()
        
        self.setMouseTracking(True)
        
        self.search_handler = TextSearchAndReplaceHandler(self)
        
        self.count_find = QLabel(self.plane)
        self.count_find.setStyleSheet(self.css)
        self.count_find.setGeometry(75, -1, 200, 20)
        self.count_find.setStyleSheet('color: white;')

        self.line_find = QLineEdit(self.plane)
        self.line_find.setObjectName("line_find")
        self.line_find.setStyleSheet(self.css)
        self.line_find.setGeometry(75, 20, 200, 30)
        self.line_find.setMaxLength(2000)
        self.line_find.setPlaceholderText("Find")
        self.line_find.setToolTip("Find")
        # Подключение поиска к полю ввода
        self.line_find.textChanged.connect(lambda: self.search_handler.set_search_term(self.line_find.text()))

        self.line_replace = QLineEdit(self.plane)
        self.line_replace.setObjectName("line_find")
        self.line_replace.setStyleSheet(self.css)
        self.line_replace.setGeometry(75, 55, 200, 30)
        self.line_replace.setMaxLength(2000)
        self.line_replace.setPlaceholderText("Replace")
        self.line_replace.setToolTip("Replace all element")
        # Установить текст для замены
        self.line_replace.textChanged.connect(lambda: self.search_handler.set_replace_term(self.line_replace.text()))
        
        
        self.button_replace = QPushButton(self.plane)
        self.button_replace.setIcon(QIcon(':img/replace.png'))
        self.button_replace.setGeometry(280, 55, 30, 30)
        self.button_replace.setObjectName("button_down_find")
        self.button_replace.setStyleSheet(self.css)
        self.button_replace.setToolTip("Replace")
        self.button_replace.clicked.connect(self.search_handler.replace_current)
        
        # Заменить все совпадения
        self.button_replace_all = QPushButton(self.plane)
        self.button_replace_all.setIcon(QIcon(':img/replace_all.png'))
        self.button_replace_all.setGeometry(315, 55, 30, 30)
        self.button_replace_all.setObjectName("button_down_find")
        self.button_replace_all.setStyleSheet(self.css)
        self.button_replace_all.setToolTip("Replace All")
        self.button_replace_all.clicked.connect(self.search_handler.replace_all)

        self.button_next_find = QPushButton('↓', self.plane)
        self.button_next_find.setObjectName('button_down_find')
        self.button_next_find.setGeometry(280, 20, 30, 30)
        self.button_next_find.setToolTip("Next Match")
        self.button_next_find.setStyleSheet(css_style)
        self.button_next_find.clicked.connect(self.search_handler.find_next)
        
        self.button_previous_find = QPushButton('↑', self.plane)
        self.button_previous_find.setObjectName('button_down_find')
        self.button_previous_find.setGeometry(315, 20, 30, 30)
        self.button_previous_find.setToolTip("Previous Match")
        self.button_previous_find.setStyleSheet(css_style)
        self.button_previous_find.clicked.connect(self.search_handler.find_previous)

        self.plane_close_find = QPushButton('✕', self.plane)
        self.plane_close_find.setObjectName('button_down_find')
        self.plane_close_find.setGeometry(5, 20, 30, 30)
        self.plane_close_find.clicked.connect(self.close_find_panel)
        
        self.line_replace.hide()
        self.button_replace.hide()
        self.button_replace_all.hide()

        self.plane_open_replace = QPushButton(self.plane)
        self.plane_open_replace.setObjectName('button_down_find')
        self.plane_open_replace.setGeometry(40, 20, 30, 30)
        self.plane_open_replace.setIcon(QIcon(":img/right-arrow.png"))
        self.plane_open_replace.clicked.connect(self.show_replace_elements)
        # 8F8F8F
        # self.plane_open_replace.clicked.connect(self.close_find_panel)
        
        boxvlayout.addWidget(self.plane, 0, Qt.AlignTop | Qt.AlignRight)
        self.setLayout(boxvlayout)

        pal = self.palette()
        pal.setColor(QPalette.HighlightedText, QColor("#BFFFF4"))
        pal.setColor(QPalette.Highlight, QColor("#606060"))
        self.setPalette(pal)

        self.count_find_block_start = 1
        self.count_find_block_end = 1
        
        self.search_term = ""
        self.match_count = 0
        self.current_match_index = -1
                
        self.underline_format = QTextCharFormat()
        self.underline_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.underline_format.setForeground(QColor("#FF5733"))

        
    def show_replace_elements(self):
        if self.line_replace.isHidden() \
            and self.button_replace.isHidden() \
            and self.button_replace_all:
            self.line_replace.show()
            self.button_replace.show()
            self.button_replace_all.show()
            self.plane_open_replace.setIcon(QIcon(":img/down-arrow.png"))
            self.plane.setFixedSize(360, 90)
        else:
            self.line_replace.hide()
            self.button_replace.hide()
            self.button_replace_all.hide()
            self.plane_open_replace.setIcon(QIcon(":img/right-arrow.png"))
            self.plane.setFixedSize(360, 60)
             

    def lineNumberAreaWidth(self):
        """Рассчитывает ширину области для номеров строк с учетом их максимального количества."""
        digits = 1
        max_value = max(1, self.blockCount())
        
        # Рассчитываем количество цифр в числе
        while max_value >= 10:
            max_value /= 10
            digits += 1

        # Минимальная ширина области нумерации строк — 50px
        min_width = 20
        calculated_width = 3 + self.fontMetrics().width('9') * digits

        # Если вычисленная ширина меньше минимальной, то используем минимальную
        return max(min_width, calculated_width)


    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
  
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))


    def highlightCurrentLine(self):
        """Выделяет текущий блок."""

        extraSelections = []
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        selected_text = cursor.selectedText()

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#202020").lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)        



    def lineNumberAreaPaintEvent(self, event):
        """Рисуем нумерацию строк с подсветкой текущей строки."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        block_line = cursor.blockNumber()
        
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#202020"))  # Фон области нумерации

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()

        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                
                # Если это строка с курсором, рисуем белым, иначе — серым
                if blockNumber == block_line:
                    painter.setPen(Qt.white)  # Подсвечиваем текущую строку белым
                else:
                    painter.setPen(Qt.gray)   # Остальные строки серым
                    
                painter.setFont(QFont("Consolas"))

                # Рисуем номер строки
                painter.drawText(0, int(top), self.lineNumberArea.width(), height, Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def keyPressEvent(self, event):
            # self.updateCursorStyle()
            
        if event.key() == Qt.Key_BraceLeft:  # '{'
            cursor = self.textCursor()
            if cursor.selectedText():  # Если есть выделенный текст
                # Оборачиваем выделенный текст в скобки
                cursor.insertText('{' + cursor.selectedText() + '}')
            else:  # Если выделенного текста нет
                # Вставляем {}
                cursor.insertText('}')
                cursor.movePosition(cursor.Left)  # Перемещаем курсор в середину
            self.setTextCursor(cursor)  # Устанавливаем курсор обратно
            
        elif event.key() == Qt.Key_BracketLeft:  # '['
            self.insertPlainText(']')
            self.moveCursor(self.textCursor().Left)
        
        elif event.key() == 39:  # Для одинарных кавычек (')
            self.insertPlainText("'")
            self.moveCursor(self.textCursor().Left)

        elif event.key() == Qt.Key_QuoteDbl:  # Для двойных кавычек (")
            self.insertPlainText('"')
            self.moveCursor(self.textCursor().Left)
            
        elif event.key() == Qt.Key_ParenLeft:  # '('
            self.insertPlainText(')')
            self.moveCursor(self.textCursor().Left)
            
        if event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            cursor = self.textCursor()
            cursor.select(QTextCursor.LineUnderCursor)
            self.setTextCursor(cursor)
        

        if event.key() == 35 and event.modifiers() & Qt.ShiftModifier:
            self.add_hashtags()

        if event.key() == Qt.Key_ParenLeft and event.modifiers() & Qt.ShiftModifier \
            and event.modifiers() & Qt.ControlModifier:
            selection = self.textCursor().selectedText()
            if selection != "":
                self.add_hashtags_scob()
                
        if event.key() == Qt.Key_F and event.modifiers() & Qt.ControlModifier:
            self.plane_find_menu()
            
                    
        if event.key() == 16777220:  # Проверка на нажатие Enter
            cursor = self.textCursor()

            current_line = cursor.block().text()  # Текущая строка текста
            cursor_position = cursor.position() - cursor.block().position()  # Позиция курсора в строке

            # Определяем текущую глубину отступа (в пробелах)
            leading_spaces = self.calculate_depth(current_line, flag=True)

            # Проверяем, нужно ли увеличить отступ (если курсор перед ":")
            try:
                if current_line[cursor_position-1] == ":":
                    leading_spaces += self.tab_width  # Добавляем дополнительный уровень отступа
            except IndexError:
                pass
            
            # Вставляем новую строку с рассчитанным количеством пробелов
            cursor.insertText("\n" + " " * leading_spaces)
            return
        
        else:
            super().keyPressEvent(event)    

        
       
    def add_hashtags(self):
        cursor = self.textCursor().selectedText()
        lines = cursor.splitlines()
        list = []
        for line in lines:
            if line != "":
                if "#" != line[0]:
                    list.append("#" + line)

                if "#" == line[0]:
                    list.append(line[1:])

            if line == "":
                list.append("")
        
        new_text = ""

        if list != []:
            new_text = "\n".join(list)

        self.insertPlainText(new_text)


    def plane_find_menu(self):
        selection = self.textCursor().selectedText()
        if self.plane.isHidden():
            self.plane.show()
            self.line_find.setText(selection)
        elif selection:
            self.line_find.setText(selection)

    def close_find_panel(self):
        self.plane.hide()

    def add_hashtags_scob(self):
        selection = self.textCursor().selectedText()
        lines = selection.splitlines()        
        new_lines = ["(" + line + ")" for line in lines]
        new_text = "\n".join(new_lines)
        self.insertPlainText(new_text)


            

    def paintEvent(self, event):
        """Переопределение отрисовки, чтобы добавить полосы глубины."""
        super().paintEvent(event)  # Сохраняем стандартное поведение редактора

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)

        block = self.firstVisibleBlock()
        
        
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                text = block.text()
                depth = self.calculate_depth(text)
                if depth > 0:
                    self.draw_depth_bars(painter, block, depth)

            block = block.next()
            
            
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
        # self.update_status()

    

    def calculate_depth(self, text, flag=False):
        """Определяет глубину строки на основе начальных пробелов и табуляций."""
        leading_spaces = 0

        for char in text:
            if char == ' ':
                leading_spaces += 1
            elif char == '\t':
                # Считаем ширину табуляции как 4 пробела
                tab_width = self.tabStopDistance() // self.fontMetrics().horizontalAdvance(' ')
                leading_spaces += int(tab_width)
            else:
                break
        
        if flag:
            return leading_spaces
        # Глубина = количество отступов (4 пробела или эквивалент табуляции = 1 уровень)
        return leading_spaces // self.tab_width

    def draw_depth_bars(self, painter, block, depth):
        """Рисует полосы глубины для строки."""
        bar_width = 1
        height = self.fontMetrics().height()
        tab_width = self.tabStopDistance()

        color = QColor(128, 128, 128, 200)  # Полупрозрачный синий
        for level in range(depth):
            x_offset = self.contentOffset().x() + (level * tab_width) + 5
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            painter.fillRect(QRect(int(x_offset), int(top) + 2, bar_width, height - 4), color)