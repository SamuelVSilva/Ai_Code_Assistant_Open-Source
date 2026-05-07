# TECNOLOGIAS - AI Code Assistant

**Documento de Tecnologias Utilizadas**  
**Versão:** V0.4.7-b17-060426  
**Idioma:** Português (Brasil)

---

## Índice

1. [Stack Principal](#stack-principal)
2. [Provedores de IA](#provedores-de-ia)
3. [Especializações por Área](#especializações-por-área)
4. [Custos por Provider](#custos-por-provider)
5. [Templates de IA](#templates-de-ia)
## Arquitetura

---

## Stack Principal

### Frontend/Desktop

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem principal |
| PyQt6 | 6.6+ | Interface gráfica |
| Pygments | 2.17+ | Syntax highlighting |

### Backend/Core

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| tiktoken | 0.5+ | Contagem de tokens |
| requests | 2.31+ | Requisições HTTP |
| PyYAML | 6.0+ | Configurações |
| openai | 1.0+ | SDK OpenAI |
| anthropic | 0.8+ | SDK Anthropic |

---

## Provedores de IA

### Provedores Suportados

| Provider | Modelos Disponíveis | Especialidade |
|----------|---------------------|---------------|
| **OpenAI** | GPT-4 Turbo, GPT-4, GPT-3.5 Turbo | Propósito geral, código |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | Análise, criatividade, código |
| **DeepSeek** | DeepSeek Coder, DeepSeek Chat | Código (custo muito baixo) |
| **Grok** | Grok 2 | Criatividade, análise |
| **Gemini** | Gemini Pro, Gemini Nano Banana | Multimodal, imagens |

### Provedores Especializados (Planejados)

| Provider | Especialidade | Status |
|----------|--------------|--------|
| **Meshy AI** | Modelos 3D | 🔜 Planejado |
| **Speechigy Studio** | Texto para Fala | 🔜 Planejado |
| **Rosebud AI** | Criação de Jogos | 🔜 Planejado |
| **Runway ML** | Geração de Vídeo | 🔜 Planejado |

---

## Especializações por Área

### Criatividade, Identificação de Imagens e Programação

| IA Recomendada | Especialidade |
|----------------|---------------|
| **Claude Opus** | Máxima qualidade em análise e criatividade |
| **Claude 3.5 Sonnet** | Código e análise balanceados |
| **DeepSeek Coder** | Código com baixo custo |

### Geração de Imagens (Reais e Criativas)

| IA Recomendada | Tipo de Imagem |
|----------------|----------------|
| **Gemini Nano Banana** | Imagens realistas |
| **Grok** | Imagens criativas |
| **ChatGPT (DALL-E)** | Propósito geral |

### Geração de Vídeos

| IA Recomendada | Funcionalidade |
|----------------|----------------|
| **ChatGPT (Sora)** | Vídeo de alta qualidade |
| **Grok** | Vídeos criativos |
| **Nano Banana** | Vídeos rápidos |

### Modelos 3D

| IA Recomendada | Funcionalidade |
|----------------|----------------|
| **Meshy AI** | Texto/Imagem para 3D |
| **TripoSR** | Imagem para 3D |
| **Shap-E** | Texto para 3D |

### Texto para Fala e Modelos de Vozes

| IA Recomendada | Funcionalidade |
|----------------|----------------|
| **Speechigy Studio** | TTS alta qualidade |
| **ElevenLabs** | Clonagem de voz |
| **Coqui TTS** | TTS local |

### Criação de Jogos

| IA Recomendada | Funcionalidade |
|----------------|----------------|
| **Rosebud AI** | Jogos 2D/3D do zero |
| **Claude Opus** | Game design e código |

---

## Custos por Provider (por 1000 tokens)

| Provider | Input ($) | Output ($) | Melhor Para |
|----------|-----------|------------|-------------|
| **DeepSeek** | $0.0001 | $0.0002 | Código (100x mais barato) |
| **GPT-3.5 Turbo** | $0.0005 | $0.0015 | Tarefas simples |
| **Claude Haiku** | $0.00025 | $0.00125 | Rápido e barato |
| **Claude Sonnet** | $0.003 | $0.015 | Balanceado |
| **GPT-4 Turbo** | $0.01 | $0.03 | Alta qualidade |
| **Claude Opus** | $0.015 | $0.075 | Máximo |

**💡 Recomendação:** Use DeepSeek para código e Claude/GPT para tarefas complexas.

---

## Templates de IA Disponíveis

| Template | Temperatura | Melhor Para |
|----------|-------------|-------------|
| **Assistente de Código** | 0.3 | Programação, debug |
| **Escritor Criativo** | 0.9 | Textos, histórias |
| **Analista de Dados** | 0.2 | Análise, relatórios |
| **Tutor Educacional** | 0.5 | Ensino, explicações |
| **IA em Branco** | 0.7 | Customização total |

---

## Arquitetura

### Camadas do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAMADA DE APRESENTAÇÃO                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  Chat   │  │ Editor  │  │ 3D View │  │ Media   │            │
│  │ Widget  │  │  Code   │  │  Panel  │  │ Player  │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼──────────────────┐
│                     CAMADA DE ORQUESTRAÇÃO                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Token     │  │   Response   │  │   Custom AI  │           │
│  │  Optimizer   │  │    Cache     │  │   Manager    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      CAMADA DE PROVIDERS                        │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ OpenAI │ │ Claude │ │DeepSeek│ │  Grok  │ │ Gemini │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Fluxo de Tokens

```
Usuário → [IA Personalizada] → Sem Limite de Retorno ✅
         ↓
         [Consulta Externa] → Limite Otimizado (tokens)
         ↓
         [Provedores: DeepSeek/Claude/GPT/etc] → Resposta
         ↓
         [Cache] → Economia de tokens futuros
```

---

## BotForge Studio Integration (Rev 17.0.4)

### Módulo de Criação de IA/Bot — 6 Abas

| Aba | Função |
|-----|--------|
| 📋 Dados Básicos | Nome, descrição, provider, modelo, system prompt, temperatura, tokens |
| 🔗 Fluxo | Lista de nodes do fluxo + importação de JSON BotForge |
| 💬 Chat Teste | Simulador de conversa local com motor de respostas baseado em configuração |
| 🎭 Personalidade | Saudação, tom, 8 traços, criatividade, conhecimento RAG, fallback |
| ⚙️ Config Bot | Canal (WhatsApp/Web/Multi), status, número mestre, horários, PIX |
| 📦 Catálogo | 56 tipos de cards em 6 categorias |

### Catálogo de Cards BotForge (56 tipos)

| Categoria | Qtd | Exemplos |
|-----------|-----|----------|
| 🔄 Fluxo | 8 | Saudação, Pergunta, Condição, Menu, Transferir, Encerrar |
| 🧠 IA & NLP | 7 | Resposta IA, ComboBox Keywords, NLP Router, Sentimento |
| 📥 Recebimento | 10 | Texto, Áudio, Imagem, Vídeo, Doc, Localização, Email, CPF |
| 📤 Envio | 9 | Msg, Áudio, Imagem, Botões, Lista, Sticker, Localização |
| 🔗 Integrações | 6 | API Call, Webhook, Banco Dados, CRM, Email, Agendar |
| 🚀 Avançado | 6 | Triagem, Análise Contexto, Notificar Mestre, Busca Web |

### Motor de Respostas Local

O Chat de Teste utiliza um motor de respostas local que simula o comportamento do bot sem necessidade de API externa:

1. **Saudações:** Detecta "oi", "olá", etc. e retorna o texto de saudação configurado
2. **Fluxo:** Verifica keywords dos nodes cadastrados no fluxo
3. **Conhecimento:** Busca termos no campo de conhecimento RAG
4. **System Prompt:** Retorna trechos do prompt para perguntas genéricas
5. **Intenções:** Detecta cardápio, preço, pedido, despedidas
6. **Fallback:** Mensagem padrão para entradas não reconhecidas

---

*Documento atualizado em 07/04/2026*  
*Mantido por: @S.V.S - Try Technology*
