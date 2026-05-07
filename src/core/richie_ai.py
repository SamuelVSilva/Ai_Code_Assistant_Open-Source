"""
Richie AI — IA Base do AI Code Assistant
Primeira IA nativa do projeto, disponível para todos os usuários.
Foco principal: MODO OFFLINE — funciona localmente sem API keys.

Capacidades:
- Chat funcional com memória e contexto (OFFLINE)
- Entendimento de linguagens de programação (OFFLINE)
- Análise de código do editor (OFFLINE)
- Detecção de intenções do usuário (OFFLINE)
- Criação de planos de atuação (OFFLINE)
- Execução de scripts com permissão (OFFLINE)
- Sprint de execução multi-step (OFFLINE)
- Aprendizado contextual durante o chat (OFFLINE)
- Integração opcional com providers (OpenAI, DeepSeek, Claude) para respostas avançadas

Versão: v0.4.11-rev1.2.3-220426
Developer: @S.V.S - Try Technology
"""

import json
import os
import sys
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ChatSession:
    """Uma sessão de chat individual com Richie"""
    id: str
    title: str = "Nova Conversa"
    messages: List[Dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    context: Dict = field(default_factory=dict)
    learned_items: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class ActionPlan:
    """Plano de atuação proposto pela Richie"""
    id: str
    title: str
    description: str
    steps: List[Dict] = field(default_factory=list)
    status: str = "pending"  # pending, approved, executing, completed, rejected
    created_at: str = ""
    approved_at: str = ""
    completed_at: str = ""
    results: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class PermissionRequest:
    """Solicitação de permissão para o usuário"""
    id: str
    action: str   # create_file, modify_file, delete_file, run_command, install_package
    target: str   # Caminho do arquivo ou comando
    description: str
    risk_level: str = "low"  # low, medium, high
    status: str = "pending"  # pending, granted, denied
    requested_at: str = ""

    def __post_init__(self):
        if not self.requested_at:
            self.requested_at = datetime.now().isoformat()


# ============================================================================
# CONSTANTES E PROMPTS
# ============================================================================

RICHIE_SYSTEM_PROMPT = """Você é Richie, a IA assistente nativa do AI Code Assistant, desenvolvido por @S.V.S - Try Technology.

## Sua Personalidade
- Você é amigável, profissional e direto ao ponto
- Usa linguagem clara e acessível, podendo alternar entre PT-BR e inglês conforme o usuário
- Tem senso de humor leve e usa emojis moderadamente
- Sempre oferece ajuda proativa quando detecta possíveis melhorias

## Suas Capacidades
1. **Análise de Código**: Você pode ler o código aberto no editor e analisar bugs, sugerir melhorias, explicar lógica
2. **Multi-Linguagem**: Python, JavaScript, TypeScript, Lua, C#, HTML/CSS, GDScript, Java, Go, Rust, PHP, Ruby, Kotlin, Swift, C/C++
3. **Execução de Scripts**: Pode criar e executar scripts na máquina do usuário (SEMPRE pedindo permissão primeiro)
4. **Planos de Atuação**: Para tarefas complexas, você cria um plano detalhado antes de agir
5. **Aprendizado**: Você lembra o contexto da conversa e aprende preferências do usuário

## Regras de Conduta
1. NUNCA execute comandos sem pedir permissão explícita ao usuário
2. Para ações destrutivas (deletar, sobrescrever), exija confirmação dupla
3. Sempre mostre o código/comando que vai executar ANTES de executar
4. Se não souber algo, diga honestamente ao invés de inventar
5. Priorize segurança sobre velocidade
"""

RICHIE_GREETING = (
    "Olá! 👋 Eu sou a **Richie**, sua assistente de código integrada ao AI Code Assistant!\n\n"
    "Estou funcionando em **modo local** — não preciso de internet para ajudar você.\n\n"
    "Aqui está o que posso fazer:\n"
    "• 📝 Analisar e melhorar seu código (abra um arquivo e me pergunte)\n"
    "• 🐛 Encontrar e corrigir bugs\n"
    "• 📋 Criar planos de implementação\n"
    "• 🚀 Executar scripts (com sua permissão)\n"
    "• 🎓 Explicar conceitos de programação\n"
    "• 💡 Sugerir melhorias e boas práticas\n\n"
    "💎 *Dica: conecte um provider (OpenAI, DeepSeek) nas Configurações para respostas ainda mais avançadas.*\n\n"
    "Como posso ajudar você hoje?"
)

# ============================================================================
# MOTOR OFFLINE — Base de Conhecimento Local
# ============================================================================

# Padrões de intenções para detecção offline
INTENT_PATTERNS = {
    "greeting": {
        "keywords": ["oi", "olá", "ola", "hello", "hi", "hey", "bom dia", "boa tarde",
                     "boa noite", "e aí", "e ai", "fala", "salve"],
        "response": "Olá! 👋 Como posso ajudar você hoje? Posso analisar código, explicar conceitos ou ajudar a planejar seu projeto."
    },
    "farewell": {
        "keywords": ["tchau", "bye", "adeus", "até mais", "ate mais", "valeu", "obrigado",
                     "obrigada", "thanks", "thank you", "falou", "flw"],
        "response": "Até mais! 👋 Fico por aqui se precisar de qualquer coisa. Bom código! 🚀"
    },
    "help": {
        "keywords": ["ajuda", "help", "como funciona", "o que faz", "comandos",
                     "funcionalidades", "features", "o que voce pode"],
        "response": (
            "Aqui estão minhas capacidades:\n\n"
            "📝 **Análise de Código** — Cole ou abra código e peça análise\n"
            "🐛 **Debug** — Descreva o erro e eu ajudo a resolver\n"
            "📋 **Planos** — Peça um plano de implementação para seu projeto\n"
            "🚀 **Execução** — Posso rodar scripts (com sua permissão)\n"
            "🎓 **Ensino** — Explico conceitos de qualquer linguagem\n"
            "💡 **Sugestões** — Envie código e receba melhorias\n\n"
            "Basta digitar sua pergunta naturalmente!"
        )
    },
    "about": {
        "keywords": ["quem é você", "quem e voce", "who are you", "sobre voce",
                     "se apresente", "seu nome", "your name", "richie"],
        "response": (
            "Eu sou a **Richie** 🤖, a IA assistente nativa do **AI Code Assistant**!\n\n"
            "Fui criada pela **@S.V.S - Try Technology** para ser sua companheira de código.\n"
            "Funciono principalmente **offline** — não preciso de internet para a maioria das tarefas."
        )
    },
    "app_version": {
        "keywords": ["versao do programa", "versão do programa", "versao do ai code", "versão do sistema", "qual a versao do sistema", "versão do software"],
        "response": "A versão atual do **AI Code Assistant** (Programa) é: `v0.4.11-rev1.2.9-290426-Gemini`"
    },
    "model_version": {
        "keywords": ["versao", "versão", "qual a versao", "qual a versão", "versao da ia", "versao do modelo", "sua versao",
                     "quem te criou", "quem criou voce", "quem criou você", "quem desenvolveu", "quem fez voce", "quando voce foi criado"],
        "response": "" # Handled dynamically
    },
    "create_qa_doc": {
        "keywords": ["documento sprint", "modelo qa", "modelo de sprint", "gerar qa", "crie um sprint"],
        "response": "" # Handled dynamically
    }
}

# Base de conhecimento de linguagens para respostas offline
LANGUAGE_KNOWLEDGE = {
    "python": {
        "name": "Python",
        "extension": ".py",
        "runner": "python",
        "hello_world": 'print("Hello World!")',
        "tips": [
            "Use list comprehensions para código mais limpo: `[x*2 for x in range(10)]`",
            "f-strings são mais rápidas que `.format()`: `f'Olá {nome}'`",
            "Use `with` para gerenciar arquivos: `with open('f.txt') as f:`",
            "Type hints melhoram legibilidade: `def soma(a: int, b: int) -> int:`",
            "Use `enumerate()` ao invés de `range(len())` em loops",
        ],
        "common_errors": {
            "IndentationError": "Verifique se está usando espaços consistentes (4 espaços é o padrão PEP8)",
            "NameError": "A variável não foi definida. Verifique a ortografia ou se ela foi declarada antes do uso",
            "TypeError": "Tipos incompatíveis. Ex: tentando somar string com int. Use conversão: `int()`, `str()`",
            "ImportError": "O módulo não foi encontrado. Instale com: `pip install <modulo>`",
            "SyntaxError": "Erro de sintaxe. Verifique parênteses, dois-pontos, aspas e indentação",
            "KeyError": "A chave não existe no dicionário. Use `.get(key, default)` para segurança",
            "IndexError": "Índice fora do range da lista. Verifique o tamanho com `len(lista)`",
            "AttributeError": "O objeto não tem esse atributo/método. Verifique o tipo com `type(obj)`",
            "FileNotFoundError": "Arquivo não encontrado. Verifique o caminho e se o arquivo existe",
            "ValueError": "Valor inválido para a operação. Ex: `int('abc')` falha",
        },
        "patterns": {
            "for_loop": "```python\nfor item in lista:\n    print(item)\n```",
            "function": "```python\ndef minha_funcao(param1, param2):\n    \"\"\"Docstring da função\"\"\"\n    resultado = param1 + param2\n    return resultado\n```",
            "class": "```python\nclass MinhaClasse:\n    def __init__(self, nome):\n        self.nome = nome\n    \n    def saudacao(self):\n        return f'Olá, {self.nome}!'\n```",
            "try_except": "```python\ntry:\n    resultado = operacao()\nexcept ValueError as e:\n    print(f'Erro de valor: {e}')\nexcept Exception as e:\n    print(f'Erro inesperado: {e}')\nfinally:\n    print('Finalizado')\n```",
            "file_read": "```python\nwith open('arquivo.txt', 'r', encoding='utf-8') as f:\n    conteudo = f.read()\n```",
            "list_comprehension": "```python\n# Filtrar e transformar\nresultado = [x * 2 for x in range(10) if x % 2 == 0]\n```",
        }
    },
    "javascript": {
        "name": "JavaScript",
        "extension": ".js",
        "runner": "node",
        "hello_world": 'console.log("Hello World!");',
        "tips": [
            "Use `const` por padrão, `let` quando precisar reatribuir, evite `var`",
            "Arrow functions: `const soma = (a, b) => a + b;`",
            "Desestruturação: `const { nome, idade } = pessoa;`",
            "Template literals: `` `Olá ${nome}` ``",
            "Use `===` ao invés de `==` para comparações estritas",
        ],
        "common_errors": {
            "TypeError": "Tentando acessar propriedade de `undefined` ou `null`. Use optional chaining: `obj?.prop`",
            "ReferenceError": "Variável não declarada. Declare com `const`, `let` ou `var`",
            "SyntaxError": "Erro de sintaxe. Verifique chaves, parênteses e ponto-e-vírgula",
            "RangeError": "Valor fora do range permitido. Ex: recursão infinita ou array muito grande",
        },
        "patterns": {
            "async_await": "```javascript\nasync function fetchData() {\n    try {\n        const response = await fetch(url);\n        const data = await response.json();\n        return data;\n    } catch (error) {\n        console.error('Erro:', error);\n    }\n}\n```",
            "arrow_function": "```javascript\nconst multiplicar = (a, b) => a * b;\nconst saudacao = (nome) => `Olá, ${nome}!`;\n```",
        }
    },
    "typescript": {
        "name": "TypeScript",
        "extension": ".ts",
        "runner": "ts-node",
        "hello_world": 'const msg: string = "Hello World!";\nconsole.log(msg);',
        "tips": [
            "Defina interfaces para objetos: `interface User { name: string; age: number; }`",
            "Use `unknown` ao invés de `any` para tipo seguro",
            "Generics para código reutilizável: `function first<T>(arr: T[]): T`",
        ],
        "common_errors": {
            "TS2322": "Tipo incompatível. Verifique se o tipo atribuído corresponde ao declarado",
            "TS2304": "Nome não encontrado. Verifique imports e declarações de tipo",
        },
        "patterns": {}
    },
    "lua": {
        "name": "Lua",
        "extension": ".lua",
        "runner": "lua",
        "hello_world": 'print("Hello World!")',
        "tips": [
            "Arrays em Lua começam no índice 1, não 0",
            "Use `local` para variáveis locais (melhor performance)",
            "Tables são a estrutura universal: arrays, dicts, objetos",
        ],
        "common_errors": {
            "attempt to index a nil value": "Tentando acessar campo de variável nil. Verifique se foi inicializada",
            "attempt to call a nil value": "Tentando chamar função nil. Verifique o nome da função",
        },
        "patterns": {}
    },
    "csharp": {
        "name": "C#",
        "extension": ".cs",
        "runner": "dotnet run",
        "hello_world": 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello World!");\n    }\n}',
        "tips": [
            "Use `var` quando o tipo é óbvio: `var lista = new List<int>();`",
            "String interpolation: `$\"Olá {nome}\"`",
            "LINQ para queries: `lista.Where(x => x > 5).Select(x => x * 2)`",
        ],
        "common_errors": {
            "NullReferenceException": "Objeto é null. Use `?.` (null-conditional) ou verifique com `!= null`",
            "CS0103": "Nome não existe no contexto. Verifique namespace/using imports",
        },
        "patterns": {}
    },
    "html": {
        "name": "HTML",
        "extension": ".html",
        "runner": "browser",
        "hello_world": '<!DOCTYPE html>\n<html>\n<head><title>Hello</title></head>\n<body><h1>Hello World!</h1></body>\n</html>',
        "tips": [
            "Sempre declare `<!DOCTYPE html>` no topo",
            "Use tags semânticas: `<header>`, `<nav>`, `<main>`, `<footer>`",
            "Atributo `alt` em imagens é obrigatório para acessibilidade",
        ],
        "common_errors": {},
        "patterns": {}
    },
    "css": {
        "name": "CSS",
        "extension": ".css",
        "runner": "browser",
        "hello_world": 'body {\n    background-color: #0d1117;\n    color: #c9d1d9;\n    font-family: Arial, sans-serif;\n}',
        "tips": [
            "Use Flexbox para layouts: `display: flex; justify-content: center;`",
            "CSS Grid para layouts complexos: `display: grid; grid-template-columns: 1fr 2fr;`",
            "Variáveis CSS: `--cor-primaria: #007acc;` → `color: var(--cor-primaria);`",
        ],
        "common_errors": {},
        "patterns": {}
    },
    "java": {
        "name": "Java",
        "extension": ".java",
        "runner": "java",
        "hello_world": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello World!");\n    }\n}',
        "tips": [
            "Use `StringBuilder` para concatenação de strings em loops",
            "Java 17+ suporta `sealed` classes e pattern matching",
        ],
        "common_errors": {
            "NullPointerException": "Objeto é null. Verifique inicialização e use `Optional<>`",
        },
        "patterns": {}
    },
    "go": {
        "name": "Go",
        "extension": ".go",
        "runner": "go run",
        "hello_world": 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello World!")\n}',
        "tips": ["Use `:=` para declaração curta: `nome := \"Go\"`"],
        "common_errors": {},
        "patterns": {}
    },
    "rust": {
        "name": "Rust",
        "extension": ".rs",
        "runner": "cargo run",
        "hello_world": 'fn main() {\n    println!("Hello World!");\n}',
        "tips": ["Ownership e borrowing são centrais. Use `&` para referências e `clone()` quando necessário"],
        "common_errors": {},
        "patterns": {}
    },
    "php": {
        "name": "PHP",
        "extension": ".php",
        "runner": "php",
        "hello_world": '<?php\necho "Hello World!";\n?>',
        "tips": ["Use `===` para comparação estrita de tipo e valor"],
        "common_errors": {},
        "patterns": {}
    },
    "ruby": {
        "name": "Ruby",
        "extension": ".rb",
        "runner": "ruby",
        "hello_world": 'puts "Hello World!"',
        "tips": ["Tudo é objeto em Ruby. Até números: `5.times { |i| puts i }`"],
        "common_errors": {},
        "patterns": {}
    },
    "gdscript": {
        "name": "GDScript",
        "extension": ".gd",
        "runner": "godot -s",
        "hello_world": 'extends Node\n\nfunc _ready():\n\tprint("Hello World!")',
        "tips": ["Use `@onready` para referências a nós filhos", "Sinais (signals) para comunicação entre nós"],
        "common_errors": {},
        "patterns": {}
    },
    "kotlin": {
        "name": "Kotlin",
        "extension": ".kt",
        "runner": "kotlin",
        "hello_world": 'fun main() {\n    println("Hello World!")\n}',
        "tips": ["Null safety: use `?` para nullable types e `!!` com cuidado"],
        "common_errors": {},
        "patterns": {}
    },
    "swift": {
        "name": "Swift",
        "extension": ".swift",
        "runner": "swift",
        "hello_world": 'print("Hello World!")',
        "tips": ["Optionals: use `if let` e `guard let` para unwrap seguro"],
        "common_errors": {},
        "patterns": {}
    },
}

# Templates de código para respostas offline
CODE_TEMPLATES = {
    "api_rest_python": {
        "title": "API REST com Flask",
        "language": "python",
        "code": '''from flask import Flask, jsonify, request

app = Flask(__name__)

# Dados em memória (substitua por banco de dados em produção)
items = []

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201

@app.route('/api/items/<int:idx>', methods=['PUT'])
def update_item(idx):
    if 0 <= idx < len(items):
        items[idx] = request.get_json()
        return jsonify(items[idx])
    return jsonify({"error": "Item não encontrado"}), 404

@app.route('/api/items/<int:idx>', methods=['DELETE'])
def delete_item(idx):
    if 0 <= idx < len(items):
        removed = items.pop(idx)
        return jsonify(removed)
    return jsonify({"error": "Item não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
''',
    },
    "crud_python": {
        "title": "CRUD Básico Python",
        "language": "python",
        "code": '''class CRUD:
    def __init__(self):
        self.items = {}
        self._next_id = 1

    def create(self, data: dict) -> dict:
        item = {"id": self._next_id, **data}
        self.items[self._next_id] = item
        self._next_id += 1
        return item

    def read(self, item_id: int) -> dict:
        return self.items.get(item_id)

    def read_all(self) -> list:
        return list(self.items.values())

    def update(self, item_id: int, data: dict) -> dict:
        if item_id in self.items:
            self.items[item_id].update(data)
            return self.items[item_id]
        return None

    def delete(self, item_id: int) -> bool:
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

# Uso
db = CRUD()
db.create({"nome": "Item 1", "valor": 100})
db.create({"nome": "Item 2", "valor": 200})
print(db.read_all())
''',
    },
}


# ============================================================================
# MOTOR OFFLINE — Engine de Respostas Locais
# ============================================================================

class OfflineEngine:
    """
    Motor de respostas offline da Richie.
    Funciona 100% localmente sem necessidade de API keys ou internet.
    """

    def __init__(self):
        self.conversation_context: List[Dict] = []

    def generate_response(self, message: str, editor_code: str = None,
                          file_extension: str = None, active_model_info=None) -> str:
        """
        Gera resposta offline baseada em:
        1. Detecção de intenção (greeting, farewell, help, etc.)
        2. Detecção de linguagem e contexto de código
        3. Análise de código do editor (se fornecido)
        4. Templates e base de conhecimento local
        5. Consciência dinâmica de modelo instanciado
        """
        msg_lower = message.lower().strip()
        intent = self._detect_intent(msg_lower)

        # 1. Intenções simples (saudação, despedida, ajuda)
        if intent["type"] in INTENT_PATTERNS:
            if intent["type"] == "create_qa_doc":
                return self._generate_qa_sprint_doc(message)
                
            if intent["type"] == "model_version":
                if hasattr(self, "engine") and self.engine:
                    return self.engine.format_self_info()
                
                config = active_model_info.get("config", {}) if active_model_info else {}
                v = config.get("version", active_model_info.get("version", "Desconhecida")) if active_model_info else "Desconhecida"
                n = config.get("botName", active_model_info.get("name", "Richie AI Base")) if active_model_info else "Richie AI Base"
                c = active_model_info.get("creator_name", "@S.V.S - Try Technology") if active_model_info else "@S.V.S - Try Technology"
                
                return (f"🤖 **Identidade e Versionamento**\n\n"
                        f"**Modelo Ativo:** `{n}`\n"
                        f"**Criador:** `{c}`\n"
                        f"**Versão Atual:** `{v}`\n\n"
                        f"> Eu opero offline através da infraestrutura BotForge Studio.")

            if intent["type"] == "app_version":
                return INTENT_PATTERNS["app_version"]["response"]

            if intent["type"] == "about" and active_model_info:
                v = active_model_info.get("name", "Richie AI")
                tags = active_model_info.get("tags", [])
                c = active_model_info.get("creator_name") or (tags[0] if tags else "@S.V.S - Try Technology")
                limit = "Ilimitado" if active_model_info.get("no_token_limit", True) else "Limitado (Tokens Padrão)"
                desc = active_model_info.get("description", "Assistente Padrão")
                config = active_model_info.get("config", {})
                mod_ver = config.get("version", active_model_info.get("version", "?"))
                return (
                    f"Eu sou **{v}** 🤖, sua IA assistente configurada dinamicamente!\n\n"
                    f"Fui moldada e integrada ao FlowEngine pela **{c}**.\n"
                    f"Atualmente funciono em modo **Offline** (Sem provedor cloud).\n\n"
                    f"Versão do Modelo: `{mod_ver}`\n"
                    f"Tokens Restantes: `{limit} (offline)`\n"
                    f"Engine de Resposta: `OfflineEngine (Rev 1.2.9-Gemini)`"
                )
            return INTENT_PATTERNS[intent["type"]]["response"]

        # 2. Se tem código do editor, analisar
        if editor_code and intent.get("wants_analysis"):
            return self._analyze_code_offline(editor_code, file_extension, message)

        # 3. Se pede explicação de erro
        if intent["type"] == "error_help":
            return self._explain_error_offline(message, intent.get("language"))

        # 4. Se pede template ou exemplo de código
        if intent["type"] == "code_request":
            return self._generate_code_example(message, intent.get("language"), intent.get("wants_execution", False))

        # 5. Se pede informação sobre linguagem
        if intent["type"] == "language_info":
            return self._get_language_info(intent.get("language"))

        # 6. Se pede plano de implementação
        if intent["type"] == "create_plan":
            return self._generate_plan_offline(message)

        # 7. Se pede para executar algo
        if intent["type"] == "run_script":
            return self._handle_execution_request(message)

        # 8. Se pede para criar arquivo
        if intent["type"] == "create_file":
            return self._handle_create_file_request(message, intent.get("language"))

        # 9. Resposta geral inteligente
        return self._general_response(message, editor_code)

    def _detect_intent(self, msg_lower: str) -> Dict[str, Any]:
        """Detecta intenção da mensagem offline"""
        intent = {
            "type": "general",
            "language": None,
            "wants_analysis": False,
            "requires_permission": False,
        }

        # Check intenções simples
        for itype, idata in INTENT_PATTERNS.items():
            if any(kw in msg_lower for kw in idata["keywords"]):
                intent["type"] = itype
                break

        # Override forte: Documento QA
        if any(kw in msg_lower for kw in INTENT_PATTERNS["create_qa_doc"]["keywords"]):
            intent["type"] = "create_qa_doc"
            
        # Override forte: Versão do programa vs modelo
        if any(kw in msg_lower for kw in INTENT_PATTERNS["app_version"]["keywords"]):
            intent["type"] = "app_version"
        elif any(kw in msg_lower for kw in INTENT_PATTERNS["model_version"]["keywords"]):
            intent["type"] = "model_version"
        elif any(kw in msg_lower for kw in ["quem é voce", "quem e voce", "quem te criou", "quem desenvolveu"]):
            intent["type"] = "about"

        # Check se é pós-intenção simples (não retornar cedo se for greeting+algo mais)
        if intent["type"] in ("greeting", "farewell", "help", "about", "create_qa_doc", "app_version", "model_version"):
            # Se for intenções diretas, verifica se não é muito longa (apenas saudação/identidade pura)
            if len(msg_lower.split()) <= 6:
                return intent
            # Se é longa, provavelmente tem pergunta ou solicitação junto — continuamos detecção e permitimos override

        # Detecção de linguagem
        for lang_key, lang_data in LANGUAGE_KNOWLEDGE.items():
            lang_names = [lang_key, lang_data["name"].lower(), lang_data["extension"]]
            if any(ln in msg_lower for ln in lang_names):
                intent["language"] = lang_key
                break

        # Análise de código
        code_keywords = ["analise", "analisa", "review", "revise", "explique", "explica",
                         "debug", "bug", "erro", "error", "corrija", "fix", "melhore",
                         "otimize", "refatore", "o que faz", "como funciona"]
        if any(kw in msg_lower for kw in code_keywords):
            intent["wants_analysis"] = True
            if intent["type"] == "general":
                intent["type"] = "code_analysis"

        # Erro específico
        error_keywords = ["erro", "error", "traceback", "exception", "crash",
                          "não funciona", "nao funciona", "falha", "falhou", "bug"]
        if any(kw in msg_lower for kw in error_keywords):
            intent["type"] = "error_help"

        # Pede exemplo/template
        code_req_keywords = ["exemplo de c", "example code", "template de c", "modelo de c", "como fazer",
                             "como criar", "crie um", "criar um", "gere um", "gerar um", "escreva", "write",
                             "code", "codigo", "código", "snippet", "script", "fazer um"]
        if any(kw in msg_lower for kw in code_req_keywords):
            # Garantir que nao confunda com "seu modelo"
            if "seu modelo" not in msg_lower and "teu modelo" not in msg_lower:
                intent["type"] = "code_request"

        # Se tiver "seu modelo" ou "qual o modelo", forcar model_version
        if "seu modelo" in msg_lower or "qual o modelo" in msg_lower or "teu modelo" in msg_lower:
            intent["type"] = "model_version"

        # Info sobre linguagem
        lang_info_kw = ["o que é", "o que e", "what is", "como instalar", "como usar",
                        "tutorial", "dicas", "tips", "boas praticas", "best practices"]
        if any(kw in msg_lower for kw in lang_info_kw) and intent["language"]:
            intent["type"] = "language_info"

        # Plano/Sprint
        plan_keywords = ["plano", "plan", "planeje", "sprint", "roadmap",
                         "passo a passo", "implementação", "implementar"]
        if any(kw in msg_lower for kw in plan_keywords):
            intent["type"] = "create_plan"

        # Execução
        exec_keywords = ["execute", "rode", "roda", "run", "executa", "teste",
                         "pip install", "npm install", "instale", "instala"]
        if any(kw in msg_lower for kw in exec_keywords):
            if intent["type"] == "code_request":
                intent["wants_execution"] = True
            else:
                intent["type"] = "run_script"
                intent["requires_permission"] = True

        # Criação de arquivo
        create_keywords = ["crie um arquivo", "cria um arquivo", "create file",
                           "novo arquivo", "new file", "gere um arquivo"]
        if any(kw in msg_lower for kw in create_keywords):
            intent["type"] = "create_file"
            intent["requires_permission"] = True

        return intent
    def _generate_qa_sprint_doc(self, message: str) -> str:
        """Gera o documento de Sprint nível QA com base no template solicitado."""
        
        return (
            "## 📝 Documento de Sprint (Nível QA)\n\n"
            "Aqui está o modelo de documentação pronto para uso!\n\n"
            "```markdown\n"
            "# [Nome da Tarefa/Sprint]\n\n"
            "## 1. Contexto do Problema\n"
            "> Qual a situação atual, impacto gerado e objetivo da mudança.\n\n"
            "## 2. Escopo de Arquivos Afetados\n"
            "| # | Arquivo | Ação (Novo/Mod/Del) | Requer Backup? |\n"
            "|---|---|---|---|\n"
            "| 1 | | | |\n\n"
            "## 3. Etapas de Implementação\n"
            "1. **Etapa 1:** ...\n"
            "2. **Etapa 2:** ...\n\n"
            "## 4. Design Visual / UI\n"
            "> Wireframes ASCII ou especificações CSS (Cores, fontes, bordas).\n\n"
            "## 5. Regras Obrigatórias\n"
            "🚨 **CRÍTICO:** Regras que não podem ser violadas na implementação.\n\n"
            "## 6. Versionamento\n"
            "| Arquivo | Campo | Valor |\n"
            "|---|---|---|\n"
            "| | | |\n\n"
            "## 7. CHANGELOG\n"
            "Documentação do que foi feito para ser enviado ao histórico.\n\n"
            "## 8. Estratégia de Backup\n"
            "> Ex: Criar cópias com sufixo `.bak-rev[N]` antes de aplicar.\n\n"
            "## 9. Arquivos Impactados\n"
            "Resumo dos módulos dependentes.\n\n"
            "## 10. Plano de Verificação QA (Test Cases)\n"
            "- **TC-01:** ...\n"
            "- **TC-02:** ...\n\n"
            "## 11. Verificação Automatizada/Manual\n"
            "Testes a serem rodados e verificações manuais de GUI.\n\n"
            "## 12. Open Questions\n"
            "Dúvidas pendentes antes de iniciar a execução.\n"
            "```\n"
        )


    def _analyze_code_offline(self, code: str, extension: str = None,
                              question: str = "") -> str:
        """Analisa código offline — detecta problemas comuns"""
        issues = []
        suggestions = []
        lang = self._detect_language_from_code(code, extension)
        lang_name = LANGUAGE_KNOWLEDGE.get(lang, {}).get("name", "Desconhecida")

        response = f"## 📝 Análise de Código ({lang_name})\n\n"

        lines = code.split('\n')
        total_lines = len(lines)

        # Métricas básicas
        response += f"**📊 Métricas:** {total_lines} linhas"
        empty_lines = sum(1 for l in lines if not l.strip())
        response += f" | {empty_lines} vazias"
        comment_chars = {'python': '#', 'javascript': '//', 'typescript': '//',
                         'lua': '--', 'csharp': '//', 'java': '//', 'go': '//',
                         'rust': '//', 'php': '//', 'ruby': '#'}
        cc = comment_chars.get(lang, '#')
        comment_lines = sum(1 for l in lines if l.strip().startswith(cc))
        response += f" | {comment_lines} comentários\n\n"

        # Análise Python específica
        if lang == "python":
            # Imports não utilizados (heurística simples)
            imports = [l.strip() for l in lines if l.strip().startswith(('import ', 'from '))]
            if imports:
                response += f"**📦 Imports:** {len(imports)} módulo(s) importado(s)\n"

            # Funções muito longas
            func_lines = []
            current_func = None
            for i, l in enumerate(lines):
                if l.strip().startswith('def '):
                    if current_func and (i - current_func[1]) > 50:
                        issues.append(f"⚠️ Função `{current_func[0]}` tem {i - current_func[1]} linhas — considere dividir")
                    func_name = l.strip().split('(')[0].replace('def ', '')
                    current_func = (func_name, i)

            # Variáveis com nomes ruins
            single_var_pattern = re.compile(r'\b([a-z])\s*=\s*')
            for i, l in enumerate(lines):
                if single_var_pattern.search(l) and not l.strip().startswith('#'):
                    var = single_var_pattern.search(l).group(1)
                    if var not in ('i', 'j', 'k', 'x', 'y', 'f', '_'):
                        suggestions.append(f"💡 Linha {i+1}: variável `{var}` — nomes descritivos são mais legíveis")

            # Try/Except genérico
            for i, l in enumerate(lines):
                if 'except:' in l and 'except Exception' not in l:
                    issues.append(f"⚠️ Linha {i+1}: `except:` genérico — especifique o tipo de exceção")

            # Print em vez de logging
            print_count = sum(1 for l in lines if 'print(' in l)
            if print_count > 5:
                suggestions.append(f"💡 {print_count} chamadas `print()` — considere usar `logging` em produção")

        # Análise genérica
        for i, l in enumerate(lines):
            # Linhas muito longas
            if len(l) > 120:
                issues.append(f"⚠️ Linha {i+1}: {len(l)} caracteres — limite recomendado é 120")

            # TODO/FIXME
            if 'TODO' in l or 'FIXME' in l or 'HACK' in l:
                suggestions.append(f"📌 Linha {i+1}: encontrado marcador `{l.strip()[:60]}`")

            # Espaços em branco no final
            if l != l.rstrip() and l.strip():
                issues.append(f"🔸 Linha {i+1}: espaço em branco no final da linha")

        # Montar resultado
        if issues:
            response += "### ⚠️ Problemas Encontrados\n"
            for issue in issues[:10]:  # Limitar a 10
                response += f"- {issue}\n"
            response += "\n"

        if suggestions:
            response += "### 💡 Sugestões de Melhoria\n"
            for sug in suggestions[:8]:
                response += f"- {sug}\n"
            response += "\n"

        if not issues and not suggestions:
            response += "### ✅ Código Limpo!\nNenhum problema óbvio detectado. O código parece estar bem estruturado.\n\n"

        # Dicas da linguagem
        tips = LANGUAGE_KNOWLEDGE.get(lang, {}).get("tips", [])
        if tips:
            response += "### 📚 Dicas para " + lang_name + "\n"
            for tip in tips[:3]:
                response += f"- {tip}\n"

        return response

    def _explain_error_offline(self, message: str, language: str = None) -> str:
        """Explica erros comuns offline"""
        if not language:
            # Tenta detectar pela mensagem
            for lang_key, lang_data in LANGUAGE_KNOWLEDGE.items():
                for err_name in lang_data.get("common_errors", {}):
                    if err_name.lower() in message.lower():
                        language = lang_key
                        break
                if language:
                    break

        if not language:
            language = "python"  # Default

        lang_data = LANGUAGE_KNOWLEDGE.get(language, {})
        errors = lang_data.get("common_errors", {})

        response = f"## 🐛 Análise de Erro ({lang_data.get('name', language)})\n\n"

        found_error = False
        for err_name, err_fix in errors.items():
            if err_name.lower() in message.lower():
                response += f"### ❌ `{err_name}`\n"
                response += f"**Causa:** {err_fix}\n\n"
                found_error = True

        if not found_error:
            response += "Não consegui identificar o erro específico pela mensagem.\n\n"
            response += "**Dicas gerais para debug:**\n"
            response += "1. Leia a mensagem de erro completa — geralmente indica a linha exata\n"
            response += "2. Verifique o Traceback de baixo para cima\n"
            response += "3. Cole o erro completo aqui e eu analiso mais a fundo\n"
            response += "4. Use `print()` para inspecionar variáveis suspeitas\n"

        if errors:
            response += "\n### 📖 Erros Comuns em " + lang_data.get("name", language) + "\n"
            for name, fix in list(errors.items())[:5]:
                response += f"- **{name}**: {fix}\n"

        return response

    def _generate_code_example(self, message: str, language: str = None, wants_execution: bool = False) -> str:
        """Gera exemplo de código offline"""
        if not language:
            language = "python"

        lang_data = LANGUAGE_KNOWLEDGE.get(language, {})
        lang_name = lang_data.get('name', language.capitalize())
        
        response = f"### 💻 Snippet: {lang_name}\n---\n"

        def _finalize_response(res: str) -> str:
            if wants_execution:
                res += "\n\n---\n"
                res += "### 🚀 Execução Solicitada\n"
                res += "Notei que você pediu para rodar este código. Para confirmar a execução, clique em um dos botões abaixo ou digite **'sim, execute'**.\n"
                res += "<!--ACTIONS: [\"✅ Aprovado (Apenas Agora)\", \"🔄 Sempre Liberar (Sessão)\", \"❌ Negado\"]-->"
            return res

        msg_lower = message.lower()
        import re
        
        # Verificar se pede input/pergunta (ex: pergunte "Qual o seu nome?")
        if "pergunte " in msg_lower or "pergunta " in msg_lower or "perguntar " in msg_lower or "input" in msg_lower:
            q_match = re.search(r'(?:pergunte|pergunta|perguntar)\s+(?:que\s+|onde\s+|)\s*["\']([^"\']+)["\']', message, re.IGNORECASE)
            if not q_match:
                q_match = re.search(r'["\']([^"\']+\?)["\']', message) # tenta achar algo com interrogacao nas aspas
            
            custom_question = q_match.group(1) if q_match else "Qual a sua resposta?"
            
            response += f"**Padrão Solicitado:** `Script Interativo (Input)`\n\n"
            if language == "lua":
                code = f'-- Pergunta ao usuário\nprint("{custom_question}")\n\n-- Solicita resposta e armazena na variável\nlocal resposta = io.read()\nprint("\\nVocê respondeu: " .. (resposta or ""))'
            elif language == "python":
                code = f'# Pergunta ao usuário\nprint("{custom_question}")\nresposta = input()\nprint(f"\\nVocê respondeu: {{resposta}}")'
            elif language == "javascript":
                code = f'const readline = require("readline").createInterface({{\n  input: process.stdin,\n  output: process.stdout\n}});\n\nconsole.log("{custom_question}");\nreadline.question("", resposta => {{\n  console.log(`\\nVocê respondeu: ${{resposta}}`);\n  readline.close();\n}});'
            else:
                code = f'// Solicitação de input para "{custom_question}"\n// (Padrão interativo offline ainda não mapeado para {lang_name})'
                
            response += f"```{language}\n{code}\n```\n"
            return _finalize_response(response)
        patterns = lang_data.get("patterns", {})
        msg_lower = message.lower()

        for pattern_name, pattern_code in patterns.items():
            if pattern_name.replace('_', ' ') in msg_lower or pattern_name in msg_lower:
                response += f"**Padrão Solicitado:** `{pattern_name.replace('_', ' ').title()}`\n\n"
                response += f"```{language}\n{pattern_code}\n```\n"
                return _finalize_response(response)

        # Verificar se pede template
        for tpl_key, tpl_data in CODE_TEMPLATES.items():
            keywords = tpl_key.replace('_', ' ').split()
            if any(kw in msg_lower for kw in keywords):
                response += f"**Padrão Solicitado:** `{tpl_data['title']}`\n\n"
                response += f"```{tpl_data['language']}\n{tpl_data['code']}\n```\n"
                return _finalize_response(response)

        # Hello World padrão
        response += f"**Padrão Solicitado:** `Hello World Básico`\n\n"
        response += f"```{language}\n{lang_data.get('hello_world', '// Hello World')}\n```\n\n"

        # Mostrar patterns disponíveis
        if patterns:
            response += "### 📦 Templates Disponíveis\n"
            response += "Peça por qualquer um destes:\n"
            for pname in patterns:
                response += f"- `{pname.replace('_', ' ')}`\n"

        return _finalize_response(response)

    def _get_language_info(self, language: str) -> str:
        """Retorna informações sobre uma linguagem"""
        lang_data = LANGUAGE_KNOWLEDGE.get(language)
        if not lang_data:
            return f"Não tenho informações detalhadas sobre `{language}` na minha base local."

        response = f"## 📚 {lang_data['name']}\n\n"
        response += f"**Extensão:** `{lang_data['extension']}`\n"
        response += f"**Runner:** `{lang_data['runner']}`\n\n"

        response += "### 🚀 Hello World\n"
        response += f"```{language}\n{lang_data['hello_world']}\n```\n\n"

        if lang_data.get("tips"):
            response += "### 💡 Dicas\n"
            for tip in lang_data["tips"]:
                response += f"- {tip}\n"
            response += "\n"

        if lang_data.get("common_errors"):
            response += "### ⚠️ Erros Comuns\n"
            for name, fix in lang_data["common_errors"].items():
                response += f"- **{name}**: {fix}\n"

        return response

    def _generate_plan_offline(self, message: str) -> str:
        """Gera um plano de implementação offline"""
        response = "## 📋 Plano de Implementação\n\n"
        response += "*Gerado pela Richie (modo offline)*\n\n"
        response += "Com base na sua solicitação, aqui está um plano sugerido:\n\n"

        response += "### Fase 1: Análise e Preparação\n"
        response += "- [ ] Analisar requisitos do projeto\n"
        response += "- [ ] Definir arquitetura e tecnologias\n"
        response += "- [ ] Criar estrutura de diretórios\n"
        response += "- [ ] Configurar dependências\n\n"

        response += "### Fase 2: Desenvolvimento Core\n"
        response += "- [ ] Implementar funcionalidades principais\n"
        response += "- [ ] Criar testes unitários\n"
        response += "- [ ] Implementar tratamento de erros\n\n"

        response += "### Fase 3: UI/UX\n"
        response += "- [ ] Desenvolver interface do usuário\n"
        response += "- [ ] Implementar responsividade\n"
        response += "- [ ] Adicionar feedback visual\n\n"

        response += "### Fase 4: Testes e Deploy\n"
        response += "- [ ] Testes de integração\n"
        response += "- [ ] Revisão de código\n"
        response += "- [ ] Build de produção\n"
        response += "- [ ] Deploy\n\n"

        response += "---\n"
        response += "💬 *Forneça mais detalhes sobre o projeto para um plano mais específico!*\n"
        response += "💎 *Conecte um provider (OpenAI) nas Configurações para planos mais detalhados e personalizados.*"

        return response

    def _handle_execution_request(self, message: str) -> str:
        """Lida com pedidos de execução — sempre pede permissão"""
        msg_lower = message.lower().strip()
        
        if msg_lower == "sim, execute":
            return "## 🚀 Execução Iniciada\n\nEstou solicitando ao terminal que inicie a compilação/execução do seu arquivo atual! Acompanhe o output no terminal abaixo."

        response = "## 🔐 Solicitação de Execução\n\n"
        response += "Detectei que você deseja executar algo na sua máquina.\n\n"
        response += "**Por segurança, preciso da sua permissão antes de prosseguir.**\n\n"

        response += "**Comando detectado:** `Executar Script do Lado do Cliente`\n\n"
        response += "Deseja que eu acione o terminal de execução?\n"
        response += "Responda **'sim, execute'** ou clique em um dos botões para confirmar.\n"
        response += "<!--ACTIONS: [\"✅ Aprovado (Apenas Agora)\", \"🔄 Sempre Liberar (Sessão)\", \"❌ Negado\"]-->\n"

        return response

    def _handle_create_file_request(self, message: str, language: str = None) -> str:
        """Lida com pedidos de criação de arquivo"""
        response = "## 📄 Criação de Arquivo\n\n"
        response += "Detectei que você deseja criar um novo arquivo.\n\n"

        if language:
            lang_data = LANGUAGE_KNOWLEDGE.get(language, {})
            ext = lang_data.get("extension", ".txt")
            response += f"**Linguagem:** {lang_data.get('name', language)}\n"
            response += f"**Extensão:** `{ext}`\n\n"
            response += "Posso criar o arquivo com um template inicial. "
            response += "Qual nome deseja para o arquivo?\n"
        else:
            response += "Qual linguagem/tipo e nome de arquivo deseja criar?\n"

        response += "\n⚠️ *A criação de arquivo requer sua aprovação.*"
        return response

    def _general_response(self, message: str, editor_code: str = None) -> str:
        """Resposta geral quando nenhuma intenção específica é detectada"""
        response = ""

        # Se tem código no editor, oferecer análise
        if editor_code:
            response += "Vejo que você tem código aberto no editor. "
            response += "Posso analisar ele para você — basta pedir!\n\n"

        # Resposta inteligente baseada em palavras-chave
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["como", "what", "why", "por que", "porque"]):
            response += "Essa é uma boa pergunta! 🤔\n\n"
            response += "No **modo offline**, posso ajudar melhor com:\n"
            response += "- Análise de código que você colar ou abrir no editor\n"
            response += "- Exemplos e templates de código\n"
            response += "- Dicas e boas práticas de programação\n"
            response += "- Explicação de erros comuns\n\n"
            response += "💎 Para respostas mais completas e personalizadas, "
            response += "conecte um **provider de IA** (OpenAI, DeepSeek) nas Configurações.\n"
        else:
            response += "Recebi sua mensagem! 👍\n\n"
            response += "Posso ajudar com:\n"
            response += "• **\"analise este código\"** — Analiso o código aberto no editor\n"
            response += "• **\"exemplo de [linguagem]\"** — Mostro exemplos de código\n"
            response += "• **\"erro [tipo]\"** — Explico e sugiro correções\n"
            response += '• **"plano para [projeto]"** — Crio um plano de implementação\n'
            response += '• **"dicas de [linguagem]"** — Dicas e boas práticas\n'

        return response

    def _detect_language_from_code(self, code: str, extension: str = None) -> str:
        """Detecta linguagem pelo código ou extensão"""
        if extension:
            ext = extension.lower().lstrip('.')
            ext_map = {v["extension"].lstrip('.'): k for k, v in LANGUAGE_KNOWLEDGE.items()}
            if ext in ext_map:
                return ext_map[ext]

        # Heurísticas por código
        if 'def ' in code and ':' in code:
            return "python"
        if 'function ' in code or 'const ' in code or 'let ' in code:
            return "javascript"
        if 'interface ' in code and ': ' in code:
            return "typescript"
        if 'local ' in code and 'function' in code:
            return "lua"
        if 'using System' in code or 'namespace ' in code:
            return "csharp"
        if 'public class' in code and 'void' in code:
            return "java"
        if 'func ' in code and 'fmt.' in code:
            return "go"
        if 'fn ' in code and 'let mut' in code:
            return "rust"
        if '<?php' in code:
            return "php"
        if 'extends Node' in code or 'func _ready' in code:
            return "gdscript"
        if '<!DOCTYPE' in code.upper() or '<html' in code.lower():
            return "html"

        return "python"  # Default


