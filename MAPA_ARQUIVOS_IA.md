# MAPA DE ARQUIVOS - INTEGRACAO IA

## Arquivos Criados/Modificados

### CORE (Logica Central)
```
src/core/
├── __init__.py           # [MODIFICADO] Exporta novos modulos
├── token_optimizer.py    # [NOVO] Otimizacao de tokens (60-80% economia)
├── response_cache.py     # [NOVO] Cache de respostas (20-30% economia)
├── ai_manager.py         # [NOVO] Gerenciador central de IAs
├── custom_ai_manager.py  # [NOVO] Gerenciador de IAs customizadas
└── project_manager.py    # [EXISTENTE] Sem alteracoes
```

### PROVIDERS (Provedores de IA)
```
src/providers/
├── __init__.py           # [MODIFICADO] Factory get_provider()
├── base_provider.py      # [EXISTENTE] Interface base
├── openai_provider.py    # [EXISTENTE] GPT-4, GPT-3.5
├── anthropic_provider.py # [NOVO] Claude 3.5, Claude 3
└── deepseek_provider.py  # [NOVO] DeepSeek Coder (mais barato)
```

### GUI (Interface)
```
src/gui/
├── main_window.py        # [MODIFICADO] Integrado com IA + Performance
├── dialogs/
│   ├── __init__.py       # [NOVO]
│   └── create_ai_dialog.py # [NOVO] Dialog criar/gerenciar IAs
└── components.py         # [VAZIO] Para implementar futuramente
```

### MODELS (IAs Customizadas)
```
models/
└── custom/               # [NOVO] Armazena IAs criadas pelo usuario
    └── index.json        # Indice de modelos
```

### CONFIG (Configuracao)
```
config/
├── settings.yaml         # [EXISTENTE] Configuracoes gerais
└── providers.yaml        # [NOVO] Configuracao de providers IA
```

### RAIZ
```
.env.example              # [NOVO] Template de API keys
requirements.txt          # [MODIFICADO] Novas dependencias
run_test.py               # [NOVO] Script de teste
MAPA_ARQUIVOS_IA.md       # [NOVO] Este arquivo
DOCUMENTACAO_MELHORIAS_v1.md    # [NOVO] Documentacao completa
DOCUMENTACAO_IMPLEMENTACAO_v1.md # [NOVO] Guia de implementacao
```

---

## COMO RODAR O PROJETO

### 1. Instalar Dependencias
```bash
cd Ai_Code_Assistant_Open-Source-main
pip install -r requirements.txt
```

### 2. Configurar API Keys (escolha uma opcao)

**Opcao A - Variaveis de ambiente (Recomendado para teste):**
```bash
# Windows (CMD)
set DEEPSEEK_API_KEY=sk-sua-chave-aqui

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="sk-sua-chave-aqui"

# Linux/Mac
export DEEPSEEK_API_KEY=sk-sua-chave-aqui
```

**Opcao B - Arquivo .env:**
```bash
cp .env.example .env
# Edite .env com suas chaves
```

### 3. Testar Instalacao
```bash
python run_test.py
```

### 4. Executar o Programa
```bash
python src/main.py
```

---

## FUNCIONALIDADES NOVAS

### Criar IA Customizada
1. Menu **IA > Criar Nova IA...**
2. Escolha nome, descricao e modelo base
3. Configure o prompt do sistema
4. Ajuste temperatura e tokens
5. Use templates prontos ou crie do zero

### Gerenciar IAs
1. Menu **IA > Gerenciar IAs...**
2. Veja todas as IAs criadas
3. Exporte para arquivo `.aica`
4. Importe de arquivo `.aica`
5. Delete IAs nao utilizadas

### Usar IA no Chat
1. No combo de selecao (canto superior direito do chat)
2. Escolha entre:
   - **Providers**: DeepSeek, GPT-4, Claude
   - **Suas IAs**: IAs customizadas criadas

---

## Fluxo de Dados

```
[Usuario digita mensagem]
        |
        v
[handle_send() em main_window.py]
        |
        +---> [IA Customizada ativa?]
        |           |
        |           v
        |     [Usa system_prompt customizado]
        |
        v
[AIStreamThread inicia em background]
        |
        v
[AIManager.send_message()]
        |
        +---> [ResponseCache.get()] --> Cache HIT? --> Retorna
        |
        +---> [TokenOptimizer.optimize_code_context()]
        |
        v
[Provider.send_message()] --> OpenAI/Claude/DeepSeek
        |
        v
[ResponseCache.set()] --> Salva resposta
        |
        v
[_on_ai_response()] --> Atualiza GUI
```

---

## Melhorias de Performance

### Implementadas:
- [x] **Limite de mensagens**: Maximo 50 mensagens no chat
- [x] **Threads em background**: IA nao bloqueia interface
- [x] **Cache de respostas**: Evita requisicoes duplicadas
- [x] **Otimizacao de tokens**: Reduz contexto de codigo
- [x] **Finalizacao limpa**: Threads encerradas ao fechar
- [x] **Prevencao de envios duplicados**: Bloqueia enquanto processa

### Para Implementar:
- [ ] Streaming real (chunks)
- [ ] Lazy loading de mensagens antigas
- [ ] Virtualizacao de lista de arquivos

---

## Templates de IA Disponiveis

| Template | Temperatura | Melhor Para |
|----------|-------------|-------------|
| Assistente de Codigo | 0.3 | Programacao, debug |
| Escritor Criativo | 0.9 | Textos, historias |
| Analista de Dados | 0.2 | Analise, relatorios |
| Tutor Educacional | 0.5 | Ensino, explicacoes |
| IA em Branco | 0.7 | Customizacao total |

---

## Custos por Provider (por 1000 tokens)

| Provider | Input | Output | Melhor Para |
|----------|-------|--------|-------------|
| DeepSeek | $0.0001 | $0.0002 | Codigo (100x mais barato) |
| GPT-3.5  | $0.0005 | $0.0015 | Tarefas simples |
| Claude Haiku | $0.00025 | $0.00125 | Rapido e barato |
| Claude Sonnet | $0.003 | $0.015 | Balanceado |
| GPT-4 Turbo | $0.01 | $0.03 | Alta qualidade |
| Claude Opus | $0.015 | $0.075 | Maximo |

**Recomendacao:** Use DeepSeek para codigo e Claude/GPT para tarefas complexas.

---

## Checklist de Continuacao

### Basico (Feito)
- [x] Sistema de IAs customizadas
- [x] Interface de criacao de IA
- [x] Selecao de modelo base
- [x] Integracao ao chat
- [x] Melhorias de performance
- [x] Correcoes de estabilidade

### Proximo Passo
- [ ] Adicionar streaming real (chunks)
- [ ] Sistema de treinamento (fine-tuning)
- [ ] Historico persistente de conversas

### Futuro
- [ ] Modulo de imagem (DALL-E, SD)
- [ ] Modulo de audio (TTS, STT)
- [ ] Modulo 3D (geracao, rigging)
- [ ] Sincronizacao WebSocket
- [ ] Integracao SAGE / Social Try

---

## Estrutura de Arquivo .aica (Exportacao)

```json
{
  "format": "aica",
  "version": "1.0",
  "model": {
    "id": "abc123",
    "name": "Minha IA",
    "description": "Descricao",
    "base_provider": "deepseek",
    "base_model": "deepseek-coder",
    "system_prompt": "...",
    "temperature": 0.7,
    "max_tokens": 4096,
    "training_data": [],
    "knowledge_base": [],
    "tags": ["codigo", "python"]
  }
}
```
