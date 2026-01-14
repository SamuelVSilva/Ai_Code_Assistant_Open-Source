from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTreeView, QTextEdit, QLineEdit, 
                             QPushButton, QToolBar, QStatusBar, QFrame, QLabel, 
                             QTabWidget, QScrollArea, QComboBox, QSizePolicy, 
                             QToolButton, QDialog, QGraphicsOpacityEffect, QMenu,
                             QMenuBar, QStackedWidget, QInputDialog, QMessageBox,
                             QFileDialog, QApplication)
from PyQt6.QtCore import (Qt, QSize, QDir, QRect, QPropertyAnimation, 
                          QEasingCurve, QSequentialAnimationGroup, QThread, 
                          pyqtSignal, QProcess, QEvent)
from PyQt6.QtGui import (QIcon, QFont, QColor, QPalette, QFileSystemModel, 
                         QSyntaxHighlighter, QTextCharFormat, QAction, QKeyEvent,
                         QCursor, QPixmap, QImage)

import os
import sys
import subprocess
import tempfile
import shutil

# Pygments for syntax highlighting
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
    from pygments.token import Token
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, filename_or_ext):
        super().__init__(parent)
        self._lexer = None
        if PYGMENTS_AVAILABLE:
            try:
                if "." in filename_or_ext:
                    self._lexer = get_lexer_for_filename(filename_or_ext)
                else:
                    self._lexer = get_lexer_by_name(filename_or_ext)
            except:
                pass
        self.formats = {}

    def highlightBlock(self, text):
        if not self._lexer: return
        lexer = self._lexer
        for token, content in lexer.get_tokens(text):
            length = len(content)
            idx = 0
            while True:
                idx = text.find(content, idx)
                if idx == -1: break
                fmt = self.get_format(token)
                self.setFormat(idx, length, fmt)
                idx += length
                break

    def get_format(self, token):
        if token in self.formats: return self.formats[token]
        fmt = QTextCharFormat()
        if token in Token.Keyword: fmt.setForeground(QColor("#569cd6"))
        elif token in Token.Name.Function: fmt.setForeground(QColor("#dcdcaa"))
        elif token in Token.Name.Class: fmt.setForeground(QColor("#4ec9b0"))
        elif token in Token.String: fmt.setForeground(QColor("#ce9178"))
        elif token in Token.Comment: fmt.setForeground(QColor("#6a9955"))
        elif token in Token.Number: fmt.setForeground(QColor("#b5cea8"))
        else: fmt.setForeground(QColor("#cccccc"))
        self.formats[token] = fmt
        return fmt

