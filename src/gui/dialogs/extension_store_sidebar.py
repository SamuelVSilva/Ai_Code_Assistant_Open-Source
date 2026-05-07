import traceback
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

class ExtensionStoreSidebar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setStyleSheet("background-color: #0d1117;")
        def get_cmd(win_cmd, lin_cmd, mac_cmd):
            import sys
            if sys.platform == "win32": return win_cmd
            elif sys.platform == "darwin": return mac_cmd
            else: return lin_cmd

        self.extensions = [
            # === IA NATIVA ===
            {"id": "ai.richie", "name": "🤖 Richie — IA Assistente Base", "author": "@S.V.S - Try Technology", "type": "IA Nativa",
             "desc": "A primeira IA integrada do AI Code Assistant. Chat funcional offline, análise de código, execução de scripts, planos de atuação e aprendizado contextual. Disponível para todos sem necessidade de API key."},
            
            # === TEMAS ===
            {"id": "theme.dracula", "name": "Tema Dracula", "author": "Zeno Rocha", "type": "Tema", 
             "desc": "O tema sombrio mais famoso para milhares de aplicações. Torne seu código elegante e reduza a fadiga visual com contraste preciso."},
            {"id": "theme.semitransparent", "name": "Tema Semi Transparente", "author": "Try Technology", "type": "Tema",
             "desc": "Deixa a interface da sua IDE enevoada e refletindo o background do seu Sistema Operacional."},
            {"id": "theme.yellow_light", "name": "Tema Claro Amarelado", "author": "Comunidade", "type": "Tema",
             "desc": "Um tema Solarized refinado. Excelente para ambientes super iluminados."},
            
            # === LINGUAGENS (Com comandos reais de instalação) ===
            {"id": "lang.python", "name": "Python Extension Pack", "author": "Microsoft", "type": "Linguagem",
             "desc": "Suporte massivo a linguagem Python com bibliotecas nativas, linting inteligente e intellisense.",
             "cmd": get_cmd("python --version && python -m pip install --upgrade pip", "python3 --version && python3 -m pip install --upgrade pip", "python3 --version && python3 -m pip install --upgrade pip")},
            {"id": "lang.nodejs", "name": "Node.js Runtime", "author": "OpenJS Foundation", "type": "Linguagem",
             "desc": "Runtime JavaScript para servidor. Essencial para rodar scripts .js fora do navegador.",
             "cmd": get_cmd("node --version && npm --version", "node --version && npm --version", "node --version && npm --version")},
            {"id": "lang.tsnode", "name": "TypeScript Node Compiler", "author": "Microsoft", "type": "Linguagem",
             "desc": "TS-Node engatilha compilação TS transparente. F5 compila sem gerar cache temporário.",
             "cmd": get_cmd("npm install -g ts-node typescript", "echo 'Use o terminal para instalar: sudo npm install -g ts-node typescript' && sh -c 'pkexec npm install -g ts-node typescript || true'", "npm install -g ts-node typescript")},
            {"id": "lang.lua", "name": "Lua Compiler V5", "author": "PUC-Rio", "type": "Linguagem",
             "desc": "Interpretador super leve para games e engine plugins nativos.",
             "cmd": get_cmd("winget install DEVCOM.Lua --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install lua5.3' && sh -c 'pkexec apt-get install -y lua5.3 || true'", "brew install lua")},
            {"id": "lang.gd", "name": "Godot Script Engine", "author": "Godot Foundation", "type": "Linguagem",
             "desc": "Roda debug mode emulado por terminal (GDScript/Godot).",
             "cmd": get_cmd("winget install GodotEngine.GodotEngine --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install godot3' && sh -c 'pkexec apt-get install -y godot3 || true'", "brew install godot")},
            {"id": "lang.java", "name": "Java Development Kit", "author": "Red Hat", "type": "Linguagem",
             "desc": "Integração completa para projetos Java.",
             "cmd": get_cmd("winget install Microsoft.OpenJDK.21 --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install default-jdk' && sh -c 'pkexec apt-get install -y default-jdk || true'", "brew install openjdk")},
            {"id": "lang.csharp", "name": "C# / .NET SDK 8", "author": "Microsoft", "type": "Linguagem",
             "desc": "Motor .NET integrado para compilar, rodar scripts C# e Unity.",
             "cmd": get_cmd("winget install Microsoft.DotNet.SDK.8 --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install dotnet-sdk-8.0' && sh -c 'pkexec apt-get install -y dotnet-sdk-8.0 || true'", "brew install dotnet")},
            {"id": "lang.ruby", "name": "Ruby (Rube)", "author": "Penguin", "type": "Linguagem",
             "desc": "Interpretador nativo Rube / Ruby para web e scripts rápidos.",
             "cmd": get_cmd("winget install RubyInstallerTeam.Ruby.3.2 --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install ruby-full' && sh -c 'pkexec apt-get install -y ruby-full || true'", "brew install ruby")},
            {"id": "lang.kotlin", "name": "Kotlin Language", "author": "JetBrains", "type": "Linguagem",
             "desc": "Moderna programação JVM para Android e Web.",
             "cmd": get_cmd("winget install JetBrains.Kotlin.Compiler --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install kotlin' && sh -c 'pkexec apt-get install -y kotlin || true'", "brew install kotlin")},
            {"id": "lang.swift", "name": "Swift for Windows", "author": "Apple Community", "type": "Linguagem",
             "desc": "Permite compilação e validação do ecossistema Swift da Apple no seu PC.",
             "cmd": get_cmd("winget install Swift.Toolchain --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install swiftlang' && sh -c 'pkexec apt-get install -y swiftlang || true'", "brew install swift")},
            {"id": "lang.go", "name": "Go (Golang)", "author": "Google", "type": "Linguagem",
             "desc": "A linguagem forte em concorrência feita para a nuvem.",
             "cmd": get_cmd("winget install GoLang.Go --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install golang' && sh -c 'pkexec apt-get install -y golang || true'", "brew install go")},
            {"id": "lang.rust", "name": "Rust Analyzer", "author": "Mozilla", "type": "Linguagem",
             "desc": "Performance crítica e memória segura. Compilador Rust V1.",
             "cmd": get_cmd("winget install Rustlang.Rustup --accept-source-agreements --accept-package-agreements", "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y", "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")},
            {"id": "lang.react", "name": "React Snippets", "author": "Meta", "type": "Linguagem",
             "desc": "Melhore sua experiência codando interfaces JSX/React.",
             "cmd": get_cmd("npm install -g create-react-app", "echo 'Por favor instale via terminal: sudo npm install -g create-react-app' && sh -c 'pkexec npm install -g create-react-app || true'", "npm install -g create-react-app")},
            {"id": "lang.php", "name": "PHP Runtime", "author": "The PHP Group", "type": "Linguagem",
             "desc": "Linguagem server-side para web. Essencial para WordPress, Laravel e APIs.",
             "cmd": get_cmd("winget install PHP.PHP --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install php' && sh -c 'pkexec apt-get install -y php || true'", "brew install php")},
            {"id": "lang.cpp", "name": "C/C++ Compiler (MinGW)", "author": "GNU", "type": "Linguagem",
             "desc": "Compilador GCC para Windows. Compile e execute código C e C++.",
             "cmd": get_cmd("winget install MSYS2.MSYS2 --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install build-essential' && sh -c 'pkexec apt-get install -y build-essential || true'", "xcode-select --install")},
             
            # === BANCO DE DADOS ===
            {"id": "db.sql", "name": "SQL & PostgreSQL Server", "author": "Try DB", "type": "Banco de Dados",
             "desc": "Pacote contendo Rube, SQL, Sqlite, psql. Rode e valide queries nativamente no console.",
             "cmd": get_cmd("python -m pip install sqlite3 psycopg2-binary", "python3 -m pip install sqlite3 psycopg2-binary", "python3 -m pip install sqlite3 psycopg2-binary")},
            {"id": "db.mongodb", "name": "MongoDB Tools", "author": "MongoDB Inc", "type": "Banco de Dados",
             "desc": "Ferramentas de linha de comando para MongoDB.",
             "cmd": get_cmd("winget install MongoDB.Shell --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install mongodb-clients' && sh -c 'pkexec apt-get install -y mongodb-clients || true'", "brew tap mongodb/brew && brew install mongodb-community")},
             
            # === APLICATIVOS ===
            {"id": "app.android_emu", "name": "Simulador de Android", "author": "Google Inc", "type": "Aplicativo",
             "desc": "Emulador robusto de Android para simular e testar aplicativos híbridos ou nativos direto na IDE."},
            {"id": "app.docker", "name": "Docker Desktop", "author": "Docker Inc", "type": "Aplicativo",
             "desc": "Containerização de aplicações. Execute ambientes isolados.",
             "cmd": get_cmd("winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install docker.io' && sh -c 'pkexec apt-get install -y docker.io || true'", "brew install --cask docker")},
             
            # === PACOTES / BIBLIOTECAS ===
            {"id": "lib.tkinter", "name": "Biblioteca: Python Tkinter", "author": "Python Auth", "type": "Pacote",
             "desc": "Instala o motor gráfico padrão do Python para testar UI de programas (Pip auto mode).",
             "cmd": get_cmd("python -m pip install tk", "python3 -m pip install tk", "python3 -m pip install tk")},
            {"id": "lib.love2d", "name": "Engine: LÖVE 2D", "author": "LÖVE Foundation", "type": "Pacote",
             "desc": "Framework de jogos 2D para linguagem LUA. Instalação via winget.",
             "cmd": get_cmd("winget install love.love --accept-source-agreements --accept-package-agreements", "echo 'Por favor instale via terminal: sudo apt-get install love' && sh -c 'pkexec apt-get install -y love || true'", "brew install --cask love")},
            {"id": "lib.lapis", "name": "Lapis Server (Lua)", "author": "Leaf", "type": "Pacote",
             "desc": "Framework web ultrarrápido rodando sob OpenResty/Lua.",
             "cmd": get_cmd("luarocks install lapis", "echo 'Por favor instale via terminal: sudo luarocks install lapis' && sh -c 'pkexec luarocks install lapis || true'", "luarocks install lapis")},
            {"id": "lib.pygame", "name": "Biblioteca: Pygame", "author": "Pygame Community", "type": "Pacote",
             "desc": "Desenvolvimento de jogos 2D em Python. Gráficos, sons e inputs.",
             "cmd": get_cmd("python -m pip install pygame", "python3 -m pip install pygame", "python3 -m pip install pygame")},
            {"id": "lib.flask", "name": "Biblioteca: Flask", "author": "Pallets", "type": "Pacote",
             "desc": "Micro-framework web Python para APIs e sites.",
             "cmd": get_cmd("python -m pip install flask", "python3 -m pip install flask", "python3 -m pip install flask")},
            {"id": "lib.django", "name": "Biblioteca: Django", "author": "Django Foundation", "type": "Pacote",
             "desc": "Framework web Python completo para aplicações robustas.",
             "cmd": get_cmd("python -m pip install django", "python3 -m pip install django", "python3 -m pip install django")},
            {"id": "lib.numpy", "name": "Biblioteca: NumPy", "author": "NumPy Contributors", "type": "Pacote",
             "desc": "Computação numérica de alto desempenho em Python.",
             "cmd": get_cmd("python -m pip install numpy", "python3 -m pip install numpy", "python3 -m pip install numpy")},
            {"id": "lib.pandas", "name": "Biblioteca: Pandas", "author": "Wes McKinney", "type": "Pacote",
             "desc": "Análise de dados poderosa e estruturada em Python.",
             "cmd": get_cmd("python -m pip install pandas", "python3 -m pip install pandas", "python3 -m pip install pandas")},
            {"id": "lib.tensorflow", "name": "Biblioteca: TensorFlow", "author": "Google Brain", "type": "Pacote",
             "desc": "Plataforma avançada para Machine Learning e Redes Neurais.",
             "cmd": get_cmd("python -m pip install tensorflow", "python3 -m pip install tensorflow", "python3 -m pip install tensorflow")},
            {"id": "lib.express", "name": "Biblioteca: Express.js", "author": "TJ Holowaychuk", "type": "Pacote",
             "desc": "Framework web minimalista para Node.js.",
             "cmd": get_cmd("npm install -g express-generator", "echo 'Por favor instale via terminal: sudo npm install -g express-generator' && sh -c 'pkexec npm install -g express-generator || true'", "npm install -g express-generator")},
            {"id": "lib.electron", "name": "Biblioteca: Electron", "author": "GitHub", "type": "Pacote",
             "desc": "Construa aplicações desktop multiplataforma com JavaScript, HTML e CSS.",
             "cmd": get_cmd("npm install -g electron", "echo 'Por favor instale via terminal: sudo npm install -g electron' && sh -c 'pkexec npm install -g electron || true'", "npm install -g electron")},
            {"id": "lib.react", "name": "Biblioteca: React (Next.js)", "author": "Meta / Vercel", "type": "Pacote",
             "desc": "Biblioteca p/ criar interfaces modernas de UI. (Instalação Global Next CLI)",
             "cmd": get_cmd("npm install -g create-next-app", "echo 'Por favor instale via terminal: sudo npm install -g create-next-app' && sh -c 'pkexec npm install -g create-next-app || true'", "npm install -g create-next-app")},
            {"id": "lib.tailwindcss", "name": "Biblioteca: Tailwind CSS", "author": "Tailwind Labs", "type": "Pacote",
             "desc": "Framework CSS Utility-first acelerado.",
             "cmd": get_cmd("npm install -g tailwindcss", "echo 'Por favor instale via terminal: sudo npm install -g tailwindcss' && sh -c 'pkexec npm install -g tailwindcss || true'", "npm install -g tailwindcss")},
        ]
        self.card_widgets = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(10, 5, 10, 5)
        
        btn_back = QPushButton("⬅️ Voltar")
        btn_back.setStyleSheet("background: transparent; color: #58a6ff; border:none; padding: 5px; font-weight:bold;")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self._go_back)
        h_lay.addWidget(btn_back)
        h_lay.addStretch()
        main_layout.addWidget(header)
        
        # Search Box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filtrar extensões, linguagens...")
        self.search_box.setStyleSheet("background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; padding: 6px; margin: 0 10px; border-radius: 3px;")
        self.search_box.textChanged.connect(self._filter_list)
        main_layout.addWidget(self.search_box)
        main_layout.addSpacing(10)
        
        # Scroll Area for List
        self.scroll_list = QScrollArea()
        self.scroll_list.setWidgetResizable(True)
        self.scroll_list.setStyleSheet("border: none; background-color: transparent;")
        
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_list.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_list)
        
        self._build_list()

    def _build_list(self):
        for e in self.extensions:
            card = QPushButton()
            card.setStyleSheet("""
                QPushButton { background-color: transparent; border: none; border-bottom: 1px solid #30363d; text-align: left; padding: 10px; }
                QPushButton:hover { background-color: #21262d; }
            """)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            
            cw_lay = QVBoxLayout(card)
            cw_lay.setContentsMargins(0,0,0,0)
            ln = QLabel(e['name'])
            ln.setStyleSheet("color: #58a6ff; font-weight: bold;")
            ld = QLabel(e['type'])
            ld.setStyleSheet("color: #8b949e; font-size: 11px;")
            
            # Indicador de comando disponível
            has_cmd = "cmd" in e and e["cmd"]
            cmd_indicator = QLabel("✅ Instalável" if has_cmd else "📋 Mock")
            cmd_indicator.setStyleSheet(f"color: {'#3fb950' if has_cmd else '#8b949e'}; font-size: 10px;")
            
            cw_lay.addWidget(ln)
            cw_lay.addWidget(ld)
            cw_lay.addWidget(cmd_indicator)
            
            card.clicked.connect(lambda ch, ext=e: self._open_detail(ext))
            self.list_layout.addWidget(card)
            self.card_widgets.append((card, e))

    def _filter_list(self, text):
        search_text = text.lower()
        for card, ext in self.card_widgets:
            match = search_text in ext['name'].lower() or search_text in ext['type'].lower() or search_text in ext['desc'].lower()
            card.setVisible(match)

    def _open_detail(self, ext):
        try:
            # Card da Richie: ativar no chat ao invés de abrir tab de instalação
            if ext.get("id") == "ai.richie":
                # Selecionar Richie no ComboBox do chat
                for i in range(self.main_window.ai_select.count()):
                    if self.main_window.ai_select.itemText(i) == "🤖 Richie":
                        self.main_window.ai_select.setCurrentIndex(i)
                        break
                self.main_window.status.showMessage("🤖 Richie AI ativada! Use o chat à direita.", 3000)
                return
            self.main_window._open_store_tab_for(ext)
        except Exception as e:
            print("Error open detail", str(e))
            traceback.print_exc()

    def _go_back(self):
        # Transitar o QStackedWidget principal
        self.main_window.extensions_stack.setCurrentIndex(0)