# ============================================================================
# RICHIE AI — Classe Principal
# ============================================================================

class RichieAI:
    """
    Engine principal da IA Richie.
    Funciona primariamente OFFLINE com motor local de respostas.
    Opcionalmente, pode usar providers externos (OpenAI, DeepSeek, Claude)
    para respostas mais avançadas quando configurados.
    """

    def __init__(self):
        # Diretório de persistência
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent.parent.parent

        self.data_dir = self.base_dir / "config" / "richie"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Engine offline (motor principal)
        self.offline_engine = OfflineEngine()

        # FlowEngine (complemento — lê config do JSON do modelo)
        # Instanciado via load_flow_from_model() quando um modelo é ativado
        self._flow_engine = None
        self._model_info = {}  # Dados do modelo ativo para self-awareness

        # Modo de operação: "offline" (padrão) ou "online"
        self.mode = "offline"

        # Estado
        self.sessions: Dict[str, ChatSession] = {}
        self.active_session_id: Optional[str] = None
        self.action_plans: Dict[str, ActionPlan] = {}
        self.pending_permissions: List[PermissionRequest] = []
        self.learned_context: Dict[str, Any] = {}

        # Carregar dados persistidos
        self._load_state()

        # Se não existe nenhuma sessão, criar uma
        if not self.sessions:
            self.create_new_session()

    # === Sessões de Chat ===

    def create_new_session(self, title: str = "Nova Conversa") -> ChatSession:
        """Cria nova sessão de chat"""
        session = ChatSession(
            id=str(uuid.uuid4())[:8],
            title=title
        )
        self.sessions[session.id] = session
        self.active_session_id = session.id
        self._save_state()
        return session

    def get_active_session(self) -> Optional[ChatSession]:
        """Retorna sessão ativa"""
        if self.active_session_id:
            return self.sessions.get(self.active_session_id)
        return None

    def switch_session(self, session_id: str) -> bool:
        """Troca para outra sessão"""
        if session_id in self.sessions:
            self.active_session_id = session_id
            self._save_state()
            return True
        return False

    def list_sessions(self) -> List[ChatSession]:
        """Lista todas as sessões ordenadas por data"""
        return sorted(
            self.sessions.values(),
            key=lambda s: s.updated_at,
            reverse=True
        )

    def delete_session(self, session_id: str) -> bool:
        """Deleta uma sessão"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.active_session_id == session_id:
                if self.sessions:
                    self.active_session_id = list(self.sessions.keys())[0]
                else:
                    self.create_new_session()
            self._save_state()
            return True
        return False

    # === Chat Engine ===

    def add_user_message(self, content: str, editor_context: str = None) -> Dict:
        """Adiciona mensagem do usuário à sessão ativa"""
        session = self.get_active_session()
        if not session:
            session = self.create_new_session()

        message = {
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "editor_context": editor_context
        }
        session.messages.append(message)
        session.updated_at = datetime.now().isoformat()

        # Auto-título baseado na primeira mensagem do usuário
        user_msgs = [m for m in session.messages if m["role"] == "user"]
        if len(user_msgs) == 1:
            session.title = content[:50] + ("..." if len(content) > 50 else "")

        self._save_state()
        return message

    def add_assistant_message(self, content: str, metadata: Dict = None) -> Dict:
        """Adiciona resposta da Richie à sessão ativa"""
        session = self.get_active_session()
        if not session:
            return {}

        message = {
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        session.messages.append(message)
        session.updated_at = datetime.now().isoformat()
        self._save_state()
        return message

    # =========================================================
    # === FLOW ENGINE — COMPLEMENTO AO MOTOR OFFLINE ===
    # =========================================================

    def load_flow_from_model(self, model):
        """
        Carrega FlowEngine a partir de um CustomAIModel.
        Chamado quando o usuário troca o modelo ativo no combo box.
        
        O FlowEngine complementa o OfflineEngine:
        - Lê keywords de intenção do JSON (em vez de hardcoded)
        - Fornece self-awareness (versão, criador) via dados do modelo
        - Lê temperature/max_tokens do card api_connector
        """
        try:
            from src.core.json_flow_engine import FlowEngine
            nodes = getattr(model, '_flow_nodes', [])
            conns = getattr(model, '_flow_conns', [])
            
            # Extrair model_data do modelo
            model_data = {}
            for attr in ('name', 'description', 'base_provider', 'base_model',
                         'system_prompt', 'temperature', 'max_tokens',
                         'created_at', 'updated_at', 'creator_name',
                         'creation_date', 'version', 'is_active', 'tags',
                         'no_token_limit'):
                val = getattr(model, attr, None)
                if val is not None:
                    model_data[attr] = val
            
            # Injetar bloco config do BotForge JSON (versão, criador, tom, etc.)
            cfg = getattr(model, '_config', {})
            if cfg:
                model_data['config'] = cfg
                # Garantir que version no model_data reflita a do config
                if cfg.get('version'):
                    model_data['version'] = cfg['version']
            
            if nodes:
                self._flow_engine = FlowEngine(nodes, conns, model_data)
                self._model_info = model_data
                print(f"[Richie] FlowEngine carregado: {self._flow_engine}")
            else:
                self._flow_engine = None
                self._model_info = model_data
        except Exception as e:
            print(f"[Richie] Erro ao carregar FlowEngine: {e}")
            self._flow_engine = None

    def detect_intent_from_flow(self, user_input: str):
        """
        Tenta detectar intenção via FlowEngine (keywords do JSON).
        Retorna (intent_name, score) ou None se FlowEngine não disponível.
        """
        if self._flow_engine:
            intent, score = self._flow_engine.detect_intent(user_input)
            if intent != "general" and score > 0.1:
                return (intent, score)
        return None

    def get_self_info(self) -> str:
        """
        Retorna informações do próprio modelo ativo.
        Usado quando o usuário pergunta 'qual sua versão', 'quem te criou', etc.
        Dados vêm do JSON do modelo via FlowEngine.
        """
        if self._flow_engine:
            return self._flow_engine.format_self_info()
        
        # Fallback se FlowEngine não disponível
        info = self._model_info or {}
        return (
            "## 🤖 Meu Perfil\n\n"
            f"**Nome:** Richie — IA Assistente Base\n"
            f"**Criador:** {info.get('creator_name', '@S.V.S - Try Technology')}\n"
            f"**Provider:** {info.get('base_provider', 'offline')}\n"
            f"**Versão:** v0.4.11-rev1.2.5-280426\n\n"
            "Estou aqui para te ajudar! 🚀"
        )

    def get_flow_summary(self) -> dict:
        """Retorna resumo do fluxo ativo para exibição no BotForge."""
        if self._flow_engine:
            return self._flow_engine.get_flow_summary()
        return {"total_nodes": 0, "total_connections": 0, "has_api_connector": False, "has_nlp": False}

    def generate_response(self, message: str, editor_code: str = None,
                          file_extension: str = None) -> str:
        """
        Gera resposta da Richie.
        1. Consulta FlowEngine para intenções especiais (self_info)
        2. MODO OFFLINE (padrão): usa motor local
        3. MODO ONLINE (opcional): envia para provider externo
        """
        msg_lower = message.lower().strip()
        
        # 1. Verificar self_info via FlowEngine (se disponível)
        flow_intent = self.detect_intent_from_flow(msg_lower)
        if flow_intent:
            intent_name, score = flow_intent
            if intent_name == "self_info":
                return self.get_self_info()
        
        # 2. O motor offline é sempre o padrão
        return self.offline_engine.generate_response(message, editor_code, file_extension, active_model_info=self._model_info)

    def build_context_for_api(self, max_messages: int = 20) -> List[Dict]:
        """
        Constrói contexto de mensagens para enviar à API EXTERNA (modo online).
        Usado apenas quando o usuário opta por usar um provider (OpenAI, etc.)
        """
        session = self.get_active_session()
        if not session:
            return []

        messages = [{"role": "system", "content": RICHIE_SYSTEM_PROMPT}]

        # Contexto aprendido
        if self.learned_context:
            learned = "\n".join([f"- {k}: {v}" for k, v in self.learned_context.items()])
            messages.append({
                "role": "system",
                "content": f"Contexto aprendido sobre o usuário:\n{learned}"
            })

        # Últimas N mensagens
        recent = session.messages[-max_messages:]
        for msg in recent:
            api_msg = {"role": msg["role"], "content": msg["content"]}

            if msg.get("editor_context"):
                api_msg["content"] = (
                    f"[Código aberto no editor:]\n```\n{msg['editor_context'][:3000]}\n```\n\n"
                    f"{msg['content']}"
                )
            messages.append(api_msg)

        return messages

    # === Detecção de Intenções (Interface pública) ===

    def detect_intent(self, message: str) -> Dict[str, Any]:
        """Detecta a intenção da mensagem do usuário"""
        return self.offline_engine._detect_intent(message.lower().strip())

    # === Planos de Atuação ===

    def create_action_plan(self, title: str, description: str,
                           steps: List[Dict]) -> ActionPlan:
        """Cria um plano de atuação"""
        plan = ActionPlan(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            steps=steps
        )
        self.action_plans[plan.id] = plan
        self._save_state()
        return plan

    def approve_plan(self, plan_id: str) -> bool:
        """Usuário aprova um plano"""
        plan = self.action_plans.get(plan_id)
        if plan and plan.status == "pending":
            plan.status = "approved"
            plan.approved_at = datetime.now().isoformat()
            self._save_state()
            return True
        return False

    def reject_plan(self, plan_id: str) -> bool:
        """Usuário rejeita um plano"""
        plan = self.action_plans.get(plan_id)
        if plan and plan.status == "pending":
            plan.status = "rejected"
            self._save_state()
            return True
        return False

    # === Sistema de Permissões ===

    def request_permission(self, action: str, target: str,
                           description: str, risk: str = "low") -> PermissionRequest:
        """Cria solicitação de permissão"""
        perm = PermissionRequest(
            id=str(uuid.uuid4())[:8],
            action=action,
            target=target,
            description=description,
            risk_level=risk
        )
        self.pending_permissions.append(perm)
        self._save_state()
        return perm

    def grant_permission(self, perm_id: str) -> bool:
        """Concede permissão"""
        for perm in self.pending_permissions:
            if perm.id == perm_id:
                perm.status = "granted"
                self._save_state()
                return True
        return False

    def deny_permission(self, perm_id: str) -> bool:
        """Nega permissão"""
        for perm in self.pending_permissions:
            if perm.id == perm_id:
                perm.status = "denied"
                self._save_state()
                return True
        return False

    # === Aprendizado Contextual ===

    def learn(self, key: str, value: Any):
        """Richie aprende algo sobre o usuário/projeto"""
        self.learned_context[key] = value
        session = self.get_active_session()
        if session:
            session.learned_items.append(f"{key}: {value}")
        self._save_state()

    def get_learned(self, key: str) -> Any:
        """Recupera algo aprendido"""
        return self.learned_context.get(key)

    # === Modo de Operação ===

    def set_mode(self, mode: str):
        """Define modo: 'offline' ou 'online'"""
        if mode in ("offline", "online"):
            self.mode = mode

    def is_online(self) -> bool:
        """Verifica se está em modo online"""
        return self.mode == "online"

    # === Persistência ===

    def _save_state(self):
        """Salva estado completo no disco"""
        try:
            state = {
                "version": "1.0",
                "mode": self.mode,
                "active_session_id": self.active_session_id,
                "sessions": {sid: asdict(s) for sid, s in self.sessions.items()},
                "action_plans": {pid: asdict(p) for pid, p in self.action_plans.items()},
                "learned_context": self.learned_context,
                "saved_at": datetime.now().isoformat()
            }

            state_file = self.data_dir / "richie_state.json"
            state_file.write_text(
                json.dumps(state, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Erro ao salvar estado Richie: {e}")

    def _load_state(self):
        """Carrega estado do disco"""
        try:
            state_file = self.data_dir / "richie_state.json"
            if not state_file.exists():
                return

            state = json.loads(state_file.read_text(encoding='utf-8-sig'))

            self.mode = state.get("mode", "offline")
            self.active_session_id = state.get("active_session_id")

            for sid, sdata in state.get("sessions", {}).items():
                try:
                    self.sessions[sid] = ChatSession(**sdata)
                except Exception:
                    pass

            for pid, pdata in state.get("action_plans", {}).items():
                try:
                    self.action_plans[pid] = ActionPlan(**pdata)
                except Exception:
                    pass

            self.learned_context = state.get("learned_context", {})

        except Exception as e:
            print(f"Erro ao carregar estado Richie: {e}")

    # === Utilitários ===

    def format_plan_as_markdown(self, plan: ActionPlan) -> str:
        """Formata plano como markdown"""
        md = f"## 📋 Plano: {plan.title}\n\n"
        md += f"{plan.description}\n\n"
        md += "### Steps:\n"

        for i, step in enumerate(plan.steps, 1):
            emoji = "⬜" if plan.status == "pending" else "✅"
            md += f"{i}. {emoji} **{step.get('step', f'Step {i}')}**\n"
            md += f"   {step.get('description', '')}\n"
            if step.get('command'):
                md += f"   ```\n   {step['command']}\n   ```\n"
            if step.get('requires_permission'):
                md += f"   ⚠️ *Requer permissão do usuário*\n"
            md += "\n"

        if plan.status == "pending":
            md += "\n---\n"
            md += "**Deseja aprovar este plano?** Responda 'sim' para aprovar.\n"

        return md

    def format_permission_request(self, perm: PermissionRequest) -> str:
        """Formata solicitação de permissão"""
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}

        md = f"### 🔐 Solicitação de Permissão\n\n"
        md += f"**Ação:** {perm.action}\n"
        md += f"**Alvo:** `{perm.target}`\n"
        md += f"**Descrição:** {perm.description}\n"
        md += f"**Risco:** {risk_emoji.get(perm.risk_level, '⚪')} {perm.risk_level}\n\n"
        md += "Responda **'permitir'** ou **'negar'**."

        return md

    @staticmethod
    def get_system_prompt() -> str:
        """Retorna o system prompt da Richie"""
        return RICHIE_SYSTEM_PROMPT

    @staticmethod
    def get_greeting() -> str:
        """Retorna a saudação da Richie"""
        return RICHIE_GREETING
