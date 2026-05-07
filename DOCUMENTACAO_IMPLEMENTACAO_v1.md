# GUIA DE IMPLEMENTACAO DETALHADO
## AI Code Assistant - Codigo e Exemplos Praticos

**Versao:** 1.0
**Complemento de:** DOCUMENTACAO_MELHORIAS_v1.md

---

## 1. IMPLEMENTACAO PRIORITARIA - OTIMIZACAO DE TOKENS

### 1.1 Arquivo: src/core/token_optimizer.py

```python
"""
Token Optimizer - Sistema de otimizacao de uso de tokens
Reducao estimada: 60-80% no consumo de tokens
"""

import tiktoken
from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib
import json

@dataclass
class TokenStats:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float

class TokenOptimizer:
    """Otimizador de tokens para reducao de custos e melhor uso de contexto"""

    # Limites por modelo
    MODEL_LIMITS = {
        "gpt-4": {"context": 8192, "output": 4096, "cost_in": 0.03, "cost_out": 0.06},
        "gpt-4-turbo": {"context": 128000, "output": 4096, "cost_in": 0.01, "cost_out": 0.03},
        "gpt-3.5-turbo": {"context": 16385, "output": 4096, "cost_in": 0.0005, "cost_out": 0.0015},
        "claude-3-opus": {"context": 200000, "output": 4096, "cost_in": 0.015, "cost_out": 0.075},
        "claude-3.5-sonnet": {"context": 200000, "output": 8192, "cost_in": 0.003, "cost_out": 0.015},
        "deepseek-coder": {"context": 32768, "output": 4096, "cost_in": 0.0001, "cost_out": 0.0002},
    }

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.encoder = self._get_encoder(model)
        self.limits = self.MODEL_LIMITS.get(model, self.MODEL_LIMITS["gpt-4"])

    def _get_encoder(self, model: str):
        """Obtem encoder apropriado para o modelo"""
        try:
            if "gpt" in model:
                return tiktoken.encoding_for_model(model)
            else:
                # Fallback para cl100k_base (compativel com maioria)
                return tiktoken.get_encoding("cl100k_base")
        except:
            return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Conta tokens em um texto"""
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """Conta tokens em lista de mensagens (formato OpenAI)"""
        total = 0
        for msg in messages:
            # Overhead por mensagem (~4 tokens)
            total += 4
            total += self.count_tokens(msg.get("role", ""))
            total += self.count_tokens(msg.get("content", ""))
        return total + 2  # Overhead final

    def trim_history(
        self,
        messages: List[Dict],
        max_tokens: int = None,
        keep_system: bool = True,
        keep_last_n: int = 2
    ) -> List[Dict]:
        """
        Trunca historico mantendo dentro do limite de tokens

        Args:
            messages: Lista de mensagens
            max_tokens: Limite maximo (usa limite do modelo - reserva se None)
            keep_system: Manter mensagem de sistema
            keep_last_n: Minimo de mensagens recentes a manter
        """
        if max_tokens is None:
            max_tokens = self.limits["context"] - self.limits["output"] - 500

        # Separar sistema das outras
        system_msg = None
        other_msgs = []

        for msg in messages:
            if msg.get("role") == "system" and keep_system:
                system_msg = msg
            else:
                other_msgs.append(msg)

        # Calcular tokens do sistema
        system_tokens = self.count_tokens(system_msg["content"]) if system_msg else 0
        available = max_tokens - system_tokens

        # Manter ultimas mensagens
        trimmed = []
        current_tokens = 0

        # Processar de tras para frente (mensagens mais recentes primeiro)
        for msg in reversed(other_msgs):
            msg_tokens = self.count_tokens(msg["content"]) + 4
            if current_tokens + msg_tokens <= available:
                trimmed.insert(0, msg)
                current_tokens += msg_tokens
            elif len(trimmed) < keep_last_n:
                # Forcar manter minimo
                trimmed.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break

        # Reconstruir com sistema
        result = []
        if system_msg:
            result.append(system_msg)
        result.extend(trimmed)

        return result

    def summarize_for_context(
        self,
        messages: List[Dict],
        max_summary_tokens: int = 500
    ) -> str:
        """
        Cria resumo das mensagens antigas para manter contexto

        Retorna string de resumo para usar como contexto
        """
        # Extrair conteudo relevante
        content_parts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Extrair apenas partes importantes
            if role == "user":
                # Perguntas/comandos do usuario
                content_parts.append(f"Usuario perguntou: {content[:200]}")
            elif role == "assistant":
                # Resumo da resposta
                content_parts.append(f"Assistente respondeu sobre: {content[:150]}")

        summary = " | ".join(content_parts)

        # Truncar se necessario
        while self.count_tokens(summary) > max_summary_tokens:
            content_parts = content_parts[1:]  # Remove mais antigo
            summary = " | ".join(content_parts)

        return f"[Resumo do contexto anterior: {summary}]"

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estima custo da requisicao"""
        cost_in = (input_tokens / 1000) * self.limits["cost_in"]
        cost_out = (output_tokens / 1000) * self.limits["cost_out"]
        return cost_in + cost_out

    def get_stats(self, input_text: str, output_text: str) -> TokenStats:
        """Retorna estatisticas de uso"""
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)

        return TokenStats(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost=self.estimate_cost(input_tokens, output_tokens)
        )

    def optimize_code_context(
        self,
        code: str,
        max_tokens: int = 2000,
        mode: str = "signatures"
    ) -> str:
        """
        Otimiza codigo para enviar menos tokens

        Modes:
            - full: Codigo completo (truncado se necessario)
            - signatures: Apenas assinaturas de funcoes/classes
            - compressed: Remove comentarios e espacos extras
        """
        if mode == "signatures":
            return self._extract_signatures(code, max_tokens)
        elif mode == "compressed":
            return self._compress_code(code, max_tokens)
        else:
            # Full - apenas truncar
            tokens = self.count_tokens(code)
            if tokens <= max_tokens:
                return code

            # Truncar mantendo estrutura
            lines = code.split('\n')
            result = []
            current_tokens = 0

            for line in lines:
                line_tokens = self.count_tokens(line + '\n')
                if current_tokens + line_tokens <= max_tokens:
                    result.append(line)
                    current_tokens += line_tokens
                else:
                    result.append("# ... codigo truncado ...")
                    break

            return '\n'.join(result)

    def _extract_signatures(self, code: str, max_tokens: int) -> str:
        """Extrai apenas assinaturas de funcoes e classes"""
        import ast

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self._compress_code(code, max_tokens)

        signatures = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Classe com docstring
                docstring = ast.get_docstring(node) or ""
                bases = [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]
                base_str = f"({', '.join(bases)})" if bases else ""
                signatures.append(f"class {node.name}{base_str}:")
                if docstring:
                    signatures.append(f'    """{docstring[:100]}"""')

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Funcao com argumentos e docstring
                args = []
                for arg in node.args.args:
                    arg_str = arg.arg
                    if arg.annotation:
                        arg_str += f": {ast.unparse(arg.annotation)}"
                    args.append(arg_str)

                returns = ""
                if node.returns:
                    returns = f" -> {ast.unparse(node.returns)}"

                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                signatures.append(f"{prefix} {node.name}({', '.join(args)}){returns}:")

                docstring = ast.get_docstring(node)
                if docstring:
                    signatures.append(f'    """{docstring[:100]}"""')

        result = '\n'.join(signatures)

        # Truncar se ainda muito grande
        while self.count_tokens(result) > max_tokens and signatures:
            signatures = signatures[:-1]
            result = '\n'.join(signatures)

        return result

    def _compress_code(self, code: str, max_tokens: int) -> str:
        """Remove comentarios e espacos desnecessarios"""
        lines = code.split('\n')
        compressed = []

        for line in lines:
            stripped = line.strip()

            # Pular linhas vazias e comentarios
            if not stripped or stripped.startswith('#'):
                continue

            # Remover comentarios inline
            if '#' in stripped and not stripped.startswith('"') and not stripped.startswith("'"):
                stripped = stripped.split('#')[0].strip()

            if stripped:
                compressed.append(stripped)

        result = '\n'.join(compressed)

        # Truncar se necessario
        while self.count_tokens(result) > max_tokens:
            compressed = compressed[:-1]
            result = '\n'.join(compressed)

        return result
```

