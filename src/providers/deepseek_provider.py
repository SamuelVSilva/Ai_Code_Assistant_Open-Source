"""
DeepSeek Provider - Integracao com DeepSeek API
Otimizado para codigo - custo muito baixo
"""

from .base_provider import BaseAIProvider
from typing import List, Dict, Any, Optional, Generator
import requests
import json
import re

class DeepSeekProvider(BaseAIProvider):
    """Provider para DeepSeek API - especializado em codigo"""

    BASE_URL = "https://api.deepseek.com/v1"

    MODELS = {
        "deepseek-coder": "deepseek-coder",
        "deepseek-chat": "deepseek-chat",
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.history = []
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'deepseek-coder')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def send_message(
        self,
        message: str,
        context: List[Dict] = None,
        system_prompt: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Envia mensagem para DeepSeek"""
        if not self.api_key:
            return "Erro: API key nao configurada"

        messages = []

        # Sistema
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Historico
        for hist_msg in self.history[-10:]:
            messages.append(hist_msg)

        # Contexto adicional
        if context:
            for ctx in context:
                messages.append(ctx)

        # Mensagem atual
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }

        if stream:
            return self._stream_response(payload, message)

        try:
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                return f"Erro DeepSeek: {response.status_code} - {response.text}"

            result = response.json()["choices"][0]["message"]["content"]
            self.add_to_history("user", message)
            self.add_to_history("assistant", result)
            return result

        except Exception as e:
            return f"Erro: {str(e)}"

    def _stream_response(self, payload: Dict, user_content: str) -> Generator:
        """Stream de resposta"""
        try:
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                stream=True,
                timeout=60
            )

            full_response = ""

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_response += content
                                yield content
                        except:
                            continue

            self.add_to_history("user", user_content)
            self.add_to_history("assistant", full_response)

        except Exception as e:
            yield f"Erro: {str(e)}"

    def analyze_code(self, code: str, language: str = None, analysis_type: str = "review") -> Dict[str, Any]:
        """Analisa codigo - DeepSeek e otimizado para isso"""
        prompts = {
            "review": f"Revise este codigo {language or ''}:",
            "security": f"Encontre vulnerabilidades neste codigo {language or ''}:",
            "performance": f"Otimize a performance deste codigo {language or ''}:",
            "explain": f"Explique este codigo {language or ''}:",
            "refactor": f"Refatore este codigo {language or ''} para melhor legibilidade:"
        }

        system = "Voce e um especialista em revisao de codigo. Seja direto e objetivo."
        prompt = prompts.get(analysis_type, prompts["review"])
        full_prompt = f"{prompt}\n\n```{language or ''}\n{code}\n```"

        response = self.send_message(full_prompt, system_prompt=system, temperature=0.2)

        return {
            "analysis_type": analysis_type,
            "language": language,
            "result": response,
            "model": self.model
        }

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Gera codigo - ponto forte do DeepSeek"""
        system = f"""Voce e um programador expert em {language}.
Gere codigo limpo, eficiente e bem documentado.
Retorne apenas o codigo solicitado."""

        response = self.send_message(
            message=f"Gere codigo {language} para: {prompt}",
            system_prompt=system,
            temperature=0.3
        )

        return self._extract_code(response)

    def complete_code(self, code: str, cursor_position: int = None) -> str:
        """Autocomplete de codigo"""
        prompt = "Complete o codigo a seguir de forma natural:"
        full_prompt = f"{prompt}\n\n```\n{code}\n```"

        response = self.send_message(full_prompt, temperature=0.1, max_tokens=500)
        return self._extract_code(response)

    def _extract_code(self, text: str) -> str:
        """Extrai codigo da resposta"""
        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        return text.strip()

    def clear_history(self):
        """Limpa historico de conversacao"""
        self.history = []
