from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QTreeView, QTextEdit, QLineEdit, 
                            QPushButton, QToolBar, QFileSystemModel, 
                            QStatusBar, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QIcon
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AI Code Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Criar barra de menu
        self.create_menu_bar()
        
        # Criar barra de ferramentas
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Painel esquerdo - Navegador de arquivos
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_tree.setModel(self.file_model)
        self.file_tree.setColumnWidth(0, 250)
        
        # Painel central - Chat
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        
        send_button = QPushButton("Enviar")
        send_button.clicked.connect(self.send_message)
        
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(send_button)
        
        # Painel direito - Informações do projeto
        info_panel = QWidget()
        info_layout = QVBoxLayout(info_panel)
        
        self.project_info = QTextEdit()
        self.project_info.setReadOnly(True)
        
        info_layout.addWidget(self.project_info)
        
        # Adicionar widgets ao splitter
        splitter.addWidget(self.file_tree)
        splitter.addWidget(chat_panel)
        splitter.addWidget(info_panel)
        splitter.setSizes([300, 600, 300])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Pronto")
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")
        
        open_action = QAction("Abrir Projeto", self)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu IA
        ai_menu = menu_bar.addMenu("IA")
        
        add_ai_action = QAction("Adicionar IA", self)
        add_ai_action.triggered.connect(self.add_ai_provider)
        ai_menu.addAction(add_ai_action)
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar("Ferramentas")
        self.addToolBar(toolbar)
        
        open_btn = QPushButton("Abrir Projeto")
        open_btn.clicked.connect(self.open_project)
        toolbar.addWidget(open_btn)
        
        analyze_btn = QPushButton("Analisar Projeto")
        analyze_btn.clicked.connect(self.analyze_project)
        toolbar.addWidget(analyze_btn)
        
    def open_project(self):
        from PyQt6.QtWidgets import QFileDialog
        
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Projeto")
        if folder:
            self.file_model.setRootPath(folder)
            self.file_tree.setRootIndex(self.file_model.index(folder))
            self.statusBar().showMessage(f"Projeto aberto: {folder}")
            
    def analyze_project(self):
        # Implementar análise do projeto
        self.chat_display.append("Analisando projeto...")
        
    def send_message(self):
        message = self.chat_input.toPlainText().strip()
        if message:
            self.chat_display.append(f"Você: {message}")
            self.chat_input.clear()
            # Aqui você processaria a mensagem com a IA
    
    def add_ai_provider(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Adicionar IA")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Selecione o provedor de IA:"))
        
        provider_combo = QComboBox()
        provider_combo.addItems(["OpenAI", "Anthropic", "Local", "Custom"])
        layout.addWidget(provider_combo)
        
        add_button = QPushButton("Adicionar")
        add_button.clicked.connect(dialog.accept)
        layout.addWidget(add_button)
        
        if dialog.exec():
            provider = provider_combo.currentText()
            self.chat_display.append(f"Adicionando provedor: {provider}")
    
    def show_about(self):
        QMessageBox.about(self, "Sobre", 
                         "AI Code Assistant\n\n"
                         "Versão 1.0\n"
                         "Um assistente de código com suporte a múltiplas IAs")