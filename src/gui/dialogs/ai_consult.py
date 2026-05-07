"""
Consulta de IAs / Bots — Estilo BotForge Studio
Cards ricos com suporte a importação/exportação JSON compatível
com o schema ari-milkshaketeria.json (BotForge v6.0)
"""
import json
import os
import traceback
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QScrollArea, QGridLayout,
    QFrame, QMessageBox, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen


class AnimatedSwitch(QWidget):
    """Switch animado estilo iOS/Android para ativar/desativar integração ao Chat Global"""
    toggled = pyqtSignal(bool)

    def __init__(self, checked=True, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 24)
        self._checked = checked
        self._cx = 22 if checked else 2
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._anim = QPropertyAnimation(self, b"cx")
        self._anim.setDuration(200)

    def isChecked(self):
        return self._checked

    def setChecked(self, val):
        self._checked = val
        self._cx = 22 if val else 2
        self.update()

    def getCx(self):
        return self._cx

    def setCx(self, val):
        self._cx = val
        self.update()

    cx = pyqtProperty(int, getCx, setCx)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        end = 22 if self._checked else 2
        self._anim.setStartValue(self._cx)
        self._anim.setEndValue(end)
        self._anim.start()
        self.toggled.emit(self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Track
        if self._checked:
            p.setBrush(QBrush(QColor("#22c55e")))
        else:
            p.setBrush(QBrush(QColor("#4b5563")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, 44, 24, 12, 12)
        # Knob
        p.setBrush(QBrush(QColor("#ffffff")))
        p.drawEllipse(int(self._cx), 2, 20, 20)
        p.end()


class AICard(QFrame):
    """Card rico estilo BotForge Studio — Layout melhorado inspirado no screenshot v1.1.2"""

    def __init__(self, model_data, manager, parent_dialog=None, version_count=1, parent=None):
        super().__init__(parent)
        self.model = model_data
        self.manager = manager
        self.parent_dialog = parent_dialog
        self.version_count = version_count
        self.setFixedSize(300, 300)
        
        card_color = getattr(self.model, '_card_color', '#7c5cfc')
        icon = getattr(self.model, '_card_icon', '🤖')
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }}
            QFrame:hover {{ border-color: #58a6ff; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(14, 12, 14, 10)

        # === Row 1: Icon + Nome + Data + Status Badge ===
        header = QHBoxLayout()
        
        # Ícone com fundo gradiente
        icon_frame = QFrame()
        icon_frame.setFixedSize(42, 42)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_color}, stop:1 #9333ea);
                border-radius: 10px; border: none;
            }}
        """)
        icon_lbl = QLabel(icon, icon_frame)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        icon_lbl.setGeometry(0, 0, 42, 42)
        header.addWidget(icon_frame)

        # Nome + Data
        header_text = QVBoxLayout()
        header_text.setSpacing(0)
        lbl_name = QLabel(self.model.name)
        lbl_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: #f0f6fc; border: none; background: transparent;")
        header_text.addWidget(lbl_name)
        
        date_str = getattr(self.model, 'creation_date', '') or getattr(self.model, 'created_at', '')[:10]
        lbl_date = QLabel(date_str)
        lbl_date.setStyleSheet("color: #8b949e; font-size: 10px; border: none; background: transparent;")
        header_text.addWidget(lbl_date)
        header.addLayout(header_text)
        header.addStretch()

        # Badge ATIVO/INATIVO
        is_active = getattr(self.model, 'is_active', True)
        badge_text = "ATIVO" if is_active else "RASCUNHO"
        badge_bg = "rgba(63,185,80,0.15)" if is_active else "rgba(245,158,11,0.15)"
        badge_color = "#3fb950" if is_active else "#f59e0b"
        lbl_badge = QLabel(badge_text)
        lbl_badge.setStyleSheet(f"""
            color: {badge_color}; background: {badge_bg}; border: none;
            font-size: 9px; font-weight: bold; padding: 3px 10px; border-radius: 10px;
        """)
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(lbl_badge)
        layout.addLayout(header)

        # === Row 2: Canal + Conversas ===
        stats = QHBoxLayout()
        ch = getattr(self.model, '_channel', 'Chat')
        cv = getattr(self.model, '_conversations', 0)
        for label_text, value_text in [("Canal:", ch), ("Conversas:", f"{cv:,}".replace(",", "."))]:
            lbl = QLabel(f'<span style="color:#8b949e;">{label_text}</span> <b style="color:#f0f6fc;">{value_text}</b>')
            lbl.setStyleSheet("font-size: 11px; border: none; background: transparent;")
            stats.addWidget(lbl)
        stats.addStretch()
        layout.addLayout(stats)

        # === Row 3: Switch Ativo + Creator ===
        switch_row = QHBoxLayout()
        self.chat_switch = AnimatedSwitch(checked=is_active)
        self.chat_switch.toggled.connect(self._on_chat_toggle)
        switch_row.addWidget(self.chat_switch)
        lbl_active = QLabel("ATIVO" if is_active else "INATIVO")
        lbl_active.setStyleSheet(f"color: {'#3fb950' if is_active else '#8b949e'}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        switch_row.addWidget(lbl_active)
        switch_row.addStretch()
        layout.addLayout(switch_row)

        # Creator
        creator = getattr(self.model, 'creator_name', 'Desconhecido')
        lbl_creator = QLabel(f"👤 {creator}")
        lbl_creator.setStyleSheet("color: #8b949e; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(lbl_creator)

        # === Row 4: Versões link ===
        ver_label = getattr(self.model, 'version_label', 'v1')
        if self.version_count > 1:
            ver_text = f"🗂️ {self.version_count} versões ({ver_label} ativa)"
        else:
            ver_text = f"📌 {ver_label} — Sem outras versões"
        btn_versions = QPushButton(ver_text)
        btn_versions.setStyleSheet("""
            QPushButton { color: #58a6ff; font-size: 10px; border: none; background: transparent; text-align: left; padding: 2px 0; }
            QPushButton:hover { color: #79c0ff; text-decoration: underline; }
        """)
        btn_versions.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_versions.clicked.connect(self._open_version_repo)
        layout.addWidget(btn_versions)

        layout.addStretch()

        # === Row 5: Botões de Ação (linha completa como no screenshot) ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        btn_style_main = """
            QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 5px 10px; border-radius: 6px; font-size: 10px; }
            QPushButton:hover { background-color: #30363d; border-color: #58a6ff; }
        """
        btn_style_icon = """
            QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 5px; border-radius: 6px; font-size: 12px; }
            QPushButton:hover { background-color: #30363d; border-color: #58a6ff; }
        """
        btn_style_delete = """
            QPushButton { background-color: #21262d; color: #f85149; border: 1px solid #30363d; padding: 5px; border-radius: 6px; font-size: 12px; }
            QPushButton:hover { background-color: #f85149; color: white; }
        """

        btn_edit = QPushButton("📝 Editar")
        btn_edit.setStyleSheet(btn_style_main)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(self._show_details)
        btn_layout.addWidget(btn_edit)

        # Botão Histórico/Versões
        btn_history = QPushButton("🗂️")
        btn_history.setFixedWidth(32)
        btn_history.setToolTip("Repositório de Versões")
        btn_history.setStyleSheet(btn_style_icon)
        btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_history.clicked.connect(self._open_version_repo)
        btn_layout.addWidget(btn_history)

        # Botão Exportar
        btn_export = QPushButton("📤")
        btn_export.setFixedWidth(32)
        btn_export.setToolTip("Exportar JSON")
        btn_export.setStyleSheet(btn_style_icon)
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.clicked.connect(self._export_botforge)
        btn_layout.addWidget(btn_export)

        # Botão Excluir
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedWidth(32)
        btn_delete.setToolTip("Excluir")
        btn_delete.setStyleSheet(btn_style_delete)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(self._delete_model)
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)

    def _open_version_repo(self):
        """Abre o diálogo de Repositório de Versões para este bot."""
        dlg = VersionRepositoryDialog(self.model, self.manager, parent=self)
        dlg.exec()
        # Recarregar cards após alterações
        if self.parent_dialog:
            self.parent_dialog._load_cards()
            # Atualizar combo na MainWindow
            if hasattr(self.parent_dialog, 'main_window') and self.parent_dialog.main_window:
                try:
                    self.parent_dialog.main_window._refresh_ai_combo()
                except Exception:
                    pass

    def _on_chat_toggle(self, checked):
        """Toggle integração ao Chat Global IDE com persistência imediata"""
        self.model.chat_integration = checked
        self.manager.update_model(self.model.id, chat_integration=checked)
        # Atualizar o combo box na MainWindow via referência direta
        if self.parent_dialog and hasattr(self.parent_dialog, 'main_window') and self.parent_dialog.main_window:
            try:
                self.parent_dialog.main_window._refresh_ai_combo()
            except Exception:
                pass

    def _export_botforge(self):
        """Exporta no formato BotForge Studio (schema ari-milkshaketeria.json)"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar IA (BotForge JSON)",
            f"{self.model.name.replace(' ', '_')}.json",
            "JSON (*.json)"
        )
        if not path:
            return
        try:
            export_data = {
                "name": self.model.name,
                "platform": "BotForge Studio",
                "version": "6.0",
                "exportedAt": datetime.now().isoformat() + "Z",
                "cardTypes": {},
                "ari": {
                    "bot": {
                        "id": self.model.id,
                        "name": self.model.name,
                        "status": "active" if getattr(self.model, 'is_active', True) else "inactive",
                        "ch": getattr(self.model, '_channel', 'Chat'),
                        "created": getattr(self.model, 'created_at', '')[:10],
                        "cv": getattr(self.model, '_conversations', 0),
                        "icon": getattr(self.model, '_card_icon', '🤖'),
                        "color": getattr(self.model, '_card_color', '#007acc'),
                        "desc": self.model.description,
                        "base_provider": self.model.base_provider,
                        "base_model": self.model.base_model,
                        "system_prompt": self.model.system_prompt,
                        "temperature": self.model.temperature,
                        "max_tokens": self.model.max_tokens,
                        "creator_name": getattr(self.model, 'creator_name', ''),
                        "tags": getattr(self.model, 'tags', [])
                    },
                    "flow": {
                         "nodes": getattr(self.model, '_flow_nodes', []), 
                         "connections": getattr(self.model, '_flow_conns', []),
                         "groups": getattr(self.model, '_flow_groups', [])
                    },
                    "config": getattr(self.model, '_config', {
                        "botName": self.model.name,
                        "tone": "amigável"
                    })
                }
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "✅ Exportação Concluída",
                                    f"IA '{self.model.name}' exportada no formato BotForge Studio v6.0.\n\nDestino: {path}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erro na Exportação", f"Falha ao exportar:\n{str(e)}")

    def _show_details(self):
        """Abre o BotForge Studio configurado no modo 'Visualizar' com os dados do Web JSON"""
        try:
            from .create_ai_dialog import CreateAIDialog, FlowGroup
            dialog = CreateAIDialog(self.manager, self.parent_dialog)
            
            # Preencher os dados basicos
            dialog.name_input.setText(str(self.model.name))
            dialog.desc_input.setText(str(getattr(self.model, 'description', '')))
            dialog.prompt_input.setPlainText(str(getattr(self.model, 'system_prompt', '')))
            dialog.temp_slider.setValue(int(getattr(self.model, 'temperature', 0.7) * 100))
            
            # Provider / Model matching
            idx_p = dialog.provider_combo.findText(str(getattr(self.model, 'base_provider', 'OpenAI')))
            if idx_p >= 0: dialog.provider_combo.setCurrentIndex(idx_p)
            idx_m = dialog.model_combo.findText(str(getattr(self.model, 'base_model', 'GPT-4omini')))
            if idx_m >= 0: dialog.model_combo.setCurrentIndex(idx_m)
            
            # Se a IA possuir dados brutos do Flow (for importada via BotForge), parsear para a visualização
            if hasattr(self.model, '_flow_nodes'):
                from .create_ai_dialog import FlowNode, FlowConnection
                # 1. Carregar Nodes
                node_map = {}
                for idx, ndata in enumerate(self.model._flow_nodes):
                    # Extração avançada para suportar o formato BotForge Web
                    inner_data = ndata.get('data', {})
                    label_val = inner_data.get('label', ndata.get('label', ndata.get('name', ndata.get('type', 'Node'))))
                    ntype_val = ndata.get('type', inner_data.get('type', 'action'))
                    message_val = inner_data.get('msg', ndata.get('msg', ndata.get('message', '')))
                    
                    # Paleta visual inteligente BotForge para mapeamentos não conhecidos
                    palette = ["#22c55e", "#06b6d4", "#8b5cf6", "#ec4899", "#f97316", "#eab308", "#14b8a6", "#3b82f6", "#f43f5e"]
                    hash_idx = sum(ord(c) for c in ntype_val) % len(palette)
                    ncolor = ndata.get('color', ndata.get('ui', {}).get('color', palette[hash_idx]))
                    
                    # Obter a cor e o ícone do card_types
                    node_icon = ""
                    if hasattr(self.model, '_card_types') and isinstance(self.model._card_types, dict):
                        node_icon = self.model._card_types.get(ntype_val, {}).get("ic", "")
                        
                    if node_icon and not label_val.startswith(node_icon):
                        label_val = f"{node_icon} {label_val}".strip()
                    
                    # Processar as rotas (routes) se existirem no formato web
                    out_labels = None
                    out_colors = None
                    out_keywords = []

                    if "routes" in inner_data and isinstance(inner_data["routes"], list):
                        # Formato Exportação Web BotForge
                        out_labels = [r.get("name", "Rota") for r in inner_data["routes"]]
                        out_colors = [r.get("color", "#58a6ff") for r in inner_data["routes"]]
                        
                        # Extrair Lógica do Christopher (nlpRules => words)
                        try:
                            nlp_rules = bot_data.get("nlpRules", {})
                            for r in inner_data["routes"]:
                                route_name = r.get("name", "").lower()
                                k_words = []
                                # Tenta buscar matching entre o nome da rota e nlpRules
                                for rule_key, rule_data in nlp_rules.items():
                                    if route_name in rule_key.lower() or rule_key.lower() in route_name:
                                        if "w" in rule_data and isinstance(rule_data["w"], list):
                                            k_words.extend(rule_data["w"])
                                out_keywords.append(", ".join(k_words) if k_words else "")
                        except Exception:
                            out_keywords = []
                    else:
                        # Formato Salvo Localmente na IDE (Desktop)
                        l_arr = ndata.get("out_labels", [])
                        c_arr = ndata.get("out_colors", [])
                        if l_arr and isinstance(l_arr, list) and len(l_arr) > 0:
                            out_labels = l_arr
                            out_colors = c_arr
                    
                    # Sprint 31 Fallback Universal: Tentar ler de extra_data.keywords e nlpRules independente da estrutura
                    if not out_keywords or not any(out_keywords):
                        extra = ndata.get('extra_data', inner_data.get('extra_data', {}))
                        if 'keywords' in extra and isinstance(extra['keywords'], list):
                            flat_kws = extra['keywords']
                            num_labels = len(out_labels) if out_labels else 1
                            chunk_size = max(1, len(flat_kws) // num_labels)
                            out_keywords = []
                            for i in range(num_labels):
                                chunk = flat_kws[i*chunk_size : (i+1)*chunk_size]
                                out_keywords.append(", ".join(chunk))
                                
                    if not out_keywords:
                        out_keywords = [""] * len(out_labels or [])
                    
                    # Instanciar FlowNode com IDs maleáveis
                    node_id = str(ndata.get('id', ndata.get('nodeId', ndata.get('cardId', idx))))
                    # Preservar campos extras do JSON (api_config, intents, model_info)
                    # para que o FlowEngine possa lê-los ao salvar
                    extra_fields = {}
                    for ekey in ('api_config', 'intents', 'model_info', 'response_template', 'condition', 'true_next', 'false_next', 'extra_data'):
                        if ekey in ndata:
                            extra_fields[ekey] = ndata[ekey]
                        elif ekey in inner_data:
                            extra_fields[ekey] = inner_data[ekey]
                            
                    # Sprint 31: API Connector e NLP herdam as config globais se não existirem
                    if any(x in str(ntype_val).lower() for x in ["api", "connector", "nlp", "router"]):
                        if 'system_prompt' not in extra_fields:
                            extra_fields['system_prompt'] = getattr(self.model, 'system_prompt', '')
                        if 'temperature' not in extra_fields:
                            extra_fields['temperature'] = getattr(self.model, 'temperature', 0.7)
                        if 'max_tokens' not in extra_fields:
                            extra_fields['max_tokens'] = getattr(self.model, 'max_tokens', 4096)
                        if 'base_provider' not in extra_fields:
                            extra_fields['base_provider'] = getattr(self.model, 'base_provider', '')
                        if 'base_model' not in extra_fields:
                            extra_fields['base_model'] = getattr(self.model, 'base_model', '')
                            
                    node = FlowNode(node_id, str(ntype_val), str(label_val), str(message_val), str(ncolor), out_labels, out_colors, extra_data=extra_fields)
                    node.out_keywords = out_keywords if out_keywords else ndata.get("out_keywords", [])
                    
                    # Suporte topográfico a N schemas (position vs ui vs nativo)
                    pos = ndata.get('position', ndata.get('ui', ndata))
                    dx = float(pos.get('x', 50 + (idx % 4)*200))
                    dy = float(pos.get('y', 50 + (idx // 4)*150))
                    
                    node.setPos(dx, dy)
                    dialog.flow_scene.addItem(node)
                    dialog.flow_nodes.append(node)
                    node_map[node_id] = node
                
                # 2. Carregar Connections
                if hasattr(self.model, '_flow_conns'):
                    for cdata in self.model._flow_conns:
                        src_id = str(cdata.get('source', cdata.get('from', cdata.get('sourceId', cdata.get('f')))))
                        tgt_id = str(cdata.get('target', cdata.get('to', cdata.get('targetId', cdata.get('t')))))
                        
                        # Procurar se a linha sai de uma porta NLP especifica (ex: out_2)
                        src_port = str(cdata.get('source_port', cdata.get('sourceHandle', cdata.get('sourcePort', cdata.get('fromPort', 'out')))))
                        tgt_port = str(cdata.get('target_port', cdata.get('targetHandle', cdata.get('targetPort', cdata.get('toPort', 'in')))))
                        
                        if src_id in node_map and tgt_id in node_map:
                            conn = FlowConnection(node_map[src_id], src_port, node_map[tgt_id], tgt_port)
                            dialog.flow_scene.addItem(conn)
                            node_map[src_id].add_connection(conn)
                            node_map[tgt_id].add_connection(conn)
                            
                # 3. Carregar Sessões (FlowGroups)
                if hasattr(self.model, '_flow_groups') and self.model._flow_groups:
                    from PyQt6.QtCore import QRectF
                    for gdata in self.model._flow_groups:
                        rect = QRectF(0, 0, float(gdata.get('w', 300)), float(gdata.get('h', 200)))
                        group = FlowGroup(rect, gdata.get('title', 'Sessão'), gdata.get('color', '#3fb950'))
                        group.group_id = gdata.get('id', group.group_id)
                        dialog.flow_scene.addItem(group)
                        group.setPos(float(gdata.get('x', 0)), float(gdata.get('y', 0)))
                        
                        # Reconectar nós ao grupo
                        group_node_ids = gdata.get('nodes', [])
                        for nid in group_node_ids:
                            if str(nid) in node_map:
                                group.contained_nodes.append(node_map[str(nid)])

                # Disparar updates visuais apos a inicializacao nativa do Qt (render pipeline)
                def force_update():
                    for item in dialog.flow_scene.items():
                        if isinstance(item, FlowConnection):
                            item.update_path()
                
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(50, force_update)
                
            else:
                dialog.flow_scene.addText("Nenhum fluxo BotForge associado. Crie os cards abaixo.", dialog.font())

            # Change buttons/label if needed
            dialog.setWindowTitle(f"Visualizando BotForge Studio: {self.model.name}")
            
            # Transformar botão Criar IA em Atualizar IA para salvar conexões editadas
            # Encontrar botão pelo texto
            for btn in dialog.findChildren(QPushButton):
                if 'Criar IA' in btn.text():
                    btn.setText('✅ Atualizar IA')
                    btn.disconnect()
                    btn.clicked.connect(lambda: self._save_flow_updates(dialog))
                    break
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao abrir visualizador do modelo:\n{e}")

    def _save_flow_updates(self, dialog):
        """Salva as conexões e nodes editados manualmente de volta no modelo"""
        try:
            from .create_ai_dialog import FlowNode, FlowConnection, FlowGroup
            import uuid
            saved_nodes = []
            saved_conns = []
            saved_groups = []
            
            for item in dialog.flow_scene.items():
                if isinstance(item, FlowNode):
                    node_data = {
                        "id": item.node_id,
                        "type": item.node_type,
                        "label": item.label,
                        "msg": getattr(item, "message", ""),
                        "color": getattr(item, "color", "#fff"),
                        "x": item.pos().x(),
                        "y": item.pos().y(),
                        "out_labels": getattr(item, "out_labels", []),
                        "out_colors": getattr(item, "out_colors", []),
                        "out_keywords": getattr(item, "out_keywords", [])
                    }
                    # Preservar extra_data
                    if hasattr(item, 'extra_data') and item.extra_data:
                        for key, val in item.extra_data.items():
                            if key not in node_data:
                                node_data[key] = val
                        
                        # Extrair identity_ai para _config do modelo
                        is_identity_ai = ("identity_ai" in item.node_type.lower()
                                         or ("identidade" in getattr(item, 'label', '').lower() and "code" not in getattr(item, 'label', '').lower()))
                        if is_identity_ai:
                            if not isinstance(self.model._config, dict):
                                self.model._config = {}
                            for k, v in item.extra_data.items():
                                self.model._config[k] = v
                                if k == "version":
                                    self.model.version = v
                                elif k == "creator":
                                    self.model.creator_name = v
                    saved_nodes.append(node_data)
                    
            for item in dialog.flow_scene.items():
                if isinstance(item, FlowConnection) and item.source_node and item.dest_node:
                    saved_conns.append({
                        "source": item.source_node.node_id,
                        "source_port": item.source_port,
                        "target": item.dest_node.node_id,
                        "target_port": item.dest_port
                    })
                    
            for item in dialog.flow_scene.items():
                if isinstance(item, FlowGroup):
                    saved_groups.append({
                        "id": getattr(item, "group_id", f"group_{uuid.uuid4().hex[:8]}"),
                        "title": item.title,
                        "color": item.color,
                        "x": item.pos().x() + item.rect().x(),
                        "y": item.pos().y() + item.rect().y(),
                        "w": item.rect().width(),
                        "h": item.rect().height(),
                        "nodes": [n.node_id for n in item.contained_nodes if hasattr(n, 'node_id')]
                    })
            
            # Atualizar modelo via manager
            self.model._flow_nodes = saved_nodes
            self.model._flow_conns = saved_conns
            self.model._flow_groups = saved_groups
            self.manager.update_model(self.model.id, 
                                      _flow_nodes=saved_nodes, 
                                      _flow_conns=saved_conns,
                                      _flow_groups=saved_groups)
            
            QMessageBox.information(self, "✅ Atualizado",
                                    f"IA '{self.model.name}' atualizada com sucesso!\n\n"
                                    f"Nodes: {len(saved_nodes)}\n"
                                    f"Conexões: {len(saved_conns)}\n"
                                    f"Sessões: {len(saved_groups)}")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar:\n{e}")

    def _delete_model(self):
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a IA '{self.model.name}'?\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete_model(self.model.id)
            QMessageBox.information(self, "Excluído", f"IA '{self.model.name}' removida.")
            if self.parent_dialog:
                self.parent_dialog._load_cards()


class VersionRepositoryDialog(QDialog):
    """Dialog de Repositório de Versões — Estilo ttkbootstrap/BotForge (Screenshots)"""

    def __init__(self, model, manager, parent=None):
        super().__init__(parent)
        self.model = model
        self.manager = manager
        self.setWindowTitle("🗂️ Repositório de Versões")
        self.setMinimumSize(550, 500)
        self.setStyleSheet("""
            QDialog { background-color: #161b22; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            QPushButton { font-family: 'Segoe UI', sans-serif; }
            QLabel { font-family: 'Segoe UI', sans-serif; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        # === Header: Ícone + Nome + Contagem ===
        header = QHBoxLayout()
        icon_lbl = QLabel("🗂️")
        icon_lbl.setStyleSheet("font-size: 22px;")
        header.addWidget(icon_lbl)
        title = QLabel("Repositório de Versões")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #f0f6fc;")
        header.addWidget(title)
        header.addStretch()
        btn_close_x = QPushButton("✕")
        btn_close_x.setFixedSize(28, 28)
        btn_close_x.setStyleSheet("""
            QPushButton { background: transparent; color: #8b949e; font-size: 16px; border: none; border-radius: 14px; }
            QPushButton:hover { background: #30363d; color: #f0f6fc; }
        """)
        btn_close_x.clicked.connect(self.accept)
        header.addWidget(btn_close_x)
        layout.addLayout(header)

        # === Bot Info ===
        bot_info = QHBoxLayout()
        icon_frame = QFrame()
        icon_frame.setFixedSize(36, 36)
        card_color = getattr(self.model, '_card_color', '#7c5cfc')
        icon_frame.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_color}, stop:1 #9333ea);
                      border-radius: 8px; border: none; }}
        """)
        icon_char = QLabel(getattr(self.model, '_card_icon', '🤖'), icon_frame)
        icon_char.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_char.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        icon_char.setGeometry(0, 0, 36, 36)
        bot_info.addWidget(icon_frame)
        
        info_text = QVBoxLayout()
        info_text.setSpacing(0)
        lbl_bot_name = QLabel(f"<b>{self.model.name}</b>")
        lbl_bot_name.setStyleSheet("color: #f0f6fc; font-size: 13px;")
        info_text.addWidget(lbl_bot_name)
        
        versions = self.manager.get_version_group(self.model.name)
        lbl_count = QLabel(f"{len(versions)} versão(ões) no Repositório")
        lbl_count.setStyleSheet("color: #8b949e; font-size: 10px;")
        info_text.addWidget(lbl_count)
        bot_info.addLayout(info_text)
        bot_info.addStretch()
        layout.addLayout(bot_info)

        # === Action Buttons: Salvar + Importar ===
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        
        btn_save = QPushButton("+ Salvar Versão Atual")
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c5cfc, stop:1 #c840e9);
                color: white; font-weight: bold; font-size: 12px;
                border: none; border-radius: 6px; padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d4de6, stop:1 #b835d4);
            }
        """)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._save_current_version)
        action_row.addWidget(btn_save, 2)

        btn_import = QPushButton("📥 Importar como Versão")
        btn_import.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #c9d1d9; font-size: 11px;
                border: 1px solid #30363d; border-radius: 6px; padding: 10px 16px;
            }
            QPushButton:hover { border-color: #58a6ff; background: #30363d; }
        """)
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.clicked.connect(self._import_as_version)
        action_row.addWidget(btn_import, 1)
        layout.addLayout(action_row)

        # === Version List (Scroll) ===
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.setContentsMargins(0, 4, 0, 4)
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)

        self._populate_versions()

        # === Footer: Fechar ===
        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("""
            QPushButton { background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                          border-radius: 6px; padding: 8px 24px; font-size: 12px; }
            QPushButton:hover { background: #30363d; }
        """)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def _populate_versions(self):
        # Limpar
        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        versions = self.manager.get_version_group(self.model.name)
        
        if not versions:
            empty = QLabel("📭 Nenhuma versão salva.\nClique \"Salvar Versão Atual\" para começar.")
            empty.setStyleSheet("color: #8b949e; font-size: 12px; padding: 30px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(empty)
        else:
            for ver in versions:
                row = QFrame()
                is_active = ver.is_active
                border_color = "#3fb950" if is_active else "#30363d"
                row.setStyleSheet(f"""
                    QFrame {{ background-color: #0d1117; border: 1px solid {border_color}; border-radius: 8px; }}
                    QFrame:hover {{ border-color: #58a6ff; }}
                """)
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(12, 8, 12, 8)

                # Dot indicator
                dot_color = "#3fb950" if is_active else "#4b5563"
                dot = QLabel("●")
                dot.setStyleSheet(f"color: {dot_color}; font-size: 14px; border: none; background: transparent;")
                row_layout.addWidget(dot)

                # Info
                info = QVBoxLayout()
                info.setSpacing(0)
                ver_label = getattr(ver, 'version_label', 'v1')
                lbl_ver = QLabel(f"<b>{ver_label}</b> ({ver.name})")
                lbl_ver.setStyleSheet("color: #f0f6fc; font-size: 12px; border: none; background: transparent;")
                info.addWidget(lbl_ver)
                
                date_str = ver.updated_at[:16].replace("T", " ") if ver.updated_at else ""
                lbl_date = QLabel(date_str)
                lbl_date.setStyleSheet("color: #8b949e; font-size: 10px; border: none; background: transparent;")
                info.addWidget(lbl_date)
                row_layout.addLayout(info, 1)

                if is_active:
                    badge = QLabel("ATIVA")
                    badge.setStyleSheet("""
                        color: #3fb950; background: rgba(63,185,80,0.15); border: none;
                        font-size: 10px; font-weight: bold; padding: 3px 12px; border-radius: 8px;
                    """)
                    row_layout.addWidget(badge)
                else:
                    btn_activate = QPushButton("Ativar")
                    btn_activate.setStyleSheet("""
                        QPushButton { background: #1f6feb; color: white; border: none; border-radius: 4px; padding: 4px 12px; font-size: 10px; }
                        QPushButton:hover { background: #388bfd; }
                    """)
                    btn_activate.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn_activate.clicked.connect(lambda _, vid=ver.id: self._activate_version(vid))
                    row_layout.addWidget(btn_activate)

                # Edit Info Button
                btn_edit = QPushButton("✏️")
                btn_edit.setFixedWidth(28)
                btn_edit.setStyleSheet("""
                    QPushButton { background: transparent; color: #f0f6fc; border: none; font-size: 12px; border-radius: 4px; }
                    QPushButton:hover { background: rgba(88,166,255,0.15); }
                """)
                btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_edit.clicked.connect(lambda _, m=ver: self._edit_version_info(m))
                row_layout.addWidget(btn_edit)

                if not is_active:
                    btn_del = QPushButton("🗑️")
                    btn_del.setFixedWidth(28)
                    btn_del.setStyleSheet("""
                        QPushButton { background: transparent; color: #f85149; border: none; font-size: 12px; border-radius: 4px; }
                        QPushButton:hover { background: rgba(248,81,73,0.15); }
                    """)
                    btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn_del.clicked.connect(lambda _, vid=ver.id: self._delete_version(vid))
                    row_layout.addWidget(btn_del)

                self.scroll_layout.addWidget(row)

        self.scroll_layout.addStretch()

    def _save_current_version(self):
        active = self.manager.get_active_version(self.model.name)
        if not active:
            QMessageBox.warning(self, "Aviso", "Nenhum modelo ativo encontrado.")
            return
        clone = self.manager.save_current_as_version(active.id)
        if clone:
            QMessageBox.information(self, "✅ Versão Salva",
                                    f"Versão '{clone.version_label}' salva como snapshot.\n"
                                    f"A versão original permanece ativa.")
            self._populate_versions()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao salvar versão.")

    def _import_as_version(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar JSON como nova versão", "",
            "JSON Files (*.json);;AICA Files (*.aica);;Todos (*)"
        )
        if not path:
            return
        model = self.manager.import_as_version(self.model.name, path)
        if model:
            QMessageBox.information(self, "✅ Importado",
                                    f"Importado como {model.version_label} ({model.name})")
            self._populate_versions()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao importar. Verifique o formato do JSON.")

    def _activate_version(self, model_id):
        if self.manager.set_active_version(model_id):
            self._populate_versions()
            QMessageBox.information(self, "✅ Ativada", "Versão ativada com sucesso! Ela será usada como padrão agora.")

    def _delete_version(self, model_id):
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            "Excluir esta versão? Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.manager, 'delete_model'):
                self.manager.delete_model(model_id)
            else:
                self.manager.delete_version(model_id)
            self._populate_versions()
            
    def _edit_version_info(self, model_obj):
        new_label, ok = QInputDialog.getText(
            self, "✏️ Editar Informação", 
            "Novo nome/rótulo para esta versão:", 
            text=getattr(model_obj, 'version_label', '')
        )
        if ok and new_label.strip():
            model_obj.version_label = new_label.strip()
            self.manager._save_models()
            self._populate_versions()


class AIConsultWindow(QDialog):
    """Janela de Consulta de IAs/Bots — Grid de Cards estilo BotForge Studio"""

    def __init__(self, manager, parent=None, main_window=None):
        super().__init__(parent)
        self.manager = manager
        self.main_window = main_window  # Referência direta à MainWindow
        self.setWindowTitle("📋 Consulta de IAs — BotForge Studio")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #cccccc; }
        """)
        self._setup_ui()
        self._load_cards()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # === Header ===
        header = QHBoxLayout()
        title = QLabel("IAs / Bots Disponíveis")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header.addWidget(title)

        subtitle = QLabel("Gerencie, importe e exporte seus assistentes de IA")
        subtitle.setStyleSheet("color: #858585; font-size: 11px;")
        header.addWidget(subtitle)
        header.addStretch()

        btn_import = QPushButton("⬇️ Importar JSON")
        btn_import.setStyleSheet("""
            QPushButton { background-color: #007acc; color: white; padding: 8px 18px; border-radius: 4px; font-weight: bold; border: none; font-size: 12px; }
            QPushButton:hover { background-color: #005a9e; }
        """)
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.clicked.connect(self._import_from_json)
        header.addWidget(btn_import)

        btn_new = QPushButton("➕ Criar Nova IA")
        btn_new.setStyleSheet("""
            QPushButton { background-color: #2d2d30; color: white; padding: 8px 18px; border-radius: 4px; border: 1px solid #424242; font-size: 12px; }
            QPushButton:hover { background-color: #333333; }
        """)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self._open_create_dialog)
        header.addWidget(btn_new)

        layout.addLayout(header)

        # === Separator ===
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #424242;")
        layout.addWidget(sep)

        # === Área de Cards (Scroll + Grid) ===
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background-color: #1e1e1e;")

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: #1e1e1e;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)

        # === Log area ===
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(80)
        self.log_area.setStyleSheet("background-color: #181818; color: #4ec9b0; font-family: Consolas; font-size: 11px; border: 1px solid #424242;")
        self.log_area.setPlaceholderText("Log de operações...")
        layout.addWidget(self.log_area)

    def _log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"INFO": "#4ec9b0", "WARN": "#dcdcaa", "ERROR": "#f44747", "OK": "#66bb6a"}
        color = colors.get(level, "#cccccc")
        self.log_area.append(f'<span style="color:{color}">[{timestamp}] [{level}] {msg}</span>')

    def _load_cards(self):
        """Carrega cards agrupados por bot (1 card por grupo, versão ativa)"""
        # Limpar grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        unique_bots = self.manager.get_unique_bots() if self.manager else []
        
        if not unique_bots:
            lbl = QLabel("Nenhuma IA/Bot registrada. Use 'Importar JSON' ou 'Criar Nova IA' para começar.")
            lbl.setStyleSheet("color: #858585; font-size: 13px; padding: 40px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(lbl, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
            self._log(f"Nenhuma IA encontrada no storage.", "WARN")
            return

        row, col = 0, 0
        for bot_info in unique_bots:
            model = bot_info['active_model']
            ver_count = bot_info['version_count']
            card = AICard(model, self.manager, parent_dialog=self, version_count=ver_count)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 2:  # 3 cards por linha
                col = 0
                row += 1

        self._log(f"{len(unique_bots)} bot(s) carregado(s) com sucesso.", "OK")

    def _import_from_json(self):
        """Importa IA de arquivo JSON (BotForge ou .aica)"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar IA (BotForge JSON ou .aica)", "",
            "JSON Files (*.json);;AICA Files (*.aica);;Todos (*)"
        )
        if not path:
            return

        self._log(f"Abrindo arquivo: {os.path.basename(path)}")

        # Copiar JSON original para pasta templates-modelos (backup físico visível)
        if hasattr(self.manager, 'import_json_file'):
            copied = self.manager.import_json_file(path)
            if copied:
                self._log(f"JSON copiado para templates-modelos: {os.path.basename(copied)}", "OK")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                self._log("Arquivo vazio!", "ERROR")
                QMessageBox.warning(self, "Arquivo Vazio", "O arquivo selecionado está vazio.")
                return

            try:
                # Remove possível BOM e espaços
                content = content.strip()
                if content.startswith('\ufeff'):
                    content = content[1:]
                    
                data = json.loads(content)
            except json.JSONDecodeError as e:
                # Fallback: tentar recuperar ignorando garbage (Extra data) no fim do arquivo
                try:
                    self._log(f"Aviso no parsing: {str(e)}. Tentando raw_decode...", "WARN")
                    decoder = json.JSONDecoder()
                    data, _ = decoder.raw_decode(content)
                    self._log("JSON recuperado com sucesso ignorando dados extras no final.", "OK")
                except Exception as raw_e:
                    self._log(f"JSON inválido (falha irrecuperável): {str(e)}", "ERROR")
                    QMessageBox.warning(self, "JSON Inválido",
                                        f"O arquivo não contém JSON válido.\n\nDetalhes: {str(e)}")
                    return

            # ============ TRATAMENTO DE JSON ARRAY (Opção B / Múltiplos Elementos) ============
            if isinstance(data, list):
                if len(data) == 0:
                    self._log("JSON é um array vazio!", "ERROR")
                    QMessageBox.warning(self, "Array Vazio", "O arquivo contém um array JSON vazio.")
                    return
                elif len(data) > 1:
                    self._log(f"JSON é um array com {len(data)} elementos. Usando o primeiro elemento.", "WARN")
                
                # Extrai o primeiro elemento (assume que é o modelo desejado)
                first_element = data[0]
                if not isinstance(first_element, dict):
                    self._log("O primeiro elemento do array não é um objeto JSON válido.", "ERROR")
                    QMessageBox.warning(self, "Formato Inválido", "O array JSON contém elementos que não são objetos.")
                    return
                
                data = first_element
                self._log(f"JSON array convertido para objeto. Elementos no array: {len(data)}", "INFO")

            self._log(f"JSON parseado. Formato detectado: {'BotForge' if isinstance(data, dict) and 'ari' in data else 'Padrão'}")

            # ============ SCHEMA BOTFORGE (ari-milkshaketeria.json) ============
            if isinstance(data, dict) and "ari" in data and isinstance(data["ari"], dict) and "bot" in data["ari"]:
                bot = data["ari"]["bot"]
                
                # Handle bot as array (Option B) - take first valid dict element
                if isinstance(bot, list):
                    if len(bot) > 0 and isinstance(bot[0], dict):
                        bot = bot[0]
                        self._log(f"Schema BotForge detectado (formato array). Usando primeiro elemento: '{bot.get('name', '?')}'", "INFO")
                    else:
                        self._log("BotForge: 'bot' é um array inválido ou vazio", "ERROR")
                        bot = None
                else:
                    self._log(f"Schema BotForge detectado. Bot: '{bot.get('name', '?')}' | Platform: {data.get('platform', '?')} v{data.get('version', '?')}", "INFO")
                
                if bot and isinstance(bot, dict):
                    # Extrair dados usando schema real do BotForge
                    bot_name = bot.get("name", "IA Importada")
                    bot_desc = bot.get("desc", "Bot importado via BotForge Studio")
                    bot_provider = bot.get("base_provider", "openai")
                    bot_model = bot.get("base_model", "gpt-4o")
                    bot_prompt = bot.get("system_prompt", bot_desc)
                    bot_temp = bot.get("temperature", 0.7)
                    bot_tokens = bot.get("max_tokens", 4096)
                    bot_tags = bot.get("tags", [])
                    bot_creator = bot.get("creator_name", data.get("name", "BotForge"))
                    bot_icon = bot.get("icon", "🤖")
                    bot_color = bot.get("color", "#007acc")
                    bot_channel = bot.get("ch", "Chat")
                    bot_cv = bot.get("cv", 0)

                    # Se não há system_prompt explicito, construir um a partir dos dados
                    if not bot.get("system_prompt"):
                        config = data["ari"].get("config", {})
                        greeting = config.get("greeting", "")
                        tone = config.get("tone", "amigável")
                        bot_name_cfg = config.get("botName", bot_name)
                        bot_prompt = (
                            f"Você é {bot_name_cfg}, um assistente virtual de tom {tone}. "
                            f"{greeting} {bot_desc}. "
                            f"Você atende pelo canal {bot_channel}."
                        )
                        self._log(f"System prompt gerado automaticamente a partir do config.", "INFO")

                    try:
                        model = self.manager.create_model(
                            name=bot_name,
                            description=bot_desc,
                            base_provider=bot_provider,
                            base_model=bot_model,
                            system_prompt=bot_prompt,
                            temperature=bot_temp,
                            max_tokens=bot_tokens,
                            tags=bot_tags,
                            creator_name=bot_creator,
                        )
                        # Armazenar metadados extras para o card
                        model._card_icon = bot_icon
                        model._card_color = bot_color
                        model._channel = bot_channel
                        model._conversations = bot_cv

                        # Capturar bloco config do ari (versão, criador, tom, propriedade)
                        ari_config = data["ari"].get("config", {})
                        if ari_config:
                            model._config = ari_config
                            # Sobrescrever version com a do config (prioridade)
                            if ari_config.get("version"):
                                model.version = ari_config["version"]
                            if ari_config.get("creator"):
                                model.creator_name = ari_config["creator"]

                        # Contar nodes e connections
                        flow = data["ari"].get("flow", {})
                        if not flow:
                            flow = data.get("ari", {}).get("flow", {})
                        
                        n_nodes_data = flow.get("nodes", [])
                        n_conns_data = flow.get("connections", [])
                        n_groups_data = flow.get("groups", [])
                        n_nodes = len(n_nodes_data)
                        n_conns = len(n_conns_data)
                        n_groups = len(n_groups_data)
                        
                        # Salva no modelo para renderização no FlowScene
                        model._flow_nodes = n_nodes_data
                        model._flow_conns = n_conns_data
                        model._flow_groups = n_groups_data
                        
                        # Força save para memória local
                        self.manager._save_models()

                        self._log(f"✅ IA '{bot_name}' importada com sucesso! (Nodes: {n_nodes}, Connections: {n_conns}, Sessões: {n_groups})", "OK")
                        QMessageBox.information(self, "✅ Importação BotForge",
                                                f"IA '{bot_name}' importada com sucesso!\n\n"
                                                f"🏢 Provider: {bot_provider}\n"
                                                f"📡 Canal: {bot_channel}\n"
                                                f"💬 Conversas: {bot_cv}\n"
                                                f"🔗 Nodes no fluxo: {n_nodes}\n"
                                                f"🔗 Conexões: {n_conns}\n"
                                                f"📦 Sessões: {n_groups}")
                    except Exception as create_err:
                        self._log(f"Erro ao criar modelo: {str(create_err)}", "ERROR")
                        QMessageBox.critical(self, "Erro ao Criar", f"Falha ao registrar IA:\n{str(create_err)}")
                        return

            # ============ FORMATO TEMPLATE INTERNO (AI Code Assistant) ============
            elif isinstance(data, dict) and "_model_data" in data and "_model_id" in data:
                self._log("Formato template interno (AI Code Assistant) detectado.", "INFO")
                model_data = data.get("_model_data", {})
                if not isinstance(model_data, dict):
                    self._log("Template interno: _model_data inválido.", "ERROR")
                    QMessageBox.warning(self, "Formato Inválido", "Dados do modelo ausentes ou inválidos no template interno.")
                    return
                
                try:
                    # Extrair dados do _model_data
                    model_name = model_data.get("name", "Modelo Importado")
                    model_desc = model_data.get("description", "")
                    model_provider = model_data.get("base_provider", "offline")
                    model_base = model_data.get("base_model", "richie-v1")
                    model_prompt = model_data.get("system_prompt", "")
                    model_temp = model_data.get("temperature", 0.7)
                    model_tokens = model_data.get("max_tokens", 4096)
                    model_tags = model_data.get("tags", [])
                    model_creator = model_data.get("creator_name", "Desconhecido")
                    
                    # Criar modelo via manager
                    model = self.manager.create_model(
                        name=model_name,
                        description=model_desc,
                        base_provider=model_provider,
                        base_model=model_base,
                        system_prompt=model_prompt,
                        temperature=model_temp,
                        max_tokens=model_tokens,
                        tags=model_tags,
                        creator_name=model_creator,
                    )
                    
                    # Restaurar campos extras do template
                    model._flow_nodes = model_data.get("_flow_nodes", [])
                    model._flow_conns = model_data.get("_flow_conns", [])
                    model._card_icon = model_data.get("_card_icon", "🤖")
                    model._card_color = model_data.get("_card_color", "#007acc")
                    model._channel = model_data.get("_channel", "Chat")
                    model._conversations = model_data.get("_conversations", 0)
                    
                    # Salvar alterações
                    self.manager._save_models()
                    
                    self._log(f"✅ Template interno '{model_name}' importado com sucesso!", "OK")
                    QMessageBox.information(self, "✅ Importação OK", 
                                            f"Modelo '{model_name}' importado do formato interno!\n\n"
                                            f"🏢 Provider: {model_provider}\n"
                                            f"📡 Canal: {model._channel}")
                    
                except Exception as e:
                    self._log(f"Erro ao importar template interno: {str(e)}", "ERROR")
                    QMessageBox.critical(self, "Erro na Importação", f"Falha ao importar template interno:\n{str(e)}")
                    return

            # ============ FORMATO .AICA (NATIVO) ============
            elif isinstance(data, dict) and data.get("format") == "aica":
                self._log("Formato .aica nativo detectado.")
                try:
                    model = self.manager.import_model(path)
                    if model:
                        self._log(f"✅ IA '{model.name}' importada (.aica).", "OK")
                        QMessageBox.information(self, "Importação OK", f"IA '{model.name}' importada do formato nativo .aica!")
                    else:
                        self._log("import_model retornou None.", "ERROR")
                        QMessageBox.warning(self, "Aviso", "Formato .aica reconhecido mas modelo retornou vazio.")
                except Exception as e:
                    self._log(f"Erro .aica: {str(e)}", "ERROR")
                    QMessageBox.critical(self, "Erro", f"Falha na importação .aica:\n{str(e)}")
                    return

            # ============ FORMATO WEB BOTFORGE (exportedAt + cardTypes + nomeDoBot) ============
            elif isinstance(data, dict) and ("exportedAt" in data or "cardTypes" in data):
                self._log("BotForge Web export detectado. Tentando import inteligente...")
                bot_name_orig = data.get("name", "IA Importada (Web)")
                
                # ============ DIALOG DE IMPORTAÇÃO — NOME + ATUALIZADO POR ============
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
                import_dlg = QDialog(self)
                import_dlg.setWindowTitle("📥 Importar Bot — Configuração")
                import_dlg.setFixedSize(420, 220)
                import_dlg.setStyleSheet("background-color: #161b22; color: #c9d1d9; border-radius: 8px;")
                dlg_layout = QVBoxLayout(import_dlg)
                dlg_layout.setSpacing(12)
                dlg_layout.setContentsMargins(20, 20, 20, 20)
                
                dlg_layout.addWidget(QLabel("📦 Nome do Bot (editável):"))
                name_input = QLineEdit(bot_name_orig)
                name_input.setStyleSheet("background-color: #0d1117; color: #c9d1d9; padding: 8px; border: 1px solid #30363d; border-radius: 4px; font-size: 13px;")
                dlg_layout.addWidget(name_input)
                
                dlg_layout.addWidget(QLabel("👤 Atualizado por:"))
                updater_input = QLineEdit("@S.V.S - Try Technology")
                updater_input.setStyleSheet("background-color: #0d1117; color: #c9d1d9; padding: 8px; border: 1px solid #30363d; border-radius: 4px; font-size: 13px;")
                dlg_layout.addWidget(updater_input)
                
                btn_row = QHBoxLayout()
                btn_import_ok = QPushButton("✅ Importar")
                btn_import_ok.setStyleSheet("background-color: #238636; color: white; padding: 8px 16px; border-radius: 4px; border: none; font-weight: bold;")
                btn_import_ok.clicked.connect(import_dlg.accept)
                btn_import_cancel = QPushButton("Cancelar")
                btn_import_cancel.setStyleSheet("background-color: #21262d; color: #8b949e; padding: 8px 16px; border-radius: 4px; border: 1px solid #30363d;")
                btn_import_cancel.clicked.connect(import_dlg.reject)
                btn_row.addWidget(btn_import_ok)
                btn_row.addWidget(btn_import_cancel)
                dlg_layout.addLayout(btn_row)
                
                if import_dlg.exec() != QDialog.DialogCode.Accepted:
                    self._log("Importação cancelada pelo usuário.", "WARN")
                    return
                
                bot_name = name_input.text().strip() or bot_name_orig
                import_updated_by = updater_input.text().strip()
                
                # ============ CHECK DUPLICATA → REPOSITÓRIO DE VERSÕES ============
                existing_versions = self.manager.get_version_group(bot_name)
                if existing_versions:
                    ver_count = len(existing_versions)
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("⚠️ Bot já existente")
                    msg_box.setText(f"O bot \"{bot_name}\" já existe com {ver_count} versão(ões) no repositório.")
                    msg_box.setInformativeText("O que deseja fazer?")
                    btn_version = msg_box.addButton("Importar como Nova Versão", QMessageBox.ButtonRole.AcceptRole)
                    btn_replace = msg_box.addButton("Substituir Versão Ativa", QMessageBox.ButtonRole.DestructiveRole)
                    btn_cancel = msg_box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
                    msg_box.exec()
                    
                    clicked = msg_box.clickedButton()
                    if clicked == btn_cancel:
                        self._log("Importação cancelada pelo usuário.", "WARN")
                        return
                    elif clicked == btn_version:
                        # Importar como versão: será tratado como nova versão
                        result = self.manager.import_as_version(bot_name, path)
                        if result:
                            self._log(f"✅ Importado como {result.version_label} no repositório de '{bot_name}'!", "OK")
                            QMessageBox.information(self, "✅ Nova Versão", 
                                                    f"Importado como {result.version_label} ({bot_name})")
                            self._load_cards()
                            return
                        else:
                            self._log("Falha ao importar como versão.", "ERROR")
                            return
                    elif clicked == btn_replace:
                        active = self.manager.get_active_version(bot_name)
                        if active:
                            self.manager.delete_model(active.id)
                
                platform = data.get("platform", "botforge-web")
                version = data.get("version", "?")
                card_types = data.get("cardTypes", [])
                
                # Buscar a chave que contém os dados do bot (é uma dict com nodes/connections)
                bot_data = None
                bot_key = None
                for key, val in data.items():
                    if key in ("name", "platform", "version", "exportedAt", "cardTypes"):
                        continue
                    if isinstance(val, dict):
                        # Esta chave parece conter dados de fluxo do bot
                        bot_data = val
                        bot_key = key
                        break
                
                if not bot_data:
                    # Tentar extrair nodes diretamente do cardTypes como fallback
                    bot_data = {"nodes": card_types, "connections": []}
                    bot_key = bot_name
                
                # Extrair nodes e connections do bot_data
                nodes = []
                connections = []
                
                if isinstance(bot_data, dict):
                    # Percorrer os dados do bot buscando nodes/connections
                    nodes = bot_data.get("nodes", bot_data.get("cards", []))
                    connections = bot_data.get("connections", bot_data.get("conns", bot_data.get("edges", [])))
                    
                    # Se não encontrou diretamente, buscar recursivamente
                    if not nodes:
                        for k, v in bot_data.items():
                            if isinstance(v, list) and len(v) > 0:
                                if isinstance(v[0], dict):
                                    nodes = v
                                    break
                            elif isinstance(v, dict):
                                nodes = v.get("nodes", v.get("cards", []))
                                connections = v.get("connections", v.get("conns", []))
                                if nodes:
                                    break
                
                # BUGFIX 2: Muitas vezes as connections no BotForge Web vêm embutidas DENTRO dos nodes
                if not connections and nodes and isinstance(nodes, list):
                    for node in nodes:
                        if isinstance(node, dict) and "outputs" in node:
                            outputs_dict = node.get("outputs", {})
                            if isinstance(outputs_dict, dict):
                                for port_id, port_data in outputs_dict.items():
                                    if isinstance(port_data, dict) and "connections" in port_data:
                                        node_conns = port_data.get("connections", [])
                                        for c in node_conns:
                                            # Formato: { "node": "destino_id", "output": "input_id" }
                                            connections.append({
                                                "source": node.get("id"),
                                                "source_port": port_id,
                                                "target": c.get("node"),
                                                "target_port": c.get("output", "in")
                                            })
                
                n_nodes = len(nodes) if isinstance(nodes, list) else 0
                n_conns = len(connections) if isinstance(connections, list) else 0
                n_card_types = len(card_types)
                
                self._log(f"Bot: '{bot_key}' | Platform: {platform} v{version} | CardTypes: {n_card_types} | Nodes: {n_nodes} | Connections: {n_conns}")
                
                # Construir system prompt a partir do que temos
                bot_desc = f"Bot '{bot_name}' importado do BotForge Web ({platform} v{version})"
                bot_prompt = f"Você é {bot_name}, um assistente virtual."
                
                # Tentar extrair config/prompt dos dados
                if isinstance(bot_data, dict):
                    config = bot_data.get("config", {})
                    if isinstance(config, dict):
                        greeting = config.get("greeting", config.get("welcomeMessage", ""))
                        tone = config.get("tone", "amigável")
                        if greeting:
                            bot_prompt = f"Você é {bot_name}, um assistente virtual de tom {tone}. {greeting}"
                    # Buscar system_prompt direto
                    sp = bot_data.get("system_prompt", bot_data.get("systemPrompt", ""))
                    if sp:
                        bot_prompt = sp
                
                try:
                    model = self.manager.create_model(
                        name=bot_name,
                        description=bot_desc,
                        base_provider="openai",
                        base_model="gpt-4o",
                        system_prompt=bot_prompt,
                        temperature=0.7,
                        max_tokens=4096,
                        tags=["botforge-web", "imported"],
                        creator_name=data.get("name", "BotForge Web"),
                    )
                    model._card_icon = "🌐"
                    model._card_color = "#58a6ff"
                    model._web_data = bot_data  # Preservar dados originais
                    model._flow_nodes = nodes
                    model._flow_conns = connections
                    model._card_types = card_types
                    
                    # Metadados de atualização (created_at e creator_name são IMUTÁVEIS)
                    model.updated_by = import_updated_by
                    model.last_updated_at = datetime.now().isoformat()
                    model.update_logs = [{
                        "date": datetime.now().isoformat(),
                        "by": import_updated_by,
                        "desc": f"Importação inicial do BotForge Web ({platform} v{version})"
                    }]
                    
                    self.manager.save_models() # Salvar explicitamente a nova IA na base local (persistência)
                    
                    self._log(f"✅ IA '{bot_name}' importada do BotForge Web!", "OK")
                    QMessageBox.information(self, "✅ Importação BotForge Web",
                                            f"IA '{bot_name}' importada com sucesso!\n\n"
                                            f"📦 Platform: {platform} v{version}\n"
                                            f"📑 CardTypes: {n_card_types}\n"
                                            f"🔗 Nodes: {n_nodes}\n"
                                            f"🔗 Conexões: {n_conns}\n\n"
                                            f"Os dados de fluxo foram preservados para visualização.")
                except Exception as create_err:
                    self._log(f"Erro ao criar modelo web: {str(create_err)}", "ERROR")
                    QMessageBox.critical(self, "Erro ao Criar", f"Falha ao registrar IA web:\n{str(create_err)}")
                    return

            else:
                self._log(f"Formato não reconhecido. Chaves: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}", "ERROR")
                QMessageBox.warning(self, "Formato Desconhecido",
                                    f"O arquivo não segue o schema do BotForge (ari.bot) nem o formato .aica.\n\n"
                                    f"Chaves encontradas: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                return

            self._load_cards()
            
            # Forçar o refresh na MainWindow caso importação tenha sucesso
            if hasattr(self, 'main_window') and self.main_window:
                try:
                    self.main_window._refresh_ai_combo()
                except Exception:
                    pass

        except IOError as e:
            self._log(f"I/O Error: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Erro de Leitura", f"Impossível ler o arquivo:\n{str(e)}")
        except Exception as e:
            self._log(f"Erro inesperado: {traceback.format_exc()}", "ERROR")
            QMessageBox.critical(self, "Erro Crítico", f"Falha inesperada:\n{str(e)}")

    def _open_create_dialog(self):
        """Abre o dialog de criação de IA"""
        try:
            from .create_ai_dialog import CreateAIDialog
            dialog = CreateAIDialog(self.manager, self)
            dialog.ai_created.connect(lambda model: (
                self._log(f"✅ IA '{model.name}' criada com sucesso!", "OK"),
                self._load_cards()
            ))
            dialog.exec()
        except Exception as e:
            self._log(f"Erro ao abrir CreateAIDialog: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Erro", f"Falha ao abrir formulário de criação:\n{str(e)}")
