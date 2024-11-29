css_style = """
            QScrollBar:vertical {
                background-color: #292929;
            }
            QScrollBar::handle:vertical {
                background-color: #303030;
                border-radius: 1px;
                width: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #393939;
            }
            QScrollBar::sub-line:vertical
            {
                margin: 3px 0px 3px 0px;
                border-color: none;  
                height: 10px;
                width: 10px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:vertical
            {
                margin: 3px 0px 3px 0px;
                border-color: none;
                height: 10px;
                width: 10px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
            {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
            {
                background: none;
            }
            QScrollBar:horizontal {
                background-color: #292929;
            }
            QScrollBar::handle:horizontal {
                background-color: #303030;
                border-radius: 1px;
                width: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #464646;
            }
            QScrollBar::sub-line:horizontal
            {
                margin: 3px 0px 3px 0px;
                border-color: none;  
                height: 10px;
                width: 10px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:horizontal
            {
                margin: 3px 0px 3px 0px;
                border-color: none;
                height: 10px;
                width: 10px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
            {
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
            {
                background: none;
            }

            QPlainTextEdit {
                background-color: #1F1F1F;
                font-size: 15px;
                color: silver;
                border: 1px solid #757575;
            }
            
            QPlainTextEdit#terminal {
                background-color: #1F1F1F;
                font-size: 15px;
                color: silver;
                border: 1px solid #757575;
                padding: 10px;
            }
            
            
            QLineEdit#terminal_commands_line {
                color: white;
                font-size: 16px;
                padding: 10px;
            }
            
            QLineEdit#terminal_commands_line:active {
                border: 1px solid gray;                
            }
            
            QPlainTextEdit#info_tool {
                font-size: 14px;
                padding: 10px;
            }
            QToolTip {
                background-color: #454545;
                color: silver;
                font-size: 14px;
                border: 1px solid #454545;
            }
            
            QTreeView {
                color: white;
                background-color: #181818;
            }
            QTreeView QLineEdit {
                color: white;
            }
            QTreeView::item {
                padding: 3px;  /* Расстояние внутри ячейки */
                border: none;
            }
            QTreeView::item:editable {
                border: 1px solid #cccccc;  /* Устанавливаем свой стиль */
                background: #f9f9f9;       /* Или добавляем фон */
            }
            QTreeView::item:open {
                background-color: #333333;
                color: #3babdf;
            }
            QTreeView::item:selected {
                background-color: #474e58;
                color: white;
                border: none;
            }
            QTreeView::branch {
                border-left: 1px solid #313131;
                padding: 3px;
            }
            QTreeView::branch:open {
                image: url(:img/down-arrow.png);
                border-left: 2px solid #0078D4;
            }
            QTreeView::branch:closed:has-children {
                image: url(:img/right-arrow.png);
            }
            
"""

tab_widget_styles = """
    QTabBar::close-button:hover {
        image: url(:img/close2.png);
    }
    
    QTabBar::close-button {
        image: url(:img/close3.png);
    }
    
    QTabWidget:pane
    { 
        background-color:rgb(255,255,255); 
        border: -1px solid ; 
        top:0px solid;
    }

    QTabBar::tab:hover {
        background: #363636;
    }
    
    QTabBar::tab:selected {
        border-top-color: #0078D4;
        color: white;
        font:11px "Microsoft YaHei";
    }
      QTabBar::tab {
        color: gray;
        border: 1px solid gray;
        padding: 10px;
        min-width: 100px;
    }
   
    QTabBar::tab:first { 
        border-top-left-radius:8px;
    }
    QTabBar::tab:last {
        border-top-right-radius:8px;
    }


    QTabBar::scroller {
        border: 1px solid silver; 
    }
    
    QPushButton#button_down_find {
        color: white;
        border-radius: 2px;
        background-color: #222222;
    }
    QPushButton#button_down_find:hover {
        background-color: #528CC8;
    }
    QPushButton#button_down_find:pressed {
        background-color: #323232;
    }
    
    QLineEdit#line_find {
        color: white;
        border: 1px solid gray;
        padding: 2px;
    }
    
    QPushButton#ReplaceAll {
        color: white;
        border;
    }
    
    
    QWidget#plane_match {
        border-radius: 5px;
    }


"""

menu_bar_status = """
    QStatusBar:hover {
        background-color: #292929;
    }
"""


menu_bar_buttons = """
    QPushButton#github {
        color: white;
        border: none;
        font-size: 14px;
    }
    QPushButton#github:hover {
        background-color: #0078D4
    }

    QLabel {
        color: white;
        font-size: 12px;
    }
        
"""

progress_bar = """
    QProgressBar#GreenProgressBar {
        min-height: 12px;
        max-height: 12px;
        border-radius: 6px;
    }
    QProgressBar#GreenProgressBar::chunk {
        border-radius: 6px;
        background-color: #009688;
    }
"""

menu_bar_style = """
    QMenu {background-color:rgba(17,24,47,1);border:1px solid rgba(82,130,164,1);}
    QMenu::item {min-width:50px;font-size: 12px;color: rgb(225,225,225);background:rgba(75,120,154,0.5);border:1px solid rgba(82,130,164,1);padding:1px 1px;margin:1px 1px;}
    QMenu::item:selected {background:rgba(82,130,164,1);border:1px solid rgba(82,130,164,1);}
    QMenu::item:pressed {background:rgba(82,130,164,0.4);border:1px solid rgba(82,130,164,1);}
    
    QMenuBar{background-color:transparent;}                          
    QMenuBar::selected{background-color:transparent;}
    QMenuBar::item{font-family:Microsoft YaHei;color:rgba(255,255,255,1);}
"""


dialog_flow_style = """
            QInputDialog {
                background-color: #282C34;
                color: #ABB2BF;
                font-size: 14px;
                border: 1px solid #61AFEF;
            }
            QLabel {
                color:#61AFEF;
            }
            QLineEdit {
                height: 25px;                
                background-color: #1E1E1E;
                color:rgba(255,255,255,1);
                border: 1px solid #61AFEF;
                border-radius: 5px;
                padding: 2px;
                font-size: 14px;
                font-family:Microsoft YaHei;
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
        """


plain_suggle_style = """
    QListWidget {
        background-color: #393939;
        color: white;
        font-size: 16px;
    }
"""

css_numeration_plain = """
    QWidget#lineNumberArea {
        font-size: 15px;
    }
"""