### 1.2 Arquivo: src/core/response_cache.py

```python
"""
Response Cache - Cache de respostas para evitar requisicoes duplicadas
Reducao estimada: 20-30% em tokens repetidos
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import threading

@dataclass
class CacheEntry:
    prompt_hash: str
    context_hash: str
    response: str
    model: str
    timestamp: float
    tokens_saved: int = 0
    hit_count: int = 0

class ResponseCache:
    """Cache de respostas de IA com TTL e invalidacao"""

    def __init__(
        self,
        cache_dir: str = ".cache/ai_responses",
        ttl_hours: int = 24,
        max_entries: int = 1000
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
        self.max_entries = max_entries
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.lock = threading.Lock()

        # Carregar cache existente
        self._load_cache()

    def _get_hash(self, text: str) -> str:
        """Gera hash SHA256 do texto"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _get_cache_key(self, prompt: str, context: str, model: str) -> str:
        """Gera chave unica para cache"""
        combined = f"{model}:{prompt}:{context}"
        return self._get_hash(combined)

    def get(
        self,
        prompt: str,
        context: str = "",
        model: str = "default"
    ) -> Optional[str]:
        """
        Busca resposta no cache

        Returns:
            Resposta cacheada ou None se nao encontrada/expirada
        """
        key = self._get_cache_key(prompt, context, model)

        with self.lock:
            # Verificar memoria primeiro
            if key in self.memory_cache:
                entry = self.memory_cache[key]

                # Verificar TTL
                if time.time() - entry.timestamp < self.ttl_seconds:
                    entry.hit_count += 1
                    return entry.response
                else:
                    # Expirado
                    del self.memory_cache[key]
                    self._delete_file(key)
                    return None

            # Verificar disco
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                try:
                    data = json.loads(cache_file.read_text())
                    entry = CacheEntry(**data)

                    if time.time() - entry.timestamp < self.ttl_seconds:
                        entry.hit_count += 1
                        self.memory_cache[key] = entry
                        return entry.response
                    else:
                        cache_file.unlink()
                except:
                    pass

        return None

    def set(
        self,
        prompt: str,
        context: str,
        response: str,
        model: str = "default",
        tokens_used: int = 0
    ):
        """Armazena resposta no cache"""
        key = self._get_cache_key(prompt, context, model)

        entry = CacheEntry(
            prompt_hash=self._get_hash(prompt),
            context_hash=self._get_hash(context),
            response=response,
            model=model,
            timestamp=time.time(),
            tokens_saved=tokens_used,
            hit_count=0
        )

        with self.lock:
            # Verificar limite
            if len(self.memory_cache) >= self.max_entries:
                self._evict_oldest()

            self.memory_cache[key] = entry

            # Salvar em disco
            cache_file = self.cache_dir / f"{key}.json"
            cache_file.write_text(json.dumps(asdict(entry)))

    def invalidate(self, prompt: str = None, model: str = None):
        """Invalida entradas do cache"""
        with self.lock:
            if prompt is None and model is None:
                # Limpar tudo
                self.memory_cache.clear()
                for f in self.cache_dir.glob("*.json"):
                    f.unlink()
            else:
                # Invalidacao seletiva
                to_remove = []
                for key, entry in self.memory_cache.items():
                    if prompt and self._get_hash(prompt) == entry.prompt_hash:
                        to_remove.append(key)
                    elif model and entry.model == model:
                        to_remove.append(key)

                for key in to_remove:
                    del self.memory_cache[key]
                    self._delete_file(key)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do cache"""
        total_hits = sum(e.hit_count for e in self.memory_cache.values())
        total_tokens_saved = sum(e.tokens_saved * e.hit_count for e in self.memory_cache.values())

        return {
            "entries": len(self.memory_cache),
            "total_hits": total_hits,
            "tokens_saved": total_tokens_saved,
            "estimated_savings_usd": total_tokens_saved * 0.00003  # Estimativa GPT-4
        }

    def _load_cache(self):
        """Carrega cache do disco"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text())
                entry = CacheEntry(**data)

                # Verificar TTL
                if time.time() - entry.timestamp < self.ttl_seconds:
                    key = cache_file.stem
                    self.memory_cache[key] = entry
                else:
                    cache_file.unlink()
            except:
                continue

    def _evict_oldest(self):
        """Remove entrada mais antiga"""
        if not self.memory_cache:
            return

        oldest_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].timestamp
        )
        del self.memory_cache[oldest_key]
        self._delete_file(oldest_key)

    def _delete_file(self, key: str):
        """Remove arquivo de cache"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
```

