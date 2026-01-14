"""
AI Code Assistant - VS Code Style Interface
Versão corrigida - sem erro de "unknown option -width"
"""
import sys
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
from tkinter.font import Font

class VSCodeStyleApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Code Assistant")
        self.root.geometry("1400x900")
        
        # Variáveis
        self.current_folder = None
        self.project_files = []
        
        # Configurar tema dark (similar VS Code)
        self.setup_dark_theme()
        
        # Configurar ícones e fontes
        self.setup_fonts()
        
        # Criar interface
        self.create_widgets()
        
        # Centralizar janela
        self.center_window()
        
    def setup_dark_theme(self):
        """Configura o tema dark similar ao VS Code"""
        self.root.configure(bg='#1e1e1e')
        
        # Cores do tema
        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#252526',
            'bg_tertiary': '#2d2d30',
            'text_primary': '#cccccc',
            'text_secondary': '#858585',
            'accent': '#007acc',
            'accent_hover': '#005a9e',
            'border': '#424242',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f44747',
            'tree_bg': '#181818',
            'editor_bg': '#1e1e1e',
            'editor_line': '#2d2d30',
            'chat_bg': '#252526',
            'chat_input_bg': '#2d2d30',
        }
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos personalizados
        self.configure_styles()
        
    def configure_styles(self):
        """Configura estilos personalizados"""
        colors = self.colors
        
        # Frame principal
        self.style.configure('Main.TFrame', background=colors['bg_primary'])
        
        # Painéis
        self.style.configure('Panel.TFrame', background=colors['bg_secondary'])
        self.style.configure('Panel.TLabel', 
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'],
                           font=('Segoe UI', 10))
        
        # Botões
        self.style.configure('Accent.TButton',
                           background=colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focusthickness=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('Accent.TButton',
                      background=[('active', colors['accent_hover'])])
        
        self.style.configure('Secondary.TButton',
                           background=colors['bg_tertiary'],
                           foreground=colors['text_primary'],
                           borderwidth=1,
                           bordercolor=colors['border'],
                           font=('Segoe UI', 9))
        
        # Treeview (explorer)
        self.style.configure('Treeview',
                           background=colors['tree_bg'],
                           foreground=colors['text_primary'],
                           fieldbackground=colors['tree_bg'],
                           borderwidth=0,
                           font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading',
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'],
                           borderwidth=1,
                           bordercolor=colors['border'],
                           font=('Segoe UI', 10, 'bold'))
        
        # Scrollbars
        self.style.configure('Vertical.TScrollbar',
                           background=colors['bg_tertiary'],
                           troughcolor=colors['bg_secondary'],
                           bordercolor=colors['border'],
                           arrowcolor=colors['text_primary'])
        
        # Notebook (abas)
        self.style.configure('TNotebook',
                           background=colors['bg_primary'],
                           borderwidth=0)
        self.style.configure('TNotebook.Tab',
                           background=colors['bg_secondary'],
                           foreground=colors['text_secondary'],
                           padding=[10, 5],
                           font=('Segoe UI', 10))
        self.style.map('TNotebook.Tab',
                      background=[('selected', colors['accent'])],
                      foreground=[('selected', 'white')])
        
    def setup_fonts(self):
        """Configura as fontes"""
        self.font_normal = Font(family='Consolas', size=11)
        self.font_small = Font(family='Segoe UI', size=9)
        self.font_medium = Font(family='Segoe UI', size=10)
        self.font_large = Font(family='Segoe UI', size=12, weight='bold')
        self.font_code = Font(family='Consolas', size=12)
        
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra superior (similar VS Code)
        self.create_top_bar(main_frame)
        
        # Área principal (split horizontal) - CORRIGIDO
        main_panels = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg=self.colors['bg_primary'], sashwidth=5)
        main_panels.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Painel esquerdo (Explorer)
        left_panel = self.create_left_panel()
        main_panels.add(left_panel, minsize=250, width=280)  # Usar minsize em vez de width
        
        # Painel central (Editor + Chat)
        center_panel = self.create_center_panel()
        main_panels.add(center_panel, minsize=500)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_top_bar(self, parent):
        """Cria a barra superior com menu e ações"""
        top_frame = ttk.Frame(parent, style='Panel.TFrame', height=40)
        top_frame.pack(fill=tk.X, padx=0, pady=0)
        top_frame.pack_propagate(False)
        
        # Logo/título
        title_label = ttk.Label(top_frame,
                              text="🤖 AI Code Assistant",
                              style='Panel.TLabel',
                              font=self.font_large)
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Botões de ação
        button_frame = ttk.Frame(top_frame, style='Panel.TFrame')
        button_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Botão Abrir Projeto
        open_btn = ttk.Button(button_frame,
                            text="📂 Abrir Projeto",
                            style='Accent.TButton',
                            command=self.open_project_folder)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão Nova IA
        new_ai_btn = ttk.Button(button_frame,
                              text="➕ Nova IA",
                              style='Secondary.TButton',
                              command=self.add_new_ai)
        new_ai_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão Configurações
        settings_btn = ttk.Button(button_frame,
                                text="⚙️ Configurações",
                                style='Secondary.TButton',
                                command=self.open_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
    def create_left_panel(self):
        """Cria o painel esquerdo (Explorer)"""
        left_frame = ttk.Frame(self.root, style='Panel.TFrame')
        
        # Título do explorer
        explorer_header = ttk.Frame(left_frame, style='Panel.TFrame', height=40)
        explorer_header.pack(fill=tk.X)
        explorer_header.pack_propagate(False)
        
        explorer_label = ttk.Label(explorer_header,
                                 text="EXPLORER",
                                 style='Panel.TLabel',
                                 font=self.font_medium)
        explorer_label.pack(side=tk.LEFT, padx=15, pady=12)
        
        # Botão refresh
        refresh_btn = ttk.Button(explorer_header,
                               text="↻",
                               style='Secondary.TButton',
                               width=3,
                               command=self.refresh_explorer)
        refresh_btn.pack(side=tk.RIGHT, padx=10, pady=8)
        
        # Área do explorer (treeview)
        explorer_container = ttk.Frame(left_frame, style='Panel.TFrame')
        explorer_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Treeview para mostrar arquivos
        self.tree = ttk.Treeview(explorer_container,
                                style='Treeview',
                                selectmode='browse',
                                show='tree',
                                height=20)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(explorer_container,
                                  orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Empacotar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar treeview
        self.tree.heading('#0', text='', anchor=tk.W)
        
        # Bind evento de clique
        self.tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Status do projeto
        project_status = ttk.Label(left_frame,
                                 text="Nenhum projeto aberto",
                                 style='Panel.TLabel',
                                 font=self.font_small)
        project_status.pack(fill=tk.X, padx=10, pady=(10, 5))
        self.project_status_label = project_status
        
        return left_frame
        
    def create_center_panel(self):
        """Cria o painel central com editor e chat"""
        center_frame = ttk.Frame(self.root, style='Panel.TFrame')
        
        # Split vertical entre editor e chat - CORRIGIDO
        center_split = tk.PanedWindow(center_frame, orient=tk.VERTICAL, bg=self.colors['bg_primary'], sashwidth=5)
        center_split.pack(fill=tk.BOTH, expand=True)
        
        # Editor (parte superior)
        editor_panel = self.create_editor_panel()
        center_split.add(editor_panel, minsize=300, height=500)
        
        # Chat (parte inferior)
        chat_panel = self.create_chat_panel()
        center_split.add(chat_panel, minsize=200)
        
        return center_frame
        
    def create_editor_panel(self):
        """Cria o painel do editor de código"""
        editor_frame = ttk.Frame(self.root, style='Panel.TFrame')
        
        # Barra de abas do editor
        self.notebook = ttk.Notebook(editor_frame, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba inicial
        initial_tab = ttk.Frame(self.notebook, style='Panel.TFrame')
        self.notebook.add(initial_tab, text="welcome.py")
        
        # Frame para linha números + editor
        editor_container = ttk.Frame(initial_tab, style='Panel.TFrame')
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Número de linhas
        line_numbers = tk.Text(editor_container,
                             width=4,
                             bg=self.colors['editor_line'],
                             fg=self.colors['text_secondary'],
                             font=self.font_code,
                             relief=tk.FLAT,
                             borderwidth=0,
                             padx=5,
                             pady=10,
                             state='disabled')
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor de código inicial
        welcome_text = '''# Bem-vindo ao AI Code Assistant! 🤖

1. Clique em "📂 Abrir Projeto" para carregar uma pasta
2. Selecione arquivos no explorer à esquerda
3. Converse com a IA no chat abaixo

## Funcionalidades:
- Análise de código inteligente
- Geração de código com IA
- Suporte a múltiplos provedores (OpenAI, Anthropic, etc.)
- Interface similar ao VS Code

## Comandos disponíveis no chat:
/analyze - Analisar código atual
/generate [linguagem] - Gerar novo código
/explain - Explicar código selecionado
/refactor - Sugerir refatoração

Comece abrindo um projeto ou conversando com a IA!'''
        
        self.editor = scrolledtext.ScrolledText(editor_container,
                                              wrap=tk.WORD,
                                              bg=self.colors['editor_bg'],
                                              fg=self.colors['text_primary'],
                                              insertbackground=self.colors['text_primary'],
                                              font=self.font_code,
                                              relief=tk.FLAT,
                                              borderwidth=0)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.insert(tk.END, welcome_text)
        self.editor.configure(state='disabled')
        
        # Adicionar números de linha
        for i in range(1, 30):
            line_numbers.insert(tk.END, f"{i}\n")
        
        return editor_frame
        
    def create_chat_panel(self):
        """Cria o painel do chat com IA"""
        chat_frame = ttk.Frame(self.root, style='Panel.TFrame')
        
        # Cabeçalho do chat
        chat_header = ttk.Frame(chat_frame, style='Panel.TFrame', height=40)
        chat_header.pack(fill=tk.X)
        chat_header.pack_propagate(False)
        
        chat_label = ttk.Label(chat_header,
                             text="CHAT IA",
                             style='Panel.TLabel',
                             font=self.font_medium)
        chat_label.pack(side=tk.LEFT, padx=15, pady=12)
        
        # Seletor de IA
        ai_frame = ttk.Frame(chat_header, style='Panel.TFrame')
        ai_frame.pack(side=tk.RIGHT, padx=10, pady=8)
        
        ttk.Label(ai_frame,
                 text="IA:",
                 style='Panel.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        
        self.ai_selector = ttk.Combobox(ai_frame,
                                      values=["OpenAI GPT-4", "Anthropic Claude", "DeepSeek", "Local"],
                                      state='readonly',
                                      width=15)
        self.ai_selector.pack(side=tk.LEFT)
        self.ai_selector.set("OpenAI GPT-4")
        
        # Área de mensagens do chat
        chat_container = ttk.Frame(chat_frame, style='Panel.TFrame')
        chat_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Canvas para scroll das mensagens
        self.chat_canvas = tk.Canvas(chat_container,
                                    bg=self.colors['chat_bg'],
                                    highlightthickness=0)
        
        # Scrollbar
        chat_scroll = ttk.Scrollbar(chat_container,
                                  orient=tk.VERTICAL,
                                  command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=chat_scroll.set)
        
        # Frame interno para mensagens
        self.messages_inner = ttk.Frame(self.chat_canvas, style='Panel.TFrame')
        self.chat_canvas.create_window((0, 0), window=self.messages_inner, anchor=tk.NW)
        
        # Empacotar
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar scroll
        self.messages_inner.bind('<Configure>', 
                               lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox('all')))
        
        # Área de entrada
        input_frame = ttk.Frame(chat_frame, style='Panel.TFrame')
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Campo de entrada
        self.chat_input = scrolledtext.ScrolledText(input_frame,
                                                  height=5,
                                                  wrap=tk.WORD,
                                                  bg=self.colors['chat_input_bg'],
                                                  fg=self.colors['text_primary'],
                                                  insertbackground=self.colors['text_primary'],
                                                  font=self.font_medium,
                                                  relief=tk.FLAT,
                                                  borderwidth=1)
        self.chat_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botões de ação do chat
        button_frame = ttk.Frame(input_frame, style='Panel.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Botão enviar
        send_btn = ttk.Button(button_frame,
                            text="📤 Enviar Mensagem",
                            style='Accent.TButton',
                            command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=5)
        
        # Botão limpar
        clear_btn = ttk.Button(button_frame,
                             text="🗑️ Limpar Chat",
                             style='Secondary.TButton',
                             command=self.clear_chat)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Botão anexar
        attach_btn = ttk.Button(button_frame,
                              text="📎 Anexar Arquivo",
                              style='Secondary.TButton',
                              command=self.attach_file)
        attach_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter para enviar (Ctrl+Enter)
        self.chat_input.bind('<Control-Return>', lambda e: self.send_message())
        
        # Adicionar mensagem inicial
        self.add_chat_message("🤖 Assistente", "Olá! Sou seu assistente de código. Como posso ajudar você hoje?")
        
        return chat_frame
        
    def create_status_bar(self, parent):
        """Cria a barra de status inferior"""
        status_frame = ttk.Frame(parent, style='Panel.TFrame', height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Status à esquerda
        left_status = ttk.Frame(status_frame, style='Panel.TFrame')
        left_status.pack(side=tk.LEFT, padx=10)
        
        self.status_label = ttk.Label(left_status,
                                    text="Pronto",
                                    style='Panel.TLabel',
                                    font=self.font_small)
        self.status_label.pack(pady=3)
        
        # Status à direita
        right_status = ttk.Frame(status_frame, style='Panel.TFrame')
        right_status.pack(side=tk.RIGHT, padx=10)
        
        # Contador de tokens
        token_label = ttk.Label(right_status,
                              text="Tokens: 0",
                              style='Panel.TLabel',
                              font=self.font_small)
        token_label.pack(side=tk.RIGHT, padx=10, pady=3)
        
        # Linguagem atual
        lang_label = ttk.Label(right_status,
                             text="Python",
                             style='Panel.TLabel',
                             font=self.font_small)
        lang_label.pack(side=tk.RIGHT, padx=10, pady=3)
        
        # Número de linha/coluna
        pos_label = ttk.Label(right_status,
                            text="Ln 1, Col 1",
                            style='Panel.TLabel',
                            font=self.font_small)
        pos_label.pack(side=tk.RIGHT, padx=10, pady=3)
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def open_project_folder(self):
        """Abre diálogo para selecionar pasta do projeto"""
        folder_path = filedialog.askdirectory(
            title="Selecionar Pasta do Projeto",
            initialdir=Path.home()
        )
        
        if folder_path:
            self.current_folder = Path(folder_path)
            self.project_status_label.config(
                text=f"Projeto: {self.current_folder.name}"
            )
            self.status_label.config(text=f"Projeto aberto: {self.current_folder}")
            self.load_project_files()
            
    def load_project_files(self):
        """Carrega arquivos do projeto para o explorer"""
        if not self.current_folder:
            return
            
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Adicionar projeto como raiz
        project_root = self.tree.insert('', 'end', 
                                      text=f"📁 {self.current_folder.name}",
                                      open=True)
        
        # Carregar arquivos recursivamente
        self.load_files_recursive(self.current_folder, project_root)
        
    def load_files_recursive(self, folder_path, parent_node, depth=0, max_depth=3):
        """Carrega arquivos recursivamente"""
        if depth > max_depth:
            return
            
        try:
            for item in folder_path.iterdir():
                if item.is_dir():
                    # Ignorar diretórios ocultos e venv
                    if item.name.startswith('.') or item.name in ['__pycache__', 'venv', 'node_modules']:
                        continue
                        
                    node = self.tree.insert(parent_node, 'end',
                                          text=f"📁 {item.name}")
                    self.load_files_recursive(item, node, depth + 1, max_depth)
                    
                else:
                    # Ícone baseado na extensão
                    icon = self.get_file_icon(item.suffix)
                    self.tree.insert(parent_node, 'end',
                                   text=f"{icon} {item.name}",
                                   values=[str(item)])
        except PermissionError:
            pass
            
    def get_file_icon(self, extension):
        """Retorna ícone baseado na extensão do arquivo"""
        icons = {
            '.py': '🐍', '.js': '📜', '.jsx': '⚛️', '.ts': '📘', '.tsx': '⚛️',
            '.html': '🌐', '.css': '🎨', '.json': '📋', '.md': '📝', '.txt': '📄',
            '.java': '☕', '.cpp': '⚙️', '.c': '🔧', '.cs': '🌀', '.go': '🚀',
            '.rs': '🦀', '.php': '🐘', '.rb': '💎', '.swift': '🐦', '.kt': '⚡',
            '.sql': '🗄️', '.yml': '⚙️', '.yaml': '⚙️', '.xml': '📊', '.csv': '📈',
        }
        return icons.get(extension.lower(), '📄')
        
    def on_file_select(self, event):
        """Quando um arquivo é selecionado no explorer"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        if values:  # É um arquivo
            file_path = Path(values[0])
            self.open_file_in_editor(file_path)
            
    def open_file_in_editor(self, file_path):
        """Abre um arquivo no editor"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Criar nova aba
            tab_frame = ttk.Frame(self.notebook, style='Panel.TFrame')
            self.notebook.add(tab_frame, text=f"📄 {file_path.name}")
            
            # Frame para linha números + editor
            editor_container = ttk.Frame(tab_frame, style='Panel.TFrame')
            editor_container.pack(fill=tk.BOTH, expand=True)
            
            # Números de linha
            line_numbers = tk.Text(editor_container,
                                 width=4,
                                 bg=self.colors['editor_line'],
                                 fg=self.colors['text_secondary'],
                                 font=self.font_code,
                                 relief=tk.FLAT,
                                 borderwidth=0,
                                 padx=5,
                                 pady=10,
                                 state='disabled')
            line_numbers.pack(side=tk.LEFT, fill=tk.Y)
            
            # Editor
            editor = scrolledtext.ScrolledText(editor_container,
                                             wrap=tk.NONE,
                                             bg=self.colors['editor_bg'],
                                             fg=self.colors['text_primary'],
                                             insertbackground=self.colors['text_primary'],
                                             font=self.font_code,
                                             relief=tk.FLAT,
                                             borderwidth=0)
            editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            editor.insert(tk.END, content)
            
            # Contar linhas
            num_lines = len(content.split('\n'))
            for i in range(1, num_lines + 1):
                line_numbers.insert(tk.END, f"{i}\n")
            
            # Salvar referência
            editor.file_path = file_path
            
            # Mudar para a nova aba
            self.notebook.select(len(self.notebook.tabs()) - 1)
            
            # Atualizar status
            self.status_label.config(text=f"Aberto: {file_path.name}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{str(e)}")
            
    def send_message(self):
        """Envia mensagem no chat"""
        message = self.chat_input.get('1.0', tk.END).strip()
        if not message:
            return
            
        # Adicionar mensagem do usuário
        self.add_chat_message("👤 Você", message)
        
        # Limpar input
        self.chat_input.delete('1.0', tk.END)
        
        # Simular resposta da IA (substituir por integração real)
        self.simulate_ai_response(message)
        
    def add_chat_message(self, sender, message):
        """Adiciona mensagem ao chat"""
        message_frame = ttk.Frame(self.messages_inner, style='Panel.TFrame')
        message_frame.pack(fill=tk.X, padx=10, pady=5, anchor=tk.W)
        
        # Cabeçalho da mensagem
        header = ttk.Frame(message_frame, style='Panel.TFrame')
        header.pack(fill=tk.X)
        
        sender_label = ttk.Label(header,
                               text=sender,
                               style='Panel.TLabel',
                               font=('Segoe UI', 10, 'bold'),
                               foreground=self.colors['accent'])
        sender_label.pack(side=tk.LEFT)
        
        # Corpo da mensagem
        body = tk.Text(message_frame,
                      wrap=tk.WORD,
                      height=4,
                      bg=self.colors['chat_input_bg'],
                      fg=self.colors['text_primary'],
                      font=self.font_medium,
                      relief=tk.FLAT,
                      borderwidth=0,
                      padx=5,
                      pady=5)
        body.pack(fill=tk.X)
        body.insert(tk.END, message)
        body.configure(state='disabled')
        
        # Auto-ajustar altura
        num_lines = len(message.split('\n')) + 1
        body.configure(height=min(num_lines, 10))
        
        # Scroll para baixo
        self.chat_canvas.yview_moveto(1)
        
    def simulate_ai_response(self, user_message):
        """Simula resposta da IA (substituir por integração real)"""
        import time
        import random
        
        # Mostrar "digitando..."
        typing_frame = ttk.Frame(self.messages_inner, style='Panel.TFrame')
        typing_frame.pack(fill=tk.X, padx=10, pady=5, anchor=tk.W)
        
        typing_label = ttk.Label(typing_frame,
                               text="🤖 Assistente está digitando...",
                               style='Panel.TLabel',
                               font=self.font_small,
                               foreground=self.colors['text_secondary'])
        typing_label.pack()
        
        self.root.update()
        time.sleep(1)  # Simular delay
        
        # Remover "digitando..."
        typing_frame.destroy()
        
        # Resposta simulada
        responses = [
            "Entendi sua solicitação! Aqui está minha análise...",
            "Com base no seu código, sugiro as seguintes melhorias...",
            "Vou ajudar você com isso. Aqui está o código gerado:",
            "Analisei seu projeto e encontrei algumas oportunidades de otimização.",
            "Com base nos padrões da indústria, recomendo essa abordagem:"
        ]
        
        response = random.choice(responses)
        
        # Exemplo de resposta com código
        if "código" in user_message.lower() or "code" in user_message.lower():
            response += "\n\n```python\ndef exemplo():\n    print('Hello, World!')\n    return True\n```"
            
        self.add_chat_message("🤖 Assistente", response)
        
    def clear_chat(self):
        """Limpa todas as mensagens do chat"""
        for widget in self.messages_inner.winfo_children():
            widget.destroy()
            
        # Adicionar mensagem inicial novamente
        self.add_chat_message("🤖 Assistente", "Chat limpo. Como posso ajudar você?")
        
    def attach_file(self):
        """Anexa arquivo ao chat"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.add_chat_message("📎 Sistema", f"Arquivo anexado: {Path(file_path).name}")
            
    def refresh_explorer(self):
        """Atualiza o explorer de arquivos"""
        if self.current_folder:
            self.load_project_files()
            self.status_label.config(text="Explorer atualizado")
            
    def add_new_ai(self):
        """Adiciona novo provedor de IA"""
        messagebox.showinfo("Nova IA", "Funcionalidade para adicionar novos provedores de IA.\n\nEm desenvolvimento...")
        
    def open_settings(self):
        """Abre configurações"""
        messagebox.showinfo("Configurações", "Configurações do AI Code Assistant.\n\nEm desenvolvimento...")
        
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        app = VSCodeStyleApp()
        app.run()
    except Exception as e:
        import traceback
        error_msg = f"Erro ao iniciar a aplicação:\n\n{str(e)}\n\n{traceback.format_exc()}"
        
        # Tentar mostrar erro em uma janela simples
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Crítico", error_msg)
        except:
            # Se não conseguir mostrar janela, pelo menos imprimir
            print(error_msg)
            input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()