"""
Custom AI Manager - Gerenciador de IAs Customizadas
Permite criar, treinar e gerenciar modelos de IA personalizados
"""

import json
import os
import uuid
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class CustomAIModel:
    """Modelo de IA customizado com suporte a treinamento avançado"""
    id: str
    name: str
    description: str
    base_provider: str  # openai, anthropic, deepseek
    base_model: str  # gpt-4, claude-3.5-sonnet, etc
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 4096
    created_at: str = ""
    updated_at: str = ""
    training_data: List[Dict] = field(default_factory=list)
    knowledge_base: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    version: str = "1.0"
    # === Assinatura do Criador ===
    creator_name: str = "Desconhecido"
    creation_date: str = ""
    creation_location: str = "Local"
    creator_signature: str = ""
    # === Novos campos para treinamento avançado ===
    specialization: str = ""  # Área de especialização (code, image, video, 3d, voice, game)
    training_project_ids: List[str] = field(default_factory=list)  # Projetos de treinamento
    training_mode: str = "creative"  # 'creative' (livre) ou 'specialized' (específico)
    no_token_limit: bool = True  # IAs personalizadas NÃO têm limite de retorno
    external_query_limit: int = 4096  # Limite apenas para consultas EXTERNAS
    learned_context: str = ""  # Contexto aprendido dos projetos
    total_training_tokens: int = 0  # Total de tokens usados em treinamento
    
    # === Meta Data Visuais e BotForge ===
    _flow_nodes: List[Dict] = field(default_factory=list)
    _flow_conns: List[Dict] = field(default_factory=list)
    _card_types: List[Dict] = field(default_factory=list)
    _config: Dict = field(default_factory=dict)  # Bloco config do JSON BotForge (version, creator, tone, etc.)
    _flow_groups: List[Dict] = field(default_factory=list)  # Sessões visuais (grupos de nodes)
    chat_integration: bool = True
    
    # === Repositório de Versões ===
    repo_group: str = ""       # Chave de agrupamento (nome normalizado do bot)
    version_label: str = "v1"  # Rótulo da versão (v1, v2, v3...)
    
    # === Logs de Atualização (created_at e creator_name são IMUTÁVEIS) ===
    updated_by: str = ""                    # Quem fez a última atualização
    last_updated_at: str = ""               # Data da última atualização (ISO)
    update_logs: List[Dict] = field(default_factory=list)  # Histórico de atualizações [{date, by, desc}]

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.last_updated_at:
            self.last_updated_at = self.updated_at
        # Auto-preencher repo_group se vazio
        if not self.repo_group:
            self.repo_group = self.name.lower().strip()


# Modelos base disponiveis
AVAILABLE_BASE_MODELS = {
    "openai": [
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context": 128000, "best_for": "Tarefas complexas"},
        {"id": "gpt-4", "name": "GPT-4", "context": 8192, "best_for": "Alta precisao"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context": 16385, "best_for": "Rapido e economico"},
    ],
    "anthropic": [
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "context": 200000, "best_for": "Codigo e analise"},
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context": 200000, "best_for": "Maximo desempenho"},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context": 200000, "best_for": "Rapido e barato"},
    ],
    "deepseek": [
        {"id": "deepseek-coder", "name": "DeepSeek Coder", "context": 32768, "best_for": "Codigo (muito barato)"},
        {"id": "deepseek-chat", "name": "DeepSeek Chat", "context": 32768, "best_for": "Chat geral"},
    ],
}