---

## 2. IMPLEMENTACAO DOS PROVIDERS

### 2.1 Arquivo: src/providers/anthropic_provider.py (COMPLETAR)

```python
"""
Anthropic Provider - Integracao com Claude API
"""

from typing import Dict, List, Optional, Generator
from .base_provider import BaseAIProvider

class AnthropicProvider(BaseAIProvider):
    """Provider para Anthropic Claude API"""

    MODELS = {
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
    }

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.model = self.MODELS.get(
            config.get('model', 'claude-3.5-sonnet'),
            self.MODELS['claude-3.5-sonnet']
        )
        self.client = None
        self._init_client()

    def _init_client(self):
        """Inicializa cliente Anthropic"""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Instale anthropic: pip install anthropic")

    def send_message(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str | Generator:
        """
        Envia mensagem para Claude

        Args:
            message: Mensagem do usuario
            context: Contexto adicional (codigo, arquivo, etc)
            system_prompt: Prompt de sistema customizado
            max_tokens: Maximo de tokens na resposta
            temperature: Temperatura (0-1)
            stream: Se True, retorna generator para streaming

        Returns:
            Resposta do modelo ou generator se stream=True
        """
        # Construir mensagens
        messages = []

        # Adicionar historico
        for hist_msg in self.history:
            messages.append({
                "role": hist_msg["role"],
                "content": hist_msg["content"]
            })

        # Construir mensagem atual
        content = message
        if context:
            content = f"Contexto:\n```\n{context}\n```\n\nPergunta: {message}"

        messages.append({"role": "user", "content": content})

        # Sistema
        system = system_prompt or "Voce e um assistente de programacao especializado."

        if stream:
            return self._stream_response(messages, system, max_tokens, temperature)

        # Requisicao normal
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            temperature=temperature
        )

        result = response.content[0].text

        # Adicionar ao historico
        self.add_to_history("user", content)
        self.add_to_history("assistant", result)

        return result

    def _stream_response(
        self,
        messages: List[Dict],
        system: str,
        max_tokens: int,
        temperature: float
    ) -> Generator:
        """Gera resposta em streaming"""
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

            # Adicionar ao historico apos completar
            self.add_to_history("user", messages[-1]["content"])
            self.add_to_history("assistant", full_response)

    def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "review"
    ) -> Dict:
        """
        Analisa codigo com Claude

        Args:
            code: Codigo a analisar
            language: Linguagem do codigo
            analysis_type: Tipo de analise (review, security, performance, explain)
        """
        prompts = {
            "review": f"Faca uma revisao detalhada deste codigo {language}, identificando problemas, sugestoes de melhoria e boas praticas:",
            "security": f"Analise este codigo {language} em busca de vulnerabilidades de seguranca:",
            "performance": f"Analise a performance deste codigo {language} e sugira otimizacoes:",
            "explain": f"Explique detalhadamente o que este codigo {language} faz:"
        }

        prompt = prompts.get(analysis_type, prompts["review"])

        response = self.send_message(
            message=prompt,
            context=code,
            temperature=0.3  # Mais deterministico para analise
        )

        return {
            "analysis_type": analysis_type,
            "language": language,
            "result": response,
            "model": self.model
        }

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict:
        """Gera codigo baseado no prompt"""
        system = f"""Voce e um especialista em {language}.
        Gere codigo limpo, bem documentado e seguindo boas praticas.
        Retorne APENAS o codigo, sem explicacoes adicionais."""

        response = self.send_message(
            message=prompt,
            context=context,
            system_prompt=system,
            temperature=0.5
        )

        # Extrair codigo do response
        code = self._extract_code(response)

        return {
            "code": code,
            "language": language,
            "full_response": response
        }

    def _extract_code(self, text: str) -> str:
        """Extrai bloco de codigo da resposta"""
        import re

        # Procurar blocos de codigo markdown
        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Se nao encontrar, retornar texto limpo
        return text.strip()
```

