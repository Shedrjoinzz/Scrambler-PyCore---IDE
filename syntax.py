from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import QRegularExpression, QRunnable, QThreadPool, QRegularExpression
import re


class FunctionUpdateWorker(QRunnable):
    """Фоновый поток для подсветки текста"""
    def __init__(self, document, callback):
        super().__init__()
        self.document = document
        self.text = document.toPlainText()
        self.callback = callback  # Функция, которую вызываем после обработки текста


    def run(self):
        # Ищем функции и классы
        new_defined_functions = set(re.findall(r"\bdef\s+(\w+)\s*\(", self.text))

        new_defined_classes = set(re.findall(r"\bclass\s+(\w+)\s*(\([^)]*\))?\s*:", self.text))

        # Передаём результат обратно через callback
        
        self.callback(new_defined_functions, new_defined_classes)

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)
        self.highlighting_rules = []        
        self.thread_pool = QThreadPool.globalInstance()


        
        self.function_name_format = QTextCharFormat()
        self.function_name_format.setForeground(QColor("#C9C97C"))  # Цвет для имени функции
        self.function_definition_pattern = QRegularExpression(r"\bdef\s+(\w+)\s*\(")
        self.highlighting_rules.append((self.function_definition_pattern, self.function_name_format))

        # # Формат для классов
        class_pattern = r"\bclass\s+(\w+)\s*(\([^)]*\))?\s*:"

        self.class_format = QTextCharFormat()
        self.class_format.setForeground(QColor("#3AC9A2"))  # Цвет для класса
        self.class_pattern = QRegularExpression(class_pattern)
        self.highlighting_rules.append((self.class_pattern, self.class_format))

        self.errorFormat = QTextCharFormat()
        self.errorFormat.setForeground(QColor("red"))
        
        # Форматы
        self.variableFormat = QTextCharFormat()
        self.variableFormat.setForeground(QColor("#8CDCDA"))

        # Данные для отслеживания переменных
        self.defined_variables = set()
        
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("red"))
        self.error_format.setUnderlineColor(QColor("red"))
        self.error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                                       
        self.defined_variables_2 = {}

        self.acess_syntax = False
        
        
    def highlightBlock(self, text):
        # self.setCurrentBlockState(0)
        """Метод подсветки каждого блока текста."""
        for pattern, fmt in self.highlighting_rules:
            if pattern == self.function_definition_pattern:
                self._apply_format(text, pattern, fmt, is_function=True)
            elif pattern == self.class_pattern:
                self._apply_format(text, pattern, fmt, is_class=True)
            else:
                self._apply_format(text, pattern, fmt)
        
        self.setup_highlighting()        
        
        
    def setup_highlighting(self):
        if self.acess_syntax == False:
            """Настраивает правила подсветки синтаксиса."""
            # Здесь вызывается оптимизированный метод, добавляющий правила
            self.add_highlighting_rules([rf"\b{kw}\b" for kw in ["as", "assert", "continue", "break", "else", "finally", "elif", "del", "except", "for", "if", "from", "import", "raise", "try", "return", "pass", "while", "with", "def", "nonlocal", "global", "class"]],
                                        "#DD5BE8")
            
            self.add_highlighting_rules([rf"\b{kw}\b" for kw in ["True", "False", "None", "and", "or",  "in", "not", "is", "lambda" ]],
                                        "#2D7AD6")
            
            self.add_highlighting_rules([re.escape(kw) for kw in ["+", "-", "=", "*", "|", "_", "%", "^", "@", "&", "?", "\\", "!", ":", "<", ">", "/"]],
                                        "silver")
            
            self.add_highlighting_rules([r'\b'+re.escape(kw)+r'\b' for kw in ["float", "complex", "dict", "int", "str", "list", "set", "tuple", "type", "bool", "frozenset", "slice", "bytes", "bytearray", "object", "classmethod", "staticmethod", "super"]],
                                        "#33BBB0")
            
            self.add_highlighting_rules([r'\b'+re.escape(kw)+r'\b' for kw in ["__init__", "filter", "print", "ord", "chr", "len", "abs", "map", "reversed", "round", "range", "divmod", "pow", "zip", "max", "min", "sum", "memoryview", "callable", "dir", "enumerate", "eval", "hash", "help", "input", "iter", "next", "exec", "sorted","open","locals","format","bin", "hex","oct","all","any","ascii","compile","id","isinstance", "issubclass","repr","setattr","getattr","hasattr","delattr", "vars"]],
                                        "#C9C97C")
            
            self.add_highlighting_rules([re.escape(kw) for kw in ["(", ")", "{", "}", "[", "]", "\\"]],
                                        "#F1D710")
            
            self.add_highlighting_rules([r"\bdef\s+(\w+)\s*\("],
                                        "#C9C97C")
            
            self.add_highlighting_rules([r"\bclass\s+(\w+)\s*(\([^)]*\))?\s*:"],
                                        "#3AC9A2")
            
            self.add_highlighting_rules([r'(\"[^\"]*\")|(\'[^\']*\')'],
                                        "#CE915B")
            
            self.add_highlighting_rules([r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"],
                                        "#B5C078")
            
            self.add_highlighting_rules([QRegularExpression(r"(?<![\"'])\b0[0-9]+\b(?!\")")],
                                        "red")
            
            self.add_highlighting_rules([QRegularExpression(r"(?<![\"'#])\b[0-9]+[a-zA-Z_]+[\w]*\b(?!\")")],
                                        "gray")

            self.add_highlighting_rules([QRegularExpression(r"(?<!['\"])#.*$")],
                                        "#65B74D")

            self.acess_syntax = True

        
    def add_highlighting_rule(self, pattern, color, underline=False, font_size=None):
        """Добавляет правило подсветки с заданным паттерном и цветом."""
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        if underline:
            format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            format.setUnderlineColor(QColor(color))
        if font_size:
            format.setFontPointSize(font_size)
        self.highlighting_rules.append((QRegularExpression(pattern), format))

    
    def add_highlighting_rules(self, patterns, color, underline=False, font_size=None):
        """Добавляет несколько правил подсветки."""
        for pattern in patterns:
            self.add_highlighting_rule(pattern, color, underline, font_size)
    

                                    
    def _apply_format(self, text, pattern, fmt, is_function=False, is_class=False):
        """Обрабатывает и применяет форматирование для заданного паттерна."""
        expression = QRegularExpression(pattern)
        match = expression.match(text)  # Получаем объект QRegularExpressionMatch

        while match.hasMatch():
            if is_function:
                # Обработка функции
                function_name = match.captured(1)  # Первая группа (захваченная функция)
                self.setFormat(match.capturedStart(1), len(function_name), fmt)
            elif is_class:
                # Обработка класса
                class_name = match.captured(1)  # Первая группа (захваченный класс)
                self.setFormat(match.capturedStart(1), len(class_name), fmt)
            else:
                # Обычная подсветка
                start = match.capturedStart()  # Начало совпадения
                length = match.capturedLength()  # Длина совпадения
                self.setFormat(start, length, fmt)

            # Находим следующее совпадение, начиная с конца текущего
            match = expression.match(text, match.capturedEnd())
            
            
    def check_unmatched_brackets(self): # функцию скорректировать
        """Проверка на незакрытые скобки с учетом переносов строки"""
        stack = []
        bracket_pairs = {'(': ')', '[': ']', '{': '}'}
        closing_brackets = {v: k for k, v in bracket_pairs.items()}
        
        # Перебираем символы текущего блока текста
        for i, char in enumerate(self.document().toPlainText()):
            try:
                if char in bracket_pairs:  # Открывающая скобка
                    stack.append((char, i))  # Сохраняем локальный индекс
                elif char in closing_brackets:  # Закрывающая скобка
                    # Проверяем соответствие с последней открытой скобкой
                    if stack and stack[-1][0] == closing_brackets[char]:
                        stack.pop()  # Убираем из стека найденную пару
                    else:
                        # Подсвечиваем закрывающую скобку без пары
                        self.setFormat(i, 1, self.error_format)
            except KeyboardInterrupt:
                pass

        self.old_char_format(stack)
        
    def old_char_format(self, stack):
        # Подсвечиваем оставшиеся открывающие скобки
        for char, index in stack:
            self.setFormat(index, 1, self.error_format)