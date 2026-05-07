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
    """Cache de respostas de IA com TTL"""

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
        self._load_cache()

    def _get_hash(self, text: str) -> str:
        """Gera hash do texto"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _get_cache_key(self, prompt: str, context: str, model: str) -> str:
        """Gera chave unica"""
        combined = f"{model}:{prompt}:{context}"
        return self._get_hash(combined)

    def get(self, prompt: str, context: str = "", model: str = "default") -> Optional[str]:
        """Busca resposta no cache"""
        key = self._get_cache_key(prompt, context, model)

        with self.lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if time.time() - entry.timestamp < self.ttl_seconds:
                    entry.hit_count += 1
                    return entry.response
                else:
                    del self.memory_cache[key]
                    self._delete_file(key)
                    return None

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
            if len(self.memory_cache) >= self.max_entries:
                self._evict_oldest()

            self.memory_cache[key] = entry
            cache_file = self.cache_dir / f"{key}.json"
            cache_file.write_text(json.dumps(asdict(entry)))

    def invalidate(self, prompt: str = None, model: str = None):
        """Invalida entradas do cache"""
        with self.lock:
            if prompt is None and model is None:
                self.memory_cache.clear()
                for f in self.cache_dir.glob("*.json"):
                    f.unlink()
            else:
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
            "estimated_savings_usd": total_tokens_saved * 0.00003
        }

    def _load_cache(self):
        """Carrega cache do disco"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text())
                entry = CacheEntry(**data)
                if time.time() - entry.timestamp < self.ttl_seconds:
                    self.memory_cache[cache_file.stem] = entry
                else:
                    cache_file.unlink()
            except:
                continue

    def _evict_oldest(self):
        """Remove entrada mais antiga"""
        if not self.memory_cache:
            return
        oldest_key = min(self.memory_cache.keys(), key=lambda k: self.memory_cache[k].timestamp)
        del self.memory_cache[oldest_key]
        self._delete_file(oldest_key)

    def _delete_file(self, key: str):
        """Remove arquivo de cache"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