class ExecutionThread(QThread):
    output_ready = pyqtSignal(str)
    finished_execution = pyqtSignal(int)

    def __init__(self, command, cwd):
        super().__init__()
        self.command = command
        self.cwd = cwd

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True
            )
            for line in process.stdout:
                self.output_ready.emit(line)
            process.wait()
            self.finished_execution.emit(process.returncode)
        except Exception as e:
            self.output_ready.emit(f"Erro na execução: {e}\n")
            self.finished_execution.emit(-1)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre")
        self.setFixedSize(400, 320)
        self.setStyleSheet("background-color: #0f172a; color: white; border: 1px solid #334155; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("AI Code Assistant")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("Versão 0.3.6-14012026-alpha"), alignment=Qt.AlignmentFlag.AlignCenter)
        info = QLabel(
            "Developer: Samuel V. Silva\n"
            "Brand: @S.V.S - Try Technology\n\n"
            "Produtividade e IA."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-size: 13px; color: #cbd5e1;")
        layout.addWidget(info)
        layout.addStretch()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #0ea5e9; padding: 8px; border-radius: 4px;")
        layout.addWidget(close_btn)

class ActivityBar(QFrame):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setFixedWidth(50)
        self.setStyleSheet("background-color: #0f172a; border-right: 1px solid #1e293b;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.callback = callback
        
        self.add_action("📁", "Explorer", 0)
        self.add_action("🔍", "Busca", 1)
        self.add_action("🧩", "Extensões", 2)
        self.add_action("🐞", "Debug", 3)
        self.add_action("🧪", "Lab", 4)
        
        self.layout.addStretch()
        self.add_action("⚙️", "Configurações", 5)

    def add_action(self, icon_text, tooltip, index):
        btn = QToolButton()
        btn.setText(icon_text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(50, 40)
        btn.setStyleSheet("""
            QToolButton { color: #64748b; font-size: 20px; border: none; background: transparent; }
            QToolButton:hover { color: #38bdf8; background-color: #1e293b; border-left: 2px solid #38bdf8; }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.callback:
            btn.clicked.connect(lambda: self.callback(index))
        self.layout.addWidget(btn)

class ChatMessage(QFrame):
    def __init__(self, sender, text, is_user=False, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        align = Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft
        self.layout.setAlignment(align)
        
        bubble = QWidget()
        bubble_layout = QVBoxLayout(bubble)
        bg_color = "#1e40af" if is_user else "#1e293b"
        bubble.setStyleSheet(f"background-color: {bg_color}; border-radius: 12px; border: 1px solid #334155; padding: 12px;")
        bubble.setMaximumWidth(600) 
        
        sender_label = QLabel(sender)
        sender_label.setStyleSheet(f"font-weight: bold; color: {'#7dd3fc' if is_user else '#2dd4bf'}; font-size: 11px;")
        
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text_label.setStyleSheet("color: #f1f5f9; font-size: 13px; line-height: 1.4;")
        
        bubble_layout.addWidget(sender_label)
        bubble_layout.addWidget(text_label)
        self.layout.addWidget(bubble)
        
        self.eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.eff)
        self.anim = QPropertyAnimation(self.eff, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

class TerminalWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.output = QTextEdit()
        self.output.setStyleSheet("background-color: #020617; color: #10b981; font-family: 'Consolas'; font-size: 13px; padding: 10px; border: none;")
        self.output.setPlaceholderText("CMD Ready. Digite e pressione Enter.")
        layout.addWidget(self.output)
        self.process = None
        self.output.installEventFilter(self)
        self.current_cwd = os.getcwd()

    def eventFilter(self, obj, event):
        if obj == self.output and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.run_command_from_input()
                return True
        return super().eventFilter(obj, event)

    def run_command_from_input(self):
        cursor = self.output.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        cmd = cursor.selectedText().strip()
        if not cmd:
            text = self.output.toPlainText()
            lines = text.split('\n')
            if lines: cmd = lines[-1].strip()
        
        self.output.moveCursor(cursor.MoveOperation.End)
        self.output.insertPlainText("\n")
        if not cmd: return

        self.output.insertPlainText(f"> {cmd}\n")
        thread = ExecutionThread(cmd, self.current_cwd)
        thread.output_ready.connect(lambda l: self.output.insertPlainText(l))
        thread.finished_execution.connect(lambda c: self.output.insertPlainText(f"\nExit: {c}\n> "))
        thread.start()
        self.last_thread = thread

class ChatInput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Digite sua pergunta... (Ctrl+V para colar)")
        self.setStyleSheet("background-color: #0f172a; border-radius: 6px; padding: 8px; border: 1px solid #334155;")

    def keyPressEvent(self, e: QKeyEvent):
        # Implement Ctrl+V for paste (images/files) logic here if needed beyond default textual paste
        if e.matches(QKeySequence.StandardKey.Paste):
             mime = QApplication.clipboard().mimeData()
             if mime.hasImage():
                 # For now, just notifying user. Proper image handling requires complex chat bubble update.
                 # self.parent().parent().add_system_message("Imagem colada (preview não implementado na alpha).")
                 pass
        super().keyPressEvent(e)

class MainWindowV3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AI Code Assistant - 0.3.6")
        self.setGeometry(100, 100, 1400, 900)
        self.current_file_path = None
        
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; color: #f8fafc; }
            QMenuBar { background-color: #1e293b; color: #cbd5e1; }
            QMenuBar::item { padding: 5px 10px; background: transparent; }
            QMenuBar::item:selected { background-color: #334155; }
            QMenu { background-color: #1e293b; border: 1px solid #334155; }
            QMenu::item { padding: 5px 20px; }
            QMenu::item:selected { background-color: #0ea5e9; }
            QSplitter::handle { background-color: #1e293b; width: 2px; }
            QScrollBar:vertical { background: #0f172a; width: 12px; border: none; }
            QScrollBar::handle:vertical { background: #334155; min-height: 20px; border-radius: 6px; }
            QTabWidget::pane { border: 0; background-color: #0f172a; }
            QTabBar::tab { background: #1e293b; color: #94a3b8; padding: 8px 20px; border-right: 1px solid #0f172a; margin-right: 1px; }
            QTabBar::tab:selected { background: #0f172a; color: #38bdf8; border-top: 2px solid #38bdf8; }
            QTreeView { background-color: #020617; border: none; color: #cbd5e1; outline: 0; }
            QTreeView::item:selected { background-color: #0ea5e9; color: white; }
            QTextEdit { background-color: #0f172a; color: #f1f5f9; border: none; font-family: 'Consolas', monospace; }
        """)
        
        self.setup_menus()
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Activity Bar
        self.activity_bar = ActivityBar(callback=self.switch_sidebar_view)
        main_layout.addWidget(self.activity_bar)
        
        # 2. Sidebar
        self.sidebar = QStackedWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("background-color: #020617; border-right: 1px solid #1e293b;")
        
        # Explorer
        self.explorer_widget = QWidget()
        exp_layout = QVBoxLayout(self.explorer_widget)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        lb_exp = QLabel("  EXPLORER")
        lb_exp.setFixedHeight(35)
        lb_exp.setStyleSheet("font-weight: bold; color: #94a3b8; background-color: #0f172a; border-bottom: 1px solid #1e293b;")
        exp_layout.addWidget(lb_exp)
        
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_tree.setModel(self.file_model)
        self.file_tree.setHeaderHidden(True)
        for i in range(1, 4): self.file_tree.setColumnHidden(i, True)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_tree.doubleClicked.connect(self.open_file)
        exp_layout.addWidget(self.file_tree)
        self.sidebar.addWidget(self.explorer_widget)
        
        # Placeholders
        for i, name in enumerate(["Busca", "Extensões", "Debug", "Lab", "Config"]):
             w = QLabel(f"\n\n  area: {name}\n  (Em breve)")
             w.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
             w.setStyleSheet("color: #64748b; font-size: 14px;")
             self.sidebar.addWidget(w)
        main_layout.addWidget(self.sidebar)
        
        # 3. Middle Area
        self.main_split = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_split)
        
        center_widget = QWidget()
        c_layout = QVBoxLayout(center_widget)
        c_layout.setContentsMargins(0, 0, 0, 0)
        self.center_split = QSplitter(Qt.Orientation.Vertical)
        c_layout.addWidget(self.center_split)
        
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.center_split.addWidget(self.editor_tabs)
        
        self.term_container = QWidget()
        t_layout = QVBoxLayout(self.term_container)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_header = QFrame()
        t_header.setFixedHeight(30)
        t_header.setStyleSheet("background-color: #1e293b; border-top: 1px solid #334155;")
        th_layout = QHBoxLayout(t_header)
        th_layout.setContentsMargins(10, 0, 10, 0)
        th_layout.addWidget(QLabel("TERMINAL", styleSheet="font-weight:bold; color:#7dd3fc;"))
        self.term_combo = QComboBox()
        self.term_combo.addItems(["CMD", "PowerShell", "Bash"])
        self.term_combo.setFixedWidth(100)
        th_layout.addWidget(self.term_combo)
        th_layout.addStretch()
        self.btn_term_toggle = QToolButton()
        self.btn_term_toggle.setText("▼")
        self.btn_term_toggle.clicked.connect(self.toggle_terminal)
        self.btn_term_toggle.setStyleSheet("border:none; color:#cbd5e1;")
        th_layout.addWidget(self.btn_term_toggle)
        t_layout.addWidget(t_header)
        self.terminal_widget = TerminalWidget()
        t_layout.addWidget(self.terminal_widget)
        self.center_split.addWidget(self.term_container)
        self.center_split.setSizes([700, 250])
        self.main_split.addWidget(center_widget)
        
        # 4. Right Panel (Chat)
        self.right_panel = QWidget()
        self.right_panel.setMinimumWidth(50) 
        r_layout = QVBoxLayout(self.right_panel)
        r_layout.setContentsMargins(0, 0, 0, 0)
        
        r_header = QFrame()
        r_header.setFixedHeight(40)
        r_header.setStyleSheet("background-color: #1e293b; border-left: 1px solid #334155;")
        rh_layout = QHBoxLayout(r_header)
        rh_layout.setContentsMargins(5, 0, 5, 0)
        
        self.btn_chat_collapse = QPushButton("▶")
        self.btn_chat_collapse.setFixedWidth(25)
        self.btn_chat_collapse.setStyleSheet("border:none; color:#38bdf8;")
        self.btn_chat_collapse.clicked.connect(self.toggle_chat)
        rh_layout.addWidget(self.btn_chat_collapse)
        
        self.chat_tools_widget = QWidget()
        ctl = QHBoxLayout(self.chat_tools_widget)
        ctl.setContentsMargins(0,0,0,0)
        
        # Chat Buttons restored
        btn_new_chat = QPushButton("＋ Novo Chat")
        btn_new_chat.setStyleSheet("background:transparent; color:#38bdf8; font-weight:bold;")
        ctl.addWidget(btn_new_chat)
        
        btn_login = QPushButton("Entrar")
        btn_login.setStyleSheet("background:#0f172a; color:white; border:1px solid #334155; border-radius:4px; padding:2px 8px;")
        ctl.addWidget(btn_login)
        
        ctl.addStretch()
        
        self.ai_select = QComboBox()
        self.ai_select.addItems(["DeepSeek", "GPT-4", "Claude"])
        self.ai_select.setFixedWidth(80)
        ctl.addWidget(self.ai_select)
        
        rh_layout.addWidget(self.chat_tools_widget)
        r_layout.addWidget(r_header)
        
        # Collapsed View (Vertical Toolbar)
        self.collapsed_widget = QWidget()
        self.collapsed_widget.setVisible(False)
        cvl = QVBoxLayout(self.collapsed_widget)
        cvl.setContentsMargins(0,5,0,0)
        btn_expand = QPushButton("◀")
        btn_expand.setStyleSheet("border:none; color:#38bdf8; font-size:16px;")
        btn_expand.clicked.connect(self.toggle_chat)
        cvl.addWidget(btn_expand)
        cvl.addWidget(QLabel("C\nH\nA\nT", styleSheet="color:#94a3b8; font-weight:bold; font-size:10px;", alignment=Qt.AlignmentFlag.AlignHCenter))
        cvl.addStretch()
        r_layout.addWidget(self.collapsed_widget)
        
        # Chat Content
        self.chat_container = QWidget()
        chat_full_layout = QVBoxLayout(self.chat_container)
        chat_full_layout.setContentsMargins(0,0,0,0)
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("border:none; border-left: 1px solid #1e293b;")
        self.chat_messages_widget = QWidget()
        self.chat_v_layout = QVBoxLayout(self.chat_messages_widget)
        self.chat_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_messages_widget)
        chat_full_layout.addWidget(self.chat_scroll)
        
        # Input Area
        self.input_frame = QFrame()
        self.input_frame.setFixedHeight(140)
        self.input_frame.setStyleSheet("border-top: 1px solid #334155; background-color: #1e293b;")
        if_layout = QVBoxLayout(self.input_frame)
        self.chat_input = ChatInput()
        if_layout.addWidget(self.chat_input)
        
        btn_box = QHBoxLayout()
        btn_attach = QPushButton("📎 Anexar")
        btn_attach.setStyleSheet("color:#cbd5e1; background:transparent;")
        btn_attach.clicked.connect(self.attach_file)
        btn_box.addWidget(btn_attach)
        btn_box.addStretch()
        btn_send = QPushButton("Enviar")
        btn_send.setStyleSheet("background-color: #0ea5e9; color: white; font-weight: bold; border-radius: 4px; padding: 5px 15px;")
        btn_send.clicked.connect(self.handle_send)
        btn_box.addWidget(btn_send)
        if_layout.addLayout(btn_box)
        chat_full_layout.addWidget(self.input_frame)
        
        r_layout.addWidget(self.chat_container)
        self.main_split.addWidget(self.right_panel)
        self.main_split.setSizes([800, 350])
        
        # Footer
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold;")
        self.status.addPermanentWidget(QLabel("0.3.6-14012026-alpha_windows @S.V.S CODE.AI - Try Technology  "))

        self.add_message("🤖 Assistente", "Olá! Sou seu assistente de código. Como posso ajudar hoje?")
        self.load_templates()

    def setup_menus(self):
        menubar = self.menuBar()
        
        # Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        new_act = QAction("Novo Arquivo", self)
        new_act.setShortcut("Ctrl+N")
        new_act.triggered.connect(self.new_file)
        file_menu.addAction(new_act)
        
        open_act = QAction("Abrir Pasta...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.open_project)
        file_menu.addAction(open_act)
        
        save_act = QAction("Salvar", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.save_file)
        file_menu.addAction(save_act)
        
        file_menu.addSeparator()
        
        exit_act = QAction("Sair", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Executar
        run_menu = menubar.addMenu("Executar")
        
        run_act = QAction("Rodar Código", self)
        run_act.setShortcut("F5")
        run_act.triggered.connect(self.run_code)
        run_menu.addAction(run_act)
        
        # Menu Visualizar
        view_menu = menubar.addMenu("Visualizar")
        
        self.view_term_act = QAction("Terminal", self, checkable=True)
        self.view_term_act.setChecked(True)
        self.view_term_act.triggered.connect(self.toggle_terminal_from_menu)
        view_menu.addAction(self.view_term_act)
        
        self.view_chat_act = QAction("Chat IA", self, checkable=True)
        self.view_chat_act.setChecked(True)
        self.view_chat_act.triggered.connect(self.toggle_chat_from_menu)
        view_menu.addAction(self.view_chat_act)

        # Ajuda
        help_menu = menubar.addMenu("Ajuda")
        
        about_act = QAction("Sobre", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

    def attach_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Anexar Arquivo")
        if f:
            self.chat_input.insertPlainText(f"\n[Anexo: {os.path.basename(f)}]")

    def switch_sidebar_view(self, index):
        self.sidebar.setCurrentIndex(index)
        
    # ... (métodos de contexto e file operations mantidos igual) ...

    def show_context_menu(self, pos):
        index = self.file_tree.indexAt(pos)
        menu = QMenu()
        new_file = menu.addAction("➕ Novo Arquivo")
        new_folder = menu.addAction("📁 Nova Pasta")
        menu.addSeparator()
        rename = menu.addAction("✏ Renomear")
        delete = menu.addAction("🗑 Excluir")
        action = menu.exec(self.file_tree.viewport().mapToGlobal(pos))
        path = self.file_model.filePath(index) if index.isValid() else self.file_model.rootPath()
        if os.path.isfile(path): parent_dir = os.path.dirname(path)
        else: parent_dir = path
            
        if action == new_file:
            name, ok = QInputDialog.getText(self, "Novo Arquivo", "Nome:")
            if ok and name: open(os.path.join(parent_dir, name), 'w').close()
        elif action == new_folder:
            name, ok = QInputDialog.getText(self, "Nova Pasta", "Nome:")
            if ok and name: os.makedirs(os.path.join(parent_dir, name), exist_ok=True)
        elif action == rename and index.isValid():
            name, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=self.file_model.fileName(index))
            if ok and name: os.rename(self.file_model.filePath(index), os.path.join(os.path.dirname(self.file_model.filePath(index)), name))
        elif action == delete and index.isValid():
             if QMessageBox.question(self, "Excluir", "Confirmar?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                 p = self.file_model.filePath(index)
                 shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    def new_file(self): self.add_editor_tab("Untitled", "", None)
    def save_file(self):
        curr = self.editor_tabs.currentWidget()
        if not curr: return
        idx = self.editor_tabs.currentIndex()
        path = self.editor_tabs.tabToolTip(idx)
        if not path or path == "None" or not os.path.exists(os.path.dirname(path)):
            fname, _ = QFileDialog.getSaveFileName(self, "Salvar")
            if not fname: return
            path = fname
            self.editor_tabs.setTabToolTip(idx, path)
            self.editor_tabs.setTabText(idx, os.path.basename(path))
        with open(path, 'w', encoding='utf-8') as f: f.write(curr.toPlainText())
        self.status.showMessage(f"Salvo: {path}", 3000)

    def load_templates(self):
        self.add_editor_tab("main.py", "print('Ola Mundo Python!')", "template_py")
        self.add_editor_tab("script.lua", "print('Ola Mundo Lua!')", "template_lua")

    def add_editor_tab(self, name, content, path):
        ed = QTextEdit()
        ed.setText(content)
        CodeHighlighter(ed.document(), name)
        idx = self.editor_tabs.addTab(ed, name)
        self.editor_tabs.setTabToolTip(idx, str(path))
        self.editor_tabs.setCurrentIndex(idx)

    def close_tab(self, i): self.editor_tabs.removeTab(i)
    def open_file(self, idx):
        path = self.file_model.filePath(idx)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f: self.add_editor_tab(os.path.basename(path), f.read(), path)

    def run_code(self):
        curr = self.editor_tabs.currentWidget()
        if not curr: return
        name = self.editor_tabs.tabText(self.editor_tabs.currentIndex())
        content = curr.toPlainText()
        self.terminal_widget.output.append(f"\n> Rodando {name}...")
        ext = os.path.splitext(name)[1].lower()
        cmd = ""
        
        # Verificações de PATH robustas
        if ext == ".py": cmd = f'"{sys.executable}"'
        elif ext == ".js": cmd = "node"
        elif ext == ".lua": 
            if shutil.which("lua"): cmd = "lua"
            else: self.terminal_widget.output.append("> Erro: Lua não encontrado no PATH.\n"); return
            
        if not cmd:
            self.terminal_widget.output.append("> Linguagem não configurada.\n")
            return
            
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode='w', encoding='utf-8') as tf:
            tf.write(content)
            tname = tf.name
        thread = ExecutionThread(f"{cmd} \"{tname}\"", os.getcwd())
        thread.output_ready.connect(lambda l: self.terminal_widget.output.insertPlainText(l))
        thread.finished_execution.connect(lambda c: self.on_exec_finished(c, tname))
        thread.start()
        self.last_exec_thread = thread

    def on_exec_finished(self, code, temp_name):
        self.terminal_widget.output.append(f"\n> Fim da execução. Código: {code}")
        try: os.unlink(temp_name)
        except: pass

    def handle_send(self):
        txt = self.chat_input.toPlainText().strip()
        if txt:
            self.add_message("👤 Você", txt, is_user=True)
            self.chat_input.clear()
            self.add_message("🤖 Assistente", "Processando...")

    def add_message(self, s, t, is_user=False):
        msg = ChatMessage(s, t, is_user)
        self.chat_v_layout.addWidget(msg)
        QApplication.processEvents()
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def toggle_terminal(self):
        # Toggle disparado pelo botão na GUI
        visible = not self.term_container.isVisible()
        self.term_container.setVisible(visible)
        self.btn_term_toggle.setText("▼" if visible else "▲")
        self.view_term_act.setChecked(visible)

    def toggle_terminal_from_menu(self):
        # Toggle disparado pelo menu (usa o estado do checkbox)
        visible = self.view_term_act.isChecked()
        self.term_container.setVisible(visible)
        self.btn_term_toggle.setText("▼" if visible else "▲")

    def toggle_chat(self):
        # Lógica original de colapso, ajustada para menu
        if self.chat_container.isVisible():
            # Recolher
            self.chat_container.hide()
            self.chat_tools_widget.hide() 
            self.collapsed_widget.show()
            self.right_panel.setFixedWidth(40)
            self.view_chat_act.setChecked(False) # Consideramos 'Recolhido' como 'Não visível' no menu? Ou criamos estado 'Recolhido'?
            # Se o usuário desmarcar "Chat IA" no menu, o chat deve sumir totalmente ou ficar recolhido?
            # Geralmente "Visualizar -> Chat" controla a existência do PAINEL DIREITO inteiro.
            # O botão de "colapso" é um estado interno de largura.
            # Vamos assumir que o menu "Visualizar -> Chat" esconde/mostra o right_panel inteiro.
        else:
            # Expandir
            self.chat_container.show()
            self.chat_tools_widget.show()
            self.collapsed_widget.hide()
            self.right_panel.setMinimumWidth(300)
            self.right_panel.setMaximumWidth(16777215)
            self.main_split.setSizes([800, 350])
            self.view_chat_act.setChecked(True)

    def toggle_chat_from_menu(self):
        visible = self.view_chat_act.isChecked()
        self.right_panel.setVisible(visible)
        # Se tornar visivel via menu, garantir que está expandido ou no último estado
        if visible and not self.chat_container.isVisible():
             # Força expansão ao reativar via menu para não ficar só a barra fina confusa
             self.toggle_chat()

    def show_about(self):
        AboutDialog(self).exec()

    def open_project(self):
        d = QFileDialog.getExistingDirectory(self, "Selecionar Projeto")
        if d:
            self.file_model.setRootPath(d)
            self.file_tree.setRootIndex(self.file_model.index(d))

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_F5:
            self.run_code()
        super().keyPressEvent(e)