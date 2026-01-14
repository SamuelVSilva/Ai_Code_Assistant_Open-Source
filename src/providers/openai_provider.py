from .base_provider import BaseAIProvider
import openai
from typing import List, Dict, Any

class OpenAIProvider(BaseAIProvider):
    """Provedor para OpenAI API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = openai.OpenAI(api_key=config.get('api_key', ''))
        
    def send_message(self, message: str, context: List[Dict] = None) -> str:
        messages = []
        
        # Adicionar contexto se existir
        if context:
            messages.extend(context)
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
            model=self.config.get('model', 'gpt-4'),
            messages=messages,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        self.add_to_history("assistant", reply)
        
        return reply
    
    def analyze_code(self, code: str, language: str = None) -> Dict[str, Any]:
        prompt = f"Analise este código {language if language else ''}:\n\n{code}"
        
        analysis = self.send_message(prompt)
        
        return {
            "analysis": analysis,
            "suggestions": [],
            "issues": []
        }
    
    def generate_code(self, prompt: str, language: str = "python") -> str:
        full_prompt = f"Gere código em {language} para: {prompt}"
        return self.send_message(full_prompt)