### 2.2 Arquivo: src/providers/deepseek_provider.py (NOVO)

```python
"""
DeepSeek Provider - Integracao com DeepSeek API
Otimizado para codigo - custo muito baixo
"""

from typing import Dict, List, Optional, Generator
import requests
from .base_provider import BaseAIProvider

class DeepSeekProvider(BaseAIProvider):
    """Provider para DeepSeek API - especializado em codigo"""

    BASE_URL = "https://api.deepseek.com/v1"

    MODELS = {
        "deepseek-coder": "deepseek-coder",
        "deepseek-chat": "deepseek-chat",
    }

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'deepseek-coder')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def send_message(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str | Generator:
        """Envia mensagem para DeepSeek"""

        # Construir mensagens
        messages = []

        # Sistema
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Historico
        for hist_msg in self.history[-10:]:  # Limitar historico
            messages.append(hist_msg)

        # Mensagem atual
        content = message
        if context:
            content = f"```\n{context}\n```\n\n{message}"

        messages.append({"role": "user", "content": content})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }

        if stream:
            return self._stream_response(payload, content)

        response = self.session.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Erro DeepSeek: {response.text}")

        result = response.json()["choices"][0]["message"]["content"]

        self.add_to_history("user", content)
        self.add_to_history("assistant", result)

        return result

    def _stream_response(self, payload: Dict, user_content: str) -> Generator:
        """Stream de resposta"""
        response = self.session.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload,
            stream=True
        )

        full_response = ""

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break

                    import json
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")

                    if content:
                        full_response += content
                        yield content

        self.add_to_history("user", user_content)
        self.add_to_history("assistant", full_response)

    def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "review"
    ) -> Dict:
        """Analisa codigo - DeepSeek e otimizado para isso"""

        system = """Voce e um especialista em revisao de codigo.
        Seja direto e objetivo nas suas analises.
        Foque em problemas reais e sugestoes praticas."""

        prompts = {
            "review": f"Revise este codigo {language}:",
            "security": f"Encontre vulnerabilidades neste codigo {language}:",
            "performance": f"Otimize a performance deste codigo {language}:",
            "explain": f"Explique este codigo {language}:",
            "refactor": f"Refatore este codigo {language} para melhor legibilidade:"
        }

        response = self.send_message(
            message=prompts.get(analysis_type, prompts["review"]),
            context=code,
            system_prompt=system,
            temperature=0.2
        )

        return {
            "analysis_type": analysis_type,
            "result": response,
            "model": self.model
        }

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict:
        """Gera codigo - ponto forte do DeepSeek"""

        system = f"""Voce e um programador expert em {language}.
        Gere codigo limpo, eficiente e bem documentado.
        Retorne apenas o codigo solicitado."""

        response = self.send_message(
            message=prompt,
            context=context,
            system_prompt=system,
            temperature=0.3
        )

        return {
            "code": self._extract_code(response),
            "language": language,
            "full_response": response
        }

    def complete_code(self, code: str, cursor_position: int = None) -> str:
        """Autocomplete de codigo - funcionalidade especial do DeepSeek"""

        prompt = "Complete o codigo a seguir de forma natural:"

        response = self.send_message(
            message=prompt,
            context=code,
            temperature=0.1,  # Muito baixo para completions
            max_tokens=500
        )

        return self._extract_code(response)

    def _extract_code(self, text: str) -> str:
        """Extrai codigo da resposta"""
        import re

        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()
        return text.strip()
```

