"""
AI Training Manager - Sistema de Treinamento de IAs Personalizadas
Suporte a treinamento local e com consulta a IAs externas
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
import hashlib


@dataclass
class TrainingProject:
    """Projeto de treinamento para uma IA"""
    id: str
    name: str
    description: str
    path: str  # Caminho da pasta do projeto
    file_extensions: List[str] = field(default_factory=list)  # Extensões a incluir
    exclude_patterns: List[str] = field(default_factory=list)  # Padrões a excluir
    indexed_files: List[str] = field(default_factory=list)  # Arquivos indexados
    total_tokens: int = 0
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class TrainingSession:
    """Sessão de treinamento"""
    id: str
    ai_model_id: str
    project_ids: List[str]
    mode: str  # 'creative' (livre) ou 'specialized' (específico)
    specialization: str = ""  # Ex: 'code', 'image', 'video', '3d', 'voice', 'game'
    external_ai_provider: str = ""  # Provider externo para consulta
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    training_data: List[Dict] = field(default_factory=list)
    created_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# Especializações de IA por área
AI_SPECIALIZATIONS = {
    "code": {
        "name": "Código e Programação",
        "description": "Especializado em desenvolvimento de software",
        "recommended_providers": ["claude-opus", "deepseek-coder", "claude-sonnet"],
        "system_prompt_template": """Você é um especialista em programação e desenvolvimento de software.
Suas habilidades incluem:
- Escrever código limpo, eficiente e bem documentado
- Debug e resolução de problemas
- Refatoração e otimização
- Boas práticas e padrões de projeto
- Múltiplas linguagens de programação

Sempre forneça código funcional com comentários explicativos.""",
        "temperature": 0.3
    },
    "creativity": {
        "name": "Criatividade e Identificação",
        "description": "Análise de conteúdo e criação criativa",
        "recommended_providers": ["claude-opus", "gpt-4-turbo"],
        "system_prompt_template": """Você é um assistente criativo com capacidades avançadas de análise.
Suas habilidades incluem:
- Identificação e análise de conteúdo visual
- Criação de textos criativos e envolventes
- Brainstorming e ideação
- Análise crítica e sugestões

Seja criativo mas mantenha a relevância e qualidade.""",
        "temperature": 0.8
    },
    "image_generation": {
        "name": "Geração de Imagens",
        "description": "Criação de imagens realistas e criativas",
        "recommended_providers": ["gemini-nano-banana", "grok", "dall-e"],
        "system_prompt_template": """Você é especializado em geração e descrição de imagens.
Suas habilidades incluem:
- Criar prompts detalhados para geração de imagens
- Descrever estilos visuais e composições
- Sugerir melhorias para prompts de imagem
- Entender e aplicar técnicas de arte digital""",
        "temperature": 0.7
    },
    "video_generation": {
        "name": "Geração de Vídeos",
        "description": "Criação de vídeos a partir de texto ou imagem",
        "recommended_providers": ["sora", "grok", "runway"],
        "system_prompt_template": """Você é especializado em criação de vídeos.
Suas habilidades incluem:
- Criar roteiros e storyboards
- Descrever cenas e transições
- Sugerir movimentos de câmera
- Criar prompts para geração de vídeo""",
        "temperature": 0.7
    },
    "3d_modeling": {
        "name": "Modelos 3D",
        "description": "Criação de modelos 3D a partir de texto ou imagem",
        "recommended_providers": ["meshy-ai", "triposr", "shap-e"],
        "system_prompt_template": """Você é especializado em modelagem 3D.
Suas habilidades incluem:
- Descrever objetos 3D detalhadamente
- Sugerir geometria e topologia
- Criar prompts para geração de modelos 3D
- Entender técnicas de texturização e rigging""",
        "temperature": 0.5
    },
    "text_to_speech": {
        "name": "Texto para Fala",
        "description": "Conversão de texto em áudio com vozes",
        "recommended_providers": ["speechigy-studio", "elevenlabs", "coqui-tts"],
        "system_prompt_template": """Você é especializado em produção de áudio e voz.
Suas habilidades incluem:
- Preparar textos para narração
- Sugerir entonações e pausas
- Descrever características de voz
- Criar scripts para dublagem""",
        "temperature": 0.4
    },
    "game_creation": {
        "name": "Criação de Jogos",
        "description": "Desenvolvimento de jogos 2D e 3D",
        "recommended_providers": ["rosebud-ai", "claude-opus", "gpt-4-turbo"],
        "system_prompt_template": """Você é especializado em desenvolvimento de jogos.
