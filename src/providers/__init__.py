"""
Providers de IA
"""

from .base_provider import BaseAIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .deepseek_provider import DeepSeekProvider

__all__ = [
    'BaseAIProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'DeepSeekProvider'
]

def get_provider(provider_name: str, config: dict):
    """Factory para obter provider por nome"""
    providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'deepseek': DeepSeekProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class:
        return provider_class(config)
    raise ValueError(f"Provider '{provider_name}' nao encontrado")