---

## 3. INTEGRACAO COM GUI - STREAMING

### 3.1 Arquivo: src/gui/components/chat_widget.py (NOVO)

```python
"""
Chat Widget com suporte a streaming
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QScrollArea, QFrame, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QTextCursor

class StreamingThread(QThread):
    """Thread para receber streaming de respostas"""

    chunk_received = pyqtSignal(str)
    finished_streaming = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, provider, message: str, context: str = None):
        super().__init__()
        self.provider = provider
        self.message = message
        self.context = context

    def run(self):
        try:
            generator = self.provider.send_message(
                message=self.message,
                context=self.context,
                stream=True
            )

            for chunk in generator:
                self.chunk_received.emit(chunk)

            self.finished_streaming.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatMessage(QFrame):
    """Widget de mensagem individual"""

    def __init__(self, role: str, content: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Header
        header = QLabel("Voce" if self.role == "user" else "Assistente")
        header.setStyleSheet(f"""
            color: {'#60a5fa' if self.role == 'user' else '#34d399'};
            font-weight: bold;
            font-size: 12px;
        """)
        layout.addWidget(header)

        # Conteudo
        self.content_label = QLabel(self.content)
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.content_label.setStyleSheet("""
            color: #e2e8f0;
            font-size: 14px;
            padding: 5px;
        """)
        layout.addWidget(self.content_label)

        # Estilo do frame
        bg_color = "#1e3a5f" if self.role == "user" else "#1e293b"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                margin: 5px;
            }}
        """)

        self.setMaximumWidth(600)

    def append_content(self, text: str):
        """Adiciona texto ao conteudo (para streaming)"""
        self.content += text
        self.content_label.setText(self.content)

    def set_content(self, text: str):
        """Define conteudo completo"""
        self.content = text
        self.content_label.setText(self.content)


class ChatWidget(QWidget):
    """Widget principal de chat com streaming"""

    message_sent = pyqtSignal(str)

    def __init__(self, provider=None, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.messages = []
        self.streaming_thread = None
        self.current_assistant_message = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Area de scroll para mensagens
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f172a;
            }
        """)

        # Container de mensagens
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(10)

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

        # Area de input
        input_layout = QHBoxLayout()

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Digite sua mensagem...")
        self.input_field.setMaximumHeight(100)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Enviar")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #475569;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def set_provider(self, provider):
        """Define provider de IA"""
        self.provider = provider

    def send_message(self):
        """Envia mensagem e inicia streaming"""
        text = self.input_field.toPlainText().strip()
        if not text or not self.provider:
            return

        # Desabilitar input durante streaming
        self.send_button.setEnabled(False)
        self.input_field.clear()

        # Adicionar mensagem do usuario
        self.add_message("user", text)

        # Criar mensagem vazia para assistente
        self.current_assistant_message = self.add_message("assistant", "")

        # Iniciar streaming
        self.streaming_thread = StreamingThread(self.provider, text)
        self.streaming_thread.chunk_received.connect(self.on_chunk_received)
        self.streaming_thread.finished_streaming.connect(self.on_streaming_finished)
        self.streaming_thread.error_occurred.connect(self.on_error)
        self.streaming_thread.start()

    def add_message(self, role: str, content: str) -> ChatMessage:
        """Adiciona mensagem ao chat"""
        message = ChatMessage(role, content)
        self.messages.append(message)
        self.messages_layout.addWidget(message)

        # Scroll para baixo
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

        return message

    def on_chunk_received(self, chunk: str):
        """Recebe chunk de streaming"""
        if self.current_assistant_message:
            self.current_assistant_message.append_content(chunk)

            # Scroll
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )

    def on_streaming_finished(self):
        """Streaming finalizado"""
        self.send_button.setEnabled(True)
        self.current_assistant_message = None

    def on_error(self, error: str):
        """Erro durante streaming"""
        self.send_button.setEnabled(True)
        if self.current_assistant_message:
            self.current_assistant_message.set_content(f"Erro: {error}")
        self.current_assistant_message = None

    def clear_chat(self):
        """Limpa todas as mensagens"""
        for message in self.messages:
            message.deleteLater()
        self.messages.clear()
```

