from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTreeView, QTextEdit, QLineEdit, 
                             QPushButton, QToolBar, QStatusBar, QFrame, QLabel, 
                             QTabWidget, QScrollArea, QComboBox, QSizePolicy, 
                             QToolButton, QDialog, QGraphicsOpacityEffect, QMenu,
                             QMenuBar, QStackedWidget, QInputDialog, QMessageBox,
                             QFileDialog, QApplication, QListWidget, QListWidgetItem)
from PyQt6.QtCore import (Qt, QSize, QDir, QRect, QPropertyAnimation, 
                          QEasingCurve, QSequentialAnimationGroup, QThread, 
                          pyqtSignal, QProcess, QEvent, QStandardPaths, QTimer)
from PyQt6.QtGui import (QIcon, QFont, QColor, QPalette, QFileSystemModel, 
                         QSyntaxHighlighter, QTextCharFormat, QAction, QKeyEvent,
                         QCursor, QPixmap, QImage, QKeySequence, QShortcut, QTextCursor)

import os
import sys
import subprocess
import tempfile
import shutil
import json
import re
from pathlib import Path
from datetime import datetime

# AI Integration - Novos componentes otimizados
from ..core import AIManager, TokenOptimizer, CustomAIManager, TrainingManager
from .dialogs import CreateAIDialog, ManageAIDialog, TrainingDialog

# Pygments for syntax highlighting
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
    from pygments.token import Token
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


