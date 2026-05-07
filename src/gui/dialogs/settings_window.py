"""
Janela de Configurações — Estilo v0.3.5-alpha
Com acesso direto ao Consulta de IAs (BotForge Studio)
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QWidget, QPushButton, QFormLayout,
    QCheckBox, QComboBox, QKeySequenceEdit, QMessageBox,
    QScrollArea, QGridLayout, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsWindow(QDialog):
    """Janela de Configurações — paleta v0.3.5-alpha"""

    def __init__(self, custom_ai_manager, parent=None):
        super().__init__(parent)
        self.manager = custom_ai_manager
        self.setWindowTitle("⚙️ Configurações do Assistente")
        self.setMinimumSize(620, 520)
        self.setStyleSheet(self._get_styles())
        self._setup_ui()

    def _get_styles(self):
        return """
            QDialog { background-color: #0d1117; color: #c9d1d9; }
            QLabel { color: #8b949e; font-size: 13px; }
            QTabWidget::pane { border: 1px solid #30363d; background-color: #161b22; border-radius: 4px; }
            QTabBar::tab { background-color: #0d1117; color: #8b949e; padding: 8px 20px; border: none; }
            QTabBar::tab:selected { background-color: #1c2128; color: #f0f6fc; border-top: 2px solid #58a6ff; }
            QPushButton { background-color: #21262d; border: 1px solid #30363d; padding: 8px 16px; color: #c9d1d9; border-radius: 3px; font-weight: bold; }
            QPushButton:hover { background-color: #30363d; }
            QPushButton#primary { background-color: #1f6feb; color: white; border: none; font-weight: bold; }
            QPushButton#primary:hover { background-color: #388bfd; }
            QComboBox { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px; }
            QCheckBox { color: #8b949e; }
            QKeySequenceEdit { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px; }
            QLineEdit { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px; border-radius: 4px; }
            QScrollArea { border: none; background-color: transparent; }
        """

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header
        header = QLabel("Configurações do AI Code Assistant")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: white; margin-bottom: 5px;")
        layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # === Tab: Opções ===
        options_tab = QWidget()
        opt_layout = QFormLayout(options_tab)
        opt_layout.setSpacing(15)
        opt_layout.setContentsMargins(20, 20, 20, 20)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["VS Code Dark (v0.3.5)", "VS Code Light", "High Contrast"])
        opt_layout.addRow("Tema de Interface:", self.theme_combo)

        self.auto_save = QCheckBox("Salvar arquivos automaticamente")
        opt_layout.addRow("", self.auto_save)

        self.show_terminal = QCheckBox("Mostrar Terminal na inicialização")
        self.show_terminal.setChecked(True)
        opt_layout.addRow("", self.show_terminal)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["DeepSeek (Econômico)", "OpenAI GPT-4", "Anthropic Claude", "Todos"])
        opt_layout.addRow("Provider Padrão:", self.provider_combo)

        tabs.addTab(options_tab, "⚙️ Opções")

        # === Tab: Ferramentas ===
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        tools_layout.setContentsMargins(20, 20, 20, 20)

        tools_info = QLabel(
            "Ferramentas integradas:\n\n"
            "• 📋 Editor de Código com Syntax Highlighting (Pygments)\n"
            "• 🖥 Terminal Integrado (CMD/PowerShell/Bash)\n"
            "• 💬 Chat com IA (Streaming Real)\n"
            "• 🤖 Gerenciador de IAs Customizadas\n"
            "• 📤 Exportação/Importação BotForge JSON\n"
            "• 🧠 Sistema de Treinamento Avançado\n"
            "• 🧩 Extensões Hello World (Python, Lua, JS, C#, HTML, Godot...)\n"
            "• ▶️ Execução via F5 no Terminal"
        )
        tools_info.setStyleSheet("color: #cccccc; font-size: 12px; line-height: 1.6;")
        tools_layout.addWidget(tools_info)

        # Card BotForge Studio
        bf_card = QFrame()
        bf_card.setFixedHeight(110)
        bf_card.setStyleSheet("QFrame { background-color: #21262d; border: 1px solid #30363d; border-top: 3px solid #58a6ff; border-radius: 8px; }")
        bf_cl = QVBoxLayout(bf_card)
        bf_title = QLabel("🛠 BotForge Studio Local v1.0")
        bf_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        bf_title.setStyleSheet("color: white; border: none; background: transparent;")
        bf_cl.addWidget(bf_title)
        bf_desc = QLabel("Crie, importe e gerencie seus bots de IA diretamente\nno desktop. Fluxo visual, cards e conexões integradas.")
        bf_desc.setStyleSheet("color: #8b949e; font-size: 11px; border: none; background: transparent;")
        bf_cl.addWidget(bf_desc)
        bf_btn = QPushButton("Abrir BotForge Studio")
        bf_btn.setStyleSheet("background-color: #1f6feb; color: white; border: none; font-weight: bold; padding: 6px; border-radius: 4px;")
        bf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bf_btn.clicked.connect(self._open_ai_consult)
        bf_cl.addWidget(bf_btn)
        tools_layout.addWidget(bf_card)

        tools_layout.addStretch()
        tabs.addTab(tools_tab, "🔧 Ferramentas")

        # === Tab: Atalhos ===
        keys_tab = QWidget()
        keys_layout = QFormLayout(keys_tab)
        keys_layout.setSpacing(15)
        keys_layout.setContentsMargins(20, 20, 20, 20)

        self.key_send = QKeySequenceEdit()
        keys_layout.addRow("Enviar Mensagem:", self.key_send)

        self.key_run = QKeySequenceEdit()
        keys_layout.addRow("Executar Código (F5):", self.key_run)

        self.key_save = QKeySequenceEdit()
        keys_layout.addRow("Salvar Arquivo:", self.key_save)

        tabs.addTab(keys_tab, "\u2328\ufe0f Atalhos")

        # === Tab: Suas IAs ===
        self.ai_tab = QWidget()
        ai_layout = QVBoxLayout(self.ai_tab)
        ai_layout.setContentsMargins(10, 10, 10, 10)
        
        self.ai_scroll = QScrollArea()
        self.ai_scroll.setWidgetResizable(True)
        self.ai_grid_widget = QWidget()
        self.ai_grid_widget.setStyleSheet("background-color: transparent;")
        self.ai_grid = QGridLayout(self.ai_grid_widget)
        self.ai_scroll.setWidget(self.ai_grid_widget)
        ai_layout.addWidget(self.ai_scroll)
        self._load_ai_cards()
        tabs.addTab(self.ai_tab, "\U0001f916 Suas IAs")

        # === Tab: Conexões IA ===
        conn_tab = QWidget()
        conn_layout = QVBoxLayout(conn_tab)
        conn_scroll = QScrollArea()
        conn_scroll.setWidgetResizable(True)
        conn_widget = QWidget()
        conn_widget.setStyleSheet("background-color: transparent;")
        conn_grid = QGridLayout(conn_widget)
        
        providers = [
            ("Claude", "\U0001f7e0", "#d97706"),
            ("OpenAI", "\U0001f7e2", "#10b981"),
            ("DeepSeek", "\U0001f7e3", "#6366f1")
        ]
        row, col = 0, 0
        for name, icon, color in providers:
            card = self._create_provider_card(name, icon, color)
            conn_grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        conn_scroll.setWidget(conn_widget)
        conn_layout.addWidget(conn_scroll)
        tabs.addTab(conn_tab, "\U0001f517 Conex\u00f5es IA")

        # === Botões do rodapé ===
        btn_layout = QHBoxLayout()

        # Botão Consulta de IAs (BotForge)
        btn_consult = QPushButton("📋 Consulta de IAs (BotForge)")
        btn_consult.setObjectName("primary")
        btn_consult.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_consult.clicked.connect(self._open_ai_consult)
        btn_layout.addWidget(btn_consult)

        btn_layout.addStretch()

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _open_ai_consult(self):
        """Abre a janela de Consulta de IAs (BotForge Studio)"""
        try:
            from .ai_consult import AIConsultWindow
            self.consult_win = AIConsultWindow(self.manager, self, main_window=self.parent())
            self.consult_win.exec()
        except ImportError as e:
            QMessageBox.critical(self, "Erro de Importação",
                                 f"Módulo ai_consult não encontrado.\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro",
                                 f"Falha ao abrir Consulta de IAs:\n{str(e)}")

    def _create_provider_card(self, name, icon, color):
        frame = QFrame()
        frame.setFixedSize(260, 160)
        frame.setStyleSheet(f"QFrame {{ background-color: #21262d; border: 1px solid #30363d; border-top: 3px solid {color}; border-radius: 8px; }}")
        layout = QVBoxLayout(frame)
        
        header = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        header.addWidget(lbl_icon)
        
        lbl_name = QLabel(name)
        lbl_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: white; border: none; background: transparent;")
        header.addWidget(lbl_name)
        
        lbl_status = QLabel("\ud83d\udd34 Desconectado")
        lbl_status.setStyleSheet("color: #8b949e; font-size: 10px; border: none; background: transparent;")
        header.addWidget(lbl_status)
        header.addStretch()
        layout.addLayout(header)
        
        layout.addWidget(QLabel("API Key:", styleSheet="color: #8b949e; border: none; background: transparent;"))
        api_input = QLineEdit()
        api_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_input.setPlaceholderText(f"sk-{name.lower()}...")
        layout.addWidget(api_input)
        
        btn_test = QPushButton("Testar Conex\u00e3o")
        btn_test.setStyleSheet("background-color: #30363d; border: none; padding: 6px; border-radius: 4px; color: white;")
        layout.addWidget(btn_test)
        
        return frame

    def _load_ai_cards(self):
        # Limpar widgets atuais (caso seja um reload)
        for i in reversed(range(self.ai_grid.count())):
            w = self.ai_grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        models = self.manager.list_models() if self.manager else []
        row, col = 0, 0
        for model in models:
            card = QFrame()
            card.setFixedSize(260, 100)
            card.setStyleSheet("QFrame { background-color: #21262d; border: 1px solid #30363d; border-radius: 6px; }")
            
            # Layout principal do card
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 10, 10, 10)
            
            # Layout Superior (Título e Lixeira)
            top_layout = QHBoxLayout()
            title = QLabel(f"🤖 {model.name}")
            title.setStyleSheet("font-weight: bold; color: white; border: none; font-size: 13px;")
            top_layout.addWidget(title)
            
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(24, 24)
            btn_del.setStyleSheet("""
                QPushButton { background: transparent; color: #f85149; border: none; border-radius: 4px; font-size: 14px; }
                QPushButton:hover { background: rgba(248,81,73,0.15); }
            """)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.clicked.connect(lambda checked, m_id=model.id: self._delete_ai_model(m_id))
            top_layout.addWidget(btn_del)
            cl.addLayout(top_layout)
            
            # Descrição
            desc = QLabel(f"Provider: {model.base_provider}\nMode: {model.base_model}\nID: {model.id[:8]}")
            desc.setStyleSheet("color: #8b949e; font-size: 11px; border: none;")
            cl.addWidget(desc)
            
            self.ai_grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def _delete_ai_model(self, model_id):
        reply = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja excluir esta IA permanentemente?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.delete_model(model_id):
                self._load_ai_cards()
            else:
                QMessageBox.warning(self, "Erro", "Falha ao excluir o modelo.")
