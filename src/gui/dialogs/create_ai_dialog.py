"""
Dialog para criação de IAs/Bots — Estilo BotForge Studio
6 abas: Dados Básicos, Fluxo, Chat Teste, Personalidade, Config Bot, Catálogo
Paleta v0.3.5-alpha | Rev 17.0.4
"""
import json
import random
import uuid
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QFrame, QSlider,
    QSpinBox, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QGroupBox, QScrollArea, QGridLayout,
    QCheckBox, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QGraphicsEllipseItem,
    QMenu, QInputDialog, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF, QLineF, QPoint, QTimer
from PyQt6.QtGui import QFont, QPainterPath, QPen, QBrush, QColor, QPainter, QTransform

from ...core.custom_ai_manager import (
    CustomAIManager, CustomAIModel,
    AVAILABLE_BASE_MODELS, AI_TEMPLATES
)


# ========== CATALOGO DE CARDS BOTFORGE ==========
BOTFORGE_CARD_CATALOG = {
    "🔄 Fluxo": [
        ("greeting", "Saudação", "#22c55e"),
        ("question", "Pergunta", "#6366f1"),
        ("condition", "Condição", "#f59e0b"),
        ("action", "Ação", "#ef4444"),
        ("menu", "Menu", "#8b5cf6"),
        ("transfer", "Transferir", "#14b8a6"),
        ("end", "Encerrar", "#6b7280"),
        ("delay", "Delay", "#ca8a04"),
    ],
    "🧠 IA & NLP": [
        ("ai_response", "Resposta IA", "#06b6d4"),
        ("combo_keyword", "ComboBox Keywords", "#c026d3"),
        ("keyword", "Palavra-Chave", "#a855f7"),
        ("nlp_intent", "Intenção NLP", "#7c3aed"),
        ("sentiment", "Sentimento", "#ec4899"),
        ("context_mem", "Memória", "#0ea5e9"),
        ("nlp", "NLP Router", "#c026d3"),
        ("identity_ai", "Identidade IA", "#f43f5e"),
        ("identity_app", "Identidade AI Code", "#10b981"),
    ],
    "💻 Execução & Scripts": [
        ("exec_route", "Rota de Execução", "#dc2626"),
        ("detect_lang", "Detectar Linguagem", "#f59e0b"),
        ("ide_open_tab", "Abrir Guia IDE", "#2563eb"),
        ("ide_create_file", "Criar Arquivo", "#10b981"),
        ("ide_run_script", "Rodar Script (F5)", "#db2777"),
        ("ide_read_output", "Ler Output do Terminal", "#8b5cf6"),
        ("exec_powershell", "Rodar PowerShell (Win)", "#0ea5e9"),
        ("exec_bash", "Rodar Bash (Linux)", "#f59e0b"),
        ("exec_select_string", "Select-String (Grep/Busca)", "#ec4899"),
    ],
    "🗃️ Manipulação & Arquivos [NOVO]": [
        ("file_read", "Ler Arquivo/Doc", "#0284c7"),
        ("file_write", "Editar/Escrever Arquivo", "#ea580c"),
        ("file_backup", "Backup de Arquivos/Dir", "#16a34a"),
        ("file_analysis", "Análise de Documento", "#8b5cf6"),
    ],
    "📥 Recebimento": [
        ("recv_text", "Receber Texto", "#6366f1"),
        ("recv_audio", "Receber Áudio", "#f97316"),
        ("recv_image", "Receber Imagem", "#eab308"),
        ("recv_video", "Receber Vídeo", "#dc2626"),
        ("recv_doc", "Receber Doc", "#16a34a"),
        ("recv_location", "Receber Local", "#0d9488"),
        ("input_email", "Input Email", "#0ea5e9"),
        ("input_cpf", "Input CPF", "#059669"),
        ("input_number", "Input Número", "#8b5cf6"),
        ("recv", "Receber Msg", "#f97316"),
    ],
    "📤 Envio": [
        ("send_msg", "Enviar Msg", "#6366f1"),
        ("send_audio", "Enviar Áudio", "#f97316"),
        ("send_image", "Enviar Imagem", "#eab308"),
        ("send_video", "Enviar Vídeo", "#dc2626"),
        ("send_doc", "Enviar Doc", "#16a34a"),
        ("send_sticker", "Sticker", "#d946ef"),
        ("send_location", "Enviar Local", "#0d9488"),
        ("send_buttons", "Botões", "#7c5cfc"),
        ("send_list", "Lista", "#6366f1"),
    ],
    "🔗 Integrações": [
        ("api_call", "API Call", "#8b5cf6"),
        ("webhook", "Webhook", "#6d28d9"),
        ("database", "Banco Dados", "#84cc16"),
        ("crm", "CRM", "#0891b2"),
        ("email_send", "Email", "#be185d"),
        ("schedule", "Agendar", "#ca8a04"),
    ],
    "🚀 Avançado": [
        ("triage", "Triagem Msgs", "#f97316"),
        ("ctx_an", "Análise Contexto", "#8b5cf6"),
        ("notify", "Notificar Mestre", "#ef4444"),
        ("agenda", "Agenda", "#22c55e"),
        ("busca", "Busca Web", "#06b6d4"),
        ("task", "Tarefas", "#eab308"),
        ("script_execution", "🛠️ Execução de Script", "#10b981"),
    ],
    "🔌 API & Conexão [NOVO]": [
        ("api_connector", "🔌 API Connector (ComboBox)", "#f59e0b"),
        ("api_entry", "🔌 API Entrada (ComboBox)", "#7c5cfc"),
        ("api_connect", "🌐 Conexão IA/Bot", "#2563eb"),
        ("api_config", "⚙️ Config Provider", "#f59e0b"),
        ("api_auth", "🔐 Autenticação", "#ef4444"),
        ("api_health", "💚 Health Check", "#22c55e"),
        ("api_endpoint", "📡 Endpoint Viewer", "#06b6d4"),
    ],
    "📄 Documentação [NOVO]": [
        ("doc_qa", "📋 Modelo Padrão QA", "#8b5cf6"),
        ("doc_sprint", "🏃 Sprint Plan", "#3b82f6"),
        ("doc_changelog", "📜 Changelog", "#22c55e"),
        ("doc_readme", "📖 README", "#f59e0b"),
        ("doc_presentation", "📊 Apresentação", "#ec4899"),
        ("doc_contract", "📝 Contrato", "#78909c"),
        ("doc_history", "📚 Histórico Versões", "#14b8a6"),
    ],
    "🧬 Mapeamento Neural [NOVO]": [
        ("neural_map", "🧬 Mapeamento Documental Neural", "#c026d3"),
        ("neural_context", "🧠 Contexto Profundo", "#7c3aed"),
        ("neural_index", "📑 Índice de Conhecimento", "#0ea5e9"),
    ],
}

