# CHANGELOG - AI Code Assistant

**Documento de Histórico de Alterações**  
**Versão:** v0.4.11-rev1.2.3-220426  
**Idioma:** Português (Brasil)

---

## Índice

## Índice

- [Build 1.2.3 - 22/04/2026](#build-123---220426)
- [Build 1.1.2 - 22/04/2026](#build-112---220426)
- [Build 1.0.1 - 21/04/2026](#build-101---210426)
- [Build 22.0.9 - 21/04/2026](#build-2209---210426)
- [Build 22.0.8 - 21/04/2026](#build-2208---210426)
- [Build 22.0.7 - 15/04/2026](#build-2207---150426)
- [Build 22.0.6 - 15/04/2026](#build-2206---150426)
- [Build 22.0.5 - 15/04/2026](#build-2205---150426)
- [Build 22.2 - 14/04/2026](#build-222---140426)
- [Build 22.1 - 14/04/2026](#build-221---140426)
- [Build 22 - 14/04/2026](#build-22---140426)
- [Build 21 - 13/04/2026](#build-21---130426)
- [Build 20 - 09/04/2026](#build-20---090426)
- [Build 19 - 07/04/2026](#build-19---070426)
- [Build 18 - 07/04/2026](#build-18---070426)
- [Build 17 - 06/04/2026](#build-17---06042026)
- [Build 16 - 24/01/2026](#build-16---24012026)
- [Build 15 - 22/01/2026](#build-15---22012026)
- [Build 14 - 14/01/2026](#build-14---14012026)


## Build 1.2.3 - 22/04/2026

### v0.4.11-rev1.2.3-220426 | Build 1.2.3 | Rev 1.2.3 | Major | Homologação

**Resumo:** Fix crítico no NLP do Richie para extração de mensagens personalizadas do prompt, novos grupos de cards no catálogo BotForge (API & Conexão, Documentação, Mapeamento Neural), campos `updated_by`/`updated_at`/`update_logs` no modelo, e dialog de importação com nome editável.

#### 🔧 Fix NLP Richie — Extração de Mensagem Personalizada
- **Bug:** Ao pedir "crie script lua dizendo Olá, Mundo", gerava `Hello World from Lua!` (hardcoded).
- **Fix:** Novo método `_extract_user_message()` com regex para extrair texto entre aspas ou padrões como `dizendo X`, `que escreva X`, `com print X`.
- **`_open_hello_world()`:** Reescrito com parâmetro `custom_message` e suporte a 20+ linguagens (py, js, ts, lua, cs, html, java, go, rs, php, rb, kt, swift, cpp, c, r, jl, dart, gd, css).

#### 🔌 Novos Cards no Catálogo BotForge
- **"🔌 API & Conexão [NOVO]":** api_entry (ComboBox), api_connect, api_config, api_auth, api_health, api_endpoint.
- **"📄 Documentação [NOVO]":** doc_qa (Modelo Padrão QA), doc_sprint, doc_changelog, doc_readme, doc_presentation, doc_contract, doc_history.
- **"🧬 Mapeamento Neural [NOVO]":** neural_map (Mapeamento Documental Neural), neural_context, neural_index.

#### 📝 Campos de Atualização no Modelo
- **Novos campos:** `updated_by`, `last_updated_at`, `update_logs[]` no `CustomAIModel`.
- **Imutáveis:** `created_at` e `creator_name` nunca são alterados após a primeira importação.
- **Mutáveis:** `updated_by`, `last_updated_at` e `update_logs` registram quem e quando atualizou.

#### 📥 Dialog de Importação Melhorado
- **Nome editável:** Campo QLineEdit pré-preenchido com o nome do bot, permitindo renomear antes de importar.
- **"Atualizado por":** Campo para registrar quem realizou a importação.
- **Log automático:** `update_logs` recebe entrada inicial com data, usuário e descrição.

#### 📝 Versionamento Atualizado
- Todos os 9 arquivos atualizados para `v0.4.11-rev1.2.3-220426`.
- Backups criados com sufixo `.bak-rev123`.
- Backup de segurança do `richie_state.json` criado.

---

## Build 1.1.2 - 22/04/2026

### v0.4.11-rev1.1.2-210426 | Build 1.1.2 | Rev 1.1.2 | Major | Homologação

**Resumo:** Implementação do sistema de Repositório de Versões para IAs/Bots no BotForge Studio, com agrupamento de modelos por nome, dialog visual estilo ttkbootstrap para gerenciamento de versões, cards melhorados com layout premium inspirado no chatbot-creator.html, import inteligente com detecção de duplicatas (3 opções), e filtro do ComboBox para exibir apenas versão ativa por bot.

#### 🗂️ Repositório de Versões (Nova Funcionalidade)
- **Modelo de Dados:** Novos campos `repo_group` (chave de agrupamento) e `version_label` (v1, v2, v3...) no `CustomAIModel`.
- **6 Novos Métodos no Manager:** `get_version_group()`, `get_active_version()`, `set_active_version()`, `save_current_as_version()`, `import_as_version()`, `get_unique_bots()`.
- **Migração Automática:** Modelos existentes recebem `repo_group` automaticamente no `__post_init__`.
- **Delete com Promoção:** Ao excluir versão ativa, a próxima é promovida automaticamente.

#### �\udfa8 Dialog Visual "Repositório de Versões" (`VersionRepositoryDialog`)
- **Design:** Background `#161b22`, botão "Salvar Versão Atual" com gradiente roxo→magenta (`#7c5cfc` → `#c840e9`).
- **Botão "Importar como Versão":** Importa JSON diretamente como nova versão do bot selecionado.
- **Lista de Versões:** Dot indicator verde/cinza, badge "ATIVA", botões Ativar/Excluir.
- **Scrollável:** Suporta N versões com QScrollArea.

#### �\udfb4 Cards BotForge Melhorados (`AICard` v1.1.2)
- **Novo Layout:** Ícone com fundo gradiente, nome + data + badge ATIVO/RASCUNHO.
- **Stats:** Canal e Conversas em linha, switch animado com label dinâmico.
- **Link de Versões:** Exibe "🗂️ X versões" ou "📌 v1 — Sem outras versões".
- **Botões de Ação:** 📝 Editar, 🗂️ Versões, 📤 Exportar, 🗑️ Excluir (estilo screenshot).
- **Agrupamento:** `_load_cards()` usa `get_unique_bots()` — 1 card por bot (versão ativa).

#### ⚠️ Import Inteligente com Detecção de Duplicata
- **3 Opções:** "Importar como Nova Versão", "Substituir Versão Ativa", "Cancelar".
- **Formato Web BotForge:** Detecção automática via `get_version_group()` antes de criar.

#### 🔧 Filtro do ComboBox de IAs
- **`_refresh_ai_combo()`:** Usa `get_unique_bots()` para popular apenas 1 entrada por bot.
- **Tooltip:** Exibe nome completo + versão + contagem de versões.
- **Elimina duplicatas:** Richies múltiplos agora aparecem como 1 único item.

#### 📝 Versionamento Atualizado
- Todos os arquivos atualizados: `main_window.py`, `main.py`, `richie_ai.py`, `build_windows2.bat`, `build_linux.sh`, `build_macos.sh`.
- Backups criados com sufixo `.bak-rev112`.

---

## Build 1.0.1 - 21/04/2026

### v0.4.11-rev1.0.1-210426 | Build 1.0.1 | Rev 1.0.1 | Major | Homologação

**Resumo:** Evolução major da interface com melhorias visuais PyQt6 (gradientes, tipografia moderna, hover effects), remoção do label "Richie" fixo no header, conexão real Richie \u2194 fluxo offline com flag `_richie_active` corrigida na inicialização, e implementação do dialog de histórico de conversas com renomear via botão \ud83d\udd0d.

#### \ud83c\udfa8 Melhorias Visuais (Equivalente ttkbootstrap p/ PyQt6)
- **Tipografia:** Font-family global `'Segoe UI', 'Inter', 'Roboto'` para UI e `'Cascadia Code', 'Consolas', 'Fira Code'` para código.
- **ScrollBar:** Gradiente sutil nas handles + hover azul (`#58a6ff`).
- **Tabs:** Hover effect em tabs não selecionadas.
- **TreeView:** Padding nos items + hover highlight.
- **ComboBox:** Borda arredondada + hover azul.
- **Tooltips:** Estilizados com background escuro, borda e border-radius.
- **Botões:** Hover global com `background-color: #30363d`.

#### \u2702\ufe0f Remoção do Label "Richie" do Header
- Removido `chat_ai_label` (QLabel estático "🤖 Richie") que aparecia ao lado do botão \u25b6 no topo do painel de chat. Removidas também todas as referências em `_on_ai_changed`.

#### \ud83d\udd17 Conexão Real Richie \u2194 Fluxo Offline
- **Fix `_richie_active`:** Adicionado `self._richie_active = True` após `_init_richie()` para garantir que o Richie está ativo desde o boot, eliminando o erro "Nenhum provider online configurado" quando o usuário envia mensagem com Richie selecionado.

#### \ud83d\udcda Histórico de Conversas via \ud83d\udd0d
- **Botão \ud83d\udd0d conectado:** Agora abre um dialog `_show_chat_history_dialog()` com lista de todas as conversas salvas.
- **Renomear inline:** Cada conversa tem botão \u270f\ufe0f que abre `QInputDialog` para editar o título.
- **Abrir conversa:** Botão "Abrir" carrega a sessão no chat principal.
- **Visual:** Cards estilizados com hover azul, datas formatadas, ícones.

#### \ud83d\udce6 Versionamento
- Todos os arquivos atualizados para `v0.4.11-rev1.0.1-210426`.
- Build scripts (Windows, Linux, macOS) sincronizados.
- Richie `about` response atualizada para nova versão.

---

## Build 22.0.9 - 21/04/2026

### v0.4.7-rev22.0.9-210426 | Build 22.0.9 | Rev 22.0.9 | Hotfix | Homologação

**Resumo:** Hotfix crítico para 3 bugs introduzidos na rev22.0.8: balões de chat cortados na direita, nome "Assistente" fixo nas mensagens em vez do nome da IA selecionada, e Richies duplicados no ComboBox.

#### 🐛 Bugs Corrigidos

##### 1. Balões de Chat Cortados na Direita
- **Causa:** `bubble.setSizePolicy(Minimum, Minimum)` impedia a bolha de expandir para preencher a largura disponível. O texto não tinha espaço para fazer word-wrap, cortando na borda direita.
- **Solução:** Alterado para `Expanding, Minimum` tanto no `bubble` quanto no `text_label`. Agora a bolha ocupa a largura disponível e o texto quebra corretamente.

##### 2. Nome "Assistente" Fixo nas Mensagens
- **Causa:** O sender das mensagens era hardcoded como `"🤖 Assistente"` em vários pontos: boas-vindas, nova conversa, erro de provider, e respostas online.
- **Solução:** Criado método `_get_ai_sender_name()` que retorna o nome correto baseado na IA ativa: `"🤖 Richie"` quando offline, `"🤖 NomeCustom"` para IAs custom, ou `"💻 DeepSeek"` etc. para providers online. Todos os `add_message` agora usam esse método.

##### 3. Richies Duplicados no ComboBox (3x)
- **Causa:** O filtro `model.id != "richie_native"` não capturava modelos Richie carregados do JSON (que possuem `id: "richie-01"` ou variações de nome).
- **Solução:** Filtro expandido para verificar `model.id in ("richie_native", "richie-01", "richie")` E também `"richie" in model.name.lower()`, eliminando qualquer duplicata.

#### 📦 Versionamento
- Todos os arquivos atualizados para `v0.4.7-rev22.0.9-210426`: `main.py`, `main_window.py`, `build_windows2.bat`, `build_linux.sh`, `build_macos.sh`.

---

## Build 22.0.8 - 21/04/2026

### v0.4.7-rev22.0.8-210426 | Build 22.0.8 | Rev 22.0.8 | Imp S | Homologação

**Resumo:** Correção integral do Chat UI (primeira mensagem cortada, scroll com espaço vazio, campo de entrada), unificação do ComboBox de seleção de IA, cabeçalho dinâmico com nome da IA ativa, atualização dos build scripts.

#### 🤖 Chat AI e UX (Reescrita do Layout)
- **Primeira Mensagem Cortada:** Removido `addStretch(1)` inicial do `chat_v_layout` que empurrava o conteúdo para fora da área visível. Substituído por `setAlignment(Qt.AlignmentFlag.AlignTop)` para que mensagens cresçam de cima para baixo naturalmente.
- **Scroll com Espaço Vazio:** Alterado `chat_messages_widget.setSizePolicy` de `Minimum/Minimum` para `Preferred/Preferred`, permitindo que o widget ocupe exatamente o espaço do conteúdo. Método `_update_chat_stretch()` simplificado (stub) por não ser mais necessário.
- **Campo de Entrada:** Melhorado `_adjust_input_frame_height` para exibir scrollbar interno quando atingir 220px e usar `QTimer.singleShot(10, ensureCursorVisible)` para garantir acompanhamento da digitação.

#### 🔗 Seletor de IA (ComboBox Unificado)
- **Remoção de "IA Nativa":** Seção "--- IA Nativa ---" removida. Agora o ComboBox mostra apenas "--- Suas IAs ---" (com Richie + custom AIs) e "--- Providers (Online) ---".
- **Auto-seleção Richie:** Ao iniciar, Richie é automaticamente selecionado (index 1).

#### 🏷️ Cabeçalho Dinâmico
- **Label `chat_ai_label`:** Novo QLabel no header do chat exibe o nome da IA ativa ("🤖 Richie", "🤖 NomeCustom", "💻 DeepSeek"). Atualizado dinamicamente em `_on_ai_changed`.

#### 📦 Build Scripts
- **Windows (`build_windows2.bat`):** VERSION=0.4.7, REV=22.0.8, BUILD_DATE=210426.
- **Linux (`build_linux.sh`):** VERSION=0.4.7, REV=22.0.8, BUILD_DATE=210426.
- **macOS (`build_macos.sh`):** VERSION=0.4.7, REV=22.0.8, BUILD_DATE=210426.

---

## Build 22.0.7 - 15/04/2026

### v0.4.10-rev22.0.7-150426 | Build 22.0.7 | Rev 22.0.7 | Imp S | Homologação

**Resumo:** Ajuste do Lifecycle IDE via linguagem NLP, BotForge Action Mapping expandido, refino drástico e re-adequação de UI do painel do chatbot.

#### 🤖 Chat AI e UX (Layout Refatorado)
- **Correção Definitiva do Wrap Layout:** Para garantir que a aba de "Você" em azul faça o `Quebra-Linhas/WordWrap` de pedidos imensos como *'crie um codigo em java ... e rode'* sem quebrar e escapar das bordas, foi feito um reset forçado das SizePolicies `text_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)`, adicionado um controle dinâmico que amarra o tamanho limite do container da Right Panel, parando vazamentos em definitivo. Todas bolhas de IA agora herdam margens responsivas limitadas (`350 * 0.85`).

#### 🧰 Pipeline Híbrida Richie / Engine
- **F5 Nativo Automático (+ Abas Contextuais):** O Richie não mais engana tentando dar F5 no script de uma janela nada a ver! Agora o script entende o intercept: *"crie", "faça", "code..."*. Quando você escreve "Crie e rode um java...", ele interpreta o tipo de requisição (via detect_intent e NLP) de forma imponente, chamando imediatamente a função `self._open_hello_world` oculta da GUI original. O Assistente virtual puxa o Java Boilerplate, empurra pra uma aba fresca dentro do ambiente local e joga um pop-up te avisando "Guia Preparada, responda 'sim, execute'.". Com mais *"Sim, execute"* ele deflagra a janela nova com a execução sem colapsos lógicos!
- Os botões de reset ("Reset Richie") inseridos globalmente no painel Custom AI se mantêm funcionais para desvincular problemas se o Bot entrar em loop local.

#### 📦 BotForge NLP Execution Nodes (Layout Flow)
- **Expansão na Rota Engine:** O Studio agora traz consigo explicitamente os Nodes visuais `"💻 Execução & Scripts"`. Esses Nodes embutem cartões de Rota, de `Detectar Linguagem`, `Abrir Guia IDE` e `Rodar Script (F5)` integrando o escopo funcional visual ao escopo logico subjacente do IDE.

---

## Build 22.0.6 - 15/04/2026

### v0.4.10-rev22.0.6-150426 | Build 22.0.6 | Rev 22.0.6 | Imp S | Homologação

**Resumo:** Correções pontuais críticas no Desktop Reportadas pelo Usuário.

#### 🤖 Chat AI e UX
- **Correção Visual de Balões:** Ajustou `text_label.setMinimumWidth(80)` e layout parameters no ChatMessage, corrigindo os quebramentos verticais quando o layout de "Suas IAs" solicitava expandir conteúdo longo (wrapping responsivo corrigido sem cortar caracteres no Desktop).

#### 🧰 CustomAIManager (Richie AI Features)
- **Instanciamento do Reset:** Agora o "Reset Richie" foi exposto nativamente com um botão dourado `🔄 Reset Richie` na janela visual de gerenciar "Suas IAs". Ele fará validação e invocará `reset_richie_to_factory`.
- **F5 Nativo para "sim, execute":** Reformulou a resposta passiva do `OfflineEngine._handle_execution_request`. Se o usuário responder "sim, execute", o engine sinalizará pro `main_window.py` forçar diretamente a execução explícita via `self.run_code()` - eliminando inconsistência do bypass estático do bot ao tentar descobrir o script.

#### 🚀 Runners de Linguagens de Fábrica (Corrigidos)
- **Node.js/Python e Terminal Cross-Platform:** Corrigido "Cannot find module C:\temp...js" ocasionado pelo parse imperfeito de `cmd.exe /c node "..."` do processo QProcess start. Alterado para usar robustamente `self._script_process.startCommand(f"cmd.exe /c {cmd}")`, garantindo escapes limpos para o Node.js v23 no Windows.

---

## Build 22.0.5 - 15/04/2026

### v0.4.10-rev22.0.3-140426 | Build 22.0.5 | Rev 22.0.3 | Imp S | Homologação

**Resumo:** Fechamento e consolidação das features vitais de execução de código (Runners Nativos), Layout do Chat AI Dinâmico, Reset Richie AI de Fábrica, Biblioteca Integrada na Loja com Repositórios reais, Nodes de Aprendizado Sprint no BotForge, Mobile IDE v0.2.2-rev2.0.5 c/ Importação e Exportação JSON cruzada Desktop/Mobile.

#### 🚀 Runners de Linguagens de Fábrica (Corrigidos)
- **Java:** Corrigido problema de localização de classe. Executa .java compilado na pasta temporária.
- **Python/Node:** Corrigida renderização com escapes em caminhos e substituição de aspas duplas quebradas no subprocesso com comando `sys.executable`.
- **C#:** Implementada compilação cross-platform usando `dotnet run` num diretório custom temporário C# projeto.
- **Lua:** Prevenção de corrupção usando gravação síncrona nos temps sem aspas conflituosas.
- **HTML e CSS:** Documentos simples exibem conteúdo no navegador web padrão automaticamente sem logs poluindo o Terminal.
- **GDScript:** Mapeado novo runner com `godot --headless`.

#### 🤖 Chat AI e UX
- **Balões Redimensionáveis (Responsivos):** Reformulação do QLabel nativo das mensagens para abraçar conteúdo usando Expand Policies, permitindo leitura livre e completa na tela do chat.
- **Box Integrado (Scrollbar Fix):** Limpeza do CSS com line-height em 1.4 permitindo leitura agradável.
- **Unificação do Richie:** Removida a cópia Mock duplicada, agora baseando-se inteiramente no motor Richie Base Nativo (Aba Suas IAs).

#### 🧰 CustomAIManager (Richie AI Features)
- **Reset de Modo Fábrica:** Nova engine `reset_richie_to_factory()` permite zerar manipulações do usuário no Richie Base para a versão de instalação.
- **Documentação Master Sprint:** Model Template base implementado no Fluxo Nativo interativo do Richie. C17 agora faz link explícito com a doc de "Padrao-QA.md" do SprintTracker para construir projetos estruturados.

#### 📦 Loja e Bibliotecas Reais
- **Aba de Bibliotecas:** Inclusão de React, Vue, TailwindCSS, Pandas, TensorFlow integrado com seus comandos `pip` / `npm` e links descritivos oficiais.

#### 📱 Mobile IDE (v0.2.2-rev2.0.5)
- **Híbrida Importação e Exportação JSON:** Funcionalidade BotForge integrada para migrar modelos entre a plataforma HTML e o Client Python Desktop através de payload cross-device.
- **Listagem de IA no Layout Mobile.**

---



### v0.4.10-rev22.0.2-140426 | Build 22.2 | Rev 22.0.2 | Imp S | Homologação

**Resumo:** Terminal Interativo com QProcess (stdin/stdout em tempo real), Richie AI integrado ao BotForge Studio via JSON estruturado (16 nodes, 24 connections), Verificação de Startup para 18+ linguagens, Indicador de modificações não salvas (*), Benchmarks gráficos na Loja de Extensões, Build scripts atualizados para rev22.0.2, Mobile IDE modular SPA.

#### 🖥️ Terminal Interativo (Rev 22.0.2)
- **QProcess com stdin:** Substituição do `subprocess.Popen` por `QProcess` para execução de scripts com suporte a `stdin` interativo em tempo real
- **ComboBox Shell Selector:** Seletor funcional no terminal (cmd, powershell, bash, node, python) que determina qual shell executa o código via F5
- **Indicador de Shell Ativo:** Label dinâmico `● cmd [executando]` ao lado do ComboBox mostrando o shell em uso e seu estado
- **Input Direto no Terminal:** O usuário pode digitar diretamente no terminal durante execução (prompts `input()`, `readline()`, etc)
- **Leitura Realtime:** Stdout e stderr capturados em tempo real via sinais `readyReadStandardOutput` e `readyReadStandardError`
- **Kill de Processo:** Processo anterior é terminado automaticamente antes de nova execução

#### 🤖 Richie AI — BotForge JSON (Rev 22.0.2)
- **Richie_AI_Assistant.json:** Modelo JSON completo no formato BotForge ari com 16 nodes e 24 connections
- **Preload Automático:** `CustomAIManager._preload_richie_model()` carrega o Richie automaticamente se não existir no index
- **Import BotForge Format:** Novo método `_import_botforge_json()` converte JSON ari para `CustomAIModel` com flow_nodes e flow_conns
- **Nodes do Richie:** Receber Mensagem → NLP Engine → 9 intenções (Saudação, Análise, Gerar Código, Explicar, Debug, Executar, BotForge, Config, Geral) → Registro de Aprendizado → Resultado → Voltar ao Chat

#### 💾 Indicador de Modificações (*) (Rev 22.0.2)
- **Asterisco na Tab:** Título da tab recebe `*` quando o conteúdo difere do original
- **Rastreamento por Tab:** Dicionário `_tab_original_content` mapeia cada tab ao seu conteúdo salvo
- **Remoção ao Salvar:** Indicador `*` removido automaticamente após Ctrl+S
- **Dialog Save/Discard:** Ao fechar tab com modificações: prompt com opções Salvar, Descartar, Cancelar
- **CloseEvent Global:** Ao fechar a aplicação com tabs não salvas, dialog lista todos os arquivos e oferece SaveAll, Discard, Cancel

#### 🔍 Startup Check 18+ (Rev 22.0.2)
- **18 Dependências Verificadas:** Python, Node.js, npm, Git, TypeScript, ts-node, Lua, C# (.NET), Java, C/C++, Go, Rust, Ruby, PHP, Kotlin, Swift, Godot, Docker
- **Box Decorativo no Terminal:** Resultado visual com ✅/❌/⚪ no terminal integrado ao iniciar
- **Status Bar:** Mostra contagem de dependências encontradas

#### 📊 Benchmarks na Loja de Extensões (Rev 22.0.2)
- **Widget de Benchmarks:** 5 métricas visuais na página de detalhes de cada extensão
- **Métricas:** Velocidade de Execução, Armazenamento (MB), Facilidade de Aprendizagem, Popularidade (TIOBE/GitHub), Score Geral
- **Barras de Progresso Coloridas:** Indicadores visuais com cores distintas por métrica (#3fb950, #f0a030, #58a6ff, #a855f7, #22c55e)
- **15 Extensões com Dados:** Python, Node.js, TypeScript, Lua, Godot, Java, C#, Ruby, Kotlin, Swift, Go, Rust, React, PHP, C/C++

#### 🏗️ Build Scripts (Rev 22.0.2)
- **build_windows2.bat:** Versão atualizada para rev22.0.2-140426
- **build_linux.sh:** REV atualizado para 22.0.2
- **build_macos.sh:** REV atualizado para 22.0.2

#### 🏷️ Versionamento (Rev 22.0.2)
- Window Title: `AI Code Assistant - v0.4.10-rev22.0.2`
- Footer: `v0.4.10-rev22.0.2-140426 | homologacao | @S.V.S - Try Technology`
- About Dialog: Atualizado com novidades da Rev 22.0.2
- Mobile IDE: `v0.2.2-rev2.0.2-140426`

---

## Build 22.1 - 14/04/2026

### v0.4.10-rev21.0.1.2-140426 | Build 22.1 | Rev 21.0.1.2 | Imp S | Homologação

**Resumo:** Correções pós-build da Rev 21.0.1. Estabilização de dependências no PyInstaller (requests, urllib3, src.*). Mensagem detalhada de extensão faltante no Runner com nome e linguagem. Richie AI com greeting, nova sessão e persistência no close. Card Richie funcional na Store. Build scripts multi-plataforma atualizados. Auto-recovery de dependências no main.py. Mobile IDE atualizada para v0.2.2.

#### 🔧 Correções de Build (Rev 21.0.1.2)
- **Hidden-Imports Completos:** Adicionados 20+ hidden-imports faltantes no build_windows2.bat, build_linux.sh e build_macos.sh (requests, requests.adapters, urllib3, charset_normalizer, certifi, idna, src.core.*, src.gui.*, src.providers)
- **Verificação Pré-Build:** Build scripts agora verificam PyQt6 e requests antes de compilar, abortando com mensagem clara se faltarem
- **Remoção ext_manager_server.js:** Removida referência residual ao ext_manager_server.js dos build scripts Linux e macOS

#### 🤖 Melhorias Richie AI (Rev 21.0.1.2)
- **Richie Greeting:** Saudação automática exibida ao selecionar Richie no ComboBox quando chat está vazio
- **Nova Sessão ao Limpar:** Limpar chat com Richie ativa cria nova sessão com greeting atualizado
- **Persistência no Close:** Estado da Richie (sessões, aprendizado) salvo automaticamente ao fechar a aplicação
- **Card Store Funcional:** Click no card Richie na Extension Store ativa a IA no chat ao invés de abrir tab de instalação

#### ⌨️ Runner Detalhado (Rev 21.0.1.2)
- **Mensagem com Nome e Linguagem:** Ao tentar rodar script sem extensão instalada, terminal mostra: nome da extensão ('Python Extension Pack'), linguagem ('Python'), comando não encontrado, e sugestão para acessar a Loja
- **Mapa de 14 Linguagens:** py, js, ts, lua, cs, java, cpp, gd, rb, kt, swift, go, rs, php mapeadas com nome de extensão e linguagem

#### 🛡️ Auto-Recovery (Rev 21.0.1.2)
- **main.py:** Se PyQt6 não encontrado, tenta instalar automaticamente via pip antes de falhar

#### 📱 Mobile IDE (Rev 2.0.1.2)
- **Versão atualizada:** v0.2.2 rev2.0.1.2-140426
- **Richie AI no Chat:** Chat mobile atualizado com referência à Richie AI
- **Versionamento consolidado:** Footer e About atualizados

#### 🏷️ Versionamento (Rev 21.0.1.2)
- Window Title: `AI Code Assistant - v0.4.10-rev21.0.1.2`
- Footer: `v0.4.10-rev21.0.1.2-140426 | homologacao | @S.V.S - Try Technology`
- About Dialog: Atualizado com correções Build 22.1
- Mobile IDE: `v0.2.2 rev2.0.1.2-140426`

---

## Build 22 - 14/04/2026

### v0.4.10-rev21.0.1-140426 | Build 22.0 | Rev 21.0.1 | Imp A+ | Homologação

**Resumo:** Criação da IA Base "Richie" — primeira IA nativa do projeto com chat funcional offline, entendimento de código, sessões múltiplas, sistema de permissões, planos de atuação e aprendizado contextual. Correção de bugs pós-build da Rev 20.0.10.11. Provider OpenAI como padrão opcional.

#### 🤖 Richie AI — IA Nativa (Rev 21.0.1)
- **Chat Funcional Offline:** Richie responde com lógica, memória de conversa e base de conhecimento local — sem necessidade de internet ou API key
- **Motor Offline Completo:** Engine de respostas locais com detecção de intenções, análise de código, templates de 15+ linguagens e explicação de erros comuns
- **Sessões Múltiplas:** Criar, trocar e deletar conversas independentes com histórico persistente em JSON
- **Análise de Código:** Analisa código aberto no editor com métricas, detecção de problemas e sugestões de melhoria
- **Detecção de Intenções:** Detecta automaticamente análise, execução, criação de arquivo ou plano
- **Planos de Atuação:** Cria plano detalhado com steps e espera aprovação do usuário
- **Sistema de Permissões:** Pede permissão antes de executar ações na máquina do usuário
- **Aprendizado Contextual:** Aprende preferências e padrões do usuário entre sessões
- **Card BotForge:** Richie aparece no BotForge Store e como primeira opção no ComboBox
- **Multi-Linguagem:** Python, JavaScript, TypeScript, Lua, C#, HTML/CSS, GDScript, Java, Go, Rust, PHP, Ruby, Kotlin, Swift, C/C++

#### 🔧 Correções Pós-Build (Rev 21.0.1)
- **Permissões Winget:** Detecção de privilégios Admin com instruções claras ao usuário
- **Sidebar Toggle:** Inicialização segura no `__init__` eliminando hasattr checks
- **ext_manager_server.js:** Remoção de referências residuais do build script
- **ComboBox Refatorado:** Richie como primeira opção, providers como secundários

#### 🏷️ Versionamento (Rev 21.0.1)
- Window Title: `AI Code Assistant - v0.4.10-rev21.0.1`
- Footer: `v0.4.10-rev21.0.1-140426 | homologacao | @S.V.S - Try Technology`
- About Dialog: Atualizado com Richie AI e correções

---

## Build 21 - 13/04/2026

### v0.4.10-rev20.0.10.11-130426 | Build 21.0 | Rev 20.0.10.11 | Imp S | Homologação

**Resumo:** Mega Update — Eliminação do ext_manager_server.js, Instalação Direta via Python Subprocess, Histórico de Bibliotecas com Badges, Sidebar Toggle Animado, Startup Check de Dependências, Scripts de Build Multi-Plataforma Atualizados, Instalador Profissional via env2installer + Inno Setup + NSIS, Versão Mobile HTML.

#### 🔧 Correção Crítica — Instalação de Extensões (Rev 20.0.10.11)
- **Eliminação do ext_manager_server.js:** Removida completamente a dependência do Node.js para instalar extensões. O erro `MODULE_NOT_FOUND` que ocorria quando o `ext_manager_server.js` não era encontrado na pasta de build foi eliminado.
- **Instalação Direta via Python Subprocess:** Todos os comandos de instalação (winget, npm, pip) agora são executados diretamente pela `ExecutionThread` nativa do Python, sem intermediário Node.js.
- **InstalledLibsManager:** Novo gerenciador persistente de bibliotecas instaladas, salvando em `config/installed_libs.json`.

#### 🧩 Histórico de Bibliotecas (Rev 20.0.10.11)
- **Badge de Contagem:** Cada extensão instalada mostra badge com quantidade de bibliotecas.
- **Popup Detalhado (LibsDetailDialog):** Ao clicar no badge, abre popup listando todas as bibliotecas com opção de desinstalar individualmente.
- **Persistência:** Dados salvos em JSON e restaurados automaticamente ao iniciar.

#### 🖥️ Sidebar Toggle Animado (Rev 20.0.10.11)
- **Recolher ao Clicar no Ícone Ativo:** Clicar no ícone da sidebar que já está ativo recolhe a sidebar completamente com animação suave (250ms OutCubic).
- **Expandir ao Clicar em Outro:** Clicar em qualquer outro ícone expande a sidebar e troca para a view correspondente.
- **Maximização de Área:** Sidebar recolhido libera espaço máximo para o editor e terminal.

#### 🚀 Startup Check de Dependências (Rev 20.0.10.11)
- **Verificação Automática:** Ao iniciar, verifica automaticamente Python, Node.js, npm e Git no PATH.
- **Resultado Visual:** Mostra ✅/❌ no terminal integrado com box decorativo.
- **Status Bar:** Mostra contagem de dependências encontradas na barra de status.

#### 📦 Extensões Completas (Rev 20.0.10.11)
- **32+ Extensões na Loja:** Temas, Linguagens (Python, Node.js, TypeScript, Lua, Godot, Java, C#, Ruby, Kotlin, Swift, Go, Rust, React, PHP, C++), Banco de Dados (SQL, MongoDB), Aplicativos (Docker), Pacotes (Tkinter, LÖVE 2D, Pygame, Flask, Django, NumPy, Express.js, Electron).
- **Comandos Reais:** Todas as extensões possuem comandos de instalação reais via winget, pip, npm ou luarocks.
- **Indicador Visual:** Badge "✅ Instalável" ou "📋 Mock" na listagem da loja.

#### 🏗️ Scripts de Build Multi-Plataforma (Rev 20.0.10.11)
- **build_windows2.bat:** Atualizado para v0.4.10-rev20.0.10.11, `--add-data templates-modelos`, cópia de ext_manager_server.js como fallback.
- **build_linux.sh:** Atualizado para v0.4.10-rev20.0.10.11, separador `:` para Linux, templates-modelos.
- **build_macos.sh:** Atualizado para v0.4.10-rev20.0.10.11, geração de .app, templates-modelos.

#### 📦 Instalador Profissional (Rev 20.0.10.11)
- **create_new_anaconda_env.bat:** Script para criar env Anaconda dedicado para build.
- **CriarInstalador_Funcional.py:** Script Python com 3 métodos em cascata:
  - Método 1: env2installer (automatizado)
  - Método 2: PyInstaller + Inno Setup (script .iss gerado)
  - Método 3: PyInstaller + NSIS (fallback)
  - Método 4: ZIP portável (último fallback)

#### 🏷️ Versionamento (Rev 20.0.10.11)
- Window Title: `AI Code Assistant - v0.4.10-rev20.0.10.11`
- Footer: `v0.4.10-rev20.0.10.11-130426 | homologacao | @S.V.S - Try Technology`
- About Dialog: Atualizado com novidades da Rev 20.0.10.11
- Bot Inicial: Mensagem de boas-vindas v0.4.10

---

## Build 20 - 09/04/2026

### V0.4.10-rev20.0.9-090426 | Build 20.0 | Rev 20.0.9 | Imp S | Homologação

**Resumo:** Animação Suave de Recolhimento/Expansão do Chat, Instalação Real de Linguagens via Winget/NPM, Correção de Paths Absolutos no Node Extension Manager, Quoting Windows-Safe para Subprocess.

---

## Build 19 - 07/04/2026

### V0.4.10-rev20.0.1-080426 | Build 20.0 | Rev 20.0.1 | Imp S | Homologação

**Resumo:** O nascimento da Loja de Extensões Nativa, Execução Multilinguagem Aprimorada via F5, e Deletor de Conexões do Botforge.

#### 🛒 Universo Store Integrado & Runners
- **Extension Store GUI:** A aba de Extensões agora carrega o botão "Abrir Loja de Extensões" ativando um Widget Massivo (Tela Central) com sistema tabular. A loja engloba Temas da IDE, SDKs, Linguagens e Apps de suporte.
- **Micro-Engine Instaladora:** Falsos Loaders implementados para simular a vivência de Loja moderna onde, as extensões rodam progresso autodefinido e alteram os status de [Desinstalar]/[Baixado] salvos no objeto de `Set()`. Ao concluir as barras lógicas os gatilhos arremessam comandos verdadeiros pro terminal via `ExecutionThread` nativa (ex: Pip Install Tkinter, Luarocks Love2D).
- **Runners Avançados C++/HTML/Java:** O construtor `_run_current_script (F5)` agora engloba compilador adaptativo:
  - Cria binários com sufixo randômico se invocado via código `cpp` -> `g++` e encadeia execução no Windows (`&& .exe`).
  - Lança HTML e CSS direto para o Browser invés de poluir Bash injetando bypass condicional pelo `start "" <temp>`.
  - Escaneia a máquina inteira usando `shutil.which` conferindo se LUA, Dotnet ou Java existem e avisa com sutileza se você não tem a Lib, indicando a "Loja". 

#### 🔧 Dinâmica Fluída do BotForge
- **Destrutor Linker de Nós (Deleção de Fios):** A malha de cabos lógicos `FlowConnection` agora tem sinalizador nativo de seleções (`ItemIsSelectable`). Ao estarem ativos, as curvas bézier acendem em vermelho cardinal e a malha do plano (`FlowScene`) ativamente monitora os botões `Backspace` ou `Delete`, desconectando permanentemente os nós com polimorfismo absoluto.
 
---

### V0.4.9-rev19.0.16-080426 | Build 19.0 | Rev 19.0.16 | Imp S | Homologação

**Resumo:** Correção crítica de Missing Import (QTimer Crash), Fix de Reescalonamento da Grid de Nodes, Proteção de Sub-labels contra Duplicação de Emojis e Integração Profunda de Regras Lógicas Ocultas nas Rotas via Parser do BotForge Web (Ex: Modelo Christopher).

#### 🧰 Major Fixes & Estabilização UI (Rev 19.0.16)
- **Safe Init no Event Loop (Crash Fix):** O botão seguro inserido na `v0.4.9-rev19.0.15` continha o objeto Timer sem declarar no cabeçalho do `create_ai_dialog.py`. Acoplada e resolvida a instabilidade para habilitar a GUI limpa.
- **Isolamento Constante de Emojis:** Identificado encadeamento iterativo que dobrava ou acumulava emojis sucessivos ao recarregar um save de disco. Regras injetadas forçam sanitização via check `.startswith(node_icon)`.
- **Salvamento Tático de Regras de Rotas (Persistence Array):** O Node Config Modal agora injeta `out_keywords` diretamente no Array nativo de Nodes.
- **A Ascenção Pura do Christopher Json:** Modificadas regras do parsing do array nativo do BotForge no `ai_consult.py` para ele localizar as lógicas obscuras separadas por intenção em `data.nlpRules` e encadear essas arrays mágicas exatamente no formulário expansível (⚙️). Também adicionada compatibilidade retroativada a conexões baseadas nas letras minificadas `"f"` (from) e `"t"` (to).
- **UX Flex View:** A aba central de FlowScene teve sua propriedade gráfica substituída com `.setSizePolicy(Expanding)` e um layout stretch. Agora, sempre que o usuário distensionar ou maximizar a janela master, em vez do espaço cinza ficar sem vida, a Malha Gráfica engole agressivamente o espaço em branco te conferindo controle irrestrito.

---

### V0.4.9-rev19.0.15-080426 | Build 19.0 | Rev 19.0.15 | Imp S | Homologação

**Resumo:** Melhorias cruciais na Estabilidade de Edição, Componente de Deleção Segura (Long Press), Color Picker Dinâmico e Preservação Exata de Inputs e Ícones via BotForge Web.

#### ⚙️ Features & Fixes (Rev 19.0.15)
- **Delete Seguro (Hold-To-Confirm):** Removidos "Botões 🗑 Lixeira" instantâneos e letais. O novo sistema bloqueia quebras na cena gráfica requerindo Hold de 5s seguido de Modal de Emergência com cooldown passivo de 5s para prevenir acidentes estruturais nas rotas.
- **Paramétricos "Limpos" de Editoração:** Inserção de Fluxo ou NLP Node manual não adoece o canvas com rotas genéricas pré-preenchidas. "Cards de Fluxo" assumiram identidade limpa pronta para customização profissional do usuário.
- **Inversor UI Guias:** A "Aba de Fluxo" foi pivotada e estabelecida visualmente como Index 0 na UI de edição principal.
- **Injeção Dinâmica de Ícone e Retenção de Conexões (Bug do Ari):** `ai_consult.py` foi reforçado para localizar nativamente o schema subjacente (`source_port` e `target_port`) ao invés do fallback `out`. Ícones embutidos na lista "cardTypes" fluem harmonicamente para dentro do Node Label via rendering da biblioteca de classes.
- **Paleta de Cores Nativa e Layout Micro-Formulário:** O seletor foi alterado do pop-up rígido (10 cores) para interface `QColorDialog.getColor()` trazendo a roda Gráfico-De-Pizza. Criado Switch "⚙️" em cada rota que abaixa um input nativo de configuração de restrição/lógica (Keywords).

---

### V0.4.9-rev19.0.14-070426 | Build 19.0 | Rev 19.0.14 | Imp S | Homologação

**Resumo:** Correção de Crash Fatal no NodeConfigModal, Parsing Avançado de JSON do BotForge Web para nós NLP, Proteção contra `NoneTypes` e Redirecionador Resolutivo nativo.

#### ⚙️ Features & Fixes (Rev 19.0.14 & 19.0.13)
- **Extração Profunda de Rotas do JSON (BotForge Web):** O sistema agora lê exatamente as tags (intents) criadas dentro da subchave `data` (ex: "routes" no Christopher) e seus respectivos labels/cores, removendo a sobrescrita hardcoded que alterava os dados ao clicar nos nós.
- **Correção de Crash Fatal no Node NLP:** Proteção em `NodeConfigModal` contra `NoneType` em arrays de cores desparelhados. Inicializada a matriz segura `self.route_inputs` eliminando a colisão de renderização que travava e ejetava a `MainWindow` pelo compilador C++ (PyQt6). 
- **Persistência Real em `.exe`:** Redirecionamento da `__file__` do PyInstaller (`_MEIPASS`) para o diretório nativo `sys.executable` no Windows. Arquivos salvos via executável agora duram pra sempre e param de sumir.
- **Refresh Global de ComboBox:** Ligação direta onde o Switch ou Edição disparam síncronamente `main_window._refresh_ai_combo()` evitando IDE "cega" pós importação.

---

### V0.4.9-rev19.0.12-070426 | Build 19.0 | Rev 19.0.12 | Imp S | Homologação

**Resumo:** Persistência física em pasta `templates-modelos/`, Switch animado iOS nos Cards, Editor de Conexões e Refresh global do ComboBox.

#### ⚙️ Features & Fixes (Rev 19.0.12)
- **Pasta `templates-modelos/`:** Criado diretório visível no root do projeto. Todo JSON importado é copiado fisicamente para essa pasta. Na inicialização, o `CustomAIManager` escaneia essa pasta e restaura todos os modelos automaticamente — eliminando perda de dados ao fechar/abrir.
- **Switch Animado (iOS Style):** Cada card de IA agora possui um toggle animado verde/cinza para ativar/desativar a integração ao Chat Global. O toggle persiste imediatamente via `update_model()` e dispara refresh no ComboBox da MainWindow.
- **Editor de Conexões (Atualizar IA):** O botão "Criar IA" no visualizador foi convertido em "Atualizar IA". Ao clicar, todas as conexões (linhas) desenhadas manualmente são serializadas e gravadas no modelo — persistindo entre sessões.
- **Dupla Gravação (index.json + templates individuais):** Cada modelo é salvo tanto no `index.json` consolidado quanto como arquivo JSON individual na pasta `templates-modelos/`, garantindo redundância e visibilidade.
- **ComboBox Refresh Reativo:** O switch no card dispara `_refresh_ai_combo()` na MainWindow, fazendo a IA aparecer/desaparecer do seletor principal instantaneamente.

### V0.4.9-rev19.0.11-070426 | Build 19.0 | Rev 19.0.11 | Imp S | Homologação

**Resumo:** Correção crítica da serialização `save_models()`, Inversão de Dragging no Canvas (IN->OUT), Salvamento local da malha de layout e Route ColorPicker Dinâmico.

#### ⚙️ Fixes & UX (Rev 19.0.11)
- **Persistência Estrutural Ativada:** A API do `CustomAIManager` recebeu correção de nomenclatura no flush de memória DB. O modelo agora é gravado globalmente, sem perdas! Além disso, a malha de nós que você constrói manualmente da tela `CreateAIDialog` está enviando e alocando as topografias nativas no formato JSON BotForge.
- **Node Route Picker Dinâmico:** Os rótulos de roteamento do NLP agora interagem com cores. Clique na bolinha lateral e um submenu PopUp aparece contendo as paletas primárias (Ciano, Roxo Pálido, Magenta, Verde-Água, etc) injetando a cor sem fechar a modal!
- **Middle-Mouse Freelook & Drag Inverso:** A fluidez da tela recebeu reforço. Use o Scroll Central para movimentar o mapa visual fora de blocos, ou clique num ponto morto para arrastar o layout inteiro de forma limpa. Adicionado também o cálculo drag INVERSE (do In para o OUT), permitindo total interatividade visual livre.
- **Timer de Render Visual:** Implementado `QTimer.singleShot` para as linhas bezier aguardarem posições absolutas da cena renderizada garantindo linhas conectadas e fluídas perfeitamente de priméira.

### V0.4.9-rev19.0.10-070426 | Build 19.0 | Rev 19.0.10 | Imp S | Homologação

**Resumo:** Pan/Zoom na prancheta de arquitetura BotForge, Integração em Multi-Sessões do GPT global e Cache Persistente.

#### ⚙️ Features & UX (Rev 19.0.10)
- **Câmera Freelook & Zoom Out:** O minimapa de Cards agora reage à rolagem central do mouse (`Scroll Scale`) e pode ser deslizado mantendo o clique ativado (`ScrollHandDrag`), provendo liberdade sobre painéis gigantescos de Inteligência Artificial.
- **Toggle de Adoção de Agentes:** Toda IA recém forjada ou importada possui um Toggle "Integrar ao Chat Global". Se habilitado, sua IA entra na lista do `ComboBox` principal do app, substituindo os modelos padrões pelas capacidades de persona instruídas na sua árvore BotForge!
- **Proteção Imortal JSON:** A importação Web parou de ser efêmera. Modelos importados são validados para evitar duplicação (*"Sobrescrever"* ou *"Copiar"*) e efetivados fisicamente na camada de `manager.save_models()`.
- **Dinâmica Modal & Anti-Trace Line:** O Modal de NodeConfig abandona os arrays mortos e lê `out_labels` dinamicamente com seletores coloridos nativos. Por debaixo dos panos, o Bug *Pink-Squiggle-Trail* (conhecido pelo arrastar pesado) foi extinto junto da devolução lógica visual de links nativos JSON restaurados em tempo real (`update_path`).

### V0.4.9-rev19.0.9-070426 | Build 19.0 | Rev 19.0.9 | Imp S | Homologação

**Resumo:** Integração de Tipografia Inline em Multi-Portas e Texturização de Conexões Inteligentes.

#### 🖌️ Melhorias Gráficas (Rev 19.0.9)
- **Rotas Roteadas Visíveis:** Os modais NLP agora imprimem os labels (`Cardápio`, `Pedido`, `Status`) de dentro para fora na borda direita ao lado de seus exatos pontos de controle, provendo visão periférica total do fluxo.
- **Cores Adaptativas Globais:** Os blocos não-nativos importados (os mais de 20 customs de Lojas do BotForge) pararam de herdar azul pálido. Implementamos um sub-sistema de *Hashing* de String na conversão JSON para colorí-los com as exatas 9 texturas bases de paletas Web.
- **Conexões Sensíveis ao Tipo:** A `FlowConnection` discerne de onde ela parte. Linhas nascidas de pontas de Roteadores NLP são geradas em grafia tracejada (DashLine). Linhas centrais fluem integralmente como traços sólidos até o destino.

### V0.4.9-rev19.0.8-070426 | Build 19.0 | Rev 19.0.8 | Imp S | Homologação

**Resumo:** Recriação tática do Modal Avançado NLP do projeto Web e correção de Multi-Portas.

#### 🔧 Avanços (Rev 19.0.8)
- **Modal Expert:** Destruído o layout antigo `QMessageBox`. No lugar instanciamos `NodeConfigModal`, um painel visual dark com sliders estéticos, roteamento inteligente e "Configuração de Inteligência (Fuzzy)" visível ao dar duplo clique num card gráfico.
- **Saídas Múltiplas Coloridas:** Inteligência artificial aplicada à pintura dos Cards; Se o Card contiver `Router`/`NLP`, o Qt divide dinamicamente o espaço da borda direita e plota `N` pinos de saídas de cores personalizadas, suportando até 9 rotas.
- **Física da Tensão Gráfica:** Extirpados os rastros / sobras no desenho durante um Drag N' Drop. A matemática do `boundingRect()` de Bézier (`QGraphicsPathItem`) foi refeita baseada nas pontas flutuantes das curvas. As conexões puxam organicamente dados coloridos dos pontos onde nasceram.

### V0.4.9-rev19.0.7-070426 | Build 19.0 | Rev 19.0.7 | Imp S | Homologação

**Resumo:** Remodelação completa do renderizador visual (Canvas) de *BotForge Studio*. Agora a visualização assume a paridade com a versão original Web.

#### 🎨 Ajustes Visuais (Rev 19.0.7)
- **Grid Magnético & Cenário:** Implementação cartográfica pontilhada nativa via `QLineF` em um grid noturno (`#0e1116`), removendo o fundo liso e imitando o Web Editor.
- **Node Design Premium:** Retângulos expandidos com cantos perfeitamente curvados e uma tarja geométrica da cor nativa de sua tag na sua lateral esquerda. Novas tipografias inter-arredondadas para os labels.
- **Portas & Conexões Orgânicas (Bézier):** Substituição das retas poligonais rígidas para cabos em *DashLine* arredondados que se inclinam conforme a tensão (`cubicTo`) num formato spline dinâmico até seus nós arredondados (*Ports*). 
- **Duplo Clique Analítico:** Adição de `mouseDoubleClickEvent` no Node renderizado para estourar um Modal revelando suas engrenagens invisíveis (*Node Type*, *ID*, e *Payload Mensagem*).

### V0.4.9-rev19.0.6-070426 | Build 19.0 | Rev 19.0.6 | Imp S | Homologação

**Resumo:** Unificação da engrenagem do visualizador BotForge que exibia canvas vazios em arquivos Web. Arquitetura adaptada para comportar matrizes não-padronizadas e topografias variadas.

#### 🚀 Correções (Rev 19.0.6)
- **BotForge Canvas Flow:** Ao invés de apresentar a tela preta `"Nenhum fluxo BotForge associado"`, a interface de detalhes de IA agora compreende o objeto `model._flow_nodes` unificado, seja pra imports via JSON Engine ou Web Engine (onde eles habitavam de forma oculta na raiz).
- **Auto-Correção Topográfica:** Adicional de fallback nativo para `position`, `ui`, além de eixos independentes `x/y`. O sistema varre `nodeId` vs `cardId` para renderizar os cards corretamente de forma flutuante como as extensões WEB nativas.
- **Roteamento de Nós:** Re-mapeamento nativo de conexões para comportar dicts web como `from` e `to` em paridade com `source` e `target`.

### V0.4.9-rev19.0.5-070426 | Build 19.0 | Rev 19.0.5 | Imp S | Homologação

**Resumo:** Hotfix final mitigatório sobre a tela de Consulta e Visualização do BotForge IAs. A engine de importação finalmente pareou a formatação legada perfeitamente com os combo boxes atuais de base_models.

#### 🚀 Correções (Rev 19.0.5)
- **BotForge Studio Viewer:** Consertado o Crash `index 0 has type 'dict' but 'str'` na aba de visualização ao disparar o trigger de *Provider Changed*. A listagem primária do manager fora refatorada em dicts complexos globalmente e o BotForge combo exigia um extrator iterador `[m.get('id',...) if isinstance... ]` para absorver os valores como strings para a UI C++. Agora 100% livre de colisões durante o View Profile.

### V0.4.9-rev19.0.4-070426 | Build 19.0 | Rev 19.0.4 | Imp S | Homologação

**Resumo:** Hotfixes direcionados nas dinâmicas de UX e de Parse. Correção de colapso de dicionário, bordas, persistência no salvamento de arquivo base (F5) e implementação do comando global (Ctrl+S).

#### 🚀 Correções (Rev 19.0.4)
- **UX UI Minimalista:** Remoção completa da barra limitadora `|` (`border-right`) inserida equivocadamente na Activity Bar, unificando a área de exploração.
- **BotForge Viewer:** Resolvido log de colisão `TypeError: dict to str` envolvendo PyQt6 e FlowNodes que explodiam na tela com fluxos recém importados.
- **Novos Arquivos + Prompt:** Ao clicar no `+` na barra de abas agora solicitará o nome inicial do arquivo em painel input, atribuindo asteriscos (`*`) de status *Unsaved*. Acionado também captação direta de Shortcut do `Ctrl + S` para salvamentos contínuos no editor interno, limpando o asterisco no processo e evitando que runners do background confudam as flags do File System.
- **Runner JS/F5 Temp:** Consertado o script temporário do Node de não-execução de cód. Limpo quando executáveis entravam em choque com a ausência do escopo na string nominal da Tab.

### V0.4.9-rev19.0.3-070426 | Build 19.0 | Rev 19.0.3 | Imp S | Homologação

**Resumo:** Refatoração de interface (Top Bar e Chat), correção na persistência de extensões em arquivos temporários (F5 Terminal) e integração plena do Flow Scene no visualizador BotForge Studio.

#### 🚀 Funcionalidades Novas e Correções (Rev 19.0.3)

- **UX/UI Interface Global:** Limpeza da *Top Bar* com a remoção de botões redundantes (Nova IA, Novo). Estilização em botões de "Configurações" e "Sobre".
- **Chat Premium (Minimalista):** Remoção de balões grandes engessados e introdução de Layout 4 dinâmico para os balões da IA e Usuário. Chat e Input ganharam visuais polidos, com padding reduzido nas bolhas de `ChatMessage`.
- **Atalho no Chat:** Restaurada lógica dinâmica do botão Toggle (`<` e `>`) do chat.
- **Explorer + Arquivos:** Botão de Criar Guias embutido dentro da aba superior (Corner Widget). Header *EXPLORER* refeito com botões `[+ Arquivo]`, `[+ Pasta]` e `[↻ Refresh]`.
- **F5 Node/Runner Fix:** Corrige bug fatal de `SyntaxError/ReferenceError` onde a execução de arquivos com `F5` gerava extensões cruas para o `.py` padrão.
- **BotForge Visual Studio:** Refatorado `_show_details`. Ao inspecionar IAs (`ai_consult.py`) modelos BotForge carregam o canvas `FlowView` e restauram nós/layouts importados do Flow Original ao invés de mensagens de alerta brutos.

### V0.4.9-rev19.0.2-070426 | Build 19.0 | Rev 19.0.2 | Imp S | Homologação

**Resumo:** Revisão completa de UX/funcionalidade. Implementação de atalho F5 para execução de scripts no terminal integrado. Criação de painel de Extensões com Hello World para 8 linguagens de programação. Modernização dos balões de chat para responsividade. Importação inteligente de JSONs BotForge Web com detecção automática de schema. Explorer padrão aberto na pasta Documentos.

#### 🚀 Funcionalidades Novas (Rev 19.0.2)

- **Atalho F5 Global:** Pressionar F5 salva o conteúdo da aba ativa em arquivo temporário e executa no terminal integrado usando o runner correto (python, node, lua, dotnet...).
- **Botão + Novo:** Adicionado à barra superior para criação rápida de arquivos em branco como novas guias.
- **Painel de Extensões:** Nova sidebar com botões para 8 linguagens (Python, JS, TS, Lua, C#, HTML, CSS, Godot Script). Cada botão abre uma aba com Hello World pré-carregado e syntax highlighting.
- **Explorer → Documentos:** O explorador de arquivos agora abre por padrão na pasta Documentos do usuário ao invés da raiz do disco.
- **Terminal Azul:** Cor do texto do terminal alterada de verde (#39d353) para azul (#58a6ff) alinhado ao Layout 4.
- **Balões de Chat Responsivos:** Margens, espaçamento e dimensionamento dos bubbles refatorados para melhor legibilidade em diferentes resoluções.
- **Campo de Input Modernizado:** Novo design com bordas arredondadas, cores Layout 4 e placeholder atualizado.
- **Tooltips Detalhados:** Cada ícone da ActivityBar agora exibe descrição expandida.
- **Import BotForge Web:** Nova branch de detecção para JSONs exportados da versão web do BotForge (com chaves `exportedAt`, `cardTypes`, e dados do bot em chave dinâmica). Extração inteligente de nodes, connections e config.
- **Card BotForge em Ferramentas:** Adicionado card visual na aba Ferramentas Integradas do Settings com botão direto para abrir o BotForge Studio.
- **Versioning:** Projeto incrementado para `v0.4.9-rev19.0.2-070426`.


## Build 18 - 07/04/2026

### V0.4.8-b18-070426 | Build 18.0 | Rev 18.0.1 | Imp S | Implementação Flow Visual

**Resumo:** Migração completa da interface para o Layout 4 (GitHub Dark palette). Implementação de sistemas ricos de interface de fluxo com diagramação visual de cards e nós no BotForge Studio (Create AI). Refatoração estrutural nas telas para acomodar as novas identidades visuais de cartões e tabs. Integração visual para conexões com provedores de IA externos.

#### 📊 Layout & Componentes Visuais (Rev 18.0.1)

- **Layout 4 Adotado:** Aplicação consistente da paleta escura (GitHub Dark) baseada em `#0d1117`, `#161b22`, `#1c2128` no lugar do `#0b1426` em todas as telas principais, dialogs e popups (main window, create ai, settings e ai_consult).
- **Aba de Settings Atualizada:** Adicionado tab específico `Suas IAs` mostrando cards dos bots customizados implementados. Adicionado tab específico `Conexões IA` listando cards integrativos para Claude, OpenAI e DeepSeek.
- **BotForge Canvas Visual:** A Aba "Fluxo" no gerenciador de bots foi reescrita utilizando um framework visual baseado em Node Graphics `FlowView` e `FlowScene`, permitindo adicionar cartões e renderizá-los em um grid virtual de diagramação de processos visuais de conversa.
- **Painéis Unificados:** Os cards e layouts em `ai_consult.py` (Consulta BotForge) foram remodelados visualmente e receberam polimento CSS condizente com a v0.4.8. Compatibilidade estrita mantida de JSON (versão 6.0).
- **Versioning:** Projeto incrementado oficialmente para `v0.4.8`.


## Build 17 - 06/04/2026

### V0.4.7-b17-070426 | Build 17.0 | Rev 17.0.6 | Imp S | Homologação

**Resumo:** Restauração completa do layout v0.3.5-alpha conforme screenshot original. Reversão de Rev 17.0.4/17.0.5. Paleta azul escuro (#0b1426, #0f172a, #0ea5e9). Activity Bar + Terminal + Right Panel Chat restaurados.

#### 🔄 Layout Restaurado (Rev 17.0.6)

- **Activity Bar:** Barra vertical esquerda com ícones coloridos restaurada.
- **Terminal Integrado:** Painel inferior com ComboBox CMD/PowerShell/Bash.
- **Right Panel Chat:** Chat à direita com seletor DeepSeek/GPT-4/Claude.
- **Paleta Azul Escuro:** Interface migrada para #0b1426/#0f172a/#0ea5e9.
- **ManageAIDialog:** Classe reintroduzida para corrigir ImportError.
- **QKeySequence:** Import adicionado para corrigir lint.

---

### V0.4.7-b17-070426 | Build 17.0 | Rev 17.0.5 | Imp S | Homologação

**Resumo:** Engenharia reversa pixel-perfect do executável Tkinter v0.3.5-alpha. Correção completa das mensagens de chat (flat `#2d2d30`, sender `#007acc`), posição dos botões (todos à direita como no Tkinter `pack(side=RIGHT)`), input flat sem `border-radius`, e tab inicial `welcome.py` com texto de boas-vindas original.

#### 🔧 Correções Visuais (Rev 17.0.5)

- **ChatMessage:** Removidas bolhas arredondadas (`border-radius: 12px`). Agora usa fundo flat `#252526` com body `#2d2d30` idêntico ao `tk.Text` do Tkinter.
- **Sender Color:** Todas as mensagens usam `#007acc` (accent) para o nome do remetente, como `foreground=self.colors['accent']` no Tkinter.
- **Botões do Chat:** Reposicionados todos à DIREITA (stretch à esquerda), na ordem `Anexar | Limpar | Enviar` idêntico ao `pack(side=tk.RIGHT)` do Tkinter.
- **ChatInput:** Removido `border-radius`, agora flat com `border: 1px solid #424242` e altura fixa 90px (≈5 linhas do `scrolledtext`).
- **Tab welcome.py:** Substituídas abas `main.py`/`script.lua` por `welcome.py` com texto de boas-vindas original do v0.3.5-alpha.
- **ManageAIDialog:** Classe reintroduzida para corrigir `ImportError` que impedia execução.
- **Versionamento:** Atualizado para `V0.4.7-b17-070426 | Rev 17.0.5`.

---

### V0.4.7-b17-060426 | Build 17.0 | Rev 17.0.4 | Imp S | Homologação

**Resumo:** Restauração total do layout Tkinter real da v0.3.5-alpha (sem Activity Bar, título à esquerda + botões à direita, chat abaixo do editor). Integração completa do portal BotForge Studio com 6 abas no criador de IA (Dados, Fluxo, Chat Teste, Personalidade, Config Bot, Catálogo de 56 cards).

#### ✨ Novidades (Rev 17.0.4)

- **Layout Tkinter v0.3.5-alpha Real:** Remoção da Activity Bar lateral. Restauração do layout original: Top Bar com título "🤖 AI Code Assistant v0.3.5-alpha" à esquerda e botões "📂 Abrir Projeto", "➕ Nova IA", "⚙️ Configurações" à direita.
- **Chat IA Abaixo do Editor:** Chat reposicionado para split vertical (editor em cima, chat embaixo), idêntico ao Tkinter `main_legacy.py` da v0.3.5-alpha.
- **Explorer com Status:** Painel esquerdo com header "EXPLORER", botão refresh "↻" e label de status do projeto.
- **Botões de Chat Tkinter:** Layout "📎 Anexar Arquivo", "🗑️ Limpar Chat" à esquerda e "📤 Enviar Mensagem" à direita, como no original.
- **Status Bar v0.3.5:** Footer com "Ln 1, Col 1 | Python | Tokens: 0 | Rev 17.0.4" (sem cor azul, tema escuro consistente).
- **CreateAIDialog — 6 Abas BotForge Studio:**
  - 📋 **Dados Básicos:** Nome, descrição, provider, modelo, system prompt, temperatura, tokens, templates.
  - 🔗 **Fluxo:** Lista de nodes com tipo/label/mensagem + importação de fluxo JSON.
  - 💬 **Chat Teste:** Simulador de conversa local (respostas baseadas no fluxo, system prompt, personalidade e conhecimento).
  - 🎭 **Personalidade:** Saudação, tom (6 opções), 8 traços, criatividade (slider), conhecimento RAG, mensagem fallback.
  - ⚙️ **Config Bot:** Canal (WhatsApp/Web/Multi/Chat), status, número mestre, horários de funcionamento, PIX, telefone.
  - 📦 **Catálogo:** Grid visual de 56 tipos de cards em 6 categorias (Fluxo, IA & NLP, Recebimento, Envio, Integrações, Avançado). Clique adiciona card ao fluxo.
- **Simulador de Respostas Local:** Motor de respostas baseado nos dados configurados: saudações, keywords do fluxo, conhecimento base, system prompt, intenções (cardápio, preço, pedido, despedidas).
- **Importação Fluxo JSON:** Suporte a importar nodes de arquivos BotForge Studio (schema `ari->flow->nodes`).

#### 🔧 Correções (Rev 17.0.4)

- **Provider Map:** Combo de seleção de IA agora usa nomes completos ("OpenAI GPT-4", "Anthropic Claude", "DeepSeek", "Local").
- **open_project():** Atualiza label de status e mostra caminho do projeto aberto.
- **Métodos toggle:** `toggle_terminal`, `toggle_chat` simplificados (layout não possui esses painéis separados).
- **run_code():** Output redirecionado para status bar ao invés do terminal removido.
- **Paleta consistente:** Todas as janelas (CreateAI, AIConsult, Settings) uniformizadas na paleta v0.3.5-alpha (`#1e1e1e`, `#252526`, `#007acc`).

---

### V0.4.7-b17-060426 | Build 17.0 | Rev 17.0.3 | Imp S | Homologação

**Resumo:** Retrofit completo da interface para paleta visual v0.3.5-alpha com Activity Bar colorida, cards BotForge Studio ricos e sistema de logs para importação/exportação JSON.

#### ✨ Novidades (Rev 17.0.3)

- **Paleta Visual v0.3.5-alpha:** Cores `#1e1e1e`, `#252526`, `#181818`, `#007acc` aplicadas em toda a interface.
- **Activity Bar Restaurada:** Barra vertical com ícones coloridos (📁💬🧩🐞🧪🤖⚙️) idêntica à captura de tela v0.3.5.
- **Top Bar Completa:** Botões `Abrir Projeto`, `+ Nova IA`, `⚙️ Configurações` e `❓ Sobre` exatamente como na referência.
- **Cards BotForge Ricos:** Cards com ícone, status, provider, canal, conversas, tags, criador e botões de ação (Exportar, Detalhes, Excluir).
- **Log de Operações:** Painel de log em tempo real na janela de Consulta de IAs para rastreamento de importações e erros.
- **Importação BotForge Enhanced:** Suporte a schema completo `ari-milkshaketeria.json` (nodes, connections, cardTypes, config, mediaProcessing).
- **Botão "Criar Nova IA" funcional:** Na janela de Consulta, o botão agora abre o `CreateAIDialog` corretamente.
- **CREATE_INSTALLER.BAT Corrigido:** Variável VERSION corrigida de `0.4.16` para `0.4.7`.

---

### V0.4.7-b17-060426 | Build 17.0 | Rev 17.0.2 | Imp S | Homologação

**Resumo:** Correção do script de criação de instalador Windows e melhorias no fluxo de importação JSON e no botão de criação de IA dentro da Consulta.

#### 🔧 Correções (Rev 17.0.2)

- **CREATE_INSTALLER.BAT:** Variável `VERSION` corrigida de `0.4.16` para `0.4.7`, resolvendo erro "Executável não encontrado".
- **Importação JSON:** Tratamento avançado de erros com mensagens detalhadas ao usuário (arquivo vazio, JSON inválido, schema incompleto).
- **Botão "Criar Limpa":** Na janela de Consulta de IAs, o botão agora abre o `CreateAIDialog` em vez de exibir mensagem genérica.

---

### V0.4.7-b17-060426 | Build 17.0 | Rev 17.0.1 | Imp S | Homologação

**Resumo:** Retrofit da interface para o modelo clássico (Botões Superiores, Tema Retrô V0.3.5) utilizando o motor avançado PyQt6 e novos fluxos de IA.

#### ✨ Novidades (Features)

- **Retrofit Visual:** Reversão visual do layout v0.4.7 com ActivityBar para a Top Bar Clássica da versão v0.3.5-alpha, mantendo multi-threads PyQt6.
- **Novos Módulos BotForge:** Janelas de Criação ('Nova IA') e Consulta baseada em Cards integrados com JSON padrão do App Studio.
- **Exportação/Importação JSON:** Custom AIs agora podem ser transferidos via json na padronização ARI e BaseProvider.

#### 🚀 Melhorias (Improvements)

- Atualização nos scripts de automação `BUILD_v2.BAT`, `build_mac.py` e `build_linux.py` para versionamento v0.4.7-b17.

---

## Build 16 - 24/01/2026

### v0.4.b16-240126 | Build 16.0 | Rev 16.0.2 | Imp C | Homologação

**Resumo:** Ajustes nos scripts de compilação e criação de instaladores.

#### 🔧 Ajustes (Rev 16.0.2)

- **Scripts de Build Atualizados**
  - `BUILD_V2.BAT` atualizado para Windows com nova versão
  - `build.sh` atualizado para Linux com verificação de dependências
  - Inclusão de todos os hidden imports necessários
  - Cópia automática de docs, config e models

- **Criação de Instaladores**
  - Novo script `CREATE_INSTALLER.BAT` para Windows (NSIS ou ZIP)
  - Novo script `create_installer.sh` para Linux (.deb e .tar.gz)
  - Criação de atalhos no Desktop e Menu Iniciar
  - Suporte a desinstalação limpa

- **Documentação**
  - Atualização de CHANGELOGs em PT, EN, ES

---

### v0.4.b16-240126 | Build 16.0 | Rev 16.0.1 | Imp A+ | Homologação

**Resumo:** Implementação de sistema avançado de IAs personalizadas com treinamento, especialização por área e otimização de tokens.

#### ✨ Novidades (Features)

- **Sistema de IAs Personalizadas Sem Limite**
  - IAs customizadas agora retornam respostas completas sem truncagem
  - Limite de tokens aplicado APENAS para consultas a provedores externos (DeepSeek, Grok, Gemini, Claude, ChatGPT)
  - Sistema de streaming real para respostas longas

- **Sistema de Treinamento Avançado**
  - Seleção de projetos para aprendizagem da IA
  - Modo criativo para aprendizagem livre
  - Treinamento local e com uso de IAs externas para consulta
  - Visualização e gerenciamento de projetos de treinamento

- **Especialização por Área de IA**
  - **Criatividade e Código**: Claude Opus
  - **Geração de Imagens**: Gemini Nano Banana, Grok, ChatGPT
  - **Geração de Vídeos**: ChatGPT, Grok, Nano Banana
  - **Modelos 3D**: Meshy AI
  - **Texto para Fala**: Speechigy Studio
  - **Criação de Jogos**: Rosebud AI

- **Provedores Especializados**
  - Novo sistema de routing inteligente por tipo de tarefa
  - Integração com provedores especializados por categoria
  - Fallback automático entre provedores

#### 🚀 Melhorias (Improvements)

- **Streaming Real (Chunks)**
  - Respostas exibidas em tempo real conforme são geradas
  - Melhoria na experiência do usuário

- **Lazy Loading de Mensagens**
  - Carregamento sob demanda de mensagens antigas do chat
  - Redução do uso de memória

- **Virtualização de Lista de Arquivos**
  - Performance otimizada para projetos grandes
  - Renderização apenas dos itens visíveis

- **Otimização de Tokens**
  - Redução de 60-80% no consumo de tokens em consultas externas
  - Cache inteligente de respostas
  - Compressão de contexto de código

#### 📚 Documentação

- Criação de documentações multilíngues (PT, EN, ES)
- CHANGELOG atualizado em todos os idiomas
- TECHNOLOGIES atualizado em todos os idiomas

#### 🔧 Correções (Bug Fixes)

- Correção de memory leak ao manter muitas mensagens no chat
- Correção de threads não finalizadas ao fechar aplicação
- Melhoria na estabilidade geral do sistema

---

## Build 15 - 22/01/2026

### v0.3.b15-220126 | Build 15.0 | Rev 15.0.0 | Imp A | Homologação

**Resumo:** Introdução do sistema de IAs customizadas e otimização de tokens.

#### ✨ Novidades

- Sistema de criação de IAs customizadas
- Templates para diferentes tipos de assistentes
- Gerenciamento de IAs (criar, editar, excluir, exportar, importar)
- Sistema de cache de respostas

#### 🚀 Melhorias

- Token Optimizer integrado
- Response Cache implementado
- Sistema de fallback entre provedores

---

## Build 14 - 14/01/2026

### v0.3.6-b14-140126 | Build 14.0 | Rev 14.0.0 | Imp A | Homologação

**Resumo:** Versão inicial alpha com suporte a múltiplos provedores de IA.

#### ✨ Novidades

- Interface principal estilo VS Code
- Suporte a DeepSeek, OpenAI e Anthropic
- Editor de código com syntax highlighting
- Terminal integrado
- Chat com IA integrado

---

## Legenda de Versão

**Formato:** `v[VERSAO_SAAS].[bVERSAO_BUILD]-[DATA] | Build [VERSAO_BUILD] | Rev [REVISAO] | Imp [IMPORTANCIA] | [AMBIENTE]`

**Importância:**
- **S** (Crítico): Mudança estrutural
- **A** (Alta): Nova build com funcionalidades significativas
- **B** (Média): Correção de funcionalidades
- **C** (Baixa): Ajustes de UI/UX
- **D** (Mínima): Correções insignificantes

---

*Documento gerado em 24/01/2026*  
*Mantido por: @S.V.S - Try Technology*