# Templates de prompts para diferentes tipos de IA
AI_TEMPLATES = {
    "richie": {
        "name": "🤖 Richie — IA Base",
        "system_prompt": (
            "Você é Richie, a IA assistente nativa do AI Code Assistant, desenvolvido por @S.V.S - Try Technology. "
            "Você é amigável, profissional e direto ao ponto. Suas capacidades incluem: análise de código, "
            "multi-linguagem (15+), execução de scripts com permissão, planos de atuação e aprendizado contextual."
        ),
        "temperature": 0.5,
        "tags": ["assistente", "código", "nativa", "base", "offline"]
    },
    "code_assistant": {
        "name": "Assistente de Codigo",
        "system_prompt": """Voce e um assistente especializado em programacao.
Suas responsabilidades:
- Ajudar a escrever codigo limpo e eficiente
- Explicar conceitos de programacao
- Debugar e corrigir erros
- Sugerir melhorias e boas praticas
Sempre forneca codigo bem comentado e explicacoes claras.""",
        "temperature": 0.3,
        "tags": ["codigo", "programacao", "desenvolvimento"]
    },
    "creative_writer": {
        "name": "Escritor Criativo",
        "system_prompt": """Voce e um escritor criativo e versatil.
Suas habilidades:
- Criar historias envolventes
- Escrever textos persuasivos
- Desenvolver dialogos naturais
- Adaptar tom e estilo conforme necessario
Seja criativo mas mantenha coerencia.""",
        "temperature": 0.9,
        "tags": ["escrita", "criativo", "conteudo"]
    },
    "data_analyst": {
        "name": "Analista de Dados",
        "system_prompt": """Voce e um analista de dados experiente.
Suas competencias:
- Analisar conjuntos de dados
- Criar visualizacoes e relatorios
- Identificar padroes e insights
- Sugerir acoes baseadas em dados
Seja preciso e baseie suas analises em evidencias.""",
        "temperature": 0.2,
        "tags": ["dados", "analise", "estatistica"]
    },
    "tutor": {
        "name": "Tutor Educacional",
        "system_prompt": """Voce e um tutor paciente e didatico.
Seu metodo:
- Explicar conceitos de forma simples
- Usar exemplos praticos
- Adaptar ao nivel do aluno
- Encorajar e motivar o aprendizado
Sempre verifique o entendimento antes de avancar.""",
        "temperature": 0.5,
        "tags": ["educacao", "ensino", "aprendizado"]
    },
    "blank": {
        "name": "IA em Branco",
        "system_prompt": "Voce e um assistente util e prestativo.",
        "temperature": 0.7,
        "tags": []
    }
}