Suas habilidades incluem:
- Game design e mecânicas de jogo
- Programação de jogos (Unity, Unreal, Godot)
- Design de níveis e balanceamento
- Narrativa e worldbuilding
- Assets e arte para jogos""",
        "temperature": 0.6
    }
}


class TrainingManager:
    """Gerenciador de treinamento de IAs"""

    def __init__(self, storage_dir: str = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path(__file__).parent.parent.parent / "models" / "training"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, TrainingProject] = {}
        self.sessions: Dict[str, TrainingSession] = {}
        self._load_data()

    def _load_data(self):
        """Carrega dados salvos"""
        # Carregar projetos
        projects_file = self.storage_dir / "projects.json"
        if projects_file.exists():
            try:
                data = json.loads(projects_file.read_text(encoding='utf-8'))
                for proj_data in data.get("projects", []):
                    proj = TrainingProject(**proj_data)
                    self.projects[proj.id] = proj
            except Exception as e:
                print(f"Erro ao carregar projetos: {e}")

        # Carregar sessões
        sessions_file = self.storage_dir / "sessions.json"
        if sessions_file.exists():
            try:
                data = json.loads(sessions_file.read_text(encoding='utf-8'))
                for sess_data in data.get("sessions", []):
                    sess = TrainingSession(**sess_data)
                    self.sessions[sess.id] = sess
            except Exception as e:
                print(f"Erro ao carregar sessões: {e}")

    def _save_data(self):
        """Salva dados no disco"""
        # Salvar projetos
        projects_file = self.storage_dir / "projects.json"
        projects_data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "projects": [asdict(p) for p in self.projects.values()]
        }
        projects_file.write_text(json.dumps(projects_data, indent=2, ensure_ascii=False), encoding='utf-8')

        # Salvar sessões
        sessions_file = self.storage_dir / "sessions.json"
        sessions_data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "sessions": [asdict(s) for s in self.sessions.values()]
        }
        sessions_file.write_text(json.dumps(sessions_data, indent=2, ensure_ascii=False), encoding='utf-8')

    def add_project(
        self,
        name: str,
        path: str,
        description: str = "",
        file_extensions: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> TrainingProject:
        """Adiciona um projeto para treinamento"""
        import uuid

        project_id = str(uuid.uuid4())[:8]

        # Extensões padrão se não especificadas
        if file_extensions is None:
            file_extensions = [".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".lua"]

        # Padrões de exclusão padrão
        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", "node_modules", ".git", ".venv", "venv", "dist", "build", ".cache"]

        project = TrainingProject(
            id=project_id,
            name=name,
            description=description,
            path=path,
            file_extensions=file_extensions,
            exclude_patterns=exclude_patterns
        )

        self.projects[project_id] = project
        self._save_data()

        return project

    def index_project(self, project_id: str) -> Dict[str, Any]:
        """Indexa arquivos de um projeto"""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Projeto não encontrado"}

        path = Path(project.path)
        if not path.exists():
            return {"error": f"Caminho não existe: {project.path}"}

        indexed_files = []
        total_tokens = 0

        # Percorrer arquivos
        for file_path in self._walk_project(path, project.file_extensions, project.exclude_patterns):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                tokens = len(content) // 4  # Estimativa
                total_tokens += tokens
                indexed_files.append(str(file_path))
            except Exception as e:
                continue

        project.indexed_files = indexed_files
        project.total_tokens = total_tokens
        project.updated_at = datetime.now().isoformat()
        self._save_data()

        return {
            "files_indexed": len(indexed_files),
            "total_tokens": total_tokens,
            "path": project.path
        }

    def _walk_project(
        self,
        path: Path,
        extensions: List[str],
        excludes: List[str]
    ) -> Generator[Path, None, None]:
        """Percorre arquivos do projeto aplicando filtros"""
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Verificar exclusões
                should_exclude = False
                for exclude in excludes:
                    if exclude in str(file_path):
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                # Verificar extensão
                if extensions:
                    if file_path.suffix.lower() in extensions:
                        yield file_path
                else:
                    yield file_path

    def get_project(self, project_id: str) -> Optional[TrainingProject]:
        """Retorna projeto por ID"""
        return self.projects.get(project_id)

    def list_projects(self, active_only: bool = True) -> List[TrainingProject]:
        """Lista todos os projetos"""
        projects = list(self.projects.values())
        if active_only:
            projects = [p for p in projects if p.is_active]
        return sorted(projects, key=lambda p: p.name)

    def remove_project(self, project_id: str) -> bool:
        """Remove um projeto"""
        if project_id in self.projects:
            del self.projects[project_id]
            self._save_data()
            return True
        return False

    def create_training_session(
        self,
        ai_model_id: str,
        project_ids: List[str],
        mode: str = "creative",
        specialization: str = "",
        external_provider: str = ""
    ) -> TrainingSession:
        """Cria uma sessão de treinamento"""
        import uuid

        session_id = str(uuid.uuid4())[:8]

        session = TrainingSession(
            id=session_id,
            ai_model_id=ai_model_id,
            project_ids=project_ids,
            mode=mode,
            specialization=specialization,
            external_ai_provider=external_provider,
            status="pending"
        )

        self.sessions[session_id] = session
        self._save_data()

        return session

    def get_project_content(
        self,
        project_id: str,
        max_tokens: int = None
    ) -> str:
        """Obtém conteúdo do projeto para treinamento"""
        project = self.projects.get(project_id)
        if not project:
            return ""

        content_parts = []
        current_tokens = 0

        for file_path_str in project.indexed_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            try:
                file_content = file_path.read_text(encoding='utf-8', errors='ignore')
                file_tokens = len(file_content) // 4

                # Verificar limite de tokens apenas se especificado
                if max_tokens and current_tokens + file_tokens > max_tokens:
                    break

                content_parts.append(f"### Arquivo: {file_path.name}\n```\n{file_content}\n```\n")
                current_tokens += file_tokens
            except Exception:
                continue

        return "\n".join(content_parts)

    @staticmethod
    def get_specializations() -> Dict:
        """Retorna especializações disponíveis"""
        return AI_SPECIALIZATIONS

    @staticmethod
    def get_specialization(name: str) -> Optional[Dict]:
        """Retorna uma especialização específica"""
        return AI_SPECIALIZATIONS.get(name)
