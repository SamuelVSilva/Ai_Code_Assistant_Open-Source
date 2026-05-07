"""
Token Optimizer - Otimizacao de uso de tokens
Reducao estimada: 60-80% no consumo
"""

import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class TokenStats:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float

class TokenOptimizer:
    """Otimizador de tokens para reducao de custos"""

    MODEL_LIMITS = {
        "gpt-4": {"context": 8192, "cost_in": 0.03, "cost_out": 0.06},
        "gpt-4-turbo": {"context": 128000, "cost_in": 0.01, "cost_out": 0.03},
        "gpt-3.5-turbo": {"context": 16385, "cost_in": 0.0005, "cost_out": 0.0015},
        "claude-3-opus": {"context": 200000, "cost_in": 0.015, "cost_out": 0.075},
        "claude-3.5-sonnet": {"context": 200000, "cost_in": 0.003, "cost_out": 0.015},
        "deepseek-coder": {"context": 32768, "cost_in": 0.0001, "cost_out": 0.0002},
    }

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.limits = self.MODEL_LIMITS.get(model, self.MODEL_LIMITS["gpt-4"])
        self._encoder = None

    @property
    def encoder(self):
        """Lazy load do encoder tiktoken"""
        if self._encoder is None:
            try:
                import tiktoken
                if "gpt" in self.model:
                    self._encoder = tiktoken.encoding_for_model(self.model)
                else:
                    self._encoder = tiktoken.get_encoding("cl100k_base")
            except ImportError:
                self._encoder = None
        return self._encoder

    def count_tokens(self, text: str) -> int:
        """Conta tokens - usa tiktoken se disponivel, senao estimativa"""
        if not text:
            return 0
        if self.encoder:
            return len(self.encoder.encode(text))
        # Estimativa: ~4 caracteres por token
        return len(text) // 4

    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """Conta tokens em lista de mensagens"""
        total = 0
        for msg in messages:
            total += 4  # Overhead por mensagem
            total += self.count_tokens(msg.get("role", ""))
            total += self.count_tokens(msg.get("content", ""))
        return total + 2

    def trim_history(
        self,
        messages: List[Dict],
        max_tokens: int = None,
        keep_system: bool = True,
        keep_last_n: int = 2
    ) -> List[Dict]:
        """Trunca historico mantendo dentro do limite"""
        if max_tokens is None:
            max_tokens = self.limits["context"] - 4096 - 500

        system_msg = None
        other_msgs = []

        for msg in messages:
            if msg.get("role") == "system" and keep_system:
                system_msg = msg
            else:
                other_msgs.append(msg)

        system_tokens = self.count_tokens(system_msg["content"]) if system_msg else 0
        available = max_tokens - system_tokens

        trimmed = []
        current_tokens = 0

        for msg in reversed(other_msgs):
            msg_tokens = self.count_tokens(msg.get("content", "")) + 4
            if current_tokens + msg_tokens <= available:
                trimmed.insert(0, msg)
                current_tokens += msg_tokens
            elif len(trimmed) < keep_last_n:
                trimmed.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break

        result = []
        if system_msg:
            result.append(system_msg)
        result.extend(trimmed)
        return result

    def summarize_context(self, messages: List[Dict], max_tokens: int = 500) -> str:
        """Cria resumo das mensagens antigas"""
        parts = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")[:150]
            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"AI: {content}")

        summary = " | ".join(parts)
        while self.count_tokens(summary) > max_tokens and parts:
            parts = parts[1:]
            summary = " | ".join(parts)

        return f"[Contexto anterior: {summary}]"

    def optimize_code_context(self, code: str, max_tokens: int = 2000, mode: str = "compressed") -> str:
        """Otimiza codigo para enviar menos tokens"""
        if mode == "signatures":
            return self._extract_signatures(code, max_tokens)
        return self._compress_code(code, max_tokens)

    def _compress_code(self, code: str, max_tokens: int) -> str:
        """Remove comentarios e espacos extras"""
        lines = code.split('\n')
        compressed = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if '#' in stripped:
                    stripped = stripped.split('#')[0].strip()
                if stripped:
                    compressed.append(stripped)

        result = '\n'.join(compressed)
        while self.count_tokens(result) > max_tokens and compressed:
            compressed = compressed[:-1]
            result = '\n'.join(compressed)
        return result

    def _extract_signatures(self, code: str, max_tokens: int) -> str:
        """Extrai assinaturas de funcoes/classes"""
        try:
            import ast
            tree = ast.parse(code)
        except:
            return self._compress_code(code, max_tokens)

        signatures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                signatures.append(f"class {node.name}:")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                signatures.append(f"{prefix} {node.name}({', '.join(args)}):")

        result = '\n'.join(signatures)
        while self.count_tokens(result) > max_tokens and signatures:
            signatures = signatures[:-1]
            result = '\n'.join(signatures)
        return result

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
