import os
import json
from pathlib import Path
from typing import Dict, List, Any

class ProjectManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.metadata_file = self.project_path / ".ai_assistant.json"
        self.load_metadata()
        
    def load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "project_name": self.project_path.name,
                "ai_providers": [],
                "chat_history": [],
                "generated_files": [],
                "analysis": {}
            }
            self.save_metadata()
    
    def save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def analyze_project_structure(self):
        """Analisa a estrutura do projeto"""
        structure = {
            "files": [],
            "directories": [],
            "languages": set(),
            "total_lines": 0
        }
        
        for root, dirs, files in os.walk(self.project_path):
            # Ignorar diretórios ocultos e venv
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'venv']
            
            for dir_name in dirs:
                structure["directories"].append(os.path.relpath(os.path.join(root, dir_name), self.project_path))
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Contar linhas
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        structure["total_lines"] += lines
                except:
                    lines = 0
                
                # Detectar linguagem por extensão
                extension = os.path.splitext(file)[1]
                structure["languages"].add(extension)
                
                structure["files"].append({
                    "path": rel_path,
                    "lines": lines,
                    "extension": extension
                })
        
        structure["languages"] = list(structure["languages"])
        return structure