def markdown_to_html(text):
    """Converte markdown básico para HTML para exibição nos balões de chat."""
    # Escapar HTML existente
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Cabeçalhos ## e ###
    text = re.sub(r'^### (.+)$', r'<b style="font-size:14px;">\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<b style="font-size:15px;">\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<b style="font-size:16px;">\1</b>', text, flags=re.MULTILINE)
    
    # Negrito **texto**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    
    # Itálico *texto*
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    
    # Código inline `texto`
    text = re.sub(r'`([^`]+)`', r'<code style="background:#2d333b; padding:1px 4px; border-radius:3px; font-family:Consolas;">\1</code>', text)
    
    # Listas com bullet •
    text = re.sub(r'^[•\-\*] (.+)$', r'&nbsp;&nbsp;• \1', text, flags=re.MULTILINE)
    
    # Quebras de linha
    text = text.replace("\n", "<br>")
    
    return text


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
            import os
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                env=env,
                bufsize=0
            )
            buffer = bytearray()
            while True:
                char = process.stdout.read(1)
                if not char and process.poll() is not None:
                    if buffer:
                        self.output_ready.emit(buffer.decode('utf-8', errors='replace'))
                    break
                if char:
                    buffer.extend(char)
                    if char in (b'\n', b'\r') or len(buffer) > 100:
                        self.output_ready.emit(buffer.decode('utf-8', errors='replace'))
                        buffer.clear()
                        
            process.wait()
            self.finished_execution.emit(process.returncode)
        except Exception as e:
            self.output_ready.emit(f"Erro na execução: {e}\n")
            self.finished_execution.emit(-1)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre")
        self.setFixedSize(450, 520)
        self.setStyleSheet("background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px;")
        layout = QVBoxLayout(self)
        title = QLabel("AI Code Assistant")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #58a6ff;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("v0.4.11-rev1.2.3-220426 | homologacao"), alignment=Qt.AlignmentFlag.AlignCenter)
        
        info = QLabel(
            "Developer: Samuel V. Silva\n"
            "Brand: @S.V.S - Try Technology\n\n"
            "Produtividade e IA.\n\n"
            "✨ Novidades v0.4.11 (Rev 1.2.3):\n"
            "• 🤖 Richie AI — IA Nativa com Chat Funcional (Offline)\n"
            "• 🖥️ Terminal Interativo com ComboBox (bash/cmd/ps/node)\n"
            "• 📋 Sessões de Chat com Histórico Persistente\n"
            "• 🔐 Sistema de Permissões para Ações na Máquina\n"
            "• 📊 Planos de Atuação com Aprovação do Usuário\n"
            "• 📊 Benchmarks na Loja de Extensões\n"
            "• 💾 Indicador * de Modificações Não Salvas\n"
            "• 🔍 Startup Check 18+ Linguagens\n"
            "• 🔧 Correção de Dependências no Build\n"
            "• Sidebar Toggle Animado (Recolher/Expandir)\n"
            "• Comandos Reais para Todas as Extensões\n"
            "• Execução via F5 no Terminal Integrado\n"
            "• Import BotForge Web Inteligente\n"
            "• Explorer padrão em Documentos"
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-size: 12px; color: #8b949e;")
        layout.addWidget(info)
        layout.addStretch()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #1f6feb; padding: 8px; border-radius: 4px; border: none; color: white;")
        layout.addWidget(close_btn)

class ActivityBar(QFrame):
    """Activity Bar vertical estilo v0.3.5-alpha com icones coloridos e toggle de sidebar"""
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setFixedWidth(48)
        self.setStyleSheet("background-color: #0d1117;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 8, 0, 8)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.callback = callback
        self.buttons = []
        self._active_index = 0
        self._colors = []
        
        self.add_action("📁", "Explorer — Clique para expandir/recolher", 0, "#e8a427")
        self.add_action("🧩", "Extensões — Clique para expandir/recolher", 1, "#66bb6a")
        self.add_action("💬", "Chat — Clique para expandir/recolher", 2, "#4fc3f7")
        self.add_action("🐞", "Debug — Clique para expandir/recolher", 3, "#ef5350")
        self.add_action("🧪", "Lab — Clique para expandir/recolher", 4, "#ab47bc")
        
        self.layout.addStretch()
        self.add_action("🤖", "IAs — Clique para expandir/recolher", 5, "#ff7043")
        self.add_action("⚙️", "Configurações — Clique para expandir/recolher", 6, "#78909c")
        
        if self.buttons:
            self.buttons[0].setStyleSheet(self._active_style("#e8a427"))

    def add_action(self, icon_text, tooltip, index, color="#858585"):
        btn = QToolButton()
        btn.setText(icon_text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(48, 42)
        btn.setStyleSheet(f"""
            QToolButton {{ color: {color}; font-size: 20px; border: none; background: transparent; }}
            QToolButton:hover {{ background-color: #333333; border-left: 2px solid {color}; }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.callback:
            btn.clicked.connect(lambda checked, i=index, c=color: self._on_click(i, c))
        self.layout.addWidget(btn)
        self.buttons.append(btn)
        self._colors.append(color)
    
    def _on_click(self, index, color):
        if self.callback:
            self.callback(index)
        for i, b in enumerate(self.buttons):
            if i < len(self._colors):
                c = self._colors[i]
                b.setStyleSheet(f"""
                    QToolButton {{ color: {c}; font-size: 20px; border: none; background: transparent; }}
                    QToolButton:hover {{ background-color: #333333; border-left: 2px solid {c}; }}
                """)
        if index < len(self.buttons):
            self.buttons[index].setStyleSheet(self._active_style(color))
        self._active_index = index
    
    def _active_style(self, color):
        return f"QToolButton {{ color: {color}; font-size: 20px; border: none; background-color: #333333; border-left: 2px solid {color}; }}"


class ChatMessage(QFrame):
    action_clicked = pyqtSignal(str)

    def __init__(self, sender, text, is_user=False, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        align = Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft
        self.layout.setAlignment(align)
        
        self.bubble = QWidget()
        self.bubble_layout = QVBoxLayout(self.bubble)
        self.bubble_layout.setContentsMargins(10, 8, 10, 8)
        self.bubble_layout.setSpacing(4)
        bg_color = "#1f6feb" if is_user else "#21262d"
        self.bubble.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px; border: 1px solid #30363d;")
        self.bubble.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        sender_label = QLabel(sender)
        sender_label.setStyleSheet(f"font-weight: bold; color: {'#7dd3fc' if is_user else '#c9d1d9'}; font-size: 10px;")
        
        self.text_label = QLabel()
        self.text_label.setTextFormat(Qt.TextFormat.RichText)
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.text_label.setStyleSheet("color: #f0f6fc; font-size: 12px; line-height: 1.3; background: transparent; border: none;")
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.actions_container = QWidget()
        self.actions_layout = QVBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(0, 5, 0, 0)
        self.actions_layout.setSpacing(5)
        self.actions_container.setVisible(False)
        self.actions_container.setStyleSheet("background: transparent;")

        self.bubble_layout.addWidget(sender_label)
        self.bubble_layout.addWidget(self.text_label)
        self.bubble_layout.addWidget(self.actions_container)
        
        self.layout.addWidget(self.bubble)
        
        self.eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.eff)
        self.anim = QPropertyAnimation(self.eff, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

        self.update_text(text)

    def update_text(self, new_text):
        """Atualiza o texto do balão (usado para streaming de IA)."""
        import re, json
        # Buscar por tags <!--ACTIONS: [...]-->
        match = re.search(r"<!--ACTIONS:\s*(\[.*?\])\s*-->", new_text)
        actions = []
        if match:
            try:
                actions = json.loads(match.group(1))
                new_text = new_text.replace(match.group(0), "").strip()
            except:
                pass

        html_text = markdown_to_html(new_text)
        self.text_label.setText(html_text)

        # Atualizar botões
        # Limpar botões antigos
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if actions:
            self.actions_container.setVisible(True)
            for action in actions:
                btn = QPushButton(action)
                btn.setStyleSheet("QPushButton { background-color: #238636; color: white; border: 1px solid #2ea043; border-radius: 4px; padding: 4px 8px; font-weight: bold; } QPushButton:hover { background-color: #2ea043; }")
                if "Negado" in action or "❌" in action:
                    btn.setStyleSheet("QPushButton { background-color: #da3633; color: white; border: 1px solid #f85149; border-radius: 4px; padding: 4px 8px; font-weight: bold; } QPushButton:hover { background-color: #f85149; }")
                elif "Sempre" in action or "🔄" in action:
                    btn.setStyleSheet("QPushButton { background-color: #1f6feb; color: white; border: 1px solid #388bfd; border-radius: 4px; padding: 4px 8px; font-weight: bold; } QPushButton:hover { background-color: #388bfd; }")
                
                btn.clicked.connect(lambda checked, a=action: self.action_clicked.emit(a))
                self.actions_layout.addWidget(btn)
            self.actions_layout.addStretch()
        else:
            self.actions_container.setVisible(False)


class ChatHistoryPanel(QWidget):
    """Painel de histórico de conversas para a sidebar com persistência JSON."""
    
    session_selected = pyqtSignal(str)  # Emite session_id ao clicar
    new_chat_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation) or tempfile.gettempdir(),
            "ai_code_assistant", "chat_sessions"
        )
        os.makedirs(self._sessions_dir, exist_ok=True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(35)
        header.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 5, 0)
        
        lb = QLabel("HISTÓRICO DE CHAT")
        lb.setStyleSheet("font-weight: bold; color: #8b949e; font-size: 11px;")
        h_layout.addWidget(lb)
        h_layout.addStretch()
        
        btn_new = QToolButton()
        btn_new.setText("+ Nova")
        btn_new.setToolTip("Nova Conversa")
        btn_new.setStyleSheet("color: #4fc3f7; background: transparent; border: none; font-weight: bold; font-size: 11px;")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self.new_chat_requested.emit)
        h_layout.addWidget(btn_new)
        
        layout.addWidget(header)
        
        # Lista de sessões com scroll
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                background-color: #161b22;
                border: none;
                color: #c9d1d9;
                font-size: 12px;
                outline: 0;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #21262d;
            }
            QListWidget::item:selected {
                background-color: #1f6feb;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #30363d;
            }
            QScrollBar:vertical {
                background: #0d1117;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #30363d;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.session_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.session_list)
        
        # Carregar sessões existentes
        self._load_session_list()
    
    def _get_sessions_index_path(self):
        return os.path.join(self._sessions_dir, "sessions_index.json")
    
    def _load_session_list(self):
        """Carrega a lista de sessões do disco."""
        self.session_list.clear()
        index_path = self._get_sessions_index_path()
        if not os.path.exists(index_path):
            return
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            
            # Ordenar por data (mais recente primeiro)
            sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
            
            for session in sessions:
                title = session.get("title", "Conversa sem título")
                date_str = session.get("updated_at", "")
                session_id = session.get("id", "")
                
                # Formatar data amigável
                try:
                    dt = datetime.fromisoformat(date_str)
                    friendly_date = dt.strftime("%d/%m %H:%M")
                except:
                    friendly_date = ""
                
                display = f"{title}\n{friendly_date}" if friendly_date else title
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, session_id)
                item.setToolTip(f"Sessão: {session_id}\n{date_str}")
                self.session_list.addItem(item)
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    def _on_item_clicked(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if session_id:
            self.session_selected.emit(session_id)
    
    def save_session(self, session_id, title, messages):
        """Salva uma sessão de chat no disco."""
        # Salvar mensagens da sessão
        session_file = os.path.join(self._sessions_dir, f"{session_id}.json")
        session_data = {
            "id": session_id,
            "title": title,
            "messages": messages,
            "updated_at": datetime.now().isoformat()
        }
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar sessão: {e}")
            return
        
        # Atualizar índice
        index_path = self._get_sessions_index_path()
        sessions = []
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
            except:
                sessions = []
        
        # Atualizar ou adicionar
        found = False
        for s in sessions:
            if s.get("id") == session_id:
                s["title"] = title
                s["updated_at"] = datetime.now().isoformat()
                found = True
                break
        if not found:
            sessions.append({
                "id": session_id,
                "title": title,
                "updated_at": datetime.now().isoformat()
            })
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar índice: {e}")
        
        self._load_session_list()
    
    def load_session(self, session_id):
        """Carrega mensagens de uma sessão."""
        session_file = os.path.join(self._sessions_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            return None
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def delete_session(self, session_id):
        """Remove uma sessão do disco."""
        session_file = os.path.join(self._sessions_dir, f"{session_id}.json")
        try:
            os.remove(session_file)
        except:
            pass
        
        index_path = self._get_sessions_index_path()
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
                sessions = [s for s in sessions if s.get("id") != session_id]
                with open(index_path, 'w', encoding='utf-8') as f:
                    json.dump(sessions, f, ensure_ascii=False, indent=2)
            except:
                pass
        self._load_session_list()


class InteractiveTerminalWidget(QWidget):
    """Terminal Interativo usando QProcess — suporta stdin/stdout em tempo real."""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.output = QTextEdit()
        self.output.setStyleSheet(
            "background-color: #0d1117; color: #58a6ff; font-family: 'Consolas'; "
            "font-size: 13px; padding: 10px; border: none;"
        )
        self.output.setPlaceholderText("Terminal Pronto. Pressione F5 para executar o script atual.")
        self.output.setReadOnly(False)
        layout.addWidget(self.output)
        
        self.process = None
        self._script_process = None
        self.current_cwd = os.getcwd()
        self._active_shell = "cmd"
        self._input_start_pos = 0
        self._waiting_input = False
        self.last_thread = None
        
        self.output.installEventFilter(self)

    def set_shell(self, shell_name):
        shell_map = {
            "cmd": "cmd",
            "powershell": "powershell",
            "bash": "bash",
            "node": "node",
            "python": "python"
        }
        self._active_shell = shell_map.get(shell_name.lower(), "cmd")

    def get_shell_command(self):
        if sys.platform == "win32":
            shell_map = {
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "bash": "bash.exe",
                "node": "node.exe",
                "python": sys.executable
            }
        else:
            shell_map = {
                "cmd": "/bin/sh",
                "powershell": "pwsh",
                "bash": "/bin/bash",
                "node": "node",
                "python": "python3"
            }
        return shell_map.get(self._active_shell, "cmd.exe" if sys.platform == "win32" else "/bin/sh")

    def eventFilter(self, obj, event):
        if obj == self.output and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            
            if self._script_process and self._script_process.state() == QProcess.ProcessState.Running:
                if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                    self._send_input_to_process()
                    return True
                return False
            
            if key == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self._run_terminal_command()
                return True
        return super().eventFilter(obj, event)

    def _send_input_to_process(self):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText().strip()
        
        for prefix in ["> ", ">>> ", "... ", "$ ", "PS> ", "# "]:
            if line_text.startswith(prefix):
                line_text = line_text[len(prefix):]
                break
        
        if self._script_process and self._script_process.state() == QProcess.ProcessState.Running:
            data = (line_text + "\n").encode("utf-8")
            self._script_process.write(data)
            self.output.moveCursor(QTextCursor.MoveOperation.End)
            self.output.insertPlainText("\n")

    def _run_terminal_command(self):
        cursor = self.output.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        cmd = cursor.selectedText().strip()
        if not cmd:
            text = self.output.toPlainText()
            lines = text.split('\n')
            if lines: cmd = lines[-1].strip()
        
        for prefix in ["> ", ">>> ", "$ ", "PS> "]:
            if cmd.startswith(prefix):
                cmd = cmd[len(prefix):]
                break
        
        self.output.moveCursor(cursor.MoveOperation.End)
        self.output.insertPlainText("\n")
        if not cmd: return

        self.output.insertPlainText(f"> {cmd}\n")
        thread = ExecutionThread(cmd, self.current_cwd)
        thread.output_ready.connect(lambda l: self.output.insertPlainText(l))
        thread.finished_execution.connect(lambda c: self.output.insertPlainText(f"\nExit: {c}\n> "))
        thread.start()
        self.last_thread = thread

    def run_script_interactive(self, cmd, cwd=None, shell_name=None):
        if shell_name:
            self.set_shell(shell_name)
        
        work_dir = cwd or self.current_cwd
        
        if self._script_process and self._script_process.state() != QProcess.ProcessState.NotRunning:
            self._script_process.kill()
            self._script_process.waitForFinished(1000)
        
        self._script_process = QProcess(self)
        self._script_process.setWorkingDirectory(work_dir)
        
        env = self._script_process.processEnvironment()
        if env.isEmpty():
            from PyQt6.QtCore import QProcessEnvironment
            env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        env.insert("PYTHONIOENCODING", "utf-8")
        self._script_process.setProcessEnvironment(env)
        
        self._script_process.readyReadStandardOutput.connect(self._on_script_stdout)
        self._script_process.readyReadStandardError.connect(self._on_script_stderr)
        self._script_process.finished.connect(self._on_script_finished)
        
        shell_exe = self.get_shell_command()
        
        if sys.platform == "win32":
            if self._active_shell == "cmd":
                self._script_process.startCommand(f"cmd.exe /c {cmd}")
            elif self._active_shell == "powershell":
                self._script_process.startCommand(f"powershell.exe -Command {cmd}")
            elif self._active_shell == "bash":
                self._script_process.startCommand(f"bash.exe -c \"{cmd}\"")
            else:
                self._script_process.startCommand(cmd)
        else:
            if self._active_shell in ("bash", "cmd"):
                self._script_process.startCommand(f"/bin/bash -c \"{cmd}\"")
            elif self._active_shell == "powershell":
                self._script_process.startCommand(f"pwsh -Command {cmd}")
            else:
                self._script_process.startCommand(cmd)
        
        self._waiting_input = True

    def _on_script_stdout(self):
        if self._script_process:
            data = self._script_process.readAllStandardOutput()
            text = bytes(data).decode("utf-8", errors="replace")
            self.output.moveCursor(QTextCursor.MoveOperation.End)
            self.output.insertPlainText(text)
            self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _on_script_stderr(self):
        if self._script_process:
            data = self._script_process.readAllStandardError()
            text = bytes(data).decode("utf-8", errors="replace")
            self.output.moveCursor(QTextCursor.MoveOperation.End)
            self.output.insertPlainText(text)
            self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _on_script_finished(self, exit_code, exit_status):
        self._waiting_input = False
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        status_text = "sucesso" if exit_code == 0 else f"código {exit_code}"
        self.output.insertPlainText(f"\n> Execução finalizada ({status_text}).\n> ")
        
        # Remove temp file se houver
        if hasattr(self, '_temp_script_file') and self._temp_script_file:
            try:
                import os
                if os.path.exists(self._temp_script_file):
                    os.remove(self._temp_script_file)
                self._temp_script_file = None
            except Exception:
                pass


class ChatInput(QTextEdit):
    """Campo de entrada de chat com expansão dinâmica, scroll e acompanhamento de linha."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enviar uma mensagem para IA...")
        self.setStyleSheet("""
            QTextEdit { 
                background-color: transparent; 
                border: none; 
                color: #c9d1d9; 
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.setMinimumHeight(40)
        self.setMaximumHeight(200)
        
        self.textChanged.connect(self.auto_resize)

    def auto_resize(self):
        """Ajusta altura e mantém o cursor visível."""
        doc_height = self.document().size().height()
        new_height = min(max(40, int(doc_height) + 12), 200)
        if self.height() != new_height:
            self.setFixedHeight(new_height)
        # Garantir que o cursor fique visível após redimensionar
        self.ensureCursorVisible()

    def keyPressEvent(self, e: QKeyEvent):
        super().keyPressEvent(e)
        # A cada tecla pressionada, garantir que o cursor esteja visível
        self.ensureCursorVisible()


class AIStreamThread(QThread):
    """Thread para streaming de respostas da IA"""
    chunk_ready = pyqtSignal(str)
    finished_streaming = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_manager, message, context=None):
        super().__init__()
        self.ai_manager = ai_manager
        self.message = message
        self.context = context
        self.system_prompt = None

    def run(self):
        try:
            full_message = self.message
            if self.system_prompt:
                full_message = f"[Sistema: {self.system_prompt}]\n\nUsuario: {self.message}"
            response = self.ai_manager.send_message(full_message, self.context)
            self.chunk_ready.emit(response)
            self.finished_streaming.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindowV3(QMainWindow):
    MAX_CHAT_MESSAGES = 50

    def __init__(self):
        super().__init__()
        self.ai_manager = None
        self.custom_ai_manager = None
        self.training_manager = None
        self.richie = None
        self.ai_thread = None
        self.current_ai_message = None
        self.active_custom_ai = None
        self._message_count = 0
        self._threads = []
        self._sidebar_collapsed = False
        self._active_sidebar_index = 0
        self._sidebar_expanded_width = 220
        self._chat_collapsed = False
        self._richie_active = False
        self._tab_original_content = {}
        
        # Histórico de sessões de chat
        self._current_session_id = None
        self._current_session_messages = []
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AI Code Assistant — v0.4.11-rev1.2.3-220426")
        self.setGeometry(100, 100, 1400, 900)
        self.current_file_path = None
        
        self.f5_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        self.f5_shortcut.activated.connect(self._run_current_script)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117; color: #c9d1d9;
                font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
            }
            QSplitter::handle { background-color: #30363d; width: 1px; }
            QScrollBar:vertical { background: #0d1117; width: 10px; border: none; }
            QScrollBar::handle:vertical {
                background: qlineargradient(y1:0, y2:1, stop:0 #3a3f47, stop:1 #30363d);
                min-height: 20px; border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #58a6ff; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QTabWidget::pane { border: 0; background-color: #0d1117; }
            QTabBar::tab {
                background: #161b22; color: #8b949e; padding: 8px 20px;
                border-right: 1px solid #21262d; margin-right: 1px;
                font-family: 'Segoe UI', sans-serif; font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #1c2128; color: #f0f6fc;
                border-top: 2px solid #58a6ff;
            }
            QTabBar::tab:hover:!selected { background: #1c2128; color: #c9d1d9; }
            QTreeView {
                background-color: #161b22; border: none;
                color: #c9d1d9; outline: 0; font-size: 12px;
            }
            QTreeView::item { padding: 2px 0px; }
            QTreeView::item:selected { background-color: #1f6feb; color: white; }
            QTreeView::item:hover:!selected { background-color: #1c2128; }
            QTextEdit {
                background-color: #0d1117; color: #c9d1d9; border: none;
                font-family: 'Cascadia Code', 'Consolas', 'Fira Code', monospace;
                font-size: 13px;
            }
            QPushButton {
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover { background-color: #30363d; }
            QComboBox {
                font-family: 'Segoe UI', sans-serif;
                border-radius: 4px;
            }
            QComboBox:hover { border: 1px solid #58a6ff; }
            QToolTip {
                background-color: #1c2128; color: #f0f6fc;
                border: 1px solid #30363d; padding: 4px 8px;
                border-radius: 4px; font-size: 11px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)
        
        # === TOP BAR ===
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(42)
        self.top_bar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(0, 0, 10, 0)
        top_layout.setSpacing(0)
        
        btn_open = QPushButton("\U0001f4c2 Abrir Projeto")
        btn_open.setStyleSheet("background-color: transparent; color: #c9d1d9; padding: 5px 12px; border-radius: 6px; font-weight: bold; border: 1px solid transparent;")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(self.open_folder)
        top_layout.addWidget(btn_open)
        
        btn_settings = QPushButton("\u2699\ufe0f Configura\u00e7\u00f5es")
        btn_settings.setStyleSheet("background-color: #21262d; color: #c9d1d9; padding: 5px 12px; border-radius: 6px; border: 1px solid #30363d; margin-left: 8px;")
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.clicked.connect(self._show_settings_dialog)
        top_layout.addWidget(btn_settings)
        
        btn_about = QPushButton("\u2753 Sobre")
        btn_about.setStyleSheet("background-color: #21262d; color: #c9d1d9; padding: 5px 12px; border-radius: 6px; border: 1px solid #30363d; margin-left: 8px;")
        btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_about.clicked.connect(self.show_about)
        top_layout.addWidget(btn_about)
        
        top_layout.addStretch()
        main_v_layout.addWidget(self.top_bar)
        
        # === CONTENT AREA ===
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_v_layout.addWidget(content_widget)
        
        # 1. Activity Bar
        self.activity_bar = ActivityBar(callback=self.switch_sidebar_view)
        main_layout.addWidget(self.activity_bar)
        
        # 2. Sidebar
        self.sidebar = QStackedWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #161b22;")
        
        # Explorer
        self.explorer_widget = QWidget()
        exp_layout = QVBoxLayout(self.explorer_widget)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        
        exp_header = QWidget()
        exp_header.setFixedHeight(35)
        exp_header.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        eh_layout = QHBoxLayout(exp_header)
        eh_layout.setContentsMargins(10, 0, 5, 0)
        
        lb_exp = QLabel("EXPLORER")
        lb_exp.setStyleSheet("font-weight: bold; color: #8b949e; font-size: 11px;")
        eh_layout.addWidget(lb_exp)
        eh_layout.addStretch()
        
        btn_new_f = QToolButton()
        btn_new_f.setText("+📄")
        btn_new_f.setToolTip("Novo Arquivo")
        btn_new_f.setStyleSheet("color: #c9d1d9; background: transparent; border: none;")
        btn_new_f.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_f.clicked.connect(self._explorer_new_file)
        eh_layout.addWidget(btn_new_f)
        
        btn_new_d = QToolButton()
        btn_new_d.setText("+📁")
        btn_new_d.setToolTip("Nova Pasta")
        btn_new_d.setStyleSheet("color: #c9d1d9; background: transparent; border: none;")
        btn_new_d.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_d.clicked.connect(self._explorer_new_folder)
        eh_layout.addWidget(btn_new_d)
        
        btn_refresh = QToolButton()
        btn_refresh.setText("↻")
        btn_refresh.setToolTip("Atualizar")
        btn_refresh.setStyleSheet("color: #c9d1d9; background: transparent; border: none;")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(lambda: self.file_model.setRootPath(self.file_model.rootPath()))
        eh_layout.addWidget(btn_refresh)
        
        exp_layout.addWidget(exp_header)
        
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        docs_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        if not docs_path: docs_path = QDir.rootPath()
        self.file_model.setRootPath(docs_path)
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(docs_path))
        self.file_tree.setHeaderHidden(True)
        for i in range(1, 4): self.file_tree.setColumnHidden(i, True)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_tree.doubleClicked.connect(self.open_file)
        exp_layout.addWidget(self.file_tree)
        self.sidebar.addWidget(self.explorer_widget)
        
        # Extensões View Stack
        self.extensions_stack = QStackedWidget()
        
        self.extensions_page0 = QWidget()
        ext_layout = QVBoxLayout(self.extensions_page0)
        ext_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        lb_ext = QLabel("  EXTENSÕES INSTALADAS / BÁSICAS")
        lb_ext.setFixedHeight(35)
        lb_ext.setStyleSheet("font-weight: bold; color: #8b949e; background-color: #161b22; border-bottom: 1px solid #30363d; font-size: 11px;")
        ext_layout.addWidget(lb_ext)
        btn_store = QPushButton("🛒 Abrir Loja de Extensões")
        btn_store.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 10px; margin: 10px; border-radius: 4px;")
        btn_store.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_store.clicked.connect(lambda ch: self.extensions_stack.setCurrentIndex(1))
        ext_layout.addWidget(btn_store)
        
        lb_desc = QLabel("Selecione uma linguagem rápida c/ Hello World:")
        lb_desc.setStyleSheet("color: #8b949e; padding: 5px 10px; font-size: 11px;")
        ext_layout.addWidget(lb_desc)
        
        langs = [("Python", "py"), ("JavaScript", "js"), ("Java", "java"), 
                 ("Lua", "lua"), ("C#", "cs"), ("HTML", "html"), ("CSS", "css"), 
                 ("Godot Script", "gd")]
        for name, ext in langs:
            row = QHBoxLayout()
            row.setSpacing(0)
            btn = QPushButton(f"  {name} (.{ext})")
            btn.setStyleSheet("text-align: left; padding: 8px; color: #c9d1d9; border: none; border-bottom: 1px solid #30363d;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, e=ext, n=name: self._open_hello_world(n, e))
            
            btn_un = QPushButton("\U0001f5d1️")
            btn_un.setToolTip("Ocultar/Desinstalar nativo")
            btn_un.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_un.setStyleSheet("color: #f85149; background: transparent; padding: 5px; border-bottom: 1px solid #30363d;")
            btn_un.clicked.connect(lambda ch, r=row: [r.itemAt(i).widget().hide() for i in range(r.count()) if r.itemAt(i).widget()])
            
            row.addWidget(btn)
            row.addWidget(btn_un)
            ext_layout.addLayout(row)
        
        self.extensions_stack.addWidget(self.extensions_page0)
        
        from .dialogs.extension_store_sidebar import ExtensionStoreSidebar
        self.store_sidebar = ExtensionStoreSidebar(self)
        self.extensions_stack.addWidget(self.store_sidebar)
        
        self.sidebar.addWidget(self.extensions_stack)
        
        # === SIDEBAR VIEWS: Chat History (index 2), Debug, Lab, IAs, Config (index 3-6) ===
        # Index 2: Chat History Panel (FUNCIONAL)
        self.chat_history_panel = ChatHistoryPanel()
        self.chat_history_panel.session_selected.connect(self._load_chat_session)
        self.chat_history_panel.new_chat_requested.connect(self._clear_chat)
        self.sidebar.addWidget(self.chat_history_panel)
        
        # Placeholders para Debug, Lab, IAs, Config (indices 3-6)
        for name in ["Debug", "Lab", "IAs", "Config"]:
             w = QLabel(f"\n\n  {name}\n  (Em breve)")
             w.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
             w.setStyleSheet("color: #858585; font-size: 13px;")
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
        
        self.btn_new_tab = QToolButton()
        self.btn_new_tab.setText("+")
        self.btn_new_tab.setToolTip("Criar Nova Guia")
        self.btn_new_tab.setStyleSheet("QToolButton { background-color: transparent; color: #c9d1d9; font-weight: bold; font-size: 16px; border: none; padding: 0 10px; } QToolButton:hover { background-color: #21262d; border-radius: 4px; }")
        self.btn_new_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_tab.clicked.connect(self._create_new_file)
        self.editor_tabs.setCornerWidget(self.btn_new_tab, Qt.Corner.TopRightCorner)
        
        self.center_split.addWidget(self.editor_tabs)
        
        # === TERMINAL ===
        self.term_container = QWidget()
        t_layout = QVBoxLayout(self.term_container)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_header = QFrame()
        t_header.setFixedHeight(30)
        t_header.setStyleSheet("background-color: #1c2128; border-top: 1px solid #30363d;")
        th_layout = QHBoxLayout(t_header)
        th_layout.setContentsMargins(10, 0, 10, 0)
        th_layout.addWidget(QLabel("TERMINAL", styleSheet="font-weight:bold; color:#3fb950;"))
        
        self.term_combo = QComboBox()
        self.term_combo.addItems(["cmd", "powershell", "bash", "node", "python"])
        self.term_combo.setFixedWidth(110)
        self.term_combo.setStyleSheet("background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d;")
        self.term_combo.currentTextChanged.connect(self._on_shell_changed)
        th_layout.addWidget(self.term_combo)
        
        self.shell_indicator = QLabel("● cmd")
        self.shell_indicator.setStyleSheet("color: #3fb950; font-size: 11px; margin-left: 8px;")
        th_layout.addWidget(self.shell_indicator)
        
        th_layout.addStretch()
        self.btn_term_toggle = QToolButton()
        self.btn_term_toggle.setText("▼")
        self.btn_term_toggle.clicked.connect(self.toggle_terminal)
        self.btn_term_toggle.setStyleSheet("border:none; color:#cccccc;")
        th_layout.addWidget(self.btn_term_toggle)
        t_layout.addWidget(t_header)
        
        self.terminal_widget = InteractiveTerminalWidget()
        t_layout.addWidget(self.terminal_widget)
        self.center_split.addWidget(self.term_container)
        self.center_split.setSizes([700, 250])
        self.main_split.addWidget(center_widget)
        
        # 4. Right Panel (Chat)
        self.right_panel = QWidget()
        self.right_panel.setMinimumWidth(50) 
        r_layout = QVBoxLayout(self.right_panel)
        r_layout.setContentsMargins(0, 0, 0, 0)
        
        self.r_header = QFrame()
        self.r_header.setFixedHeight(36)
        self.r_header.setStyleSheet("background-color: #1c2128; border-bottom: 1px solid #30363d; border-left: 1px solid #30363d;")
        rh_layout = QHBoxLayout(self.r_header)
        rh_layout.setContentsMargins(5, 0, 5, 0)
        
        self.btn_chat_collapse = QPushButton("▶")
        self.btn_chat_collapse.setFixedWidth(25)
        self.btn_chat_collapse.setStyleSheet("border:none; color:#c9d1d9; font-weight: bold;")
        self.btn_chat_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_chat_collapse.clicked.connect(self.toggle_chat)
        rh_layout.addWidget(self.btn_chat_collapse)
        
        self.chat_tools_widget = QWidget()
        ctl = QHBoxLayout(self.chat_tools_widget)
        ctl.setContentsMargins(0,0,0,0)
        
        btn_new_chat = QPushButton("+ Novo")
        btn_new_chat.setStyleSheet("background:transparent; color:#4fc3f7; font-weight:bold; font-size: 11px;")
        btn_new_chat.clicked.connect(self._clear_chat)
        ctl.addWidget(btn_new_chat)
        
        btn_search = QPushButton("🔍")
        btn_search.setStyleSheet("background:transparent; color:#cccccc; font-size: 14px; border:none;")
        btn_search.setToolTip("Histórico de Conversas")
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search.clicked.connect(self._show_chat_history_dialog)
        ctl.addWidget(btn_search)
        
        btn_login = QPushButton("Entrar")
        btn_login.setStyleSheet("background:#007acc; color:white; border:none; border-radius:4px; padding:4px 12px; font-weight:bold;")
        ctl.addWidget(btn_login)
        
        ctl.addStretch()
        
        self.ai_select = QComboBox()
        self.ai_select.addItems(["DeepSeek", "GPT-4", "Claude"])
        self.ai_select.setMinimumWidth(90)
        self.ai_select.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.ai_select.setStyleSheet("background-color: #2d2d30; color: #cccccc; border: 1px solid #424242; padding: 3px;")
        ctl.addWidget(self.ai_select)
        
        rh_layout.addWidget(self.chat_tools_widget)
        r_layout.addWidget(self.r_header)
        
        # Collapsed View
        self.collapsed_widget = QWidget()
        self.collapsed_widget.setVisible(False)
        self.collapsed_widget.setFixedWidth(35)
        cvl = QVBoxLayout(self.collapsed_widget)
        cvl.setContentsMargins(2,5,2,0)
        self.btn_expand_chat = QPushButton("◀")
        self.btn_expand_chat.setToolTip("Chat")
        self.btn_expand_chat.setStyleSheet("border:none; color:#38bdf8; font-size:16px;")
        self.btn_expand_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_expand_chat.clicked.connect(self.toggle_chat)
        cvl.addWidget(self.btn_expand_chat)
        cvl.addWidget(QLabel("C\nH\nA\nT", styleSheet="color:#94a3b8; font-weight:bold; font-size:10px;", alignment=Qt.AlignmentFlag.AlignHCenter))
        cvl.addStretch()
        r_layout.addWidget(self.collapsed_widget)
        
        # Chat Content
        self.chat_container = QWidget()
        chat_full_layout = QVBoxLayout(self.chat_container)
        chat_full_layout.setContentsMargins(0,0,0,0)
        
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet("""
            QScrollArea { border:none; border-left: 1px solid #1e293b; background: #0d1117; }
            QScrollBar:vertical {
                background: #0d1117;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #30363d;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #484f58;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.chat_messages_widget = QWidget()
        self.chat_messages_widget.setStyleSheet("background: #0d1117;")
        self.chat_messages_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.chat_v_layout = QVBoxLayout(self.chat_messages_widget)
        self.chat_v_layout.setContentsMargins(8, 8, 8, 8)
        self.chat_v_layout.setSpacing(8)
        self.chat_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_messages_widget)
        chat_full_layout.addWidget(self.chat_scroll)
        
        # Input Area
        self.input_frame = QFrame()
        self.input_frame.setMinimumHeight(60)
        self.input_frame.setMaximumHeight(220)
        self.input_frame.setStyleSheet("border-top: 1px solid #30363d; background-color: #161b22;")
        if_ext_layout = QVBoxLayout(self.input_frame)
        if_ext_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.input_inner = QFrame()
        self.input_inner.setMaximumWidth(700)
        self.input_inner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.input_inner.setStyleSheet("background-color: #0d1117; border: 1px solid #30363d; border-radius: 12px;")
        if_inner_layout = QHBoxLayout(self.input_inner)
        if_inner_layout.setContentsMargins(10, 5, 10, 5)
        
        btn_attach = QToolButton()
        btn_attach.setText("📎")
        btn_attach.setToolTip("Anexar Arquivos (Em breve)")
        btn_attach.setStyleSheet("background: transparent; color: #8b949e; border: none; font-size: 16px;")
        btn_attach.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_attach.clicked.connect(self.attach_file)
        if_inner_layout.addWidget(btn_attach)
        
        self.chat_input = ChatInput()
        self.chat_input.textChanged.connect(self._adjust_input_frame_height)
        if_inner_layout.addWidget(self.chat_input)
        
        btn_send = QToolButton()
        btn_send.setText("🚀")
        btn_send.setFixedSize(36, 36)
        btn_send.setStyleSheet("background-color: transparent; color: #58a6ff; font-size: 18px; border: none; border-radius: 8px;")
        btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send.clicked.connect(self.handle_send)
        if_inner_layout.addWidget(btn_send)
        
        if_ext_layout.addWidget(self.input_inner)
        chat_full_layout.addWidget(self.input_frame)
        
        r_layout.addWidget(self.chat_container)
        self.main_split.addWidget(self.right_panel)
        self.main_split.setSizes([800, 350])
        
        # Footer
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("background-color: #21262d; color: #8b949e; font-size: 11px;")
        self.status.showMessage("Verificando dependências...")
        self.footer_label = QLabel("v0.4.11-rev1.2.3-220426 | homologacao | @S.V.S - Try Technology")
        self.footer_label.setStyleSheet("color: #8b949e; padding-right: 15px;")
        self.status.addPermanentWidget(self.footer_label)

        # Iniciar nova sessão
        self._start_new_session()
        
        self.load_templates()

        # === INTEGRACAO IA ===
        self._init_ai_manager()
        self._init_custom_ai_manager()
        self._init_training_manager()
        self._init_richie()
        self._richie_active = True  # Richie é o padrão na inicialização
        self.ai_select.currentTextChanged.connect(self._on_ai_changed)

        # === STARTUP DEPENDENCY CHECK ===
        self._check_startup_dependencies()

    # ==========================================
    # === OPEN FOLDER (CORRIGIDO) ===
    # ==========================================

    def open_folder(self):
        """Abre um diálogo para selecionar uma pasta e atualiza o Explorer."""
        d = QFileDialog.getExistingDirectory(self, "Abrir Projeto")
        if d:
            self.file_model.setRootPath(d)
            self.file_tree.setRootIndex(self.file_model.index(d))
            self.status.showMessage(f"Projeto aberto: {d}", 3000)

    # ==========================================
    # === CHAT SESSION MANAGEMENT ===
    # ==========================================

    def _start_new_session(self):
        """Inicia uma nova sessão de chat."""
        import uuid
        self._current_session_id = str(uuid.uuid4())[:8]
        self._current_session_messages = []

    def _save_current_session(self):
        """Salva a sessão de chat atual no histórico."""
        if not self._current_session_messages:
            return
        
        # Usar a primeira mensagem do usuário como título
        title = "Nova Conversa"
        for msg in self._current_session_messages:
            if msg.get("is_user"):
                title = msg["text"][:40]
                if len(msg["text"]) > 40:
                    title += "..."
                break
        
        self.chat_history_panel.save_session(
            self._current_session_id,
            title,
            self._current_session_messages
        )

    def _load_chat_session(self, session_id):
        """Carrega e exibe uma sessão de chat do histórico."""
        data = self.chat_history_panel.load_session(session_id)
        if not data:
            self.status.showMessage("Sessão não encontrada", 2000)
            return
        
        # Limpar chat atual
        self._clear_chat_widgets()
        
        # Restaurar sessão
        self._current_session_id = session_id
        self._current_session_messages = data.get("messages", [])
        
        # Recriar mensagens
        for msg in self._current_session_messages:
            sender = msg.get("sender", "?")
            text = msg.get("text", "")
            is_user = msg.get("is_user", False)
            chat_msg = ChatMessage(sender, text, is_user)
            self.chat_v_layout.addWidget(chat_msg)
        
        self._message_count = len(self._current_session_messages)
        
        # Scroll ao final após carregar
        QTimer.singleShot(100, self._scroll_chat_to_bottom)
        self.status.showMessage(f"Sessão carregada: {data.get('title', session_id)}", 2000)

    def _clear_chat_widgets(self):
        """Remove todos os widgets de mensagem do layout."""
        while self.chat_v_layout.count():
            item = self.chat_v_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._message_count = 0

    # ==========================================
    # === SHELL COMBOBOX ===
    # ==========================================

    def _on_shell_changed(self, shell_name):
        self.terminal_widget.set_shell(shell_name)
        self.shell_indicator.setText(f"● {shell_name}")
        self.shell_indicator.setStyleSheet("color: #3fb950; font-size: 11px; margin-left: 8px;")
        self.status.showMessage(f"Terminal: shell ativo alterado para {shell_name}", 2000)

    # ==========================================
    # === AI MANAGERS ===
    # ==========================================

    def _init_ai_manager(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'providers.yaml')
            self.ai_manager = AIManager(config_path)
            self._provider_map = {
                "DeepSeek": "deepseek",
                "GPT-4": "openai",
                "Claude": "anthropic"
            }
            initial = self.ai_select.currentText()
            if initial in self._provider_map:
                self.ai_manager.set_active_provider(self._provider_map[initial])
            stats = self.ai_manager.get_stats()
            if stats['available_providers']:
                self.status.showMessage(f"IA: {', '.join(stats['available_providers'])} disponiveis", 5000)
            else:
                self.status.showMessage("IA: Configure API keys em providers.yaml", 5000)
        except Exception as e:
            self.ai_manager = None
            self.status.showMessage(f"IA: Erro ao inicializar - {str(e)[:50]}", 5000)

    def _init_custom_ai_manager(self):
        try:
            self.custom_ai_manager = CustomAIManager()
            self._refresh_ai_combo()
        except Exception as e:
            self.custom_ai_manager = None
            print(f"Erro ao inicializar CustomAIManager: {e}")

    def _init_training_manager(self):
        try:
            self.training_manager = TrainingManager()
        except Exception as e:
            self.training_manager = None
            print(f"Erro ao inicializar TrainingManager: {e}")

    def _init_richie(self):
        try:
            from ..core.richie_ai import RichieAI
            self.richie = RichieAI()
            # Carregar FlowEngine com o modelo Richie do JSON
            self._load_richie_flow_engine()
            self.status.showMessage("🤖 Richie AI inicializada (modo offline)!", 3000)
        except Exception as e:
            self.richie = None
            print(f"Erro ao inicializar Richie: {e}")

    def _load_richie_flow_engine(self):
        """Carrega FlowEngine do modelo Richie para complementar o motor offline."""
        if not self.richie or not self.custom_ai_manager:
            return
        try:
            # Buscar modelo Richie no gerenciador
            richie_model = None
            for model in self.custom_ai_manager.list_models(active_only=False):
                if model.id in ("richie-01", "richie_native", "richie") or "richie" in model.name.lower():
                    richie_model = model
                    break
            if richie_model:
                self.richie.load_flow_from_model(richie_model)
        except Exception as e:
            print(f"[MainWindow] Erro ao carregar FlowEngine do Richie: {e}")

    def _get_ai_sender_name(self):
        """Retorna o nome do sender baseado na IA ativa no ComboBox."""
        if self._richie_active:
            return "🤖 Richie"
        if self.active_custom_ai:
            return f"🤖 {self.active_custom_ai.name}"
        # Pegar do ComboBox direto
        current = self.ai_select.currentText()
        if current and not current.startswith("---"):
            return f"💻 {current}"
        return "🤖 Assistente"

    def update_ai_combo(self):
        from PyQt6.QtGui import QStandardItemModel, QStandardItem
        current_selection = self.ai_selector.currentText()
        model = QStandardItemModel()
        native_header = QStandardItem("--- IA Nativa Locais ---")
        native_header.setEnabled(False)
        model.appendRow(native_header)
        providers_header = QStandardItem("--- Providers (Online) ---")

    def _refresh_ai_combo(self):
        self.ai_select.blockSignals(True)
        self.ai_select.clear()
        self.ai_select.addItem("--- Suas IAs ---")
        self.ai_select.addItem("🤖 Richie", "richie")
        if self.custom_ai_manager:
            unique_bots = self.custom_ai_manager.get_unique_bots()
            for bot_info in unique_bots:
                model = bot_info['active_model']
                ver_count = bot_info['version_count']
                # Filtrar TODOS os modelos Richie nativos (por id ou nome)
                is_richie = (model.id in ("richie_native", "richie-01", "richie") or
                             "richie" in model.name.lower())
                if not is_richie and getattr(model, 'chat_integration', True):
                    ver_tag = f" ({model.version_label})" if ver_count > 1 else ""
                    display_name = f"🤖 {model.name}{ver_tag}"
                    if len(display_name) > 22:
                        display_name = display_name[:22] + "..."
                    self.ai_select.addItem(display_name, model.id)
                    self.ai_select.setItemData(
                        self.ai_select.count() - 1,
                        f"🤖 {model.name} {ver_tag} — {ver_count} versão(ões)",
                        Qt.ItemDataRole.ToolTipRole
                    )
        self.ai_select.addItem("--- Providers (Online) ---")
        self.ai_select.addItems(["OpenAI GPT-4", "DeepSeek", "Claude"])
        self.ai_select.blockSignals(False)
        self.ai_select.setCurrentIndex(1)  # Richie selecionado

    def _on_ai_changed(self, ai_name):
        if ai_name.startswith("---"):
            return
        if ai_name == "🤖 Richie":
            self._richie_active = True
            self.active_custom_ai = None
            # Recarregar FlowEngine ao selecionar Richie
            self._load_richie_flow_engine()
            self.status.showMessage("🤖 Richie AI ativa (modo offline)", 3000)
            if self._message_count == 0:
                from ..core.richie_ai import RICHIE_GREETING
                self.add_message("🤖 Richie", RICHIE_GREETING)
            return
        self._richie_active = False
        if ai_name.startswith("🤖 "):
            model_id = self.ai_select.currentData()
            if model_id and model_id != "richie" and self.custom_ai_manager:
                model = self.custom_ai_manager.get_model(model_id)
                if model:
                    self.active_custom_ai = model
                    if self.ai_manager:
                        self.ai_manager.set_active_provider(model.base_provider)
                    self.status.showMessage(f"IA: {model.name} ativa", 2000)
                    return
        self.active_custom_ai = None
        provider_map = {
            "OpenAI GPT-4": "openai",
            "DeepSeek": "deepseek",
            "Claude": "anthropic"
        }
        if self.ai_manager and ai_name in provider_map:
            provider = provider_map[ai_name]
            if self.ai_manager.set_active_provider(provider):
                self.status.showMessage(f"IA: {ai_name} ativa (online)", 2000)
            else:
                self.status.showMessage(f"IA: {ai_name} não configurada — configure API key", 3000)

    # ==========================================
    # === CHAT HISTORY DIALOG ===
    # ==========================================

    def _show_chat_history_dialog(self):
        """Abre dialog de gerenciamento de histórico de conversas via botão 🔍."""
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Histórico de Conversas")
        dialog.setMinimumSize(450, 500)
        dialog.setStyleSheet("""
            QDialog { background-color: #161b22; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                          border-radius: 6px; padding: 8px 16px; font-size: 12px; }
            QPushButton:hover { background-color: #30363d; border: 1px solid #58a6ff; }
            QLineEdit { background-color: #0d1117; color: #f0f6fc; border: 1px solid #30363d;
                        border-radius: 4px; padding: 6px; font-size: 12px; }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("📋 Selecione ou renomeie uma conversa")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #58a6ff; padding: 8px 0;")
        layout.addWidget(header)
        
        # Scroll area para sessões
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)
        scroll_layout.setContentsMargins(4, 4, 4, 4)
        
        # Carregar sessões do index
        index_path = self.chat_history_panel._get_sessions_index_path()
        sessions = []
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
                sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
            except:
                pass
        
        if not sessions:
            empty_label = QLabel("Nenhuma conversa salva ainda.\nEnvie mensagens e clique '+ Novo' para salvar.")
            empty_label.setStyleSheet("color: #8b949e; font-size: 12px; padding: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_layout.addWidget(empty_label)
        else:
            for session in sessions:
                row_frame = QFrame()
                row_frame.setStyleSheet("""
                    QFrame { background-color: #0d1117; border: 1px solid #21262d; border-radius: 8px; padding: 4px; }
                    QFrame:hover { border: 1px solid #58a6ff; }
                """)
                row = QHBoxLayout(row_frame)
                row.setContentsMargins(10, 6, 10, 6)
                
                # Info da sessão
                title = session.get("title", "Conversa sem título")
                sid = session.get("id", "")
                date_str = session.get("updated_at", "")
                try:
                    from datetime import datetime as dt_
                    date_friendly = dt_.fromisoformat(date_str).strftime("%d/%m/%Y %H:%M")
                except:
                    date_friendly = ""
                
                info_layout = QVBoxLayout()
                title_label = QLabel(f"💬 {title}")
                title_label.setStyleSheet("color: #f0f6fc; font-weight: bold; font-size: 12px;")
                info_layout.addWidget(title_label)
                if date_friendly:
                    date_label = QLabel(f"📅 {date_friendly}")
                    date_label.setStyleSheet("color: #8b949e; font-size: 10px;")
                    info_layout.addWidget(date_label)
                row.addLayout(info_layout, 1)
                
                # Botão Abrir
                btn_open = QPushButton("Abrir")
                btn_open.setFixedWidth(70)
                btn_open.setStyleSheet("background-color: #1f6feb; color: white; border: none; border-radius: 4px; padding: 6px;")
                btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_open.clicked.connect(lambda _, s=sid: (self._load_chat_session(s), dialog.accept()))
                row.addWidget(btn_open)
                
                # Botão Renomear
                btn_rename = QPushButton("✏️")
                btn_rename.setFixedWidth(36)
                btn_rename.setToolTip("Renomear conversa")
                btn_rename.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_rename.clicked.connect(lambda _, s=sid, lbl=title_label: self._rename_session_inline(s, lbl))
                row.addWidget(btn_rename)
                
                scroll_layout.addWidget(row_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Botão fechar
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("background-color: #21262d; color: #c9d1d9; padding: 8px; border-radius: 6px;")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.exec()

    def _rename_session_inline(self, session_id, title_label):
        """Renomeia uma sessão de chat via QInputDialog."""
        new_title, ok = QInputDialog.getText(
            self, "Renomear Conversa",
            "Novo título para a conversa:",
            text=title_label.text().replace("💬 ", "")
        )
        if ok and new_title.strip():
            # Atualizar no index
            index_path = self.chat_history_panel._get_sessions_index_path()
            if os.path.exists(index_path):
                try:
                    with open(index_path, 'r', encoding='utf-8') as f:
                        sessions = json.load(f)
                    for s in sessions:
                        if s.get("id") == session_id:
                            s["title"] = new_title.strip()
                            break
                    with open(index_path, 'w', encoding='utf-8') as f:
                        json.dump(sessions, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Erro ao renomear: {e}")
            
            # Atualizar no arquivo da sessão
            session_file = os.path.join(self.chat_history_panel._sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    data["title"] = new_title.strip()
                    with open(session_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except:
                    pass
            
            # Atualizar label visual
            title_label.setText(f"💬 {new_title.strip()}")
            # Recarregar lista no painel lateral
            self.chat_history_panel._load_session_list()
            self.status.showMessage(f"Conversa renomeada: {new_title.strip()}", 2000)

    # ==========================================
    # === SETTINGS & AI MANAGEMENT ===
    # ==========================================

    def _show_settings_dialog(self):
        try:
            from .dialogs.settings_window import SettingsWindow
            self.settings_dialog = SettingsWindow(self.custom_ai_manager, self)
            self.settings_dialog.exec()
            self._refresh_ai_combo()
        except ImportError:
            QMessageBox.information(self, "Em breve", "Módulo de configurações em desenvolvimento.")

    def _show_create_ai_dialog(self):
        if not self.custom_ai_manager:
            QMessageBox.warning(self, "Erro", "Gerenciador de IAs nao inicializado")
            return
        dialog = CreateAIDialog(self.custom_ai_manager, self)
        dialog.ai_created.connect(self._on_ai_created)
        dialog.exec()

    def _on_ai_created(self, model):
        self._refresh_ai_combo()
        for i in range(self.ai_select.count()):
            if self.ai_select.itemData(i) == model.id:
                self.ai_select.setCurrentIndex(i)
                break

    def _show_manage_ai_dialog(self):
        if not self.custom_ai_manager:
            QMessageBox.warning(self, "Erro", "Gerenciador de IAs nao inicializado")
            return
        dialog = ManageAIDialog(self.custom_ai_manager, self)
        dialog.ai_selected.connect(self._on_manage_ai_selected)
        dialog.ai_deleted.connect(lambda _: self._refresh_ai_combo())
        dialog.exec()

    def _on_manage_ai_selected(self, model):
        for i in range(self.ai_select.count()):
            if self.ai_select.itemData(i) == model.id:
                self.ai_select.setCurrentIndex(i)
                break

    def _clear_chat(self):
        """Salva sessão atual e inicia nova conversa."""
        # Salvar sessão atual antes de limpar
        self._save_current_session()
        
        self._clear_chat_widgets()
        self._start_new_session()
        
        if self._richie_active:
            from ..core.richie_ai import RICHIE_GREETING
            self.add_message(self._get_ai_sender_name(), RICHIE_GREETING)
        else:
            self.add_message(self._get_ai_sender_name(), "Nova conversa iniciada! Como posso ajudar?")
        self.status.showMessage("Nova conversa iniciada", 2000)

    def _clear_cache(self):
        if self.ai_manager:
            self.ai_manager.clear_cache()
            self.status.showMessage("Cache limpo", 2000)

    def _show_training_dialog(self):
        if not self.training_manager:
            QMessageBox.warning(self, "Erro", "Gerenciador de treinamento não inicializado")
            return
        ai_model_id = None
        if self.active_custom_ai:
            ai_model_id = self.active_custom_ai.id
        dialog = TrainingDialog(
            self.custom_ai_manager,
            self.training_manager,
            ai_model_id,
            self
        )
        dialog.training_started.connect(self._on_training_started)
        dialog.exec()

    def _on_training_started(self, session):
        self.status.showMessage(f"Treinamento iniciado: {session.id}", 3000)
        self.add_message(
            "🧠 Sistema",
            f"Sessão de treinamento iniciada!\n"
            f"Modo: {session.mode}\n"
            f"Projetos: {len(session.project_ids)}"
        )

    def _add_training_project(self):
        if not self.training_manager:
            QMessageBox.warning(self, "Erro", "Gerenciador de treinamento não inicializado")
            return
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Projeto")
        if not path:
            return
        name, ok = QInputDialog.getText(
            self, "Nome do Projeto",
            "Digite um nome para identificar este projeto:",
            text=path.split("/")[-1].split("\\")[-1]
        )
        if not ok or not name:
            return
        project = self.training_manager.add_project(
            name=name,
            path=path,
            description=f"Projeto importado de {path}"
        )
        self.status.showMessage(f"Projeto '{name}' adicionado para treinamento", 3000)
        reply = QMessageBox.question(
            self, "Indexar Projeto",
            f"Deseja indexar o projeto '{name}' agora?\n\n"
            "Isso irá analisar os arquivos para o treinamento.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.training_manager.index_project(project.id)
            if "error" in result:
                QMessageBox.warning(self, "Erro", result["error"])
            else:
                QMessageBox.information(
                    self, "Indexação Concluída",
                    f"Projeto indexado!\n\n"
                    f"Arquivos: {result['files_indexed']}\n"
                    f"Tokens estimados: {result['total_tokens']:,}"
                )

    def _view_training_projects(self):
        if not self.training_manager:
            QMessageBox.warning(self, "Erro", "Gerenciador de treinamento não inicializado")
            return
        projects = self.training_manager.list_projects()
        if not projects:
            QMessageBox.information(
                self, "Projetos",
                "Nenhum projeto de treinamento cadastrado.\n\n"
                "Use 'IA > Treinamento > Adicionar Projeto' para adicionar."
            )
            return
        info = "📁 Projetos de Treinamento:\n\n"
        for p in projects:
            status = "✅ Indexado" if p.total_tokens > 0 else "⚠️ Não indexado"
            info += f"• {p.name}\n"
            info += f"  Caminho: {p.path}\n"
            info += f"  Status: {status}\n"
            if p.total_tokens > 0:
                info += f"  Arquivos: {len(p.indexed_files)} | Tokens: {p.total_tokens:,}\n"
            info += "\n"
        QMessageBox.information(self, "Projetos de Treinamento", info)

    # ==========================================
    # === MENUS ===
    # ==========================================

    def setup_menus(self):
        menubar = self.menuBar()
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
        run_menu = menubar.addMenu("Executar")
        run_act = QAction("Rodar Código", self)
        run_act.setShortcut("F5")
        run_act.triggered.connect(self.run_code)
        run_menu.addAction(run_act)
        view_menu = menubar.addMenu("Visualizar")
        self.view_term_act = QAction("Terminal", self, checkable=True)
        self.view_term_act.setChecked(True)
        self.view_term_act.triggered.connect(self.toggle_terminal_from_menu)
        view_menu.addAction(self.view_term_act)
        self.view_chat_act = QAction("Chat IA", self, checkable=True)
        self.view_chat_act.setChecked(True)
        self.view_chat_act.triggered.connect(self.toggle_chat_from_menu)
        view_menu.addAction(self.view_chat_act)
        ai_menu = menubar.addMenu("IA")
        create_ai_act = QAction("Criar Nova IA...", self)
        create_ai_act.setShortcut("Ctrl+Shift+N")
        create_ai_act.triggered.connect(self._show_create_ai_dialog)
        ai_menu.addAction(create_ai_act)
        manage_ai_act = QAction("Gerenciar IAs...", self)
        manage_ai_act.triggered.connect(self._show_manage_ai_dialog)
        ai_menu.addAction(manage_ai_act)
        ai_menu.addSeparator()
        training_menu = ai_menu.addMenu("🧠 Treinamento")
        train_ai_act = QAction("Configurar Treinamento...", self)
        train_ai_act.setShortcut("Ctrl+Shift+T")
        train_ai_act.triggered.connect(self._show_training_dialog)
        training_menu.addAction(train_ai_act)
        add_project_act = QAction("Adicionar Projeto de Aprendizagem...", self)
        add_project_act.triggered.connect(self._add_training_project)
        training_menu.addAction(add_project_act)
        view_projects_act = QAction("Ver Projetos de Treinamento", self)
        view_projects_act.triggered.connect(self._view_training_projects)
        training_menu.addAction(view_projects_act)
        ai_menu.addSeparator()
        clear_chat_act = QAction("Limpar Chat", self)
        clear_chat_act.triggered.connect(self._clear_chat)
        ai_menu.addAction(clear_chat_act)
        clear_cache_act = QAction("Limpar Cache", self)
        clear_cache_act.triggered.connect(self._clear_cache)
        ai_menu.addAction(clear_cache_act)
        help_menu = menubar.addMenu("Ajuda")
        about_act = QAction("Sobre", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

    # ==========================================
    # === CHAT & ATTACHMENTS ===
    # ==========================================

    def attach_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Anexar Arquivo")
        if f:
            self.chat_input.insertPlainText(f"\n[Anexo: {os.path.basename(f)}]")

    # ==========================================
    # === SIDEBAR ===
    # ==========================================

    def switch_sidebar_view(self, index):
        if index == self._active_sidebar_index and not self._sidebar_collapsed:
            self._sidebar_collapsed = True
            self._sidebar_expanded_width = self.sidebar.width() if self.sidebar.width() > 10 else 220
            anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
            anim.setDuration(250)
            anim.setStartValue(self._sidebar_expanded_width)
            anim.setEndValue(0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(lambda: self.sidebar.setFixedWidth(0))
            self._sidebar_anim = anim
            anim.start()
        elif self._sidebar_collapsed:
            self._sidebar_collapsed = False
            self._active_sidebar_index = index
            self.sidebar.setCurrentIndex(index)
            target_w = self._sidebar_expanded_width if self._sidebar_expanded_width > 10 else 220
            self.sidebar.setMaximumWidth(16777215)
            self.sidebar.setFixedWidth(0)
            self.sidebar.setMinimumWidth(0)
            self.sidebar.setMaximumWidth(target_w)
            self.sidebar.setFixedWidth(target_w)
            self._sidebar_anim = None
        else:
            self._active_sidebar_index = index
            self.sidebar.setCurrentIndex(index)

    # ==========================================
    # === CONTEXT MENU & FILE OPERATIONS ===
    # ==========================================

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

    # ==========================================
    # === FILE / TAB MANAGEMENT + INDICADOR * ===
    # ==========================================

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
        self._mark_tab_saved(idx)
        self.status.showMessage(f"Salvo: {path}", 3000)

    def load_templates(self):
        self.add_editor_tab("main.py", "", "template_py")
        self.add_editor_tab("hello.js", "console.log('Olá do Node.js!');", "template_js")
        self.editor_tabs.setCurrentIndex(1)

    def add_editor_tab(self, name, content, path):
        ed = QTextEdit()
        ed.setText(content)
        CodeHighlighter(ed.document(), name)
        idx = self.editor_tabs.addTab(ed, name)
        self.editor_tabs.setTabToolTip(idx, str(path))
        self.editor_tabs.setCurrentIndex(idx)
        self._tab_original_content[idx] = content
        ed.textChanged.connect(lambda i=idx, editor=ed: self._on_tab_text_changed(i, editor))

    def _on_tab_text_changed(self, tab_idx, editor):
        if tab_idx >= self.editor_tabs.count():
            return
        current_text = editor.toPlainText()
        original = self._tab_original_content.get(tab_idx, "")
        title = self.editor_tabs.tabText(tab_idx)
        if current_text != original:
            if not title.endswith("*"):
                self.editor_tabs.setTabText(tab_idx, title + "*")
        else:
            if title.endswith("*"):
                self.editor_tabs.setTabText(tab_idx, title[:-1])

    def _mark_tab_saved(self, idx):
        if idx < 0 or idx >= self.editor_tabs.count():
            return
        editor = self.editor_tabs.widget(idx)
        if editor:
            self._tab_original_content[idx] = editor.toPlainText()
        title = self.editor_tabs.tabText(idx)
        if title.endswith("*"):
            self.editor_tabs.setTabText(idx, title[:-1])

    def _has_unsaved_tabs(self):
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i).endswith("*"):
                return True
        return False

    def _get_unsaved_tab_names(self):
        unsaved = []
        for i in range(self.editor_tabs.count()):
            title = self.editor_tabs.tabText(i)
            if title.endswith("*"):
                unsaved.append(title)
        return unsaved

    def close_tab(self, i):
        title = self.editor_tabs.tabText(i)
        if title.endswith("*"):
            reply = QMessageBox.question(
                self, "Arquivo Modificado",
                f"O arquivo '{title[:-1]}' possui modificações não salvas.\n\n"
                "Deseja salvar antes de fechar?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Save:
                old_idx = self.editor_tabs.currentIndex()
                self.editor_tabs.setCurrentIndex(i)
                self._save_current_file()
                self.editor_tabs.setCurrentIndex(old_idx)
        if i in self._tab_original_content:
            del self._tab_original_content[i]
        self.editor_tabs.removeTab(i)
        new_originals = {}
        for key, val in self._tab_original_content.items():
            if key > i:
                new_originals[key - 1] = val
            elif key < i:
                new_originals[key] = val
        self._tab_original_content = new_originals

    def open_file(self, idx):
        path = self.file_model.filePath(idx)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f: self.add_editor_tab(os.path.basename(path), f.read(), path)

    def run_code(self):
        curr = self.editor_tabs.currentWidget()
        if not curr: return
        name = self.editor_tabs.tabText(self.editor_tabs.currentIndex())
        content = curr.toPlainText()
        self.terminal_widget.output.append(f"\n> Rodando {name}...\n")
        ext = os.path.splitext(name)[1].lower()
        cmd = ""
        if ext == ".py": cmd = f'"{sys.executable}"'
        elif ext == ".js": cmd = "node"
        elif ext == ".java":
            if shutil.which("java"): cmd = "java"
            else: self.terminal_widget.output.append("> Erro: Java não encontrado no PATH.\n"); return
        elif ext == ".lua": 
            if shutil.which("lua"): cmd = "lua"
            else: self.terminal_widget.output.append("> Erro: Lua não encontrado no PATH.\n"); return
        if not cmd:
            self.terminal_widget.output.append("> Linguagem não configurada.\n")
            return
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode='w', encoding='utf-8') as tf:
            tf.write(content)
            tname = tf.name
            
        # Armazena o tempfile no painel do terminal para ele deletar ao terminar, se necessário
        self.terminal_widget._temp_script_file = tname
        
        # Executa no modo interativo (suporta Inputs do usuário no chat/terminal)
        self.terminal_widget.run_script_interactive(f'{cmd} "{tname}"', os.getcwd())

    def on_exec_finished(self, code, temp_name):
        self.terminal_widget.output.append(f"\n> Fim da execução. Código: {code}")
        try: os.unlink(temp_name)
        except: pass

    # ==========================================
    # === CHAT SEND / RICHIE ===
    # ==========================================

    def handle_send(self):
        txt = self.chat_input.toPlainText().strip()
        if not txt:
            return
        if self.ai_thread and self.ai_thread.isRunning():
            self.status.showMessage("Aguarde a resposta anterior...", 2000)
            return
        self.add_message("👤 Você", txt, is_user=True)
        self.chat_input.clear()
        if self._richie_active and self.richie:
            self._handle_richie_send(txt)
            return
        if not self.ai_manager or not self.ai_manager.get_stats()['available_providers']:
            self.add_message(self._get_ai_sender_name(), "Nenhum provider online configurado.\n\n💡 Selecione 🤖 Richie para chat offline ou configure uma API key em config/providers.yaml.")
            return
        context = None
        curr_editor = self.editor_tabs.currentWidget()
        if curr_editor and ("[código]" in txt.lower() or "analise" in txt.lower() or "codigo" in txt.lower()):
            context = curr_editor.toPlainText()[:2000]
        message = txt
        system_prompt = None
        ai_name = self._get_ai_sender_name()
        if self.active_custom_ai:
            system_prompt = self.active_custom_ai.system_prompt
        self.current_ai_message = self.add_message(ai_name, "Processando...", return_widget=True)
        self.ai_thread = AIStreamThread(self.ai_manager, message, context)
        self.ai_thread.system_prompt = system_prompt
        self.ai_thread.chunk_ready.connect(self._on_ai_response)
        self.ai_thread.error_occurred.connect(self._on_ai_error)
        self.ai_thread.finished_streaming.connect(self._on_ai_finished)
        self._threads.append(self.ai_thread)
        self.ai_thread.start()

    def _handle_richie_send(self, txt):
        editor_code = None
        file_ext = None
        curr_editor = self.editor_tabs.currentWidget()
        curr_idx = self.editor_tabs.currentIndex()
        intent = self.richie.detect_intent(txt)
        msg_lower = txt.lower().strip()
        is_create = any(w in msg_lower for w in ["crie", "cria", "gere", "faça", "fazer", "escreva", "crie um", "cria um"])
        lang = intent.get("language")
        if is_create and lang:
            ext_map = {
                "python": "py", "javascript": "js", "typescript": "ts", "lua": "lua",
                "csharp": "cs", "html": "html", "css": "css", "java": "java",
                "go": "go", "rust": "rs", "php": "php", "ruby": "rb",
                "gdscript": "gd", "kotlin": "kt", "swift": "swift", "cpp": "cpp",
                "c": "c", "r": "r", "julia": "jl", "dart": "dart",
            }
            ext = ext_map.get(lang, lang)
            
            # Gera a resposta através do modelo primeiro para obter o código complexo
            response = self.richie.generate_response(txt, editor_code, file_ext)
            
            # Tenta extrair o bloco de código markdown
            import re
            code_match = re.search(r'```[a-zA-Z]*\n(.*?)\n```', response, re.DOTALL)
            if code_match:
                extracted_code = code_match.group(1).strip()
            else:
                extracted_code = f"// Estrutura para {lang.capitalize()}"
                
            self._open_file_with_code(lang.capitalize(), ext, extracted_code)
            
            # Modifica a resposta gerada para incluir a confirmação amigável de criação (removendo os blocos brutos se quiser, mas deixamos fluir)
            if "### 🚀 Execução Solicitada" not in response:
                response += "\n\n---\n### 📄 Arquivo Criado\nAbri uma nova guia com o script gerado. Pronto para executar?\nResponda **'sim, execute'** ou clique nos botões abaixo."
                response += "\n<!--ACTIONS: [\"✅ Aprovado (Apenas Agora)\", \"🔄 Sempre Liberar (Sessão)\", \"❌ Negado\"]-->"
            else:
                response = response.replace("Notei que você pediu para rodar este código.", f"**Arquivo {lang.capitalize()} Criado!**\nNotei que você pediu para rodar este código.")
                
            self.richie.add_user_message(txt, None)
            self.richie.add_assistant_message(response)
            self.add_message("🤖 Richie", response)
            if intent.get("language"):
                self.richie.learn("linguagem_preferida", intent["language"])
            return
        if curr_editor and intent.get("wants_analysis", False):
            editor_code = curr_editor.toPlainText()[:5000]
            tab_name = self.editor_tabs.tabText(curr_idx) if curr_idx >= 0 else ""
            if '.' in tab_name:
                file_ext = '.' + tab_name.split('.')[-1].replace('*', '').strip()
        self.richie.add_user_message(txt, editor_code)
        response = self.richie.generate_response(txt, editor_code, file_ext)
        self.richie.add_assistant_message(response)
        self.add_message("🤖 Richie", response)
        if txt.lower().strip() == "sim, execute":
            self.run_code()
        if intent.get("language"):
            self.richie.learn("linguagem_preferida", intent["language"])

    def _on_ai_response(self, response):
        if self.current_ai_message:
            self.current_ai_message.update_text(response)
        self.current_ai_message = None

    def _on_ai_error(self, error):
        if self.current_ai_message:
            self.current_ai_message.update_text(f"❌ Erro: {error}")
        self.current_ai_message = None

    def _on_ai_finished(self):
        self.current_ai_message = None
        self._threads = [t for t in self._threads if t.isRunning()]

    def _update_chat_stretch(self):
        """Stub mantido por compatibilidade — stretch removido na v22.0.8."""
        pass

    def _adjust_input_frame_height(self):
        """Ajusta a altura do input_frame conforme o conteudo do chat_input."""
        doc_height = self.chat_input.document().size().height()
        desired = min(max(60, int(doc_height) + 30), 220)
        self.input_frame.setFixedHeight(desired)
        # Garantir scroll interno quando atingir limite máximo
        if desired >= 220:
            self.chat_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            self.chat_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        QTimer.singleShot(10, self.chat_input.ensureCursorVisible)

    def _scroll_chat_to_bottom(self):
        """Scroll suave para o final do chat."""
        sb = self.chat_scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _handle_chat_action(self, action: str):
        """Lida com clique em botões dinâmicos de chat."""
        if "Aprovado" in action or "Sempre" in action:
            self.chat_input.setPlainText("sim, execute")
        elif "Negado" in action or "❌" in action:
            self.chat_input.setPlainText("não")
        else:
            self.chat_input.setPlainText(action)
        self.handle_send()

    def add_message(self, s, t, is_user=False, return_widget=False):
        """Adiciona mensagem ao chat com scroll correto via QTimer."""
        self._message_count += 1

        # Limitar mensagens para performance
        if self._message_count > self.MAX_CHAT_MESSAGES:
            item = self.chat_v_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
            self._message_count -= 1

        # Remover stretch do topo quando conteudo preenche a area
        self._update_chat_stretch()

        msg = ChatMessage(s, t, is_user)
        msg.action_clicked.connect(self._handle_chat_action)
        self.chat_v_layout.addWidget(msg)

        # Registrar na sessão atual
        self._current_session_messages.append({
            "sender": s,
            "text": t,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat()
        })

        # Scroll com delay para garantir que o layout atualizou
        QTimer.singleShot(50, self._scroll_chat_to_bottom)

        if return_widget:
            return msg

    # ==========================================
    # === TERMINAL TOGGLE ===
    # ==========================================

    def toggle_terminal(self):
        visible = not self.term_container.isVisible()
        self.term_container.setVisible(visible)
        self.btn_term_toggle.setText("▼" if visible else "▲")
        if hasattr(self, 'view_term_act'):
            self.view_term_act.setChecked(visible)

    def toggle_terminal_from_menu(self):
        visible = self.view_term_act.isChecked()
        self.term_container.setVisible(visible)
        self.btn_term_toggle.setText("▼" if visible else "▲")

    def toggle_chat(self):
        self._chat_collapsed = getattr(self, '_chat_collapsed', False)
        
        if not self._chat_collapsed:
            self._chat_expanded_width = self.right_panel.width()
            self.r_header.hide()
            self.chat_container.hide()
            self.collapsed_widget.show()
            self._chat_anim = QPropertyAnimation(self.right_panel, b"maximumWidth")
            self._chat_anim.setDuration(250)
            self._chat_anim.setStartValue(self._chat_expanded_width)
            self._chat_anim.setEndValue(35)
            self._chat_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._chat_anim.finished.connect(lambda: self.right_panel.setMinimumWidth(35))
            self._chat_anim.start()
            self._chat_collapsed = True
            if hasattr(self, 'view_chat_act'):
                self.view_chat_act.setChecked(False)
        else:
            target_w = getattr(self, '_chat_expanded_width', 350)
            self.right_panel.setMinimumWidth(50)
            self.right_panel.setMaximumWidth(16777215)
            self.collapsed_widget.hide()
            self.r_header.show()
            self.chat_container.show()
            self._chat_anim = QPropertyAnimation(self.right_panel, b"maximumWidth")
            self._chat_anim.setDuration(250)
            self._chat_anim.setStartValue(35)
            self._chat_anim.setEndValue(target_w)
            self._chat_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._chat_anim.finished.connect(lambda: self.right_panel.setMaximumWidth(16777215))
            self._chat_anim.start()
            self._chat_collapsed = False
            if hasattr(self, 'view_chat_act'):
                self.view_chat_act.setChecked(True)

    def toggle_chat_from_menu(self):
        visible = self.view_chat_act.isChecked()
        self.right_panel.setVisible(visible)
        if visible and not self.chat_container.isVisible():
             self.toggle_chat()

    def show_about(self):
        AboutDialog(self).exec()

    def open_project(self):
        d = QFileDialog.getExistingDirectory(self, "Selecionar Projeto")
        if d:
            self.file_model.setRootPath(d)
            self.file_tree.setRootIndex(self.file_model.index(d))

    # ==========================================
    # === KEY PRESS ===
    # ==========================================

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_F5:
            self._run_current_script()
        elif e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_S:
            self._save_current_file()
        super().keyPressEvent(e)

    def _save_current_file(self):
        curr_idx = self.editor_tabs.currentIndex()
        if curr_idx < 0: return
        editor = self.editor_tabs.widget(curr_idx)
        content = editor.toPlainText()
        current_title = self.editor_tabs.tabText(curr_idx)
        file_path = self.editor_tabs.tabToolTip(curr_idx)
        if file_path and file_path != "None" and os.path.exists(os.path.dirname(file_path)):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                new_name = os.path.basename(file_path)
                self.editor_tabs.setTabText(curr_idx, new_name)
                self._mark_tab_saved(curr_idx)
                self.terminal_widget.output.append(f"\n> [Salvo] {file_path}")
                self.status.showMessage(f"Salvo: {file_path}", 3000)
                return
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{e}")
                return
        base_dir = self.file_model.rootPath()
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo", os.path.join(base_dir, current_title.replace('*', '')))
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                new_name = os.path.basename(path)
                self.editor_tabs.setTabText(curr_idx, new_name)
                self.editor_tabs.setTabToolTip(curr_idx, path)
                self._mark_tab_saved(curr_idx)
                self.terminal_widget.output.append(f"\n> [Salvo] {path}")
                self.status.showMessage(f"Salvo: {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{e}")

    # ==========================================
    # === EXPLORER FILE ACTIONS ===
    # ==========================================

    def _explorer_new_file(self):
        root_path = self.file_model.rootPath()
        text, ok = QInputDialog.getText(self, "Novo Arquivo", "Nome do Arquivo (com extensão):")
        if ok and text:
            file_path = os.path.join(root_path, text)
            try:
                Path(file_path).touch()
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível criar o arquivo:\n{e}")

    def _explorer_new_folder(self):
        root_path = self.file_model.rootPath()
        text, ok = QInputDialog.getText(self, "Nova Pasta", "Nome da Pasta:")
        if ok and text:
            folder_path = os.path.join(root_path, text)
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível criar a pasta:\n{e}")

    def _create_new_file(self):
        text, ok = QInputDialog.getText(self, "Nova Guia", "Nome do Arquivo (Ex: script.py, script.js):")
        if not ok or not text.strip():
            return
        editor = QTextEdit()
        editor.setStyleSheet("background-color: #0d1117; color: #f0f6fc; border: none; font-family: 'Consolas', monospace; font-size: 14px;")
        tab_name = text
        idx = self.editor_tabs.addTab(editor, tab_name)
        self.editor_tabs.setCurrentIndex(idx)
        mem_path = os.path.join(tempfile.gettempdir(), text)
        self.editor_tabs.setTabToolTip(idx, mem_path)
        self._tab_original_content[idx] = ""
        ext = text.split('.')[-1].lower() if '.' in text else 'py'
        editor.highlighter = CodeHighlighter(editor.document(), text)
        editor.textChanged.connect(lambda i=idx, ed=editor: self._on_tab_text_changed(i, ed))

    # ==========================================
    # === EXTENSION STORE ===
    # ==========================================

    def _open_store_tab_for(self, ext_dict):
        tab_name = f"📦 {ext_dict['name']}"
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i) == tab_name:
                self.editor_tabs.setCurrentIndex(i)
                return
        from .dialogs.extension_store_view import ExtensionStoreDetailTab
        detail_view = ExtensionStoreDetailTab(self, ext_dict)
        idx = self.editor_tabs.addTab(detail_view, tab_name)
        self.editor_tabs.setCurrentIndex(idx)
        self.editor_tabs.setTabToolTip(idx, f"Instalação e Detalhes de: {ext_dict['name']}")

    def _extract_user_message(self, txt):
        """Extrai mensagem personalizada do prompt do usuário.
        Ex: 'crie script lua dizendo Olá, Mundo' → 'Olá, Mundo'
        """
        import re
        # 1. Tentar extrair texto entre aspas
        quoted = re.findall(r'["\u201c\u201d](.+?)["\u201c\u201d]', txt)
        if quoted:
            return quoted[0]
        # 2. Padrões naturais em PT-BR e EN
        patterns = [
            r'(?:dizendo|que diga|que escreva|com (?:print|mensagem|texto)|escrevendo|exibindo|mostrando|printando|que exiba|que mostre|que printe|saying|that says|with message|with print)\s+["\']?(.+?)[\'"]*$',
            r'(?:print|println|echo|console\.log|puts|fmt\.Println|System\.out\.println|Console\.WriteLine)\s*\(?["\'](.+?)["\']\)?',
        ]
        for pattern in patterns:
            match = re.search(pattern, txt, re.IGNORECASE)
            if match:
                return match.group(1).strip().rstrip('.')
        return None

    def _open_hello_world(self, name, ext, custom_message=None):
        """Abre nova aba com boilerplate. Se custom_message fornecida, usa em vez de Hello World."""
        msg = custom_message or f"Hello World from {name}!"
        boilerplates = {
            "py": f"print('{msg}')\n",
            "js": f"console.log('{msg}');\n",
            "ts": f"const msg: string = '{msg}';\nconsole.log(msg);\n",
            "lua": f"print('{msg}')\n",
            "cs": f'using System;\n\nclass Program {{\n    static void Main() {{\n        Console.WriteLine("{msg}");\n    }}\n}}\n',
            "html": f'<!DOCTYPE html>\n<html>\n<head>\n  <title>{msg}</title>\n</head>\n<body>\n  <h1>{msg}</h1>\n</body>\n</html>\n',
            "css": "body {\n  background-color: #0d1117;\n  color: #c9d1d9;\n  font-family: Arial;\n}\n",
            "gd": f"extends Node\n\nfunc _ready():\n\tprint('{msg}')\n",
            "java": f'public class Main {{\n    public static void main(String[] args) {{\n        System.out.println("{msg}");\n    }}\n}}\n',
            "go": f'package main\n\nimport "fmt"\n\nfunc main() {{\n    fmt.Println("{msg}")\n}}\n',
            "rs": f'fn main() {{\n    println!("{msg}");\n}}\n',
            "php": f'<?php\necho "{msg}";\n?>\n',
            "rb": f"puts '{msg}'\n",
            "kt": f'fun main() {{\n    println("{msg}")\n}}\n',
            "swift": f'print("{msg}")\n',
            "cpp": f'#include <iostream>\nusing namespace std;\n\nint main() {{\n    cout << "{msg}" << endl;\n    return 0;\n}}\n',
            "c": f'#include <stdio.h>\n\nint main() {{\n    printf("{msg}\\n");\n    return 0;\n}}\n',
            "r": f"cat('{msg}\\n')\n",
            "jl": f'println("{msg}")\n',
            "dart": f"void main() {{\n  print('{msg}');\n}}\n",
        }
        editor = QTextEdit()
        editor.setStyleSheet("background-color: #0d1117; color: #c9d1d9; border: none; font-family: 'Consolas', monospace; font-size: 14px;")
        content = boilerplates.get(ext, f"// {msg}")
        editor.setPlainText(content)
        highlighter = CodeHighlighter(editor.document(), f"hello.{ext}")
        editor.highlighter = highlighter
        idx = self.editor_tabs.addTab(editor, f"hello.{ext}")
        self.editor_tabs.setCurrentIndex(idx)

    def _open_file_with_code(self, name, ext, code):
        """Abre uma nova aba no editor com um código específico pré-preenchido."""
        editor = QTextEdit()
        editor.setStyleSheet("background-color: #0d1117; color: #c9d1d9; border: none; font-family: 'Consolas', monospace; font-size: 14px;")
        editor.setPlainText(code)
        
        # Gera nome único
        base_name = f"script_{name.lower()}"
        file_name = f"{base_name}.{ext}"
        counter = 1
        while any(self.editor_tabs.tabText(i) == file_name for i in range(self.editor_tabs.count())):
            file_name = f"{base_name}_{counter}.{ext}"
            counter += 1
            
        highlighter = CodeHighlighter(editor.document(), file_name)
        editor.highlighter = highlighter
        idx = self.editor_tabs.addTab(editor, file_name)
        self.editor_tabs.setCurrentIndex(idx)
        self.editor_tabs.setTabToolTip(idx, file_name)
        self._tab_original_content[idx] = code
        editor.textChanged.connect(lambda i=idx, ed=editor: self._on_tab_text_changed(i, ed))

    def _open_store_tab(self):
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i) == "🛒 Loja":
                self.editor_tabs.setCurrentIndex(i)
                return
        from .dialogs.extension_store_view import ExtensionStoreWidget
        store_view = ExtensionStoreWidget(self)
        idx = self.editor_tabs.addTab(store_view, "🛒 Loja")
        self.editor_tabs.setCurrentIndex(idx)
        self.editor_tabs.setTabToolTip(idx, "Interface de Instalação e Módulos")

    # ==========================================
    # === SCRIPT RUNNER (F5) ===
    # ==========================================

    def _run_current_script(self):
        curr_idx = self.editor_tabs.currentIndex()
        if curr_idx < 0:
            self.terminal_widget.output.append("\n> [Aviso] Nenhum arquivo aberto para rodar (F5).")
            self.switch_to_terminal()
            return
        editor = self.editor_tabs.widget(curr_idx)
        code = editor.toPlainText()
        if not code.strip():
            return
        file_path = self.editor_tabs.tabToolTip(curr_idx)
        if not file_path:
            file_path = "temp.py"
        ext = 'py'
        if '.' in file_path:
            ext = file_path.split('.')[-1].lower()
        else:
            tab_title = self.editor_tabs.tabText(curr_idx).replace('*', '')
            if '.' in tab_title:
                ext = tab_title.split('.')[-1].lower()
        runner_map = {
            'py': 'python', 'js': 'node', 'ts': 'ts-node', 'lua': 'lua',
            'cs': 'csc', 'java': 'java', 'cpp': 'g++', 'html': 'python',
            'css': 'type', 'gd': 'godot -s', 'rb': 'ruby', 'kt': 'kotlin',
            'swift': 'swift', 'go': 'go run', 'rs': 'rustc', 'php': 'php',
            'r': 'Rscript', 'jl': 'julia', 'dart': 'dart',
        }
        runner = runner_map.get(ext)
        if not runner:
            self.terminal_widget.output.append(f"\n> [Aviso] Extensão .{ext} não é rodável diretamente por padrão aqui.")
            self.switch_to_terminal()
            return
        import shutil
        import sys
        base_cmd = runner.split()[0]
        if base_cmd not in ('start', 'type', 'python') and sys.platform == 'win32':
             if not shutil.which(base_cmd):
                 ext_info_map = {
                     'py': ('Python Extension Pack', 'Python'),
                     'js': ('Node.js Runtime', 'JavaScript'),
                     'ts': ('TypeScript Node Compiler', 'TypeScript'),
                     'lua': ('Lua Compiler V5', 'Lua'),
                     'cs': ('C# / .NET SDK 8', 'C#'),
                     'java': ('Java Development Kit', 'Java'),
                     'cpp': ('C/C++ Compiler (MinGW)', 'C/C++'),
                     'gd': ('Godot Script Engine', 'GDScript'),
                     'rb': ('Ruby (Rube)', 'Ruby'),
                     'kt': ('Kotlin Language', 'Kotlin'),
                     'swift': ('Swift for Windows', 'Swift'),
                     'go': ('Go (Golang)', 'Go'),
                     'rs': ('Rust Analyzer', 'Rust'),
                     'php': ('PHP Runtime', 'PHP'),
                     'r': ('R Language', 'R'),
                     'jl': ('Julia Language', 'Julia'),
                     'dart': ('Dart SDK', 'Dart'),
                 }
                 ext_name, lang_name = ext_info_map.get(ext, (f'Extensao .{ext}', ext.upper()))
                 self.terminal_widget.output.append(
                     f"\n> [Aviso Tático] Vejo que está utilizando a extensão '{ext_name}' da linguagem {lang_name}.\n"
                     f"> Vossa senhoria não possui tal extensão instalada no computador.\n"
                     f"> O comando '{base_cmd}' não foi encontrado no PATH do sistema.\n"
                     f">\n"
                     f"> Deseja baixá-la via terminal ou acessar a Loja para o download e continuidade?\n"
                     f"> ➡ Vá até a guia 'Extensoes -> Loja' e instale '{ext_name}' para rodar arquivos .{ext}\n"
                 )
                 self.switch_to_terminal()
                 return
        safe_name = os.path.splitext(os.path.basename(file_path.replace('"', '')))[0]
        if not safe_name or safe_name == "sem_titulo" or "template" in safe_name: 
            safe_name = "Program" if ext in ['java', 'cs'] else "ai_script"
        temp_file = os.path.join(tempfile.gettempdir(), f"{safe_name}.{ext}")
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            self.terminal_widget.output.append(f"\n> [Erro] Falha ao salvar temporário: {e}")
            return
        if ext == 'py':
            cmd = f'"{sys.executable}" "{temp_file}"'
        elif ext == 'js':
            cmd = f'node "{temp_file}"'
        elif ext == 'html':
            cmd = f'"{sys.executable}" -c "import os; os.startfile(r\'{temp_file}\')"'
        elif ext == 'css':
            cmd = f'"{sys.executable}" -c "import os; os.startfile(r\'{temp_file}\')"'
        elif ext == 'gd':
            cmd = f'godot --headless --script "{temp_file}"'
        elif ext == 'lua':
            cmd = f'lua "{temp_file}"'
        elif base_cmd == 'g++':
            import uuid
            exe_path = os.path.join(tempfile.gettempdir(), f"{safe_name}_{uuid.uuid4().hex[:6]}.exe")
            cmd = f'g++ "{temp_file}" -o "{exe_path}" && "{exe_path}"'
        elif ext == 'java':
            temp_dir = tempfile.gettempdir()
            cmd = f'cd /d "{temp_dir}" && java "{safe_name}.java"'
        elif ext == 'cs':
            cb_dir = os.path.join(tempfile.gettempdir(), f"cs_ai_{safe_name}")
            os.makedirs(cb_dir, exist_ok=True)
            with open(os.path.join(cb_dir, "Program.cs"), 'w', encoding='utf-8') as f: f.write(code)
            with open(os.path.join(cb_dir, "temp.csproj"), 'w', encoding='utf-8') as f: 
                f.write('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
            cmd = f'cd /d "{cb_dir}" && dotnet run'
        elif base_cmd == 'go':
            cmd = f'go run "{temp_file}"'
        elif base_cmd == 'rustc':
            import uuid
            exe_path = os.path.join(tempfile.gettempdir(), f"{safe_name}_{uuid.uuid4().hex[:6]}.exe")
            cmd = f'rustc "{temp_file}" -o "{exe_path}" && "{exe_path}"'
        else:
            cmd = f'{runner} "{temp_file}"'
        self.switch_to_terminal()
        active_shell = self.term_combo.currentText()
        self.shell_indicator.setText(f"● {active_shell} [executando]")
        self.shell_indicator.setStyleSheet("color: #f0a030; font-size: 11px; margin-left: 8px;")
        self.terminal_widget.output.append(
            f"\n==== Executando (F5): {safe_name}.{ext} ====\n"
            f"> Shell: {active_shell}\n"
            f"> Comando construído...\n"
        )
        self.terminal_widget.output.moveCursor(QTextCursor.MoveOperation.End)
        def on_finished(exit_code, exit_status):
            self.shell_indicator.setText(f"● {active_shell}")
            self.shell_indicator.setStyleSheet("color: #3fb950; font-size: 11px; margin-left: 8px;")
            try: os.unlink(temp_file)
            except: pass
        if self.terminal_widget._script_process:
            try:
                self.terminal_widget._script_process.finished.disconnect()
            except:
                pass
        self.terminal_widget.run_script_interactive(cmd, tempfile.gettempdir(), active_shell)
        if self.terminal_widget._script_process:
            self.terminal_widget._script_process.finished.connect(on_finished)

    def switch_to_terminal(self):
        if not self.term_container.isVisible():
            self.term_container.setVisible(True)
            self.btn_term_toggle.setText("▼")

    # ==========================================
    # === STARTUP DEPENDENCY CHECK (18+) ===
    # ==========================================

    def _check_startup_dependencies(self):
        import shutil
        results = []
        deps = [
            ("Python", ["python", "python3", "py"], True),
            ("Node.js (JS)", ["node"], True),
            ("Java (JDK)", ["java", "javac"], True),
            ("Lua", ["lua", "lua54", "lua53"], True),
            ("C# (.NET)", ["dotnet", "csc"], True),
            ("HTML Preview", ["cmd"], True),
            ("CSS Preview", ["cmd"], True),
            ("Git", ["git"], False),
            ("npm", ["npm"], False),
            ("C/C++ (g++)", ["g++", "gcc"], False),
            ("Go (Golang)", ["go"], False),
            ("Rust (rustc)", ["rustc", "cargo"], False),
            ("Ruby", ["ruby"], False),
            ("PHP", ["php"], False),
            ("Kotlin", ["kotlin", "kotlinc"], False),
            ("Swift", ["swift", "swiftc"], False),
            ("Godot", ["godot"], False),
            ("Docker", ["docker"], False),
        ]
        found = 0
        total = len(deps)
        for name, executables, required in deps:
            path_found = None
            for exe in executables:
                p = shutil.which(exe)
                if p:
                    path_found = p
                    break
            if path_found:
                results.append(f"  ✅ {name}: {path_found}")
                found += 1
            else:
                icon = "❌" if required else "⚪"
                suffix = " — OBRIGATÓRIO" if required else " — instale pela Loja"
                results.append(f"  {icon} {name}: não encontrado{suffix}")
        self.terminal_widget.output.append(
            "\n╔═══════════════════════════════════════════════════╗\n"
            "║  🔍 Verificação de Dependências (Startup)          ║\n"
            f"║  📊 {found}/{total} encontradas                           ║\n"
            "╚═══════════════════════════════════════════════════╝\n"
        )
        for r in results:
            self.terminal_widget.output.append(r)
        self.terminal_widget.output.append("\n> Terminal pronto. Pressione F5 para executar scripts.\n")
        self.status.showMessage(f"Deps: {found}/{total} encontradas", 5000)

    # ==========================================
    # === CLOSE EVENT ===
    # ==========================================

    def closeEvent(self, event):
        # Salvar sessão de chat atual
        self._save_current_session()
        
        unsaved = self._get_unsaved_tab_names()
        if unsaved:
            files_list = "\n".join([f"  • {name}" for name in unsaved])
            reply = QMessageBox.question(
                self, "Arquivos Não Salvos",
                f"Os seguintes arquivos possuem modificações não salvas:\n\n{files_list}\n\n"
                "O que deseja fazer?",
                QMessageBox.StandardButton.SaveAll | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.SaveAll
            )
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.SaveAll:
                for i in range(self.editor_tabs.count()):
                    if self.editor_tabs.tabText(i).endswith("*"):
                        self.editor_tabs.setCurrentIndex(i)
                        self._save_current_file()
        if self.richie:
            try:
                self.richie._save_state()
            except Exception:
                pass
        for thread in self._threads:
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)
        if self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.quit()
            self.ai_thread.wait(1000)
        if self.terminal_widget._script_process and self.terminal_widget._script_process.state() != QProcess.ProcessState.NotRunning:
            self.terminal_widget._script_process.kill()
            self.terminal_widget._script_process.waitForFinished(1000)
        event.accept()