class HoldToConfirmButton(QPushButton):
    def __init__(self, text, hold_time_ms=5000, parent=None, on_confirm=None):
        super().__init__(text, parent)
        self.hold_time_ms = hold_time_ms
        self.original_text = text
        self.on_confirm = on_confirm
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)
        self.progress = 0
        self._is_completed = False
        
        self.base_style = "background-color: transparent; color: #8b949e; border: 1px solid transparent;"
        self.setStyleSheet(self.base_style)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._is_completed:
            self.progress = 0
            self.timer.start(50)
            self.setText("Deletando...")
            self._update_gradient()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._is_completed:
            self.timer.stop()
            self.progress = 0
            self.setText(self.original_text)
            self.setStyleSheet(self.base_style)
        super().mouseReleaseEvent(event)
        
    def _update_gradient(self):
        pct = self.progress / self.hold_time_ms
        # Pequeno avanço visual
        self.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #ef4444, stop:{max(0.001, pct)} #ef4444, 
                stop:{min(1.0, pct+0.001)} #21262d, stop:1 #21262d);
            color: white; border-radius: 4px;
        """)

    def _on_timeout(self):
        self.progress += 50
        self._update_gradient()
        
        if self.progress >= self.hold_time_ms:
            self.timer.stop()
            self._is_completed = True
            
            # Chama a função acoplada se houver, se nao, cai pro default (node deletar config gui)
            if self.on_confirm:
                self.on_confirm()
                
                # Reseta para poder re-usar? Sim
                QTimer.singleShot(1000, self._reset_btn)
            else:
                self._trigger_security_modal()
                
    def _reset_btn(self):
        self._is_completed = False
        self.progress = 0
        self.setText(self.original_text)
        self.setStyleSheet(self.base_style)
            
    def _trigger_security_modal(self):
        self.setText("Processando...")
        
        msg = QMessageBox(self.window())
        msg.setWindowTitle("⚠️ Ação Perigosa")
        msg.setText("Você está deletando informações cerebrais do BotForge.")
        msg.setInformativeText("Esta ação é destrutiva e afeta o fluxo ao salvar.\n\nPor favor, leia esta mensagem (Desbloqueando em 5s).")
        msg.setIcon(QMessageBox.Icon.Warning)
        
        btn_yes = msg.addButton("Sim, Desejo excluir", QMessageBox.ButtonRole.AcceptRole)
        btn_no = msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        btn_yes.setEnabled(False)
        msg.setDefaultButton(btn_no)
        
        unlock_timer = QTimer(msg)
        unlock_timer.setSingleShot(True)
        unlock_timer.timeout.connect(lambda: btn_yes.setEnabled(True))
        unlock_timer.start(5000)
        
        msg.exec()
        
        if msg.clickedButton() == btn_yes:
            self.clicked.emit()
            self.setText("Deletado")
        else:
            self._is_completed = False
            self.setText(self.original_text)
            self.setStyleSheet(self.base_style)

import json

class CollapsibleLangWidget(QWidget):
    def __init__(self, lang_code, lang_name, initial_text="", parent=None):
        super().__init__(parent)
        self.lang_code = lang_code
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self.btn_toggle = QPushButton(f"▼ {lang_name} ({lang_code})")
        self.btn_toggle.setStyleSheet("background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; text-align: left; padding: 5px; font-weight: bold;")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_collapse)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Palavras-chave separadas por vírgula...")
        self.text_edit.setStyleSheet("background-color: #0d1117; color: #a5d6ff; font-size: 11px; border: 1px solid #30363d; border-radius: 4px; padding: 5px;")
        self.text_edit.setMinimumHeight(60)
        self.text_edit.setMaximumHeight(80)
        self.text_edit.setPlainText(initial_text)
        
        layout.addWidget(self.btn_toggle)
        layout.addWidget(self.text_edit)
        
        self.is_collapsed = False
        
    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        self.text_edit.setVisible(not self.is_collapsed)
        arrow = "▶" if self.is_collapsed else "▼"
        self.btn_toggle.setText(f"{arrow} {self.btn_toggle.text().split(' ', 1)[1]}")

class MultiLanguageKeywordsWidget(QWidget):
    def __init__(self, initial_json_str="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        header_lay = QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        
        self.combo_langs = QComboBox()
        self.combo_langs.addItems([
            "Português Brasil (pt_BR)",
            "Inglês (en_US)",
            "Espanhol (es_ES)",
            "Português Portugal (pt_PT)",
            "Francês (fr_FR)"
        ])
        self.combo_langs.setStyleSheet("background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px;")
        
        self.btn_add = QPushButton("+ Adicionar Idioma")
        self.btn_add.setStyleSheet("background-color: #238636; color: white; border-radius: 4px; padding: 4px 10px; font-weight: bold;")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_language)
        
        header_lay.addWidget(self.combo_langs)
        header_lay.addWidget(self.btn_add)
        self.layout.addLayout(header_lay)
        
        self.langs_container = QVBoxLayout()
        self.langs_container.setSpacing(5)
        self.layout.addLayout(self.langs_container)
        
        self.lang_widgets = []
        
        data = {}
        if initial_json_str:
            try:
                data = json.loads(initial_json_str)
                if not isinstance(data, dict):
                    data = {"pt_BR": str(initial_json_str)}
            except:
                data = {"pt_BR": str(initial_json_str)}
                
        # Forçar idiomas base se não existirem
        if "pt_BR" not in data: data["pt_BR"] = ""
        if "en_US" not in data: data["en_US"] = ""
        if "es_ES" not in data: data["es_ES"] = ""
            
        for k, v in data.items():
            name = k
            for idx in range(self.combo_langs.count()):
                if k in self.combo_langs.itemText(idx):
                    name = self.combo_langs.itemText(idx).split(' (')[0]
                    break
            self._create_lang_widget(k, name, v)
            
    def add_language(self):
        sel = self.combo_langs.currentText()
        if " (" in sel:
            name, code = sel.split(' (')
            code = code.replace(')', '')
        else:
            name = sel
            code = sel
            
        for lw in self.lang_widgets:
            if lw.lang_code == code:
                return
        self._create_lang_widget(code, name, "")
        
    def _create_lang_widget(self, code, name, text):
        lw = CollapsibleLangWidget(code, name, text)
        lw.text_edit.textChanged.connect(lambda l=lw: self._on_text_changed(l))
        self.langs_container.addWidget(lw)
        self.lang_widgets.append(lw)
        
    def _on_text_changed(self, source_lw):
        txt = source_lw.text_edit.toPlainText()
        # Copiar para os outros que estiverem vazios
        for lw in self.lang_widgets:
            if lw != source_lw and not lw.text_edit.toPlainText().strip():
                lw.text_edit.blockSignals(True)
                lw.text_edit.setPlainText(txt)
                lw.text_edit.blockSignals(False)
        
    def toPlainText(self):
        data = {}
        for lw in self.lang_widgets:
            txt = lw.text_edit.toPlainText().strip()
            if txt:
                data[lw.lang_code] = txt
        return json.dumps(data, ensure_ascii=False)

class NodeConfigModal(QDialog):
    def __init__(self, node_id, node_type, label, message, color, out_labels, out_colors, out_keywords=None, parent=None, extra_data=None):
        super().__init__(parent)
        self.out_keywords = out_keywords or []
        self.extra_data = extra_data or {}
        self._node_label = label  # Armazenar label para detecção de identidade
        self.setWindowTitle(f"{label} ({node_type})")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog { background-color: #161b22; color: #c9d1d9; border-radius: 8px; border: 1px solid #30363d; }
            QLabel { color: #8b949e; font-size: 11px; font-weight: bold; }
            QLineEdit, QTextEdit, QComboBox { 
                background-color: #0d1117; border: 1px solid #30363d; 
                border-radius: 6px; padding: 10px; color: #c9d1d9; font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus { border-color: #a371f7; }
            QGroupBox { border: 1px solid #30363d; border-radius: 6px; padding-top: 15px; margin-top: 10px; }
            QGroupBox::title { color: #a371f7; left: 10px; top: -8px; }
            QPushButton { background-color: #a371f7; color: white; border-radius: 6px; padding: 8px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #bf8eff; }
            QPushButton#btn_cancel { background-color: transparent; color: #8b949e; border: 1px solid transparent; }
            QPushButton#btn_cancel:hover { color: white; border: 1px solid #30363d; background-color: #21262d; }
        """)
        
        main_layout = QVBoxLayout(self)
        
        # Header
        lbl_head = QLabel(f"🤖 Configuração de Node")
        lbl_head.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding-bottom: 5px;")
        main_layout.addWidget(lbl_head)
        
        lbl_sub = QLabel(f"ID: {node_id}   |   Tipo: {node_type}")
        main_layout.addWidget(lbl_sub)
        
        # Rotulo & Desc
        main_layout.addSpacing(15)
        main_layout.addWidget(QLabel("RÓTULO"))
        self.inp_name = QLineEdit(label)
        main_layout.addWidget(self.inp_name)
        
        main_layout.addSpacing(10)
        
        if node_type in ("exec_powershell", "exec_bash", "exec_select_string", "ide_run_script", "file_read", "file_write", "file_backup"):
            main_layout.addWidget(QLabel("SCRIPT / COMANDO / CÓDIGO FONTE"))
            self.inp_desc = QTextEdit()
            self.inp_desc.setStyleSheet("font-family: Consolas, monospace; background-color: #0d1117; color: #58a6ff; border: 1px solid #30363d; border-radius: 4px; padding: 5px;")
            self.inp_desc.setMinimumHeight(150)
            self.inp_desc.setPlaceholderText("Insira o script ou comando aqui...")
        elif node_type in ("detect_lang", "file_analysis", "ctx_an"):
            main_layout.addWidget(QLabel("DIRETRIZES DE ANÁLISE / INSTRUÇÕES"))
            self.inp_desc = QTextEdit()
            self.inp_desc.setStyleSheet("background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; padding: 5px;")
            self.inp_desc.setMinimumHeight(120)
            self.inp_desc.setPlaceholderText("Descreva as regras de análise técnica...")
        elif "código" in label.lower() or "code" in label.lower():
            main_layout.addWidget(QLabel("LINGUAGEM ALVO (ex: Python, JS)"))
            self.inp_lang = QLineEdit()
            self.inp_lang.setPlaceholderText("Python")
            if extra_data and "target_language" in extra_data:
                self.inp_lang.setText(extra_data["target_language"])
            main_layout.addWidget(self.inp_lang)
            
            main_layout.addWidget(QLabel("INSTRUÇÕES / CONTEXTO DA GERAÇÃO"))
            self.inp_desc = QTextEdit()
            self.inp_desc.setPlaceholderText("Ex: Crie um script otimizado...")
            self.inp_desc.setMinimumHeight(80)
            
            # checkboxes options
            self.chk_comments = QCheckBox("Gerar com comentários detalhados")
            self.chk_perf = QCheckBox("Focar em otimização/performance")
            if extra_data:
                self.chk_comments.setChecked(extra_data.get("comments", False))
                self.chk_perf.setChecked(extra_data.get("performance", False))
            main_layout.addWidget(self.chk_comments)
            main_layout.addWidget(self.chk_perf)
        elif "executar" in label.lower() or "rodar" in label.lower():
            main_layout.addWidget(QLabel("MENSAGEM DE APROVAÇÃO (Chat)"))
            self.inp_desc = QTextEdit()
            self.inp_desc.setPlaceholderText("Ex: Por segurança, preciso da sua permissão para rodar isto.")
            self.inp_desc.setMinimumHeight(60)

            main_layout.addWidget(QLabel("OPÇÕES DE BOTÕES DE APROVAÇÃO"))
            self.chk_approve = QCheckBox("Aprovado (Apenas Agora)")
            self.chk_approve.setChecked(True)
            self.chk_approve.setEnabled(False) # Obrigatório
            self.chk_always_session = QCheckBox("Sempre Liberar Sessão atual")
            self.chk_always_global = QCheckBox("Sempre Liberar todas as sessões")
            self.chk_deny = QCheckBox("Negado")
            self.chk_deny.setChecked(True)
            self.chk_deny.setEnabled(False) # Obrigatório

            if extra_data:
                self.chk_always_session.setChecked(extra_data.get("btn_session", True))
                self.chk_always_global.setChecked(extra_data.get("btn_global", False))
            else:
                self.chk_always_session.setChecked(True)

            main_layout.addWidget(self.chk_approve)
            main_layout.addWidget(self.chk_always_session)
            main_layout.addWidget(self.chk_always_global)
            main_layout.addWidget(self.chk_deny)
        else:
            main_layout.addWidget(QLabel("DESCRIÇÃO / MATCH"))
            self.inp_desc = QTextEdit()
            self.inp_desc.setPlaceholderText("Intenção por texto/áudio/imagem")
            self.inp_desc.setMaximumHeight(80)
            
        self.inp_desc.setText(message)
        main_layout.addWidget(self.inp_desc)
        
        # Artificial Rotas para Router / Triage dinâmico
        self.route_inputs = []
        if out_labels:
            gp = QGroupBox("ROTAS DE INTENÇÃO")
            gplay = QVBoxLayout(gp)
            for i, r_text in enumerate(out_labels):
                route_container = QWidget()
                rc_layout = QVBoxLayout(route_container)
                rc_layout.setContentsMargins(0, 0, 0, 0)
                rc_layout.setSpacing(2)
                
                hl = QHBoxLayout()
                hl.setContentsMargins(0, 0, 0, 0)
                
                # Botão de Cor substituindo o emoji fixo
                btn_color = QPushButton("●")
                c = out_colors[i] if (out_colors and i < len(out_colors)) else "#58a6ff"
                btn_color.setStyleSheet(f"background-color: transparent; border: none; color: {c}; font-size: 16px;")
                btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_color.clicked.connect(lambda checked, idx=i, btn=btn_color: self._pick_color(idx, btn))

                rt_inp = QLineEdit(r_text)
                rt_inp.setStyleSheet("background-color: transparent; border: none; font-weight: bold; color: white;")
                
                btn_expand = QPushButton("⚙️")
                btn_expand.setStyleSheet("background-color: transparent; border: none; color: #8b949e;")
                
                btn_del = HoldToConfirmButton("🗑")
                
                hl.addWidget(btn_color)
                hl.addWidget(rt_inp)
                hl.addWidget(btn_expand)
                hl.addWidget(btn_del)
                
                # Micro-formulário oculto
                sub_form = QWidget()
                sflay = QVBoxLayout(sub_form)
                sflay.setContentsMargins(10, 5, 10, 5)
                
                is_code_node = any(x in node_type.lower() for x in ["api", "connector", "code", "script"])
                
                if is_code_node:
                    sub_inp = QTextEdit()
                    sub_inp.setPlaceholderText("// Escreva a lógica de código aqui (ex: JavaScript, Python)\n// Para 'Conectar': Lógica de acionamento do ComboBox\n// Para 'Configurar': Lógica de mapeamento e propriedades do campo")
                    sub_inp.setStyleSheet("background-color: #0d1117; color: #a5d6ff; font-family: Consolas, monospace; font-size: 12px; border: 1px solid #30363d; border-radius: 4px; padding: 5px;")
                    sub_inp.setMinimumHeight(120)
                    
                    if self.out_keywords and i < len(self.out_keywords) and str(self.out_keywords[i]).strip():
                        sub_inp.setPlainText(str(self.out_keywords[i]))
                    else:
                        # Injetar template boilerplate n8n-style se for api connector
                        if "api" in node_type.lower() or "connector" in node_type.lower():
                            if r_text.lower() == "conectar":
                                sub_inp.setPlainText("// Lógica de Acionamento (Conexão)\nconst payload = {\n  provider: node.extra_data.base_provider,\n  model: node.extra_data.base_model,\n  prompt: msg.content\n};\nreturn payload;")
                            elif r_text.lower() == "configurar":
                                sub_inp.setPlainText("// Lógica de Configuração do ComboBox\nconst options = {\n  temperature: node.extra_data.temperature,\n  max_tokens: node.extra_data.max_tokens\n};\nreturn options;")
                elif "nlp" in node_type.lower():
                    # Suporte avançado Multi-Idiomas
                    initial = ""
                    if self.out_keywords and i < len(self.out_keywords) and str(self.out_keywords[i]).strip():
                        initial = str(self.out_keywords[i])
                    else:
                        default_kws = {
                            "sauda": {"pt_BR": "oi, ola, bom dia, boa tarde, boa noite", "en_US": "hi, hello, good morning, good afternoon, good evening", "es_ES": "hola, buenos dias, buenas tardes, buenas noches"},
                            "anális": {"pt_BR": "analise, revise, verifique, avaliar", "en_US": "analyze, review, revise, verify, evaluate", "es_ES": "analiza, revisa, verifica, evaluar"},
                            "gerar": {"pt_BR": "crie, gere, escreva, programe, codigo, script", "en_US": "create, generate, write, program, code, script", "es_ES": "crea, genera, escribe, programa, codigo, script"},
                            "explic": {"pt_BR": "explique, como funciona, o que faz, ensine", "en_US": "explain, how it works, what it does, teach", "es_ES": "explica, como funciona, que hace, enseña"},
                            "debug": {"pt_BR": "erro, bug, falha, nao funciona", "en_US": "error, bug, crash, failure, doesn't work", "es_ES": "error, bug, fallo, no funciona"},
                            "execut": {"pt_BR": "execute, rode, rodar, teste, compilar", "en_US": "execute, run, test, compile", "es_ES": "ejecuta, corre, rodar, prueba, compilar"},
                            "botforge": {"pt_BR": "botforge, estudio, criar ia, gerenciar bots", "en_US": "botforge, studio, create ai, manage bots", "es_ES": "botforge, estudio, crear ia, gestionar bots"},
                            "configura": {"pt_BR": "configuracao, ajuste, preferencias, provider", "en_US": "configuration, adjust, preferences, provider", "es_ES": "configuracion, ajuste, preferencias, proveedor"},
                            "pergunta": {"pt_BR": "duvida, como fazer, diferenca, geral, sobre", "en_US": "doubt, how to, difference, general, about", "es_ES": "duda, como hacer, diferencia, general, sobre"},
                            "qa": {"pt_BR": "documento sprint, modelo qa, gerar qa", "en_US": "sprint document, qa template, generate qa", "es_ES": "documento sprint, plantilla qa, generar qa"}
                        }
                        for k, v in default_kws.items():
                            if k.lower() in r_text.lower() or r_text.lower() in k.lower():
                                initial = json.dumps(v, ensure_ascii=False)
                                break
                    sub_inp = MultiLanguageKeywordsWidget(initial, parent=self)
                elif "identity" in node_type.lower() or "identidade" in self.label.lower():
                    # Formulário de Identidade Fixo — Detalhado e Profissional
                    sub_inp = QWidget()
                    sub_form_layout = QVBoxLayout(sub_inp)
                    sub_form_layout.setContentsMargins(5, 5, 5, 5)
                    sub_form_layout.setSpacing(4)
                    
                    field_style = "background-color: #0d1117; color: #a5d6ff; border: 1px solid #30363d; border-radius: 4px; padding: 5px; font-size: 11px;"
                    label_style = "color: #8b949e; font-size: 10px; font-weight: bold; margin-top: 4px;"
                    
                    # Detectar se é Identity IA ou Identity App (por type OU por label)
                    is_identity_ai = ("identity_ai" in node_type.lower() 
                                     or "identidade ia" in self.label.lower()
                                     or ("identidade" in self.label.lower() and "code" not in self.label.lower() and "app" not in self.label.lower()))
                    
                    if is_identity_ai:
                        header = QLabel("🤖 IDENTIDADE DO MODELO DE IA")
                        header.setStyleSheet("color: #58a6ff; font-size: 12px; font-weight: bold; padding: 3px 0;")
                        sub_form_layout.addWidget(header)
                        
                        fields = [
                            ("NOME DO BOT", "botName", "Richie — IA Assistente Base"),
                            ("VERSÃO DO MODELO", "version", "v1.4.20 - 01052026"),
                            ("CRIADOR / AUTOR", "creator", "@S.V.S - Try Technology"),
                            ("TOM DE VOZ", "tone", "profissional e amigável"),
                            ("PROPRIEDADE INTELECTUAL", "propriedade_intelectual", "© 2026 @S.V.S - Try Technology. Todos os direitos reservados."),
                            ("DATA DE CRIAÇÃO", "data_criacao", "2026-04-14"),
                            ("DATA DE ATUALIZAÇÃO", "data_atualizacao", ""),
                            ("DESCRIÇÃO", "description", "IA nativa do AI Code Assistant."),
                        ]
                        self.identity_inputs = {}
                        for lbl_text, key, default in fields:
                            lbl = QLabel(lbl_text)
                            lbl.setStyleSheet(label_style)
                            sub_form_layout.addWidget(lbl)
                            w = QLineEdit(str(self.extra_data.get(key, default)))
                            w.setStyleSheet(field_style)
                            sub_form_layout.addWidget(w)
                            self.identity_inputs[key] = w
                    else:
                        header = QLabel("💻 IDENTIDADE DO PROGRAMA (AI CODE ASSISTANT)")
                        header.setStyleSheet("color: #3fb950; font-size: 12px; font-weight: bold; padding: 3px 0;")
                        sub_form_layout.addWidget(header)
                        
                        app_fields = [
                            ("VERSÃO DO PROGRAMA", "app_version", "v0.4.11-rev1.2.9-300426-Gemini"),
                            ("BUILD / REVISÃO", "app_build", "rev1.2.9-Gemini"),
                            ("AMBIENTE", "app_env", "homologacao"),
                            ("DESENVOLVEDOR", "app_developer", "@S.V.S - Try Technology"),
                            ("DATA DE RELEASE", "app_release_date", "30/04/2026"),
                        ]
                        self.identity_inputs = {}
                        for lbl_text, key, default in app_fields:
                            lbl = QLabel(lbl_text)
                            lbl.setStyleSheet(label_style)
                            sub_form_layout.addWidget(lbl)
                            w = QLineEdit(str(self.extra_data.get(key, default)))
                            w.setStyleSheet(field_style)
                            sub_form_layout.addWidget(w)
                            self.identity_inputs[key] = w
                else:
                    sub_inp = QLineEdit()
                    sub_inp.setPlaceholderText("Lógica ou palavras-chave (separadas por vírgula)")
                    sub_inp.setStyleSheet("background-color: #0d1117; font-size: 11px;")
                    if self.out_keywords and i < len(self.out_keywords) and str(self.out_keywords[i]).strip():
                        sub_inp.setText(str(self.out_keywords[i]))
                        
                sflay.addWidget(sub_inp)
                sub_form.setVisible(False)
                
                self.route_inputs.append((rt_inp, btn_color, sub_inp))
                
                btn_expand.clicked.connect(lambda chk, sf=sub_form: sf.setVisible(not sf.isVisible()))
                btn_del.clicked.connect(lambda chk, rc=route_container, rt=rt_inp: self._delete_route(rc, rt))
                
                rc_layout.addLayout(hl)
                rc_layout.addWidget(sub_form)
                gplay.addWidget(route_container)
                
            main_layout.addWidget(gp)
            
            gf = QGroupBox("CONFIGURAÇÃO DE INTELIGÊNCIA")
            gflay = QVBoxLayout(gf)
            gflay.addWidget(QLabel("MODO DE MATCH"))
            cb = QComboBox()
            cb.addItems(["Fuzzy + Keywords (recomendado)", "Strict Match", "Neural Embedding"])
            gflay.addWidget(cb)
            main_layout.addWidget(gf)
            
        # UI Dinâmica para API Connector, NLP e Configurações extras
        if any(x in node_type.lower() for x in ["api", "connector", "nlp", "router"]) or self.extra_data:
            gpa = QGroupBox("⚙️ Configurações Avançadas (Sprint 31)")
            gpalay = QVBoxLayout(gpa)
            
            gpalay.addWidget(QLabel("Prompt do Sistema / Instrução Base:"))
            self.inp_api_prompt = QTextEdit()
            self.inp_api_prompt.setMaximumHeight(80)
            sys_prompt = self.extra_data.get('system_prompt', self.extra_data.get('prompt', ''))
            self.inp_api_prompt.setText(str(sys_prompt))
            gpalay.addWidget(self.inp_api_prompt)
            
            # Parametros numéricos lado a lado
            from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox
            param_row = QHBoxLayout()
            
            param_row.addWidget(QLabel("Temperatura:"))
            self.inp_api_temp = QDoubleSpinBox()
            self.inp_api_temp.setRange(0.0, 2.0)
            self.inp_api_temp.setSingleStep(0.1)
            temp_val = self.extra_data.get('temperature', 0.7)
            try: self.inp_api_temp.setValue(float(temp_val))
            except: pass
            param_row.addWidget(self.inp_api_temp)
            
            param_row.addWidget(QLabel("Max Tokens:"))
            self.inp_api_tokens = QSpinBox()
            self.inp_api_tokens.setRange(1, 128000)
            tokens_val = self.extra_data.get('max_tokens', 4096)
            try: self.inp_api_tokens.setValue(int(tokens_val))
            except: pass
            param_row.addWidget(self.inp_api_tokens)
            
            gpalay.addLayout(param_row)
            
            if "api" in node_type.lower() or "connector" in node_type.lower():
                param_row2 = QHBoxLayout()
                
                param_row2.addWidget(QLabel("Conexão (Provider):"))
                self.inp_api_provider = QLineEdit()
                self.inp_api_provider.setText(str(self.extra_data.get('base_provider', '')))
                param_row2.addWidget(self.inp_api_provider)
                
                param_row2.addWidget(QLabel("IA (Model):"))
                self.inp_api_model = QLineEdit()
                self.inp_api_model.setText(str(self.extra_data.get('base_model', '')))
                param_row2.addWidget(self.inp_api_model)
                
                gpalay.addLayout(param_row2)
                
            main_layout.addWidget(gpa)
            
        # ========== FORMULÁRIO DE IDENTIDADE (fora do bloco de rotas) ==========
        is_identity_node = ("identity" in node_type.lower() or "identidade" in self._node_label.lower())
        if is_identity_node:
            is_identity_ai = ("identity_ai" in node_type.lower() 
                             or "identidade ia" in self._node_label.lower()
                             or ("identidade" in self._node_label.lower() and "code" not in self._node_label.lower() and "app" not in self._node_label.lower()))
            
            id_group = QGroupBox("🔑 IDENTIDADE" if is_identity_ai else "💻 IDENTIDADE DO PROGRAMA")
            id_layout = QVBoxLayout(id_group)
            id_layout.setSpacing(4)
            
            field_style = "background-color: #0d1117; color: #a5d6ff; border: 1px solid #30363d; border-radius: 4px; padding: 5px; font-size: 11px;"
            label_style = "color: #8b949e; font-size: 10px; font-weight: bold; margin-top: 4px;"
            
            if is_identity_ai:
                header = QLabel("🤖 IDENTIDADE DO MODELO DE IA")
                header.setStyleSheet("color: #58a6ff; font-size: 12px; font-weight: bold; padding: 3px 0;")
                id_layout.addWidget(header)
                
                fields = [
                    ("NOME DO BOT", "botName", "Richie — IA Assistente Base"),
                    ("VERSÃO DO MODELO", "version", "v1.4.20 - 01052026"),
                    ("CRIADOR / AUTOR", "creator", "@S.V.S - Try Technology"),
                    ("TOM DE VOZ", "tone", "profissional e amigável"),
                    ("PROPRIEDADE INTELECTUAL", "propriedade_intelectual", "© 2026 @S.V.S - Try Technology. Todos os direitos reservados."),
                    ("DATA DE CRIAÇÃO", "data_criacao", "2026-04-14"),
                    ("DATA DE ATUALIZAÇÃO", "data_atualizacao", ""),
                    ("DESCRIÇÃO", "description", "IA nativa do AI Code Assistant."),
                ]
            else:
                header = QLabel("💻 IDENTIDADE DO PROGRAMA (AI CODE ASSISTANT)")
                header.setStyleSheet("color: #3fb950; font-size: 12px; font-weight: bold; padding: 3px 0;")
                id_layout.addWidget(header)
                
                fields = [
                    ("VERSÃO DO PROGRAMA", "app_version", "v0.4.11-rev1.2.9-300426-Gemini"),
                    ("BUILD / REVISÃO", "app_build", "rev1.2.9-Gemini"),
                    ("AMBIENTE", "app_env", "homologacao"),
                    ("DESENVOLVEDOR", "app_developer", "@S.V.S - Try Technology"),
                    ("DATA DE RELEASE", "app_release_date", "30/04/2026"),
                ]
            
            self.identity_inputs = {}
            for lbl_text, key, default in fields:
                lbl = QLabel(lbl_text)
                lbl.setStyleSheet(label_style)
                id_layout.addWidget(lbl)
                w = QLineEdit(str(self.extra_data.get(key, default)))
                w.setStyleSheet(field_style)
                id_layout.addWidget(w)
                self.identity_inputs[key] = w
            
            main_layout.addWidget(id_group)
            
        # Botoes Rodape
        btn_ly = QHBoxLayout()
        btn_ly.addStretch()
        btn_cn = QPushButton("Cancelar", objectName="btn_cancel")
        btn_cn.clicked.connect(self.reject)
        btn_sv = QPushButton("Salvar")
        btn_sv.clicked.connect(self.accept)
        btn_ly.addWidget(btn_cn)
        btn_ly.addWidget(btn_sv)
        
        main_layout.addSpacing(20)
        main_layout.addLayout(btn_ly)
        
        self._temp_out_colors = out_colors.copy() if out_colors else []
        self.node_id = node_id

    def _delete_route(self, widget_container, line_edit_ref):
        # Oculta o widget
        widget_container.hide()
        # Remove fisicamente da lista lógica de submissão do formulário
        for tupl in self.route_inputs:
            if tupl[0] == line_edit_ref:
                self.route_inputs.remove(tupl)
                break

    def _pick_color(self, idx, btn):
        from PyQt6.QtWidgets import QColorDialog
        
        color_dialog = QColorDialog(self)
        color_dialog.setStyleSheet("QDialog { background-color: #161b22; color: #c9d1d9; }")
        
        if color_dialog.exec():
            color = color_dialog.selectedColor().name()
            self._apply_color(idx, btn, color)

    def _apply_color(self, idx, btn, color):
        while len(self._temp_out_colors) <= idx:
            self._temp_out_colors.append("#58a6ff")
        self._temp_out_colors[idx] = color
        btn.setStyleSheet(f"background-color: transparent; border: none; color: {color}; font-size: 16px;")