---

## 4. CONFIGURACAO UNIFICADA

### 4.1 Arquivo: config/providers.yaml (NOVO)

```yaml
# Configuracao de Provedores de IA

providers:
  openai:
    enabled: true
    api_key: "${OPENAI_API_KEY}"  # Usar variavel de ambiente
    default_model: "gpt-4-turbo"
    models:
      - id: "gpt-4-turbo"
        name: "GPT-4 Turbo"
        context_window: 128000
        best_for: ["general", "analysis", "creative"]
      - id: "gpt-4"
        name: "GPT-4"
        context_window: 8192
        best_for: ["accuracy", "reasoning"]
      - id: "gpt-3.5-turbo"
        name: "GPT-3.5 Turbo"
        context_window: 16385
        best_for: ["fast", "cheap"]
    settings:
      temperature: 0.7
      max_tokens: 4096
      stream: true

  anthropic:
    enabled: true
    api_key: "${ANTHROPIC_API_KEY}"
    default_model: "claude-3.5-sonnet"
    models:
      - id: "claude-3.5-sonnet"
        name: "Claude 3.5 Sonnet"
        context_window: 200000
        best_for: ["code", "analysis", "long_context"]
      - id: "claude-3-opus"
        name: "Claude 3 Opus"
        context_window: 200000
        best_for: ["complex", "reasoning"]
      - id: "claude-3-haiku"
        name: "Claude 3 Haiku"
        context_window: 200000
        best_for: ["fast", "cheap"]
    settings:
      temperature: 0.7
      max_tokens: 4096
      stream: true

  deepseek:
    enabled: true
    api_key: "${DEEPSEEK_API_KEY}"
    default_model: "deepseek-coder"
    models:
      - id: "deepseek-coder"
        name: "DeepSeek Coder"
        context_window: 32768
        best_for: ["code", "completion", "cheap"]
      - id: "deepseek-chat"
        name: "DeepSeek Chat"
        context_window: 32768
        best_for: ["general", "cheap"]
    settings:
      temperature: 0.5
      max_tokens: 4096
      stream: true

  local:
    enabled: false
    models:
      - id: "codellama"
        name: "Code Llama"
        path: "models/codellama-7b"
        context_window: 16384
      - id: "mistral"
        name: "Mistral 7B"
        path: "models/mistral-7b"
        context_window: 8192

# Roteamento inteligente
routing:
  code_analysis: ["deepseek", "anthropic", "openai"]
  code_generation: ["deepseek", "anthropic", "openai"]
  general_chat: ["anthropic", "openai", "deepseek"]
  long_context: ["anthropic", "openai"]
  fast_response: ["deepseek", "openai:gpt-3.5-turbo", "anthropic:claude-3-haiku"]

# Fallback
fallback:
  enabled: true
  order: ["openai", "anthropic", "deepseek"]
  retry_count: 2
```

