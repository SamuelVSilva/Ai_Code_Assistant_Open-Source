"""
Anthropic Provider - Integracao com Claude API
"""

from .base_provider import BaseAIProvider
from typing import List, Dict, Any, Optional, Generator
import re

class AnthropicProvider(BaseAIProvider):
    """Provider para Anthropic Claude API"""

    MODELS = {
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.history = []
        self.api_key = config.get('api_key', '')
        self.model = self.MODELS.get(
            config.get('model', 'claude-3.5-sonnet'),
            self.MODELS['claude-3.5-sonnet']
        )
        self.client = None
        self._init_client()

    def _init_client(self):
        """Inicializa cliente Anthropic"""
        if not self.api_key:
            return
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Instale anthropic: pip install anthropic")

    def send_message(
        self,
        message: str,
        context: List[Dict] = None,
        system_prompt: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Envia mensagem para Claude"""
        if not self.client:
            return "Erro: API key nao configurada"

        messages = []

        # Adicionar historico
        for hist_msg in self.history[-10:]:
            messages.append({
                "role": hist_msg["role"],
                "content": hist_msg["content"]
            })

        # Adicionar contexto se existir
        if context:
            for ctx in context:
                messages.append(ctx)

        # Mensagem atual
        messages.append({"role": "user", "content": message})

        system = system_prompt or "Voce e um assistente de programacao especializado. Responda em portugues."

        if stream:
            return self._stream_response(messages, system, max_tokens, temperature)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                temperature=temperature
            )

            result = response.content[0].text
            self.add_to_history("user", message)
            self.add_to_history("assistant", result)
            return result

        except Exception as e:
            return f"Erro: {str(e)}"

    def _stream_response(
        self,
        messages: List[Dict],
        system: str,
        max_tokens: int,
        temperature: float
    ) -> Generator:
        """Gera resposta em streaming"""
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                temperature=temperature
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    yield text

                self.add_to_history("user", messages[-1]["content"])
                self.add_to_history("assistant", full_response)
        except Exception as e:
            yield f"Erro: {str(e)}"

    def analyze_code(self, code: str, language: str = None, analysis_type: str = "review") -> Dict[str, Any]:
        """Analisa codigo com Claude"""
        prompts = {
            "review": f"Faca uma revisao deste codigo {language or ''}:",
            "security": f"Analise vulnerabilidades neste codigo {language or ''}:",
            "performance": f"Sugira otimizacoes de performance para este codigo {language or ''}:",
            "explain": f"Explique o que este codigo {language or ''} faz:"
        }

        prompt = prompts.get(analysis_type, prompts["review"])
        full_prompt = f"{prompt}\n\n```{language or ''}\n{code}\n```"

        response = self.send_message(full_prompt, temperature=0.3)

        return {
            "analysis_type": analysis_type,
            "language": language,
            "result": response,
            "model": self.model
        }

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Gera codigo baseado no prompt"""
        system = f"""Voce e um especialista em {language}.
Gere codigo limpo, bem documentado e seguindo boas praticas.
Retorne APENAS o codigo, sem explicacoes."""

        response = self.send_message(
            message=f"Gere codigo {language} para: {prompt}",
            system_prompt=system,
            temperature=0.5
        )

        return self._extract_code(response)

    def _extract_code(self, text: str) -> str:
        """Extrai bloco de codigo da resposta"""
        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        return text.strip()

    def clear_history(self):
        """Limpa historico de conversacao"""
        self.history = []