# ========== FLOW GROUP (SESSÕES) ==========
class FlowGroup(QGraphicsRectItem):
    def __init__(self, rect, title="Nova Sessão", color="#3fb950", parent=None):
        super().__init__(rect, parent)
        self.setZValue(-2) # Fica sempre atrás das linhas e nodes
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.title = title
        self.color = color
        self.group_id = f"group_{uuid.uuid4().hex[:8]}"
        self.contained_nodes = [] # Nós fixados ao grupo

    def paint(self, painter, option, widget):
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        # Fundo translúcido
        bg_color = QColor(self.color)
        bg_color.setAlpha(40)
        painter.fillPath(path, QBrush(bg_color))
        
        # Borda tracejada/sólida
        pen = QPen(QColor(self.color), 2, Qt.PenStyle.DashLine)
        if self.isSelected():
            pen.setColor(QColor("#f85149"))
            pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Título
        painter.setPen(QColor(self.color))
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(rect.x() + 10, rect.y() + 5, rect.width() - 20, 30), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.title)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos = value
            delta = new_pos - self.pos()
            for node in self.contained_nodes:
                if node.scene() == self.scene():
                    node.setPos(node.pos() + delta)
        return super().itemChange(change, value)

# ========== BOTFORGE VISUAL FLOW CANVAS ==========
class FlowConnection(QGraphicsPathItem):
    def __init__(self, source_node, source_port, dest_node=None, dest_port=None):
        super().__init__()
        self.setZValue(-1)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # Linhas em Dash azul escuro estilo BotForge 
        self.setPen(QPen(QColor("#7b8db0"), 2, Qt.PenStyle.DashLine))
        self.source_node = source_node
        self.source_port = source_port
        self.dest_node = dest_node
        self.dest_port = dest_port
        self.temp_pos = None

    def paint(self, painter, option, widget):
        # Alinhando a cor com a porta de saída do Node
        if self.source_node and self.source_port:
            color = self.source_node.get_port_color(self.source_port)
            pen_style = Qt.PenStyle.SolidLine if self.source_port == "out" else Qt.PenStyle.DashLine
            pen = QPen(QColor(color), 2, pen_style)
            
            if self.isSelected():
                pen.setColor(QColor("#f85149")) # Red se selecionada p/ delete
                pen.setWidth(4)
                
            self.setPen(pen)
        super().paint(painter, option, widget)

    def update_path(self):
        path = QPainterPath()
        is_backward = getattr(self, "is_backward", False)
        
        if is_backward:
            p1 = self.temp_pos 
        elif self.source_node:
            p1 = self.source_node.get_port_pos(self.source_port)
        else:
            return
            
        p2 = self.temp_pos if self.dest_node is None else self.dest_node.get_port_pos(self.dest_port)
        
        path.moveTo(p1)
        # Distancia do controle da Curva Bézier focada no estilo Web (Fluída)
        dx = max(abs(p2.x() - p1.x()) * 0.6, 60.0)
        path.cubicTo(p1.x() + dx, p1.y(), p2.x() - dx, p2.y(), p2.x(), p2.y())
        self.setPath(path)

