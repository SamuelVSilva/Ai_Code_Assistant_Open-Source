"""
Dialog para Treinamento Avançado de IAs
Permite selecionar projetos, definir especialização e modo de treinamento
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QFrame, QSlider,
    QSpinBox, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QGroupBox, QScrollArea, QCheckBox,
    QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from ...core.training_manager import TrainingManager, TrainingProject, AI_SPECIALIZATIONS
from ...core.custom_ai_manager import CustomAIManager


class IndexingThread(QThread):
    """Thread para indexação de projeto"""
    progress = pyqtSignal(int)
    finished_indexing = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, training_manager: TrainingManager, project_id: str):
        super().__init__()
        self.training_manager = training_manager
        self.project_id = project_id

    def run(self):
        try:
            result = self.training_manager.index_project(self.project_id)
            self.finished_indexing.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TrainingDialog(QDialog):
    """Dialog para configurar treinamento de IA"""

    training_started = pyqtSignal(object)  # Emite quando treinamento inicia

    def __init__(
        self,
        custom_ai_manager: CustomAIManager,
        training_manager: TrainingManager,
        ai_model_id: str = None,
        parent=None
    ):
        super().__init__(parent)
        self.custom_ai_manager = custom_ai_manager
        self.training_manager = training_manager
        self.ai_model_id = ai_model_id
        self.setWindowTitle("Treinamento de IA")
        self.setMinimumSize(800, 700)
        self.setStyleSheet(self._get_styles())
        self._setup_ui()
        self._load_data()

    def _get_styles(self):
        return """
            QDialog {
                background-color: #0f172a;
                color: #f1f5f9;
            }
            QLabel {
                color: #cbd5e1;
                font-size: 13px;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #f1f5f9;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #0ea5e9;
            }
            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: #f1f5f9;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton#primary {
                background-color: #0ea5e9;
            }
            QPushButton#primary:hover {
                background-color: #0284c7;
            }
            QPushButton#success {
                background-color: #22c55e;
            }
            QPushButton#success:hover {
                background-color: #16a34a;
            }
            QGroupBox {
                border: 1px solid #334155;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #94a3b8;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                border-radius: 6px;
                background-color: #1e293b;
            }
            QTabBar::tab {
                background-color: #0f172a;
                color: #94a3b8;
                padding: 8px 16px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #1e293b;
                color: #38bdf8;
            }
            QListWidget {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #f1f5f9;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #334155;
            }
            QListWidget::item:selected {
                background-color: #0ea5e9;
            }
            QCheckBox {
                color: #f1f5f9;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 4px;
                text-align: center;
                background-color: #1e293b;
            }
            QProgressBar::chunk {
                background-color: #0ea5e9;
                border-radius: 3px;
            }
        """

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Título
        title = QLabel("🧠 Treinamento Avançado de IA")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #38bdf8; margin-bottom: 10px;")
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Tab 1: Projetos
        projects_tab = self._create_projects_tab()
        tabs.addTab(projects_tab, "📁 Projetos")

        # Tab 2: Especialização
        spec_tab = self._create_specialization_tab()
        tabs.addTab(spec_tab, "🎯 Especialização")

        # Tab 3: Configurações
        config_tab = self._create_config_tab()
        tabs.addTab(config_tab, "⚙️ Configurações")

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #64748b; font-style: italic;")
        layout.addWidget(self.status_label)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_start = QPushButton("🚀 Iniciar Treinamento")
        btn_start.setObjectName("success")
        btn_start.clicked.connect(self._start_training)
        btn_layout.addWidget(btn_start)

        layout.addLayout(btn_layout)

    def _create_projects_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Descrição
        desc = QLabel(
            "Selecione projetos para a IA aprender. A IA irá analisar o código e aprender "
            "padrões, estilos e boas práticas dos projetos selecionados."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Botões de ação
        btn_layout = QHBoxLayout()

        btn_add = QPushButton("➕ Adicionar Projeto")
        btn_add.clicked.connect(self._add_project)
        btn_layout.addWidget(btn_add)

        btn_remove = QPushButton("🗑️ Remover")
        btn_remove.clicked.connect(self._remove_project)
        btn_layout.addWidget(btn_remove)

        btn_layout.addStretch()

        btn_index = QPushButton("📊 Indexar Selecionado")
        btn_index.setObjectName("primary")
        btn_index.clicked.connect(self._index_project)
        btn_layout.addWidget(btn_index)

        layout.addLayout(btn_layout)

        # Lista de projetos
        self.projects_list = QListWidget()
        layout.addWidget(self.projects_list)

        # Info do projeto selecionado
        self.project_info = QLabel("Selecione um projeto para ver detalhes")
        self.project_info.setStyleSheet("color: #64748b; padding: 10px;")
        layout.addWidget(self.project_info)

        return widget

    def _create_specialization_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Modo de treinamento
        mode_group = QGroupBox("Modo de Treinamento")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_creative = QCheckBox("🎨 Modo Criativo (aprendizagem livre)")
        self.mode_creative.setChecked(True)
        self.mode_creative.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_creative)

        self.mode_specialized = QCheckBox("🎯 Modo Especializado (área específica)")
        self.mode_specialized.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_specialized)

        layout.addWidget(mode_group)

        # Especialização
        spec_group = QGroupBox("Área de Especialização")
        spec_layout = QVBoxLayout(spec_group)

        self.spec_combo = QComboBox()
        self.spec_combo.addItem("Selecione uma área...", "")
        for key, spec in AI_SPECIALIZATIONS.items():
            self.spec_combo.addItem(f"{spec['name']}", key)
        self.spec_combo.currentIndexChanged.connect(self._on_spec_changed)
        self.spec_combo.setEnabled(False)
        spec_layout.addWidget(self.spec_combo)

        self.spec_desc = QLabel("")
        self.spec_desc.setWordWrap(True)
        self.spec_desc.setStyleSheet("color: #94a3b8; padding: 10px;")
        spec_layout.addWidget(self.spec_desc)

        self.spec_providers = QLabel("")
        self.spec_providers.setStyleSheet("color: #38bdf8; padding: 5px;")
        spec_layout.addWidget(self.spec_providers)

        layout.addWidget(spec_group)

        # Consulta a IA externa
        ext_group = QGroupBox("Consulta a IA Externa (para ajudar no treinamento)")
        ext_layout = QVBoxLayout(ext_group)

        ext_layout.addWidget(QLabel("Selecione um provider para auxiliar no treinamento:"))

        self.external_combo = QComboBox()
        self.external_combo.addItem("Sem consulta externa", "")
        self.external_combo.addItem("DeepSeek Coder (mais barato)", "deepseek")
        self.external_combo.addItem("Claude 3.5 Sonnet (balanceado)", "anthropic")
        self.external_combo.addItem("GPT-4 Turbo (alta qualidade)", "openai")
        ext_layout.addWidget(self.external_combo)

        ext_hint = QLabel("⚠️ Consultas externas consomem tokens e têm custo.")
        ext_hint.setStyleSheet("color: #f59e0b; font-size: 11px;")
        ext_layout.addWidget(ext_hint)

        layout.addWidget(ext_group)

        layout.addStretch()
        return widget

    def _create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Limite de tokens explicação
        info_group = QGroupBox("ℹ️ Sobre Limites de Tokens")
        info_layout = QVBoxLayout(info_group)

        info_text = QLabel(
            "• IAs PERSONALIZADAS: Sem limite de retorno! Respostas completas sempre.\n"
            "• Consultas EXTERNAS: Limite aplicado para economia de tokens.\n"
            "• O limite abaixo aplica-se APENAS quando a IA consulta provedores externos."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #22c55e; line-height: 1.5;")
        info_layout.addWidget(info_text)

        layout.addWidget(info_group)

        # Limite de tokens para consultas externas
        tokens_group = QGroupBox("Limite para Consultas Externas")
        tok_layout = QHBoxLayout(tokens_group)

        tok_layout.addWidget(QLabel("Max tokens por consulta:"))

        self.external_limit_spin = QSpinBox()
        self.external_limit_spin.setRange(256, 32000)
        self.external_limit_spin.setValue(4096)
        self.external_limit_spin.setSingleStep(256)
        tok_layout.addWidget(self.external_limit_spin)

        layout.addWidget(tokens_group)

        # Streaming
        stream_group = QGroupBox("Streaming de Respostas")
        stream_layout = QVBoxLayout(stream_group)

        self.enable_streaming = QCheckBox("✅ Habilitar streaming (respostas em tempo real)")
        self.enable_streaming.setChecked(True)
        stream_layout.addWidget(self.enable_streaming)

        layout.addWidget(stream_group)

        # Extensões de arquivo
        ext_group = QGroupBox("Extensões de Arquivo para Treinamento")
        ext_layout = QVBoxLayout(ext_group)

        self.extensions_input = QLineEdit()
        self.extensions_input.setText(".py, .js, .ts, .tsx, .jsx, .java, .cpp, .c, .cs, .go, .rs, .lua")
        self.extensions_input.setPlaceholderText("Extensões separadas por vírgula")
        ext_layout.addWidget(self.extensions_input)

        layout.addWidget(ext_group)

        layout.addStretch()
        return widget

    def _load_data(self):
        """Carrega dados existentes"""
        # Carregar projetos
        for project in self.training_manager.list_projects():
            item = QListWidgetItem(f"📁 {project.name}")
            item.setData(Qt.ItemDataRole.UserRole, project.id)
            if project.total_tokens > 0:
                item.setToolTip(f"Arquivos: {len(project.indexed_files)} | Tokens: {project.total_tokens:,}")
            else:
                item.setToolTip("Não indexado")
            self.projects_list.addItem(item)

        # Conectar seleção
        self.projects_list.itemClicked.connect(self._on_project_selected)

    def _add_project(self):
        """Adiciona novo projeto"""
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Projeto")
        if not path:
            return

        # Pedir nome
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self, "Nome do Projeto",
            "Digite um nome para identificar este projeto:",
            text=path.split("/")[-1].split("\\")[-1]
        )
        if not ok or not name:
            return

        # Criar projeto
        project = self.training_manager.add_project(
            name=name,
            path=path,
            description=f"Projeto importado de {path}"
        )

        # Adicionar à lista
        item = QListWidgetItem(f"📁 {project.name}")
        item.setData(Qt.ItemDataRole.UserRole, project.id)
        item.setToolTip("Não indexado")
        self.projects_list.addItem(item)

        self.status_label.setText(f"Projeto '{name}' adicionado. Indexe para usar no treinamento.")

    def _remove_project(self):
        """Remove projeto selecionado"""
        item = self.projects_list.currentItem()
        if not item:
            return

        project_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Confirmar",
            "Remover este projeto do treinamento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.training_manager.remove_project(project_id)
            self.projects_list.takeItem(self.projects_list.row(item))

    def _index_project(self):
        """Indexa projeto selecionado"""
        item = self.projects_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecione um projeto para indexar")
            return

        project_id = item.data(Qt.ItemDataRole.UserRole)

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.status_label.setText("Indexando projeto...")

        # Indexar em thread separada
        self.indexing_thread = IndexingThread(self.training_manager, project_id)
        self.indexing_thread.finished_indexing.connect(self._on_indexing_finished)
        self.indexing_thread.error.connect(self._on_indexing_error)
        self.indexing_thread.start()

    def _on_indexing_finished(self, result):
        """Callback quando indexação termina"""
        self.progress_bar.setVisible(False)

        if "error" in result:
            self.status_label.setText(f"Erro: {result['error']}")
            return

        self.status_label.setText(
            f"✅ Indexado! {result['files_indexed']} arquivos, ~{result['total_tokens']:,} tokens"
        )

        # Atualizar tooltip do item
        item = self.projects_list.currentItem()
        if item:
            item.setToolTip(f"Arquivos: {result['files_indexed']} | Tokens: {result['total_tokens']:,}")

    def _on_indexing_error(self, error):
        """Callback quando ocorre erro na indexação"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Erro: {error}")

    def _on_project_selected(self, item):
        """Mostra info do projeto selecionado"""
        project_id = item.data(Qt.ItemDataRole.UserRole)
        project = self.training_manager.get_project(project_id)

        if project:
            info = f"📁 {project.name}\n"
            info += f"📍 {project.path}\n"
            if project.total_tokens > 0:
                info += f"📊 {len(project.indexed_files)} arquivos | ~{project.total_tokens:,} tokens"
            else:
                info += "⚠️ Não indexado - clique em 'Indexar' para processar"
            self.project_info.setText(info)

    def _on_mode_changed(self, checked):
        """Atualiza quando modo de treinamento muda"""
        sender = self.sender()
        if sender == self.mode_creative and checked:
            self.mode_specialized.setChecked(False)
            self.spec_combo.setEnabled(False)
        elif sender == self.mode_specialized and checked:
            self.mode_creative.setChecked(False)
            self.spec_combo.setEnabled(True)

    def _on_spec_changed(self, index):
        """Atualiza quando especialização muda"""
        spec_key = self.spec_combo.currentData()
        if not spec_key:
            self.spec_desc.setText("")
            self.spec_providers.setText("")
            return

        spec = AI_SPECIALIZATIONS.get(spec_key, {})
        self.spec_desc.setText(spec.get("description", ""))
        providers = ", ".join(spec.get("recommended_providers", []))
        self.spec_providers.setText(f"Providers recomendados: {providers}")

    def _start_training(self):
        """Inicia o treinamento"""
        # Coletar projetos selecionados (todos na lista)
        project_ids = []
        for i in range(self.projects_list.count()):
            item = self.projects_list.item(i)
            project_ids.append(item.data(Qt.ItemDataRole.UserRole))

        if not project_ids:
            QMessageBox.warning(self, "Aviso", "Adicione pelo menos um projeto para treinamento")
            return

        # Verificar se algum projeto foi indexado
        has_indexed = False
        for pid in project_ids:
            project = self.training_manager.get_project(pid)
            if project and project.total_tokens > 0:
                has_indexed = True
                break

        if not has_indexed:
            QMessageBox.warning(
                self, "Aviso",
                "Nenhum projeto foi indexado. Indexe pelo menos um projeto antes de treinar."
            )
            return

        # Determinar modo e especialização
        mode = "creative" if self.mode_creative.isChecked() else "specialized"
        specialization = self.spec_combo.currentData() if mode == "specialized" else ""
        external_provider = self.external_combo.currentData()

        # Criar sessão de treinamento
        session = self.training_manager.create_training_session(
            ai_model_id=self.ai_model_id or "new",
            project_ids=project_ids,
            mode=mode,
            specialization=specialization,
            external_provider=external_provider
        )

        self.status_label.setText("✅ Sessão de treinamento criada!")
        self.training_started.emit(session)

        QMessageBox.information(
            self, "Treinamento Iniciado",
            f"Sessão de treinamento criada!\n\n"
            f"ID: {session.id}\n"
            f"Modo: {mode}\n"
            f"Projetos: {len(project_ids)}\n\n"
            "A IA irá aprender com os projetos selecionados."
        )

        self.accept()