---

## 5. RESUMO DE ARQUIVOS A CRIAR

### Prioridade ALTA (Implementar Primeiro):
1. `src/core/token_optimizer.py` - Otimizacao de tokens
2. `src/core/response_cache.py` - Cache de respostas
3. `src/providers/anthropic_provider.py` - Provider Claude
4. `src/providers/deepseek_provider.py` - Provider DeepSeek
5. `config/providers.yaml` - Configuracao unificada

### Prioridade MEDIA:
6. `src/gui/components/chat_widget.py` - Chat com streaming
7. `src/core/code_compressor.py` - Compressao de codigo
8. `config/token_limits.yaml` - Limites de tokens

### Prioridade BAIXA (Fases Futuras):
9. Modulos de IA (imagem, audio, video, 3D)
10. Sistema de sincronizacao
11. Automacao e workflows
12. Treinamento de modelos

---

## CONCLUSAO

Este guia fornece implementacoes prontas para uso dos componentes mais criticos:

1. **Otimizacao de Tokens**: Reducao de 60-80% no consumo
2. **Providers Completos**: Anthropic e DeepSeek implementados
3. **Streaming**: Chat com respostas em tempo real
4. **Configuracao**: Sistema unificado de providers

Comece pela Fase 1 (otimizacao e providers) antes de adicionar novos modulos de IA.
