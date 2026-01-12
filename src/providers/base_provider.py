from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAIProvider(ABC):
    """Classe base para provedores de IA"""
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.history = []
        
    @abstractmethod
    def send_message(self, message: str, context: List[Dict] = None) -> str:
        """Envia uma mensagem para a IA"""
        pass
    
    @abstractmethod
    def analyze_code(self, code: str, language: str = None) -> Dict[str, Any]:
        """Analisa um trecho de código"""
        pass
    
    @abstractmethod
    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Gera código baseado em um prompt"""
        pass
    
    def add_to_history(self, role: str, content: str):
        """Adiciona uma mensagem ao histórico"""
        self.history.append({"role": role, "content": content})