class CustomAIManager:
    """Gerenciador de IAs customizadas"""

    @staticmethod
    def _get_app_dir():
        """Retorna o diretório real da aplicação (funciona em dev e em exe compilado)"""
        import sys
        if getattr(sys, 'frozen', False):
            # Compilado com PyInstaller: usar diretório onde o .exe está
            return Path(sys.executable).parent
        else:
            # Modo desenvolvimento: usar raiz do projeto (src/../..)
            return Path(__file__).parent.parent.parent

    def __init__(self, storage_dir: str = None):
        app_dir = self._get_app_dir()
        
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = app_dir / "models" / "custom"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # === Pasta templates-modelos (ao lado do executável/projeto) ===
        self.templates_dir = app_dir / "templates-modelos"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.models: Dict[str, CustomAIModel] = {}
        self._load_models()
        self._preload_richie_model()

    def _load_models(self):
        """Carrega modelos salvos do disco (index.json + templates-modelos/)"""
        # 1. Carregar do index.json clássico
        index_file = self.storage_dir / "index.json"
        if index_file.exists():
            try:
                data = json.loads(index_file.read_text(encoding='utf-8-sig'))
                for model_data in data.get("models", []):
                    try:
                        model = CustomAIModel(**model_data)
                        self.models[model.id] = model
                    except Exception as me:
                        print(f"Erro ao carregar modelo do index: {me}")
            except Exception as e:
                print(f"Erro ao carregar index.json: {e}")
        
        # 2. Escanear pasta templates-modelos/ para JSONs individuais
        if self.templates_dir.exists():
            for json_file in self.templates_dir.glob("*.json"):
                try:
                    raw = json.loads(json_file.read_text(encoding='utf-8-sig'))
                    # Formato interno (gravado por nós): tem "_model_id"
                    if isinstance(raw, dict) and "_model_id" in raw:
                        mid = raw["_model_id"]
                        if mid not in self.models:
                            model_payload = raw.get("_model_data", {})
                            if model_payload:
                                try:
                                    model = CustomAIModel(**model_payload)
                                    self.models[model.id] = model
                                except Exception:
                                    pass
                except Exception as e:
                    print(f"Erro ao ler template {json_file.name}: {e}")

    def _preload_richie_model(self):
        """Carrega automaticamente o Richie AI como modelo base se não existir no index"""
        # Verificar se já existe um modelo Richie
        for model in self.models.values():
            if model.id == "richie-01" or "richie" in model.name.lower():
                return  # Já carregado
        
        # Buscar JSON do Richie na pasta templates-modelos
        richie_json = self.templates_dir / "Richie_AI_Assistant.json"
        if not richie_json.exists():
            return
        
        try:
            raw = json.loads(richie_json.read_text(encoding='utf-8'))
            model = self._import_botforge_json(raw)
            if model:
                self.models[model.id] = model
                self._save_models()
                print(f"[Richie] Modelo Richie AI carregado automaticamente: {model.id}")
        except Exception as e:
            print(f"[Richie] Erro ao carregar Richie_AI_Assistant.json: {e}")

    def reset_richie_to_factory(self):
        """Restaura o estado do Richie para o Padrão de Fábrica"""
        richie_json = self.templates_dir / "Richie_AI_Assistant.json"
        if not richie_json.exists():
            return False, "Arquivo Richie_AI_Assistant.json não encontrado."
            
        try:
            raw = json.loads(richie_json.read_text(encoding='utf-8'))
            model = self._import_botforge_json(raw)
            if model:
                # Remove variações antigas do Richie para evitar colisão
                to_remove = [k for k, v in self.models.items() if "richie" in v.name.lower() or k == "richie-01"]
                for k in to_remove:
                    del self.models[k]
                    
                self.models[model.id] = model
                self._save_models()
                return True, f"Richie resetado para a versão de fábrica: {model.version}"
        except Exception as e:
            return False, f"Erro ao resetar: {e}"
        return False, "Falha desconhecida no reset."

    def _import_botforge_json(self, raw: dict) -> 'Optional[CustomAIModel]':
        """Importa um JSON no formato BotForge (ari) e converte para CustomAIModel.
        Suporta bot como objeto único (padrão) ou array (Opção B)."""
        ari = raw.get("ari", {})
        bot = ari.get("bot", {})
        
        # Handle bot as array (Option B) - take first valid dict element
        if isinstance(bot, list):
            if len(bot) > 0 and isinstance(bot[0], dict):
                bot = bot[0]  # Use first element of array
            else:
                bot = {}  # Empty if array is invalid/empty
        
        # Ensure bot is a valid dict
        if not isinstance(bot, dict):
            bot = {}
        
        flow = ari.get("flow", {})
        config = ari.get("config", {})
        
        if not bot:
            return None
        
        # Usar versão do config se disponível (tem prioridade sobre default)
        model_version = config.get("version", bot.get("version", "1.0"))
        model_creator = config.get("creator", bot.get("creator_name", "Desconhecido"))
        
        model = CustomAIModel(
            id=bot.get("id", str(uuid.uuid4())[:8]),
            name=bot.get("name", "Imported Bot"),
            description=bot.get("desc", ""),
            base_provider=bot.get("base_provider", "offline"),
            base_model=bot.get("base_model", "richie-v1"),
            system_prompt=bot.get("system_prompt", ""),
            temperature=bot.get("temperature", 0.7),
            max_tokens=bot.get("max_tokens", 4096),
            tags=bot.get("tags", []),
            version=model_version,
            creator_name=model_creator,
            creation_date=bot.get("created", config.get("data_criacao", "")),
            _flow_nodes=flow.get("nodes", []),
            _flow_conns=flow.get("connections", []),
            _flow_groups=flow.get("groups", []),
            _card_types=raw.get("cardTypes", ari.get("cardTypes", [])),
            _config=config,
            chat_integration=True
        )
        return model

    def _save_models(self):
        """Salva modelos no disco (index.json + JSONs individuais em templates-modelos/)"""
        # 1. Salvar index.json consolidado
        index_file = self.storage_dir / "index.json"
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "models": [asdict(m) for m in self.models.values()]
        }
        index_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # 2. Gravar cada modelo como JSON individual em templates-modelos/
        for model in self.models.values():
            safe_name = model.name.replace(' ', '_').replace('/', '-').replace('\\', '-')
            tpl_file = self.templates_dir / f"{safe_name}_{model.id}.json"
            tpl_data = {
                "_model_id": model.id,
                "_saved_at": datetime.now().isoformat(),
                "_model_data": asdict(model)
            }
            try:
                tpl_file.write_text(json.dumps(tpl_data, indent=2, ensure_ascii=False), encoding='utf-8')
            except Exception as e:
                print(f"Erro ao gravar template {tpl_file.name}: {e}")

    def save_models(self):
        """Interface pública para flush de memória"""
        self._save_models()

    def import_json_file(self, source_path: str) -> str:
        """Copia um JSON importado para a pasta templates-modelos/ e retorna o caminho destino"""
        src = Path(source_path)
        if not src.exists():
            return ""
        dest = self.templates_dir / src.name
        # Se já existe, renomear com sufixo
        counter = 1
        while dest.exists():
            dest = self.templates_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1
        shutil.copy2(str(src), str(dest))
        return str(dest)

    def create_model(
        self,
        name: str,
        description: str,
        base_provider: str,
        base_model: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tags: List[str] = None,
        creator_name: str = "Desconhecido",
        creation_location: str = "Local"
    ) -> CustomAIModel:
        """Cria novo modelo de IA customizado"""
        model_id = str(uuid.uuid4())[:8]
        now = datetime.now()
        creation_date = now.strftime("%d/%m/%Y %H:%M:%S")
        
        # Gerar uma assinatura única baseada nos dados
        signature = f"AICA-{model_id}-{now.timestamp()}"

        model = CustomAIModel(
            id=model_id,
            name=name,
            description=description,
            base_provider=base_provider,
            base_model=base_model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            tags=tags or [],
            creator_name=creator_name,
            creation_date=creation_date,
            creation_location=creation_location,
            creator_signature=signature
        )

        self.models[model_id] = model
        self._save_models()

        return model

    def create_from_template(
        self,
        template_id: str,
        name: str,
        base_provider: str,
        base_model: str,
        description: str = ""
    ) -> Optional[CustomAIModel]:
        """Cria modelo a partir de um template"""
        template = AI_TEMPLATES.get(template_id)
        if not template:
            return None

        return self.create_model(
            name=name,
            description=description or f"IA baseada no template {template['name']}",
            base_provider=base_provider,
            base_model=base_model,
            system_prompt=template["system_prompt"],
            temperature=template["temperature"],
            tags=template["tags"]
        )

    def get_model(self, model_id: str) -> Optional[CustomAIModel]:
        """Retorna modelo por ID"""
        return self.models.get(model_id)

    def get_model_by_name(self, name: str) -> Optional[CustomAIModel]:
        """Retorna modelo por nome"""
        for model in self.models.values():
            if model.name.lower() == name.lower():
                return model
        return None

    def list_models(self, active_only: bool = True, unique_per_group: bool = False) -> List[CustomAIModel]:
        """Lista todos os modelos. unique_per_group=True retorna apenas a versão ativa de cada grupo."""
        models = list(self.models.values())
        if active_only:
            models = [m for m in models if m.is_active]
        if unique_per_group:
            seen_groups = {}
            for m in models:
                grp = m.repo_group or m.name.lower().strip()
                if grp not in seen_groups:
                    seen_groups[grp] = m
            models = list(seen_groups.values())
        return sorted(models, key=lambda m: m.name)

    def update_model(self, model_id: str, **kwargs) -> bool:
        """Atualiza modelo existente"""
        model = self.models.get(model_id)
        if not model:
            return False

        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)

        model.updated_at = datetime.now().isoformat()
        self._save_models()
        return True

    def delete_model(self, model_id: str) -> bool:
        """Remove modelo da memória e apaga os arquivos do disco."""
        if model_id in self.models:
            # Apagar da memória
            del self.models[model_id]
            # Salvar o index.json sem o modelo
            self._save_models()

            # Deletar arquivo físico se existir na pasta templates-modelos
            if self.templates_dir.exists():
                for json_file in self.templates_dir.glob("*.json"):
                    try:
                        import json
                        with open(json_file, 'r', encoding='utf-8-sig') as f:
                            data = json.load(f)
                        
                        to_delete = False
                        if isinstance(data, dict):
                            if data.get("id") == model_id:
                                to_delete = True
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and item.get("id") == model_id:
                                    to_delete = True
                                    break
                        
                        if to_delete:
                            import os
                            os.remove(json_file)
                            print(f"[AIManager] Arquivo físico deletado: {json_file.name}")
                    except Exception as e:
                        print(f"[AIManager] Erro ao deletar arquivo físico {json_file}: {e}")

            return True
        return False
    def add_training_data(self, model_id: str, user_input: str, expected_output: str) -> bool:
        """Adiciona dados de treinamento ao modelo"""
        model = self.models.get(model_id)
        if not model:
            return False

        model.training_data.append({
            "input": user_input,
            "output": expected_output,
            "added_at": datetime.now().isoformat()
        })

        model.updated_at = datetime.now().isoformat()
        self._save_models()
        return True

    def add_knowledge(self, model_id: str, knowledge: str) -> bool:
        """Adiciona conhecimento a base do modelo"""
        model = self.models.get(model_id)
        if not model:
            return False

        model.knowledge_base.append(knowledge)
        model.updated_at = datetime.now().isoformat()
        self._save_models()
        return True

    def export_model(self, model_id: str, output_path: str = None) -> Optional[str]:
        """Exporta modelo para arquivo"""
        model = self.models.get(model_id)
        if not model:
            return None

        if not output_path:
            output_path = self.storage_dir / f"{model.name.replace(' ', '_')}_{model.id}.aica"

        output_path = Path(output_path)
        data = {
            "format": "aica",
            "version": "1.0",
            "model": asdict(model)
        }

        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        return str(output_path)

    def import_model(self, file_path: str) -> Optional[CustomAIModel]:
        """Importa modelo de arquivo"""
        try:
            data = json.loads(Path(file_path).read_text(encoding='utf-8'))

            if data.get("format") != "aica":
                return None

            model_data = data.get("model", {})
            # Gerar novo ID para evitar conflitos
            model_data["id"] = str(uuid.uuid4())[:8]
            model_data["created_at"] = datetime.now().isoformat()
            model_data["updated_at"] = datetime.now().isoformat()

            model = CustomAIModel(**model_data)
            self.models[model.id] = model
            self._save_models()

            return model
        except Exception as e:
            print(f"Erro ao importar modelo: {e}")
            return None

    # ==========================================
    # === REPOSITÓRIO DE VERSÕES ===
    # ==========================================

    def get_version_group(self, bot_name: str) -> List['CustomAIModel']:
        """Retorna todas as versões de um bot agrupadas por nome normalizado."""
        key = bot_name.lower().strip()
        versions = [m for m in self.models.values() if (m.repo_group or m.name.lower().strip()) == key]
        return sorted(versions, key=lambda m: m.version_label, reverse=True)

    def get_active_version(self, bot_name: str) -> 'Optional[CustomAIModel]':
        """Retorna a versão ATIVA de um determinado bot."""
        versions = self.get_version_group(bot_name)
        for v in versions:
            if v.is_active:
                return v
        return versions[0] if versions else None

    def set_active_version(self, model_id: str) -> bool:
        """Define uma versão como ATIVA e desativa as outras do mesmo grupo."""
        target = self.models.get(model_id)
        if not target:
            return False
        grp = target.repo_group or target.name.lower().strip()
        for m in self.models.values():
            if (m.repo_group or m.name.lower().strip()) == grp:
                m.is_active = (m.id == model_id)
        self._save_models()
        return True

    def save_current_as_version(self, model_id: str, label: str = None) -> 'Optional[CustomAIModel]':
        """Salva snapshot da versão atual como nova versão no repositório."""
        source = self.models.get(model_id)
        if not source:
            return None
        grp = source.repo_group or source.name.lower().strip()
        existing = self.get_version_group(source.name)
        next_num = len(existing) + 1
        new_label = label or f"v{next_num}"
        
        import copy
        clone_data = asdict(source)
        clone_data['id'] = str(uuid.uuid4())[:8]
        clone_data['version_label'] = new_label
        clone_data['repo_group'] = grp
        clone_data['is_active'] = False
        clone_data['created_at'] = datetime.now().isoformat()
        clone_data['updated_at'] = datetime.now().isoformat()
        
        clone = CustomAIModel(**clone_data)
        self.models[clone.id] = clone
        self._save_models()
        return clone

    def import_as_version(self, target_bot_name: str, file_path: str) -> 'Optional[CustomAIModel]':
        """Importa JSON como nova versão de um bot existente."""
        try:
            raw = json.loads(Path(file_path).read_text(encoding='utf-8'))
        except Exception:
            return None
        
        # Tentar extrair como BotForge
        model = None
        if 'ari' in raw and 'bot' in raw.get('ari', {}):
            model = self._import_botforge_json(raw)
        elif raw.get('format') == 'aica':
            model_data = raw.get('model', {})
            model_data['id'] = str(uuid.uuid4())[:8]
            try:
                model = CustomAIModel(**model_data)
            except:
                return None
        else:
            return None
        
        if not model:
            return None
        
        grp = target_bot_name.lower().strip()
        existing = self.get_version_group(target_bot_name)
        next_num = len(existing) + 1
        
        model.repo_group = grp
        model.version_label = f"v{next_num}"
        model.is_active = True  # Nova versão importada fica ativa
        model.updated_at = datetime.now().isoformat()
        
        # Desativar as outras versões
        for m in self.models.values():
            if (m.repo_group or m.name.lower().strip()) == grp:
                if m.id != model.id:
                    m.is_active = False
        
        self.models[model.id] = model
        self._save_models()
        return model

    def get_unique_bots(self) -> List[Dict]:
        """Retorna lista de bots únicos (agrupados) com contagem de versões."""
        groups = {}
        for m in self.models.values():
            grp = m.repo_group or m.name.lower().strip()
            if grp not in groups:
                groups[grp] = {'name': m.name, 'versions': [], 'active_model': None}
            groups[grp]['versions'].append(m)
            if m.is_active:
                groups[grp]['active_model'] = m
        
        result = []
        for grp, data in groups.items():
            active = data['active_model'] or data['versions'][0]
            result.append({
                'name': active.name,
                'repo_group': grp,
                'active_model': active,
                'version_count': len(data['versions'])
            })
        return sorted(result, key=lambda x: x['name'])

    def delete_version(self, model_id: str) -> bool:
        """Remove uma versão específica. Se for a última, remove o bot inteiro."""
        target = self.models.get(model_id)
        if not target:
            return False
        grp = target.repo_group or target.name.lower().strip()
        was_active = target.is_active
        
        del self.models[model_id]
        
        # Se era ativa, ativar a próxima versão disponível
        if was_active:
            remaining = [m for m in self.models.values() if (m.repo_group or m.name.lower().strip()) == grp]
            if remaining:
                remaining[0].is_active = True
        
        self._save_models()
        return True

    @staticmethod
    def get_available_base_models() -> Dict:
        """Retorna modelos base disponiveis"""
        return AVAILABLE_BASE_MODELS

    @staticmethod
    def get_templates() -> Dict:
        """Retorna templates disponiveis"""
        return AI_TEMPLATES
