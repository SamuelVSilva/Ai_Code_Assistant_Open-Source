"""
FlowEngine — Motor de Execução de Fluxo BotForge
=================================================
Complemento ao richie_ai.py. Não substitui, apenas expande.

Arquitetura "Motor + Configuração JSON":
  - O MOTOR (este arquivo) é genérico — executa qualquer regra
  - A CONFIGURAÇÃO (JSON/cards do modelo) define QUAIS são as regras
  - Trocar o JSON = trocar o comportamento do bot, sem mexer no Python

Funcionalidades:
  - Percorrer fluxo de nodes (trace_flow)
  - Extrair config de API de nodes api_connector
  - Detectar intenções via keywords definidas nos cards NLP
  - Resolver templates de resposta dos cards send/ai_response
  - Navegar conexões com suporte a múltiplas saídas (out_0, out_1, ...)

Versão: v0.4.11-rev1.2.5-280426
Developer: @S.V.S - Try Technology
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class FlowEngine:
    """
    Motor genérico de execução de fluxos BotForge.
    
    Recebe nodes e connections do JSON de um modelo e permite:
    1. Percorrer o fluxo visualmente (trace_flow)
    2. Detectar intenções via keywords nos cards NLP (detect_intent)
    3. Extrair configuração de API (get_api_config)
    4. Resolver templates de resposta (get_response_template)
    5. Acessar dados do modelo para self-awareness (get_model_data)
    """

    def __init__(self, flow_nodes: List[Dict], flow_conns: List[Dict], model_data: Dict = None):
        """
        Inicializa o motor com os dados do fluxo.
        
        Args:
            flow_nodes: Lista de nodes do JSON (_flow_nodes)
            flow_conns: Lista de conexões do JSON (_flow_conns)
            model_data: Dados do modelo (_model_data) para self-awareness
        """
        self.nodes: Dict[str, Dict] = {}
        for node in (flow_nodes or []):
            nid = node.get("id")
            if nid:
                self.nodes[nid] = node

        self.connections: List[Dict] = flow_conns or []
        self.model_data: Dict = model_data or {}
        self.context: Dict[str, Any] = {}  # Estado compartilhado entre nodes

        # Cache de conexões indexado por source para performance
        self._conn_index: Dict[str, List[Dict]] = {}
        for conn in self.connections:
            src = conn.get("source", "")
            if src not in self._conn_index:
                self._conn_index[src] = []
            self._conn_index[src].append(conn)

    # =========================================================
    # === NAVEGAÇÃO DO FLUXO ===
    # =========================================================

    def find_start_node(self) -> Optional[str]:
        """
        Encontra o primeiro nó do fluxo.
        Prioridade: api_connector > api_entry > recv > primeiro nó qualquer.
        """
        priority_types = ["api_connector", "api_entry", "recv"]
        for ptype in priority_types:
            for nid, node in self.nodes.items():
                if node.get("type") == ptype:
                    return nid
        # Fallback: retorna o primeiro nó
        return next(iter(self.nodes), None)

    def get_next_nodes(self, current_id: str, port: str = None) -> List[str]:
        """
        Retorna IDs dos próximos nós conectados a partir de current_id.
        
        Args:
            current_id: ID do nó atual
            port: Porta específica (ex: 'out_0', 'out_1'). Se None, retorna todos.
        
        Returns:
            Lista de IDs dos nós destino
        """
        conns = self._conn_index.get(current_id, [])
        targets = []
        for conn in conns:
            if port is None or conn.get("source_port") == port:
                target = conn.get("target")
                if target:
                    targets.append(target)
        return targets

    def get_node_by_type(self, node_type: str) -> Optional[Dict]:
        """Retorna o primeiro nó de um tipo específico."""
        for node in self.nodes.values():
            if node.get("type") == node_type:
                return node
        return None

    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Retorna todos os nós de um tipo específico."""
        return [n for n in self.nodes.values() if n.get("type") == node_type]

    # =========================================================
    # === TRACE DO FLUXO (VISUALIZAÇÃO) ===
    # =========================================================

    def trace_flow(self, user_input: str = "") -> List[Dict]:
        """
        Percorre o fluxo do início ao fim e retorna lista de resultados por nó.
        Usado para visualização do fluxo ativo no BotForge canvas.
        
        Segue a primeira conexão de cada nó (fluxo principal).
        Para fluxos com ramificação (NLP), segue todas as saídas do nó NLP.
        
        Args:
            user_input: Texto do usuário (para contexto)
        
        Returns:
            Lista de dicts com node_id, type, label, msg, status
        """
        results = []
        current_id = self.find_start_node()
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)
            node = self.nodes.get(current_id)
            if not node:
                break

            result = {
                "node_id": current_id,
                "type": node.get("type", "unknown"),
                "label": node.get("label", ""),
                "msg": node.get("msg", node.get("message", "")),
                "color": node.get("color", "#58a6ff"),
                "status": "ok",
                "out_labels": node.get("out_labels", []),
            }
            results.append(result)

            # Próximo nó: primeira conexão disponível
            next_nodes = self.get_next_nodes(current_id)
            current_id = next_nodes[0] if next_nodes else None

        return results

    def trace_flow_for_intent(self, intent_name: str) -> List[Dict]:
        """
        Percorre o fluxo seguindo a rota de uma intenção específica.
        
        Ex: trace_flow_for_intent("create_file") → segue c1 → c2 → (out_2) → c5 → c15 → c16
        
        Args:
            intent_name: Nome da intenção para seguir
        
        Returns:
            Lista de nós percorridos na rota dessa intenção
        """
        nlp_node = self.get_node_by_type("nlp")
        if not nlp_node:
            return self.trace_flow()

        # Mapear intenção para porta de saída do NLP
        out_labels = nlp_node.get("out_labels", [])
        intent_port = None

        # Primeiro tentar match direto via intents config
        intents_config = nlp_node.get("intents", [])
        for i, intent_cfg in enumerate(intents_config):
            if intent_cfg.get("name") == intent_name:
                intent_port = f"out_{i}"
                break

        # Fallback: tentar match via out_labels
        if not intent_port:
            intent_label_map = {
                "greeting": "Saudação", "analyze_code": "Análise de Código",
                "create_file": "Gerar Código", "explain": "Explicar",
                "debug": "Debug/Erro", "run_code": "Executar Script",
                "botforge": "BotForge", "config": "Configuração",
                "general": "Pergunta Geral",
            }
            target_label = intent_label_map.get(intent_name, "")
            for i, label in enumerate(out_labels):
                if label == target_label or intent_name.lower() in label.lower():
                    intent_port = f"out_{i}"
                    break

        if not intent_port:
            return self.trace_flow()

        # Percorrer: start → NLP → porta da intenção → até o fim
        results = []
        start_id = self.find_start_node()
        nlp_id = nlp_node["id"]

        # Adicionar nós antes do NLP
        current = start_id
        visited = set()
        while current and current != nlp_id and current not in visited:
            visited.add(current)
            node = self.nodes.get(current)
            if node:
                results.append({
                    "node_id": current, "type": node.get("type"),
                    "label": node.get("label"), "status": "ok"
                })
            nexts = self.get_next_nodes(current)
            current = nexts[0] if nexts else None

        # Adicionar NLP
        results.append({
            "node_id": nlp_id, "type": "nlp",
            "label": nlp_node.get("label"), "status": "ok",
            "selected_intent": intent_name, "selected_port": intent_port
        })

        # Seguir pela porta da intenção
        current = None
        intent_targets = self.get_next_nodes(nlp_id, intent_port)
        if intent_targets:
            current = intent_targets[0]

        while current and current not in visited:
            visited.add(current)
            node = self.nodes.get(current)
            if node:
                results.append({
                    "node_id": current, "type": node.get("type"),
                    "label": node.get("label"), "status": "ok"
                })
            nexts = self.get_next_nodes(current)
            current = nexts[0] if nexts else None

        return results

    # =========================================================
    # === DETECÇÃO DE INTENÇÃO VIA KEYWORDS DO JSON ===
    # =========================================================

    def detect_intent(self, user_input: str) -> Tuple[str, float]:
        """
        Detecta intenção do usuário usando keywords definidas nos cards NLP.
        
        Lê a lista de intents do nó NLP (campo "intents") e verifica
        quais keywords batem com o input. Retorna a intenção mais relevante.
        
        Esta é a parte "Motor + Config" — o motor (este loop) é genérico,
        as keywords (no JSON) são específicas de cada bot.
        
        Args:
            user_input: Texto do usuário
        
        Returns:
            Tuple (nome_da_intencao, confianca 0.0-1.0)
        """
        if not user_input or not user_input.strip():
            return ("general", 0.0)

        txt = user_input.lower().strip()
        nlp_node = self.get_node_by_type("nlp")
        if not nlp_node:
            return ("general", 0.0)

        intents_config = nlp_node.get("intents", [])
        if not intents_config:
            # Fallback Dinâmico: Construir intents a partir de out_keywords (Multi-Language Support)
            out_keywords = nlp_node.get("out_keywords", [])
            out_labels = nlp_node.get("out_labels", [])
            
            if not out_keywords:
                return ("general", 0.0)
                
            import json
            for i, kw_str in enumerate(out_keywords):
                if not kw_str or not kw_str.strip():
                    continue
                    
                name = out_labels[i] if i < len(out_labels) else f"route_{i}"
                keywords = []
                
                # Tentar parsear como dicionário multilingue
                try:
                    kw_dict = json.loads(kw_str)
                    if isinstance(kw_dict, dict):
                        for lang_kws in kw_dict.values():
                            if isinstance(lang_kws, str):
                                keywords.extend([k.strip() for k in lang_kws.split(",") if k.strip()])
                    else:
                        keywords = [k.strip() for k in str(kw_dict).split(",") if k.strip()]
                except:
                    # String normal
                    keywords = [k.strip() for k in str(kw_str).split(",") if k.strip()]
                    
                intents_config.append({
                    "name": name,
                    "keywords": keywords,
                    "priority": 1
                })

        best_intent = "general"
        best_score = 0.0

        for intent_cfg in intents_config:
            intent_name = intent_cfg.get("name", "")
            keywords = intent_cfg.get("keywords", [])
            context_words = intent_cfg.get("context_words", [])
            priority = intent_cfg.get("priority", 1)

            # Calcular score: quantas keywords batem
            kw_matches = sum(1 for kw in keywords if kw.lower() in txt)
            ctx_matches = sum(1 for cw in context_words if cw.lower() in txt)

            if kw_matches == 0:
                continue

            # Score = (keywords + contexto * 0.5) * prioridade / total de keywords
            total = len(keywords) + len(context_words) * 0.5
            score = ((kw_matches + ctx_matches * 0.5) / total) * priority if total > 0 else 0

            if score > best_score:
                best_score = score
                best_intent = intent_name

        return (best_intent, min(best_score, 1.0))

    # =========================================================
    # === CONFIGURAÇÃO DE API (api_connector) ===
    # =========================================================

    def get_api_config(self) -> Dict:
        """
        Extrai configuração do nó api_connector (se existir).
        
        Retorna dict com:
        - models: Lista de modelos disponíveis
        - default_model: Modelo padrão
        - chat_settings: {temperature, max_tokens, system_prompt, supported_languages}
        
        Returns:
            Dict de configuração do API connector, ou {} se não existir.
        """
        for node in self.nodes.values():
            if node.get("type") in ("api_connector", "api_entry"):
                return node.get("api_config", {})
        return {}

    def get_chat_settings(self) -> Dict:
        """Atalho para get_api_config()['chat_settings']."""
        api_cfg = self.get_api_config()
        return api_cfg.get("chat_settings", {})

    def get_supported_languages(self) -> List[str]:
        """Retorna lista de linguagens suportadas pelo modelo."""
        settings = self.get_chat_settings()
        return settings.get("supported_languages", [])

    def get_temperature(self) -> float:
        """Retorna temperature do modelo (default 0.7)."""
        settings = self.get_chat_settings()
        return settings.get("temperature", 0.7)

    def get_max_tokens(self):
        """Retorna max_tokens do modelo. None = sem limite (modo offline)."""
        settings = self.get_chat_settings()
        if settings.get("no_token_limit", False):
            return None  # Sem limite no modo offline
        return settings.get("max_tokens", 4096)

    def get_system_prompt(self) -> str:
        """Retorna system_prompt do modelo."""
        settings = self.get_chat_settings()
        sp = settings.get("system_prompt", "")
        if not sp:
            # Fallback para model_data
            sp = self.model_data.get("system_prompt", "")
        return sp

    # =========================================================
    # === TEMPLATES DE RESPOSTA ===
    # =========================================================

    def get_response_template(self, intent_name: str) -> str:
        """
        Retorna o template de resposta para uma intenção específica.
        
        Busca nos nodes send/ai_response que estão conectados à
        saída do NLP correspondente à intenção.
        
        Args:
            intent_name: Nome da intenção (ex: "create_file")
        
        Returns:
            String de template com variáveis {var}, ou "" se não encontrado.
        """
        # Percorrer a rota da intenção e pegar a msg do nó send/ai_response
        trace = self.trace_flow_for_intent(intent_name)
        for step in trace:
            if step.get("type") in ("send", "ai_response"):
                node = self.nodes.get(step["node_id"], {})
                template = node.get("response_template", node.get("msg", ""))
                return template
        return ""

    # =========================================================
    # === SELF-AWARENESS (DADOS DO MODELO) ===
    # =========================================================

    def get_model_info(self) -> Dict:
        """
        Retorna informações do próprio modelo para self-awareness.
        
        O Richie pode responder "qual sua versão" usando estes dados.
        Todos os dados vêm do JSON — o Python não sabe nada hardcoded.
        
        Returns:
            Dict com name, version, creator, data_criacao, etc.
        """
        config = self.model_data.get("config", {})
        return {
            "name": config.get("botName", self.model_data.get("name", "Desconhecido")),
            "version": config.get("version", self.model_data.get("version", "?")),
            "creator": config.get("creator", self.model_data.get("creator_name", "")),
            "data_criacao": config.get("data_criacao", self.model_data.get("creation_date",
                           self.model_data.get("created_at", "?"))),
            "description": config.get("description", self.model_data.get("description", "")),
            "base_provider": self.model_data.get("base_provider", "offline"),
            "base_model": self.model_data.get("base_model", ""),
            "temperature": self.model_data.get("temperature", 0.7),
            "max_tokens": None if self.model_data.get("no_token_limit", False) else self.model_data.get("max_tokens", 4096),
            "no_token_limit": self.model_data.get("no_token_limit", False),
            "is_active": self.model_data.get("is_active", False),
            "tags": self.model_data.get("tags", []),
            "system_prompt": self.model_data.get("system_prompt", ""),
            "propriedade_intelectual": config.get("propriedade_intelectual", (
                f"© 2026 {self.model_data.get('creator_name', '@S.V.S - Try Technology')}. "
                "Todos os direitos reservados."
            )),
        }

    def format_self_info(self) -> str:
        """
        Formata as informações do modelo como resposta legível para o chat.
        
        Usado quando o usuário pergunta "qual sua versão", "quem te criou", etc.
        """
        info = self.get_model_info()
        return (
            f"## 🤖 Meu Perfil Completo\n\n"
            f"**Nome:** `{info['name']}`\n"
            f"**Versão:** `{info['version']}`\n"
            f"**Criador:** `{info['creator']}`\n"
            f"**Propriedade:** `{info['propriedade_intelectual']}`\n"
            f"**Data de Criação:** `{info['data_criacao']}`\n"
            f"**Provider:** `{info['base_provider']}`\n"
            f"**Modelo Base:** `{info['base_model']}`\n"
            f"**Temperature:** `{info['temperature']}`\n"
            f"**Max Tokens:** `{'Ilimitado (offline)' if info.get('no_token_limit') else info['max_tokens']}`\n"
            f"**Tags:** `{', '.join(info['tags'])}`\n\n"
            f"Estou aqui para te ajudar! 🚀"
        )

    # =========================================================
    # === UTILIDADES ===
    # =========================================================

    def get_flow_summary(self) -> Dict:
        """
        Retorna resumo do fluxo para exibição rápida.
        Usado pelo BotForge canvas para mostrar estatísticas.
        """
        type_counts = {}
        for node in self.nodes.values():
            ntype = node.get("type", "unknown")
            type_counts[ntype] = type_counts.get(ntype, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_connections": len(self.connections),
            "node_types": type_counts,
            "has_api_connector": any(
                n.get("type") in ("api_connector", "api_entry")
                for n in self.nodes.values()
            ),
            "has_nlp": any(n.get("type") == "nlp" for n in self.nodes.values()),
            "start_node": self.find_start_node(),
        }

    def validate_flow(self) -> List[str]:
        """
        Valida a integridade do fluxo e retorna lista de warnings.
        Útil para QA e debugging.
        """
        warnings = []

        # Check: tem nó de início?
        start = self.find_start_node()
        if not start:
            warnings.append("⚠️ Nenhum nó de início encontrado (recv/api_entry)")

        # Check: nós desconectados (sem entrada nem saída)
        connected = set()
        for conn in self.connections:
            connected.add(conn.get("source"))
            connected.add(conn.get("target"))
        for nid in self.nodes:
            if nid not in connected and nid != start:
                warnings.append(f"⚠️ Nó '{nid}' ({self.nodes[nid].get('label')}) está desconectado")

        # Check: conexões referenciando nós inexistentes
        for conn in self.connections:
            if conn.get("source") not in self.nodes:
                warnings.append(f"⚠️ Conexão referencia nó source '{conn.get('source')}' inexistente")
            if conn.get("target") not in self.nodes:
                warnings.append(f"⚠️ Conexão referencia nó target '{conn.get('target')}' inexistente")

        # Check: NLP sem intents configuradas
        nlp_node = self.get_node_by_type("nlp")
        if nlp_node and not nlp_node.get("intents"):
            warnings.append("ℹ️ Nó NLP não tem 'intents' configuradas — detecção via JSON desabilitada")

        return warnings

    def __repr__(self) -> str:
        summary = self.get_flow_summary()
        return (
            f"FlowEngine("
            f"nodes={summary['total_nodes']}, "
            f"conns={summary['total_connections']}, "
            f"api={'[OK]' if summary['has_api_connector'] else '[--]'}, "
            f"nlp={'[OK]' if summary['has_nlp'] else '[--]'}"
            f")"
        )
