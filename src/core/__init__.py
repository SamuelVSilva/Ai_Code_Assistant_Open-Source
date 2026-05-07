"""
Core - Logica central do aplicativo
"""

from .project_manager import ProjectManager
from .token_optimizer import TokenOptimizer, TokenStats
from .response_cache import ResponseCache, CacheEntry
from .ai_manager import AIManager
from .custom_ai_manager import CustomAIManager, CustomAIModel, AVAILABLE_BASE_MODELS, AI_TEMPLATES
from .training_manager import TrainingManager, TrainingProject, TrainingSession, AI_SPECIALIZATIONS
from .richie_ai import RichieAI, ChatSession, ActionPlan, PermissionRequest, RICHIE_SYSTEM_PROMPT

__all__ = [
    'ProjectManager',
    'TokenOptimizer',
    'TokenStats',
    'ResponseCache',
    'CacheEntry',
    'AIManager',
    'CustomAIManager',
    'CustomAIModel',
    'AVAILABLE_BASE_MODELS',
    'AI_TEMPLATES',
    'TrainingManager',
    'TrainingProject',
    'TrainingSession',
    'AI_SPECIALIZATIONS',
    'RichieAI',
    'ChatSession',
    'ActionPlan',
    'PermissionRequest',
    'RICHIE_SYSTEM_PROMPT'
]

