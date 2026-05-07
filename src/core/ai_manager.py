"""
AI Manager - Gerenciador central de provedores de IA
Integra cache, otimizacao de tokens e fallback automatico
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import os

from .token_optimizer import TokenOptimizer
from .response_cache import ResponseCache
from ..providers import get_provider, BaseAIProvider

class AIManager:
    """Gerenciador central de provedores de IA com otimizacao automatica"""

    def __init__(self, config_path: str = None):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.active_provider: str = None
        self.optimizer: TokenOptimizer = None
        self.cache: ResponseCache = None
        self.config: Dict = {}

        # Carregar configuracao
        if config_path:
            self._load_config(config_path)
        else:
            self._load_default_config()

        self._init_components()

    def _load_config(self, config_path: str):
        """Carrega configuracao do arquivo YAML"""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self._load_default_config()

    def _load_default_config(self):
        """Configuracao padrao"""
        self.config = {
            'providers': {
                'openai': {'enabled': True, 'api_key': os.getenv('OPENAI_API_KEY', '')},
                'anthropic': {'enabled': True, 'api_key': os.getenv('ANTHROPIC_API_KEY', '')},
                'deepseek': {'enabled': True, 'api_key': os.getenv('DEEPSEEK_API_KEY', '')},
            },
            'optimization': {
                'cache': {'enabled': True, 'ttl_hours': 24},
                'tokens': {'history_limit': 20, 'compress_code': True}
            },
            'fallback': {'enabled': True, 'order': ['openai', 'anthropic', 'deepseek']}
        }

    def _init_components(self):
        """Inicializa componentes"""
        # Inicializar cache
        cache_config = self.config.get('optimization', {}).get('cache', {})
        if cache_config.get('enabled', True):
            self.cache = ResponseCache(
                ttl_hours=cache_config.get('ttl_hours', 24),
                max_entries=cache_config.get('max_entries', 1000)
            )

        # Inicializar providers
        providers_config = self.config.get('providers', {})
        for name, pconfig in providers_config.items():
            if pconfig.get('enabled', False):
                api_key = pconfig.get('api_key', '')
                # Substituir variaveis de ambiente
                if api_key.startswith('${') and api_key.endswith('}'):
                    env_var = api_key[2:-1]
                    api_key = os.getenv(env_var, '')

                if api_key:
                    try:
                        provider = get_provider(name, {
                            'api_key': api_key,
                            'model': pconfig.get('default_model'),
                            **pconfig.get('settings', {})
                        })
                        self.providers[name] = provider
                        if not self.active_provider:
                            self.active_provider = name
                    except Exception as e:
                        print(f"Erro ao inicializar provider {name}: {e}")

    def set_active_provider(self, name: str) -> bool:
        """Define provider ativo"""
        if name in self.providers:
            self.active_provider = name
            # Atualizar otimizador para o modelo do provider
            model = self.config.get('providers', {}).get(name, {}).get('default_model', 'gpt-4')
            self.optimizer = TokenOptimizer(model)
            return True
        return False

    def get_provider(self, name: str = None) -> Optional[BaseAIProvider]:
        """Retorna provider pelo nome ou o ativo"""
        name = name or self.active_provider
        return self.providers.get(name)

    def send_message(
        self,
        message: str,
        context: str = None,
        use_cache: bool = True,
        provider_name: str = None
    ) -> str:
        """
        Envia mensagem com otimizacao automatica

        Args:
            message: Mensagem do usuario
            context: Contexto adicional (codigo, etc)
            use_cache: Se deve usar cache
            provider_name: Nome do provider (usa ativo se None)
        """
        provider_name = provider_name or self.active_provider
        provider = self.providers.get(provider_name)

        if not provider:
            return "Erro: Nenhum provider disponivel"

        # Verificar cache
        if use_cache and self.cache:
            cached = self.cache.get(message, context or "", provider_name)
            if cached:
                return cached

        # Otimizar contexto de codigo se necessario
        if context and self.optimizer:
            token_config = self.config.get('optimization', {}).get('tokens', {})
            if token_config.get('compress_code', True):
                max_tokens = token_config.get('max_code_tokens', 2000)
                context = self.optimizer.optimize_code_context(context, max_tokens)

        # Enviar mensagem
        try:
            if context:
                full_message = f"Contexto:\n```\n{context}\n```\n\n{message}"
            else:
                full_message = message

            response = provider.send_message(full_message)

            # Salvar no cache
            if use_cache and self.cache:
                self.cache.set(message, context or "", response, provider_name)

            return response

        except Exception as e:
            # Tentar fallback
            if self.config.get('fallback', {}).get('enabled', False):
                return self._try_fallback(message, context, provider_name)
            return f"Erro: {str(e)}"

    def _try_fallback(self, message: str, context: str, failed_provider: str) -> str:
        """Tenta providers de fallback"""
        fallback_order = self.config.get('fallback', {}).get('order', [])

        for name in fallback_order:
            if name != failed_provider and name in self.providers:
                try:
                    provider = self.providers[name]
                    if context:
                        full_message = f"Contexto:\n```\n{context}\n```\n\n{message}"
                    else:
                        full_message = message
                    return provider.send_message(full_message)
                except:
                    continue

        return "Erro: Todos os providers falharam"

    def analyze_code(
        self,
        code: str,
        language: str = None,
        analysis_type: str = "review",
        provider_name: str = None
    ) -> Dict[str, Any]:
        """Analisa codigo com otimizacao"""
        provider_name = provider_name or self.active_provider
        provider = self.providers.get(provider_name)

        if not provider:
            return {"error": "Nenhum provider disponivel"}

        # Otimizar codigo
        if self.optimizer:
            token_config = self.config.get('optimization', {}).get('tokens', {})
            max_tokens = token_config.get('max_code_tokens', 2000)
            optimized_code = self.optimizer.optimize_code_context(code, max_tokens)
        else:
            optimized_code = code

        return provider.analyze_code(optimized_code, language, analysis_type)

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        provider_name: str = None
    ) -> str:
        """Gera codigo"""
        provider_name = provider_name or self.active_provider
        provider = self.providers.get(provider_name)

        if not provider:
            return "Erro: Nenhum provider disponivel"

        return provider.generate_code(prompt, language)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas de uso"""
        stats = {
            "active_provider": self.active_provider,
            "available_providers": list(self.providers.keys()),
        }

        if self.cache:
            stats["cache"] = self.cache.get_stats()

        return stats

    def clear_history(self, provider_name: str = None):
        """Limpa historico de um ou todos os providers"""
        if provider_name:
            if provider_name in self.providers:
                self.providers[provider_name].clear_history()
        else:
            for provider in self.providers.values():
                if hasattr(provider, 'clear_history'):
                    provider.clear_history()

    def clear_cache(self):
        """Limpa cache de respostas"""
        if self.cache:
            self.cache.invalidate()