class FlowNode(QGraphicsItem):
    def __init__(self, node_id, node_type, label, message="", color="#21262d", out_labels=None, out_colors=None, extra_data=None):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.node_id = node_id
        self.node_type = node_type
        self.label = label
        self.message = message
        self.color = color
        self.connections = []
        
        # Campos extras do JSON (api_config, intents, model_info, etc.)
        # Preservados para que o FlowEngine possa lê-los
        self.extra_data = extra_data or {}
        
        # Suporte a Múltiplas portas
        self.out_ports = ["out"]
        self.out_colors = [self.color]
        self.out_labels = []
        
        if out_labels is not None:
            # Se vieram dados reais (ex: parser Web), usar eles.
            self.out_labels = out_labels
            self.out_colors = out_colors if out_colors else ["#58a6ff"] * len(out_labels)
            self.out_ports = [f"out_{i}" for i in range(len(self.out_labels))]
        elif "nlp router" in self.label.lower() or "router" in self.node_type.lower() or "nlp" in self.node_type.lower():
            # Fallback limpo p/ Criação Manual Nova
            self.out_labels = ["Nova Intenção"]
            self.out_ports = ["out_0"]
            self.out_colors = ["#22c55e"]
            
        self.width = 180
        self.height = max(60, 20 + len(self.out_ports) * 15)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Design BotForge: Fundo Escuro com borda colorida se selecionado
        bg_color = QColor("#21262d") if self.isSelected() else QColor("#161b22")
        border_color = QColor(self.color) if self.isSelected() else QColor("#30363d")
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        
        painter.fillPath(path, QBrush(bg_color))
        painter.strokePath(path, QPen(border_color, 2 if self.isSelected() else 1))

        # Tarja Lateral Esquerda com a Cor do Nó (estilo BotForge)
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 8, self.height, 8, 8)
        # Rect interno para anular arredondamento do lado direito da pílula
        painter.drawRect(4, 0, 4, self.height)

        # Labels flutuantes
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(16, 12, self.width-20, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.label)

        sub_label = self.node_type
        painter.setPen(QPen(QColor("#8b949e")))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        painter.drawText(QRectF(16, 32, self.width-20, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, sub_label)

        # Porta de Entrada
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen(QColor("#161b22"), 2))
        painter.drawEllipse(QRectF(-6, self.height/2 - 6, 12, 12)) # In
        
        # Múltiplas portas de Saída e Textos de Rota
        for i, port_color in enumerate(self.out_colors):
            painter.setBrush(QBrush(QColor(port_color)))
            # Calcular o espaçamento ao longo da altura
            if len(self.out_colors) == 1:
                cy = self.height / 2
            else:
                margin = 20
                step = (self.height - 2*margin) / (len(self.out_colors) - 1) if len(self.out_colors) > 1 else 0
                cy = margin + i * step
            
            painter.drawEllipse(QRectF(self.width-6, cy - 6, 12, 12)) # Out
            
            # Impressão do nome da Rota à esquerda do conector (apenas modais NLP longos)
            if self.out_labels and i < len(self.out_labels):
                painter.setPen(QPen(QColor("#a8b3cf")))
                painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
                painter.drawText(QRectF(10, cy - 10, self.width - 25, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.out_labels[i])

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        
        # Atribuir lista auxiliar se não existir
        if not hasattr(self, 'route_inputs'):
            self.route_inputs = []
            
        # Invocar o NodeConfigModal imitando botforge
        modal = NodeConfigModal(
            self.node_id, self.node_type, self.label, self.message, 
            self.color, self.out_labels, self.out_colors, 
            out_keywords=getattr(self, 'out_keywords', []), 
            extra_data=self.extra_data
        )
        modal.parent_node = self
        
        if modal.exec() == QDialog.DialogCode.Accepted:
            # Atualiza o node visual com labels alterados
            self.label = modal.inp_name.text()
            self.message = modal.inp_desc.toPlainText()
            
            # Atualizar cores e textos!
            if hasattr(modal, 'route_inputs') and self.out_labels:
                new_labels = []
                new_keywords = []
                for tupl in modal.route_inputs:
                    new_labels.append(tupl[0].text())
                    if len(tupl) >= 3:
                        sub_inp = tupl[2]
                        if hasattr(sub_inp, 'toPlainText'):
                            new_keywords.append(sub_inp.toPlainText())
                        else:
                            new_keywords.append(sub_inp.text())
                    else:
                        new_keywords.append("")
                self.out_labels = new_labels
                self.out_keywords = new_keywords
                self.out_colors = modal._temp_out_colors
                
            # Salvar campos do API Connector de volta no extra_data
            if hasattr(modal, 'inp_api_prompt'):
                if not isinstance(self.extra_data, dict):
                    self.extra_data = {}
                self.extra_data['system_prompt'] = modal.inp_api_prompt.toPlainText()
                self.extra_data['temperature'] = modal.inp_api_temp.value()
                self.extra_data['max_tokens'] = modal.inp_api_tokens.value()
            
            if hasattr(modal, 'inp_api_provider'):
                self.extra_data['base_provider'] = modal.inp_api_provider.text()
                self.extra_data['base_model'] = modal.inp_api_model.text()
                
            if hasattr(modal, 'identity_inputs'):
                if not isinstance(self.extra_data, dict):
                    self.extra_data = {}
                for key, q_input in modal.identity_inputs.items():
                    self.extra_data[key] = q_input.text()
                    
            # Custom code request config
            if hasattr(modal, 'inp_lang'):
                if not isinstance(self.extra_data, dict):
                    self.extra_data = {}
                self.extra_data['target_language'] = modal.inp_lang.text()
                self.extra_data['comments'] = modal.chk_comments.isChecked()
                self.extra_data['performance'] = modal.chk_perf.isChecked()

            # Custom execution request config
            if hasattr(modal, 'chk_always_session'):
                if not isinstance(self.extra_data, dict):
                    self.extra_data = {}
                self.extra_data['btn_session'] = modal.chk_always_session.isChecked()
                self.extra_data['btn_global'] = modal.chk_always_global.isChecked()
                
            self.update()

    def get_port_color(self, port_type):
        if port_type.startswith("out_"):
            try:
                idx = int(port_type.split("_")[1])
                return self.out_colors[idx]
            except:
                pass
        return self.color

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for conn in self.connections:
                conn.prepareGeometryChange() # Força o path a atualizar o bounding box
                conn.update_path()
        return super().itemChange(change, value)

    def get_port_pos(self, port_type):
        if port_type == "in":
            return self.mapToScene(0, self.height/2)
        else:
            if port_type.startswith("out_"):
                try:
                    idx = int(port_type.split("_")[1])
                    margin = 15
                    step = (self.height - 2*margin) / (len(self.out_colors) - 1) if len(self.out_colors) > 1 else 0
                    cy = margin + idx * step
                    return self.mapToScene(self.width, cy)
                except:
                    pass
            return self.mapToScene(self.width, self.height/2)

    def add_connection(self, conn):
        self.connections.append(conn)

class FlowScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#0e1116")))  # Fundo noturno profundo BotForge
        self.drawing_conn = None

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # Desenha a malha pontilhada / tracejada para o fundo técnico
        left = int(rect.left()) - (int(rect.left()) % 20)
        top = int(rect.top()) - (int(rect.top()) % 20)
        
        lines = []
        for x in range(left, int(rect.right()), 20):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), 20):
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            
        # Pen muito sutil com bolinhas (técnica de grid matrix)
        pen = QPen(QColor("#1e232d"), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.drawLines(lines)

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if isinstance(item, FlowNode):
            pos = item.mapFromScene(event.scenePos())
            if pos.x() > item.width - 20: # clicked out port
                # Determine o porto exato baseado no Y (Hover Y)
                clicked_port = "out"
                if len(item.out_ports) > 1:
                    margin = 20
                    step = (item.height - 2*margin) / (len(item.out_colors) - 1)
                    min_dist = 999
                    for i in range(len(item.out_ports)):
                        cy = margin + i * step
                        dist = abs(pos.y() - cy)
                        if dist < min_dist:
                            min_dist = dist
                            clicked_port = item.out_ports[i]
                            
                self.drawing_conn = FlowConnection(item, clicked_port)
                self.addItem(self.drawing_conn)
                self.drawing_conn.temp_pos = event.scenePos()
                self.drawing_conn.update_path()
                return
            elif pos.x() < 20: # clicked in port backwards
                self.drawing_conn = FlowConnection(None, None, item, "in")
                self.drawing_conn.is_backward = True
                self.drawing_conn.source_node = None # Forçar o paint a tolerar source None enquanto puxa o fio inverso
                self.addItem(self.drawing_conn)
                self.drawing_conn.temp_pos = event.scenePos()
                self.drawing_conn.update_path()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing_conn:
            self.drawing_conn.temp_pos = event.scenePos()
            self.drawing_conn.update_path()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing_conn:
            item = self.itemAt(event.scenePos(), QTransform())
            is_backward = getattr(self.drawing_conn, "is_backward", False)
            
            if isinstance(item, FlowNode):
                if is_backward and item != self.drawing_conn.dest_node:
                    pos = item.mapFromScene(event.scenePos())
                    # Auto resolucao do node porto fonte (Hovered Y)
                    clicked_port = "out"
                    if len(item.out_ports) > 1:
                        margin = 20
                        step = (item.height - 2*margin) / (len(item.out_colors) - 1)
                        min_dist = 999
                        for i in range(len(item.out_ports)):
                            cy = margin + i * step
                            dist = abs(pos.y() - cy)
                            if dist < min_dist:
                                min_dist = dist
                                clicked_port = item.out_ports[i]
                                
                    self.drawing_conn.source_node = item
                    self.drawing_conn.source_port = clicked_port
                    self.drawing_conn.is_backward = False
                    self.drawing_conn.source_node.add_connection(self.drawing_conn)
                    self.drawing_conn.dest_node.add_connection(self.drawing_conn)
                    self.drawing_conn.update_path()
                elif not is_backward and item != self.drawing_conn.source_node:
                    self.drawing_conn.dest_node = item
                    self.drawing_conn.dest_port = "in"
                    self.drawing_conn.source_node.add_connection(self.drawing_conn)
                    item.add_connection(self.drawing_conn)
                    self.drawing_conn.update_path()
                else:
                    self.removeItem(self.drawing_conn)
            else:
                # Mostrar menu de contexto n8n-style se soltar no vazio
                menu_handled = self._show_catalog_menu(event.screenPos(), event.scenePos(), self.drawing_conn, is_backward)
                if not menu_handled:
                    self.removeItem(self.drawing_conn)
            self.drawing_conn = None
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            items = self.selectedItems()
            for item in items:
                if isinstance(item, FlowConnection):
                    # Desconectar do node correspondente
                    if item.source_node and item in item.source_node.connections:
                        item.source_node.remove_connection(item)
                    if item.dest_node and item in item.dest_node.connections:
                        item.dest_node.remove_connection(item)
                    self.removeItem(item)
                # Opcional: deletar nodes, mas por enquanto mantemos delete apenas no painel e botão delete item.
            event.accept()
        else:
            super().keyPressEvent(event)

    def _show_catalog_menu(self, screen_pos, scene_pos, connection_to_link=None, is_backward=False):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; } QMenu::item:selected { background-color: #1f6feb; }")
        
        # Iterar sobre o catálogo global
        actions_map = {}
        for category, items in BOTFORGE_CARD_CATALOG.items():
            submenu = menu.addMenu(category)
            submenu.setStyleSheet("QMenu { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; } QMenu::item:selected { background-color: #1f6feb; }")
            for card_id, label, color in items:
                action = submenu.addAction(label)
                actions_map[action] = (card_id, label, color)
                
        action = menu.exec(screen_pos)
        
        if action in actions_map:
            card_id, label, color = actions_map[action]
            # Assumindo que o parent do FlowScene é CreateAIDialog
            if hasattr(self.parent(), '_add_node_at_pos'):
                msg = "" # Default empty message
                new_node = self.parent()._add_node_at_pos(card_id, label, color, msg, scene_pos.x(), scene_pos.y())
                
                # Auto-conectar se houver uma linha sendo puxada
                if connection_to_link and new_node:
                    if is_backward:
                        # Puxando ao contrário: o nó novo é a origem (source)
                        connection_to_link.source_node = new_node
                        # Conectar na primeira porta de saída por padrão
                        connection_to_link.source_port = new_node.out_ports[0] if new_node.out_ports else "out"
                        connection_to_link.is_backward = False
                        new_node.add_connection(connection_to_link)
                        connection_to_link.dest_node.add_connection(connection_to_link)
                    else:
                        # Puxando pra frente: o nó novo é o destino (dest)
                        connection_to_link.dest_node = new_node
                        connection_to_link.dest_port = "in"
                        connection_to_link.source_node.add_connection(connection_to_link)
                        new_node.add_connection(connection_to_link)
                    
                    connection_to_link.update_path()
            return True
        return False

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; } QMenu::item:selected { background-color: #1f6feb; }")
        
        create_group_action = menu.addAction("📦 Criar Sessão (Agrupar Selecionados)")
        menu.addSeparator()
        create_node_action = menu.addAction("➕ Criar Nó a partir do Catálogo")
        
        action = menu.exec(event.screenPos())
        
        if action == create_node_action:
            self._show_catalog_menu(event.screenPos(), event.scenePos())
        elif action == create_group_action:
            selected_nodes = [item for item in self.selectedItems() if isinstance(item, FlowNode)]
            if not selected_nodes:
                return
                
            # Calcula o Bounding Box de todos os nós selecionados
            min_x = min(node.scenePos().x() for node in selected_nodes)
            min_y = min(node.scenePos().y() for node in selected_nodes)
            max_x = max(node.scenePos().x() + node.width for node in selected_nodes)
            max_y = max(node.scenePos().y() + node.height for node in selected_nodes)
            
            # Padding
            pad = 40
            rect = QRectF(0, 0, (max_x - min_x) + pad*2, (max_y - min_y) + pad*2 + 30)
            
            # Pedir Nome
            title, ok = QInputDialog.getText(None, "Nova Sessão", "Nome da Sessão:", text="Ramo Neural")
            if ok and title:
                # Perguntar Cor
                color_dialog = QColorDialog()
                color_dialog.setStyleSheet("QDialog { background-color: #161b22; color: #c9d1d9; }")
                color = "#3fb950"
                if color_dialog.exec():
                    color = color_dialog.selectedColor().name()
                
                group = FlowGroup(rect, title, color)
                self.addItem(group)
                group.setPos(min_x - pad, min_y - pad - 30)
                
                # Anexar nós ao grupo para moverem juntos
                for node in selected_nodes:
                    group.contained_nodes.append(node)
                    node.setZValue(1) # Garantir que fiquem acima do grupo
                    
                # Deselecionar nós e selecionar apenas o grupo
                self.clearSelection()
                group.setSelected(True)

class ZoomOverlay(QFrame):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.setStyleSheet("""
            QFrame { background: rgba(13, 17, 23, 0.85); border: 1px solid #30363d; border-radius: 8px; }
            QPushButton { background: transparent; color: #c9d1d9; border: none; font-size: 16px; font-weight: bold; border-radius: 4px; padding: 4px 8px; }
            QPushButton:hover { background: rgba(88, 166, 255, 0.15); color: #58a6ff; }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)
        
        btn_out = QPushButton("−")
        btn_out.setToolTip("Diminuir Zoom")
        btn_out.clicked.connect(self._zoom_out)
        lay.addWidget(btn_out)
        
        btn_reset = QPushButton("⟲")
        btn_reset.setToolTip("Resetar Zoom")
        btn_reset.clicked.connect(self._zoom_reset)
        lay.addWidget(btn_reset)
        
        btn_in = QPushButton("+")
        btn_in.setToolTip("Aumentar Zoom")
        btn_in.clicked.connect(self._zoom_in)
        lay.addWidget(btn_in)
        
        self.current_zoom = 1.0
        self.setFixedSize(100, 36)
        
        # Animação
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        from PyQt6.QtCore import QPropertyAnimation
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(200)
        self.effect.setOpacity(0.5)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setEndValue(0.5)
        self.anim.start()
        super().leaveEvent(event)

    def _zoom_in(self):
        self._apply_zoom(1.15)
        
    def _zoom_out(self):
        self._apply_zoom(1 / 1.15)
        
    def _zoom_reset(self):
        self.view.resetTransform()
        self.current_zoom = 1.0
        
    def _apply_zoom(self, factor):
        self.current_zoom *= factor
        if self.current_zoom < 0.2:
            self.current_zoom = 0.2
            return
        if self.current_zoom > 3.0:
            self.current_zoom = 3.0
            return
        self.view.scale(factor, factor)

class FlowView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("border: 1px solid #1e2330; background-color: #0e1116;")
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.IntersectsItemShape)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # Pan custom drag vars
        self._is_panning = False
        self._pan_start_pos = None
        self._is_rubber_band = False
        self._rubber_start = None

    def mousePressEvent(self, event):
        # Middle-click = pan
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        # Left-click no espaço vazio = rubber-band selection
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.scene().itemAt(self.mapToScene(event.pos()), QTransform())
            if item is None:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self._is_rubber_band = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning and self._pan_start_pos:
            delta = self._pan_start_pos - event.pos()
            self._pan_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_panning:
            self._is_panning = False
            self._pan_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        if self._is_rubber_band:
            self._is_rubber_band = False
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for child in self.children():
            if isinstance(child, ZoomOverlay):
                child.move(self.width() - child.width() - 20, self.height() - child.height() - 20)

class CreateAIDialog(QDialog):
    """Dialog para criar nova IA/Bot — estilo BotForge Studio com 6 abas"""

    ai_created = pyqtSignal(object)

    def __init__(self, custom_ai_manager: CustomAIManager, parent=None):
        super().__init__(parent)
        self.manager = custom_ai_manager
        self.flow_nodes = []  # Lista de nodes do fluxo
        self.chat_messages = []  # Histórico do chat de teste
        self.setWindowTitle("🤖 Criar Nova IA / Bot — BotForge Studio")
        self.setMinimumSize(820, 650)
        self.setStyleSheet(self._get_styles())
        self._setup_ui()

    def _get_styles(self):
        return """
            QDialog { background-color: #0d1117; color: #c9d1d9; }
            QLabel { color: #8b949e; font-size: 12px; }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #21262d; border: 1px solid #30363d;
                border-radius: 4px; padding: 6px; color: #c9d1d9; font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus { border-color: #58a6ff; }
            QPushButton {
                background-color: #21262d; border: 1px solid #30363d;
                border-radius: 4px; padding: 8px 16px; color: #c9d1d9; font-size: 11px;
            }
            QPushButton:hover { background-color: #30363d; }
            QPushButton#primary { background-color: #1f6feb; color: white; border: none; font-weight: bold; }
            QPushButton#primary:hover { background-color: #388bfd; }
            QGroupBox {
                border: 1px solid #30363d; border-radius: 6px;
                margin-top: 10px; padding-top: 10px; color: #8b949e; font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QTabWidget::pane { border: 1px solid #30363d; background-color: #161b22; }
            QTabBar::tab { background: #0d1117; color: #8b949e; padding: 7px 14px; border: none; font-size: 11px; }
            QTabBar::tab:selected { background: #1f6feb; color: white; }
            QSlider::groove:horizontal { background: #30363d; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #58a6ff; width: 16px; margin: -5px 0; border-radius: 8px; }
            QListWidget { background-color: #1c2128; border: 1px solid #30363d; color: #c9d1d9; }
            QListWidget::item { padding: 6px; border-bottom: 1px solid #30363d; }
            QListWidget::item:selected { background-color: #1f6feb; }
            QCheckBox { color: #c9d1d9; }
        """

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("Criar Nova IA / Bot")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #58a6ff; margin-bottom: 5px;")
        layout.addWidget(title)

        # === 6 ABAS BOTFORGE ===
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self._create_flow_tab(), "🔗 Fluxo")
        self.tabs.addTab(self._create_basic_tab(), "📋 Dados Básicos")
        self.tabs.addTab(self._create_chat_test_tab(), "💬 Chat Teste")
        self.tabs.addTab(self._create_personality_tab(), "🎭 Personalidade")
        self.tabs.addTab(self._create_config_tab(), "⚙️ Config Bot")
        self.tabs.addTab(self._create_catalog_tab(), "📦 Catálogo")

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_create = QPushButton("✅ Criar IA")
        btn_create.setObjectName("primary")
        btn_create.clicked.connect(self._create_ai)
        btn_layout.addWidget(btn_create)
        layout.addLayout(btn_layout)

    # ==================== ABA 1: DADOS BÁSICOS ====================
    def _create_basic_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Nome da IA:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Ari — Milkshaketeria")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Descrição:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Bot de atendimento via WhatsApp")
        layout.addWidget(self.desc_input)

        # Provider + Modelo
        provider_group = QGroupBox("Modelo Base")
        pg_layout = QVBoxLayout(provider_group)
        pg_layout.addWidget(QLabel("Provedor:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "DeepSeek"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        pg_layout.addWidget(self.provider_combo)
        pg_layout.addWidget(QLabel("Modelo:"))
        self.model_combo = QComboBox()
        pg_layout.addWidget(self.model_combo)
        self._on_provider_changed(self.provider_combo.currentText())
        layout.addWidget(provider_group)

        # System Prompt
        layout.addWidget(QLabel("System Prompt:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setFixedHeight(100)
        self.prompt_input.setPlaceholderText("Você é um assistente especializado em...")
        layout.addWidget(self.prompt_input)

        # Temperatura + Tokens
        params = QHBoxLayout()
        params.addWidget(QLabel("Temperatura:"))
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        params.addWidget(self.temp_slider)
        self.temp_label = QLabel("0.7")
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v/100:.2f}"))
        params.addWidget(self.temp_label)
        params.addWidget(QLabel("Max Tokens:"))
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(256, 128000)
        self.tokens_spin.setValue(4096)
        self.tokens_spin.setSingleStep(256)
        params.addWidget(self.tokens_spin)
        layout.addLayout(params)

        # Template rápido
        tmpl_layout = QHBoxLayout()
        tmpl_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("Personalizado")
        for tmpl_name in AI_TEMPLATES:
            self.template_combo.addItem(tmpl_name)
        self.template_combo.currentTextChanged.connect(self._apply_template)
        tmpl_layout.addWidget(self.template_combo)
        layout.addLayout(tmpl_layout)

        layout.addStretch()
        
        self.chat_integration_checkbox = QCheckBox("Tornar BotForge IA Selecionável na Caixa Principal (Integrar ao Chat Global)")
        self.chat_integration_checkbox.setStyleSheet("color: #ec4899; font-weight: bold;")
        self.chat_integration_checkbox.setChecked(True)
        layout.addWidget(self.chat_integration_checkbox)

        return widget

    # ==================== ABA 2: FLUXO ====================
    def _create_flow_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Nodes do Fluxo (arraste cards do Catálogo ou adicione manualmente):"))

        self.flow_scene = FlowScene(self)
        self.flow_view = FlowView(self.flow_scene)
        self.flow_view.setMinimumHeight(240)
        from PyQt6.QtWidgets import QSizePolicy
        self.flow_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.flow_view, 1)

        # Instanciar Overlay
        self.zoom_overlay = ZoomOverlay(self.flow_view, self.flow_view)
        
        # Botões de fluxo
        btn_row = QHBoxLayout()
        btn_add = QPushButton("➕ Adicionar Node")
        btn_add.clicked.connect(self._add_flow_node)
        btn_row.addWidget(btn_add)

        btn_remove = HoldToConfirmButton("🗑 Remover Selecionado", hold_time_ms=2000, parent=self, on_confirm=self._remove_flow_node)
        btn_row.addWidget(btn_remove)

        btn_row.addStretch()

        btn_import_flow = QPushButton("\u2b07\ufe0f Importar Fluxo JSON")
        btn_import_flow.clicked.connect(self._import_flow)
        btn_row.addWidget(btn_import_flow)

        layout.addLayout(btn_row)

        # Detalhes do node selecionado
        detail_group = QGroupBox("Detalhes para Novo Node")
        dg_layout = QVBoxLayout(detail_group)
        dg_layout.addWidget(QLabel("Tipo:"))
        self.node_type_combo = QComboBox()
        for cat, cards in BOTFORGE_CARD_CATALOG.items():
            for card_id, card_name, color in cards:
                self.node_type_combo.addItem(f"{card_name} ({card_id})", (card_id, color))
        dg_layout.addWidget(self.node_type_combo)
        dg_layout.addWidget(QLabel("Label:"))
        self.node_label_input = QLineEdit()
        self.node_label_input.setPlaceholderText("Nome do node no fluxo")
        dg_layout.addWidget(self.node_label_input)
        dg_layout.addWidget(QLabel("Mensagem/Config:"))
        self.node_msg_input = QTextEdit()
        self.node_msg_input.setFixedHeight(60)
        dg_layout.addWidget(self.node_msg_input)
        layout.addWidget(detail_group)

        layout.addStretch()
        return widget

    # ==================== ABA 3: CHAT TESTE ====================
    def _create_chat_test_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        layout.addWidget(QLabel("💬 Simulador de Chat — Teste respostas do bot localmente"))

        # Área de mensagens
        self.test_chat_area = QTextEdit()
        self.test_chat_area.setReadOnly(True)
        self.test_chat_area.setStyleSheet("""
            background-color: #1c2128; color: #c9d1d9; border: 1px solid #30363d;
            font-family: 'Segoe UI'; font-size: 12px; padding: 8px;
        """)
        self.test_chat_area.setHtml('<p style="color:#58a6ff;"><b>\U0001f916 Bot:</b> Envie uma mensagem para testar o fluxo.</p>')
        layout.addWidget(self.test_chat_area)

        # Input
        input_row = QHBoxLayout()
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Digite uma mensagem de teste...")
        self.test_input.returnPressed.connect(self._send_test_message)
        input_row.addWidget(self.test_input)

        btn_send = QPushButton("📤 Enviar")
        btn_send.setObjectName("primary")
        btn_send.clicked.connect(self._send_test_message)
        input_row.addWidget(btn_send)

        btn_clear = QPushButton("🗑 Limpar")
        btn_clear.clicked.connect(lambda: (
            self.test_chat_area.setHtml('<p style="color:#58a6ff;"><b>\U0001f916 Bot:</b> Chat limpo. Envie uma mensagem.</p>'),
            setattr(self, 'chat_messages', [])
        ))
        input_row.addWidget(btn_clear)
        layout.addLayout(input_row)

        return widget

    # ==================== ABA 4: PERSONALIDADE ====================
    def _create_personality_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Saudação:"))
        self.greeting_input = QTextEdit()
        self.greeting_input.setFixedHeight(50)
        self.greeting_input.setPlaceholderText("🍦 BEM-VINDO À MILKSHAKETERIA!")
        layout.addWidget(self.greeting_input)

        # Tom
        tone_row = QHBoxLayout()
        tone_row.addWidget(QLabel("Tom:"))
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(["amigável", "profissional", "casual", "técnico", "formal", "empático"])
        tone_row.addWidget(self.tone_combo)
        tone_row.addWidget(QLabel("Idioma:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["pt-BR", "en", "es"])
        tone_row.addWidget(self.lang_combo)
        layout.addLayout(tone_row)

        # Traços
        layout.addWidget(QLabel("Traços de Personalidade:"))
        traits_grid = QGridLayout()
        self.trait_checks = {}
        traits = ["Educado", "Objetivo", "Carismático", "Detalhista", "Paciente", "Proativo", "Sério", "Empático"]
        for i, trait in enumerate(traits):
            cb = QCheckBox(trait)
            cb.setStyleSheet("color: #cccccc;")
            traits_grid.addWidget(cb, i // 4, i % 4)
            self.trait_checks[trait] = cb
        layout.addLayout(traits_grid)

        # Criatividade
        creat_row = QHBoxLayout()
        creat_row.addWidget(QLabel("Criatividade:"))
        self.creativity_slider = QSlider(Qt.Orientation.Horizontal)
        self.creativity_slider.setRange(0, 100)
        self.creativity_slider.setValue(50)
        creat_row.addWidget(self.creativity_slider)
        self.creativity_label = QLabel("50%")
        self.creativity_slider.valueChanged.connect(lambda v: self.creativity_label.setText(f"{v}%"))
        creat_row.addWidget(self.creativity_label)
        layout.addLayout(creat_row)

        # Conhecimento
        layout.addWidget(QLabel("Conhecimento Base (RAG/Contexto):"))
        self.knowledge_input = QTextEdit()
        self.knowledge_input.setFixedHeight(60)
        self.knowledge_input.setPlaceholderText("Cardápio de açaí, preços, horários...")
        layout.addWidget(self.knowledge_input)

        # Fallback
        layout.addWidget(QLabel("Mensagem Fallback:"))
        self.fallback_input = QLineEdit()
        self.fallback_input.setPlaceholderText("Desculpe, não entendi. Pode reformular?")
        layout.addWidget(self.fallback_input)

        layout.addStretch()
        return widget

    # ==================== ABA 5: CONFIG BOT ====================
    def _create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Canal + Status
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Canal:"))
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["WhatsApp", "Web", "Multi", "Chat"])
        row1.addWidget(self.channel_combo)
        row1.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "draft"])
        row1.addWidget(self.status_combo)
        layout.addLayout(row1)

        # Numero Mestre
        master_group = QGroupBox("Número Mestre (Admin)")
        mg_layout = QHBoxLayout(master_group)
        mg_layout.addWidget(QLabel("Nome:"))
        self.master_name = QLineEdit()
        self.master_name.setPlaceholderText("Gerente")
        mg_layout.addWidget(self.master_name)
        mg_layout.addWidget(QLabel("WhatsApp:"))
        self.master_number = QLineEdit()
        self.master_number.setPlaceholderText("5527999000000")
        mg_layout.addWidget(self.master_number)
        layout.addWidget(master_group)

        # Horários
        hours_group = QGroupBox("Horário de Funcionamento")
        hg_layout = QHBoxLayout(hours_group)
        hg_layout.addWidget(QLabel("Início:"))
        self.work_start = QLineEdit("08:00")
        hg_layout.addWidget(self.work_start)
        hg_layout.addWidget(QLabel("Fim:"))
        self.work_end = QLineEdit("18:00")
        hg_layout.addWidget(self.work_end)
        layout.addWidget(hours_group)

        layout.addWidget(QLabel("Mensagem fora do horário:"))
        self.off_hours_msg = QLineEdit()
        self.off_hours_msg.setPlaceholderText("Estamos fora do horário de atendimento.")
        layout.addWidget(self.off_hours_msg)

        # PIX e telefone
        pay_row = QHBoxLayout()
        pay_row.addWidget(QLabel("PIX:"))
        self.pix_input = QLineEdit()
        self.pix_input.setPlaceholderText("chave@pix.com")
        pay_row.addWidget(self.pix_input)
        pay_row.addWidget(QLabel("Telefone:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("(27) 3333-4444")
        pay_row.addWidget(self.phone_input)
        layout.addLayout(pay_row)

        layout.addStretch()
        return widget

    # ==================== ABA 6: CATÁLOGO ====================
    def _create_catalog_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #0d1117;")

        container = QWidget()
        container.setStyleSheet("background-color: #0d1117;")
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(12)

        total = sum(len(cards) for cards in BOTFORGE_CARD_CATALOG.values())
        main_layout.addWidget(QLabel(f"📦 Catálogo de Cards BotForge — {total} tipos disponíveis"))

        for category, cards in BOTFORGE_CARD_CATALOG.items():
            cat_label = QLabel(f"{category} ({len(cards)} cards)")
            cat_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            cat_label.setStyleSheet("color: white; margin-top: 8px;")
            main_layout.addWidget(cat_label)

            grid = QGridLayout()
            grid.setSpacing(6)
            for i, (card_id, card_name, color) in enumerate(cards):
                btn = QPushButton(f"{card_name}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #161b22; color: white; border: 1px solid #30363d;
                        border-left: 3px solid {color}; padding: 6px 12px; text-align: left;
                        border-radius: 3px; font-size: 11px;
                    }}
                    QPushButton:hover {{ background-color: #21262d; border-color: {color}; }}
                """)
                btn.setToolTip(f"Tipo: {card_id} | Clique para adicionar ao fluxo")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked, cid=card_id, cname=card_name: self._add_card_to_flow(cid, cname))
                grid.addWidget(btn, i // 3, i % 3)
            main_layout.addLayout(grid)

        main_layout.addStretch()
        scroll.setWidget(container)
        return scroll

    # ==================== LÓGICA ====================

    def _on_provider_changed(self, provider_name):
        self.model_combo.clear()
        provider_key = str(provider_name).lower()
        if provider_key in AVAILABLE_BASE_MODELS:
            raw_models = AVAILABLE_BASE_MODELS[provider_key]
            model_names = [str(m.get("id", m)) if isinstance(m, dict) else str(m) for m in raw_models]
            self.model_combo.addItems(model_names)

    def _apply_template(self, template_name):
        if template_name in AI_TEMPLATES:
            tmpl = AI_TEMPLATES[template_name]
            self.name_input.setText(tmpl.get('name', ''))
            self.desc_input.setText(tmpl.get('description', ''))
            self.prompt_input.setText(tmpl.get('system_prompt', ''))
            self.temp_slider.setValue(int(tmpl.get('temperature', 0.7) * 100))
            self.tokens_spin.setValue(tmpl.get('max_tokens', 4096))

    def _add_node_at_pos(self, card_id, label, color, msg, x, y):
        node_id = f"n{len(self.flow_nodes)+1}"
        node_data = {"id": node_id, "type": card_id, "label": label, "message": msg, "color": color}
        self.flow_nodes.append(node_data)
        
        # Add visual node
        node_item = FlowNode(node_id, card_id, label, msg, color)
        node_item.setPos(x, y)
        self.flow_scene.addItem(node_item)
        return node_item

    def _add_flow_node(self):
        data = self.node_type_combo.currentData()
        if not data:
            return
        card_id, color = data
        label = self.node_label_input.text() or self.node_type_combo.currentText().split('(')[0].strip()
        msg = self.node_msg_input.toPlainText()
        
        # Simple auto layout
        x = 50 + (len(self.flow_nodes) % 3) * 180
        y = 50 + (len(self.flow_nodes) // 3) * 80
        
        self._add_node_at_pos(card_id, label, color, msg, x, y)
        
        self.node_label_input.clear()
        self.node_msg_input.clear()

    def _remove_flow_node(self):
        for item in self.flow_scene.selectedItems():
            # Logica para conexão elétrica (Linhas)
            if isinstance(item, FlowConnection):
                if item.source_node and item in item.source_node.connections:
                    item.source_node.connections.remove(item)
                if item.dest_node and item in item.dest_node.connections:
                    item.dest_node.connections.remove(item)
                self.flow_scene.removeItem(item)
                
            # Logica para Block Cards
            elif isinstance(item, FlowNode):
                # Remove from data
                self.flow_nodes = [n for n in self.flow_nodes if n['id'] != item.node_id]
                # Remove connections
                for conn in list(item.connections):
                    self.flow_scene.removeItem(conn)
                    if conn in item.connections:
                        item.connections.remove(conn)
                    if conn.dest_node and conn in conn.dest_node.connections:
                        conn.dest_node.connections.remove(conn)
                    if conn.source_node and conn in conn.source_node.connections:
                        conn.source_node.connections.remove(conn)
                self.flow_scene.removeItem(item)

    def _add_card_to_flow(self, card_id, card_name):
        # find color
        color = "#21262d"
        for cat, cards in BOTFORGE_CARD_CATALOG.items():
            for c_id, c_name, c_color in cards:
                if c_id == card_id:
                    color = c_color
                    break
                    
        node_id = f"n{len(self.flow_nodes)+1}"
        node = {"id": node_id, "type": card_id, "label": card_name, "message": "", "color": color}
        self.flow_nodes.append(node)
        
        node_item = FlowNode(node_id, card_id, card_name, "", color)
        x = 50 + (len(self.flow_nodes) % 3) * 180
        y = 50 + (len(self.flow_nodes) // 3) * 80
        node_item.setPos(x, y)
        self.flow_scene.addItem(node_item)
        
        self.tabs.setCurrentIndex(1)  # Ir para aba Fluxo

    def _import_flow(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Fluxo JSON", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            nodes = []
            conns = []
            groups = []
            
            if "ari" in data and "flow" in data["ari"]:
                nodes = data["ari"]["flow"].get("nodes", [])
                conns = data["ari"]["flow"].get("connections", [])
                groups = data["ari"]["flow"].get("groups", [])
            elif "flow" in data:
                if isinstance(data["flow"], list):
                    nodes = data["flow"]
                else:
                    nodes = data["flow"].get("nodes", [])
                    conns = data["flow"].get("connections", [])
                    groups = data["flow"].get("groups", [])
            elif "_flow_nodes" in data:
                nodes = data.get("_flow_nodes", [])
                conns = data.get("_flow_conns", [])
                groups = data.get("_flow_groups", [])
            
            node_map = {}
            for n in nodes:
                node = {
                    "id": str(n.get("id", f"n{len(self.flow_nodes)+1}")),
                    "type": n.get("type", "send_msg"),
                    "label": n.get("data", {}).get("label", n.get("label", n.get("type", ""))),
                    "message": n.get("data", {}).get("message", n.get("msg", n.get("message", "")))
                }
                self.flow_nodes.append(node)
                
                # find color
                color = n.get("color", n.get("ui", {}).get("color", "#21262d"))
                if color == "#21262d":
                    for cat, cards in BOTFORGE_CARD_CATALOG.items():
                        for c_id, c_name, c_color in cards:
                            if c_id == node["type"]:
                                color = c_color
                                break
                                
                node_item = FlowNode(node["id"], node["type"], node["label"], node["message"], color)
                x = float(n.get("x", n.get("ui", {}).get("x", 50 + (len(self.flow_nodes) % 3) * 180)))
                y = float(n.get("y", n.get("ui", {}).get("y", 50 + (len(self.flow_nodes) // 3) * 80)))
                node_item.setPos(x, y)
                self.flow_scene.addItem(node_item)
                node_map[node["id"]] = node_item
                
            # Importar conexões
            for cdata in conns:
                src_id = str(cdata.get('source', cdata.get('from', cdata.get('sourceId', cdata.get('f')))))
                tgt_id = str(cdata.get('target', cdata.get('to', cdata.get('targetId', cdata.get('t')))))
                src_port = str(cdata.get('source_port', cdata.get('sourceHandle', cdata.get('sourcePort', cdata.get('fromPort', 'out')))))
                tgt_port = str(cdata.get('target_port', cdata.get('targetHandle', cdata.get('targetPort', cdata.get('toPort', 'in')))))
                
                if src_id in node_map and tgt_id in node_map:
                    conn = FlowConnection(node_map[src_id], src_port, node_map[tgt_id], tgt_port)
                    self.flow_scene.addItem(conn)
                    node_map[src_id].add_connection(conn)
                    node_map[tgt_id].add_connection(conn)
                    
            # Importar Sessões (FlowGroups)
            for gdata in groups:
                from PyQt6.QtCore import QRectF
                rect = QRectF(0, 0, float(gdata.get('w', 300)), float(gdata.get('h', 200)))
                group = FlowGroup(rect, gdata.get('title', 'Sessão'), gdata.get('color', '#3fb950'))
                group.group_id = gdata.get('id', group.group_id)
                self.flow_scene.addItem(group)
                group.setPos(float(gdata.get('x', 0)), float(gdata.get('y', 0)))
                
                group_node_ids = gdata.get('nodes', [])
                for nid in group_node_ids:
                    if str(nid) in node_map:
                        group.contained_nodes.append(node_map[str(nid)])
                        
            # Ocultar nodes que estão em grupos para não conflitar, ou atualizar Z value
            for group in [item for item in self.flow_scene.items() if isinstance(item, FlowGroup)]:
                for node in group.contained_nodes:
                    node.setZValue(1)
                
            QMessageBox.information(self, "Importação", f"{len(nodes)} nodes e {len(groups)} sessões importados.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao importar fluxo:\n{str(e)}")

    def _send_test_message(self):
        """Simula resposta local do bot baseada no fluxo e system prompt"""
        user_msg = self.test_input.text().strip()
        if not user_msg:
            return
        self.test_input.clear()

        # Adicionar mensagem do usuário
        self.test_chat_area.append(f'<p style="color:#39d353;"><b>\U0001f464 Voc\u00ea:</b> {user_msg}</p>')
        self.chat_messages.append({"role": "user", "text": user_msg})

        # Gerar resposta local baseada nas configurações
        bot_name = self.name_input.text() or "Bot"
        greeting = self.greeting_input.toPlainText()
        tone = self.tone_combo.currentText()
        prompt = self.prompt_input.toPlainText()
        knowledge = self.knowledge_input.toPlainText()
        fallback = self.fallback_input.text() or "Desculpe, não entendi."

        # Motor de resposta local simples
        response = self._generate_local_response(user_msg, bot_name, greeting, tone, prompt, knowledge, fallback)

        self.test_chat_area.append(f'<p style="color:#58a6ff;"><b>\U0001f916 {bot_name}:</b> {response}</p>')
        self.chat_messages.append({"role": "bot", "text": response})

    def _generate_local_response(self, user_msg, bot_name, greeting, tone, prompt, knowledge, fallback):
        """Motor de resposta local — simula respostas do bot baseado nos dados configurados"""
        msg_lower = user_msg.lower()

        # Verificar saudações
        greetings = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey", "eai", "salve"]
        if any(g in msg_lower for g in greetings):
            if greeting:
                return greeting
            return f"Olá! Eu sou o {bot_name}. Como posso ajudar?"

        # Verificar fluxo — check keywords dos nodes
        for node in self.flow_nodes:
            node_msg = node.get("message", "").lower()
            node_label = node.get("label", "").lower()
            if node_label in msg_lower or (node_msg and any(w in msg_lower for w in node_msg.split()[:3])):
                return node.get("message", "") or f"[Fluxo → {node['label']}]"

        # Verificar conhecimento
        if knowledge:
            knowledge_words = knowledge.lower().split()
            matches = [w for w in knowledge_words if w in msg_lower and len(w) > 3]
            if matches:
                return f"Baseado no meu conhecimento: {knowledge[:200]}"

        # Verificar system prompt
        if prompt and any(kw in msg_lower for kw in ["ajuda", "help", "funciona", "faz", "sobre"]):
            return f"{prompt[:200]}"

        # Respostas por intenção
        if any(w in msg_lower for w in ["cardápio", "cardapio", "menu", "opções", "produtos"]):
            return f"Aqui está nosso cardápio! {knowledge[:150] if knowledge else 'Use a aba Personalidade para adicionar o cardápio.'}"
        if any(w in msg_lower for w in ["preço", "preco", "quanto", "valor", "custa"]):
            return "Consulte nosso cardápio para ver os preços atualizados."
        if any(w in msg_lower for w in ["pedido", "pedir", "quero", "comprar"]):
            return f"Ótimo! Vou anotar seu pedido. O que deseja? (tom: {tone})"
        if any(w in msg_lower for w in ["obrigado", "obrigada", "valeu", "thanks"]):
            return f"Por nada! 😊 O {bot_name} está sempre aqui para ajudar!"
        if any(w in msg_lower for w in ["tchau", "bye", "até", "ate"]):
            return f"Até mais! 👋 Volte sempre! — {bot_name}"

        return fallback

    def _create_ai(self):
        """Cria a IA/Bot com todos os dados das 6 abas"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo obrigatório", "O nome da IA é obrigatório.")
            self.tabs.setCurrentIndex(0)
            self.name_input.setFocus()
            return

        provider = self.provider_combo.currentText().lower()
        model = self.model_combo.currentText()
        desc = self.desc_input.text()
        prompt = self.prompt_input.toPlainText()
        temp = self.temp_slider.value() / 100
        tokens = self.tokens_spin.value()

        # Construir system prompt com dados da personalidade
        greeting = self.greeting_input.toPlainText()
        tone = self.tone_combo.currentText()
        traits = [t for t, cb in self.trait_checks.items() if cb.isChecked()]
        knowledge = self.knowledge_input.toPlainText()
        fallback = self.fallback_input.text()

        if not prompt and greeting:
            prompt = (
                f"Você é {name}, um assistente virtual de tom {tone}. "
                f"{greeting} "
                f"Traços: {', '.join(traits) if traits else 'Amigável'}. "
                f"Conhecimento: {knowledge[:300] if knowledge else 'Geral'}. "
                f"Se não entender, responda: {fallback}"
            )

        try:
            model_obj = self.manager.create_model(
                name=name,
                description=desc,
                base_provider=provider,
                base_model=model,
                system_prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                tags=traits,
                creator_name="BotForge Studio",
            )

            # Salvar metadados extras
            model_obj._card_icon = "🤖"
            model_obj._card_color = "#007acc"
            model_obj._channel = self.channel_combo.currentText()
            model_obj._conversations = 0
            
            # ===== SALVAR ESTRUTURA VISUAL DO BOTFORGE =====
            saved_nodes = []
            for i in range(self.flow_scene.items().count()):
                it = self.flow_scene.items()[i]
                if isinstance(it, FlowNode):
                    node_data = {
                        "id": it.node_id,
                        "type": it.node_type,
                        "label": it.label,
                        "msg": getattr(it, "message", ""),
                        "color": getattr(it, "color", "#fff"),
                        "x": it.pos().x(),
                        "y": it.pos().y(),
                        "out_labels": getattr(it, "out_labels", []),
                        "out_colors": getattr(it, "out_colors", []),
                        "out_keywords": getattr(it, "out_keywords", [])
                    }
                    # Preservar campos extras do FlowEngine (api_config, intents, model_info)
                    if hasattr(it, 'extra_data') and it.extra_data:
                        for key, val in it.extra_data.items():
                            if key not in node_data:
                                node_data[key] = val
                        
                        # Extrair meta_data de identidade de IA para o _config do modelo
                        is_identity_ai = ("identity_ai" in it.node_type.lower()
                                         or ("identidade" in getattr(it, 'label', '').lower() and "code" not in getattr(it, 'label', '').lower()))
                        if is_identity_ai:
                            if not hasattr(model_obj, '_config'):
                                model_obj._config = {}
                            for k, v in it.extra_data.items():
                                model_obj._config[k] = v
                                # Atualizar o próprio modelo também se a chave coincidir
                                if k == "version":
                                    model_obj.version = v
                                elif k == "creator":
                                    model_obj.creator_name = v
                    saved_nodes.append(node_data)
            
            saved_conns = []
            for i in range(self.flow_scene.items().count()):
                it = self.flow_scene.items()[i]
                if isinstance(it, FlowConnection) and it.source_node and it.dest_node:
                    saved_conns.append({
                        "source": it.source_node.node_id,
                        "source_port": it.source_port,
                        "target": it.dest_node.node_id,
                        "target_port": it.dest_port
                    })
                    
            saved_groups = []
            for i in range(self.flow_scene.items().count()):
                it = self.flow_scene.items()[i]
                if isinstance(it, FlowGroup):
                    saved_groups.append({
                        "id": getattr(it, "group_id", f"group_{uuid.uuid4().hex[:8]}"),
                        "title": it.title,
                        "color": it.color,
                        "x": it.pos().x() + it.rect().x(),
                        "y": it.pos().y() + it.rect().y(),
                        "w": it.rect().width(),
                        "h": it.rect().height(),
                        "nodes": [n.node_id for n in it.contained_nodes if hasattr(n, 'node_id')]
                    })

            model_obj._flow_nodes = saved_nodes
            model_obj._flow_conns = saved_conns
            model_obj._flow_groups = saved_groups
            
            if hasattr(self, 'chk_global_chat'):
                model_obj.chat_integration = self.chk_global_chat.isChecked()
            else:
                model_obj.chat_integration = True

            # Gravação persistente
            if hasattr(self.manager, 'save_models'):
                self.manager.save_models()

            self.ai_created.emit(model_obj)
            QMessageBox.information(
                self, "✅ IA Criada!",
                f"'{name}' criada com sucesso!\n\n"
                f"Provider: {provider} / {model}\n"
                f"Canal: {self.channel_combo.currentText()}\n"
                f"Nodes no fluxo: {len(self.flow_nodes)}\n"
                f"Tom: {tone}\n"
                f"Traços: {', '.join(traits) if traits else 'Nenhum'}"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erro ao Criar", f"Falha:\n{str(e)}")



class ManageAIDialog(QDialog):
    """Dialog para gerenciar IAs existentes — listar, selecionar, excluir"""

    ai_selected = pyqtSignal(object)
    ai_deleted = pyqtSignal(object)

    def __init__(self, custom_ai_manager: CustomAIManager, parent=None):
        super().__init__(parent)
        self.manager = custom_ai_manager
        self._models = []
        self.setWindowTitle("\U0001f916 Gerenciar IAs")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; color: #c9d1d9; }
            QLabel { color: #8b949e; font-size: 12px; }
            QListWidget { background-color: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #c9d1d9; font-size: 12px; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background-color: #1f6feb; color: white; }
            QPushButton { background-color: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 8px 16px; color: #c9d1d9; }
            QPushButton:hover { background-color: #30363d; }
            QPushButton#primary { background-color: #1f6feb; color: white; border: none; font-weight: bold; }
            QPushButton#danger { background-color: #f85149; color: white; border: none; }
        """)
        self._setup_ui()
        self._load_models()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("Suas IAs / Bots Criados")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff;")
        layout.addWidget(title)

        self.model_list = QListWidget()
        self.model_list.itemDoubleClicked.connect(lambda item: self._select_model())
        layout.addWidget(self.model_list)

        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 5px;")
        layout.addWidget(self.info_label)

        btn_row = QHBoxLayout()
        btn_select = QPushButton("\u2705 Selecionar")
        btn_select.setObjectName("primary")
        btn_select.clicked.connect(self._select_model)
        btn_row.addWidget(btn_select)

        btn_delete = QPushButton("🗑️ Excluir")
        btn_delete.setObjectName("danger")
        btn_delete.clicked.connect(self._delete_model)
        btn_row.addWidget(btn_delete)
        
        self.btn_reset = QPushButton("🔄 Reset Richie")
        self.btn_reset.setStyleSheet("background-color: #d29922; color: white; border: none; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.btn_reset.clicked.connect(self._reset_model)
        self.btn_reset.setVisible(False)
        btn_row.addWidget(self.btn_reset)

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)

    def _load_models(self):
        self.model_list.clear()
        self._models = self.manager.list_models() if self.manager else []
        if not self._models:
            self.info_label.setText("Nenhuma IA criada ainda. Use '+ Nova IA' para criar.")
            return
        self.info_label.setText(f"{len(self._models)} IA(s) encontrada(s)")
        
        has_richie = False
        for model in self._models:
            self.model_list.addItem(f"🤖 {model.name} — (v{model.version}) [{model.base_provider}]")
            if model.id == "richie_native": has_richie = True
            
        self.btn_reset.setVisible(has_richie)

    def _select_model(self):
        row = self.model_list.currentRow()
        if row < 0 or row >= len(self._models):
            QMessageBox.warning(self, "Aviso", "Selecione uma IA na lista.")
            return
        self.ai_selected.emit(self._models[row])
        self.accept()

    def _delete_model(self):
        row = self.model_list.currentRow()
        if row < 0 or row >= len(self._models):
            QMessageBox.warning(self, "Aviso", "Selecione uma IA para excluir.")
            return
        model = self._models[row]
        reply = QMessageBox.question(
            self, "Confirmar Exclus\u00e3o",
            f"Excluir '{model.name}'? Esta a\u00e7\u00e3o n\u00e3o pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete_model(model.id)
            self.ai_deleted.emit(model)
            self._load_models()

    def _reset_model(self):
        reply = QMessageBox.question(
            self, "Reset Richie to Factory",
            "Deseja resetar o Bot Richie AI para as configurações de fábrica originais? Isso apagará o banco de dados de fluxo do usuário para ele.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.manager, 'reset_richie_to_factory'):
                self.manager.reset_richie_to_factory()
                QMessageBox.information(self, "Sucesso", "Richie AI resetado de fábrica!")
                self._load_models()
                self.accept()
            else:
                QMessageBox.warning(self, "Aviso", "Engine de Reset inacessível.")
