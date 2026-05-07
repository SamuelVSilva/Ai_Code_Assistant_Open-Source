# TECHNOLOGIES - AI Code Assistant

**Technologies Used Document**  
**Version:** v0.4.b16-240126  
**Language:** English

---

## Index

1. [Main Stack](#main-stack)
2. [AI Providers](#ai-providers)
3. [Area Specializations](#area-specializations)
4. [Costs per Provider](#costs-per-provider)
5. [AI Templates](#ai-templates)
6. [Architecture](#architecture)

---

## Main Stack

### Frontend/Desktop

| Technology | Version | Usage |
|------------|---------|-------|
| Python | 3.11+ | Main language |
| PyQt6 | 6.6+ | GUI framework |
| Pygments | 2.17+ | Syntax highlighting |

### Backend/Core

| Technology | Version | Usage |
|------------|---------|-------|
| tiktoken | 0.5+ | Token counting |
| requests | 2.31+ | HTTP requests |
| PyYAML | 6.0+ | Configuration |
| openai | 1.0+ | OpenAI SDK |
| anthropic | 0.8+ | Anthropic SDK |

---

## AI Providers

### Supported Providers

| Provider | Available Models | Specialty |
|----------|-----------------|-----------|
| **OpenAI** | GPT-4 Turbo, GPT-4, GPT-3.5 Turbo | General purpose, code |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | Analysis, creativity, code |
| **DeepSeek** | DeepSeek Coder, DeepSeek Chat | Code (very low cost) |
| **Grok** | Grok 2 | Creativity, analysis |
| **Gemini** | Gemini Pro, Gemini Nano Banana | Multimodal, images |

### Specialized Providers (Planned)

| Provider | Specialty | Status |
|----------|----------|--------|
| **Meshy AI** | 3D Models | 🔜 Planned |
| **Speechigy Studio** | Text to Speech | 🔜 Planned |
| **Rosebud AI** | Game Creation | 🔜 Planned |
| **Runway ML** | Video Generation | 🔜 Planned |

---

## Area Specializations

### Creativity, Image Identification and Programming

| Recommended AI | Specialty |
|----------------|-----------|
| **Claude Opus** | Maximum quality in analysis and creativity |
| **Claude 3.5 Sonnet** | Balanced code and analysis |
| **DeepSeek Coder** | Low-cost code |

### Image Generation (Real and Creative)

| Recommended AI | Image Type |
|----------------|------------|
| **Gemini Nano Banana** | Realistic images |
| **Grok** | Creative images |
| **ChatGPT (DALL-E)** | General purpose |

### Video Generation

| Recommended AI | Functionality |
|----------------|--------------|
| **ChatGPT (Sora)** | High quality video |
| **Grok** | Creative videos |
| **Nano Banana** | Quick videos |

### 3D Models

| Recommended AI | Functionality |
|----------------|--------------|
| **Meshy AI** | Text/Image to 3D |
| **TripoSR** | Image to 3D |
| **Shap-E** | Text to 3D |

### Text to Speech and Voice Models

| Recommended AI | Functionality |
|----------------|--------------|
| **Speechigy Studio** | High quality TTS |
| **ElevenLabs** | Voice cloning |
| **Coqui TTS** | Local TTS |

### Game Creation

| Recommended AI | Functionality |
|----------------|--------------|
| **Rosebud AI** | 2D/3D games from scratch |
| **Claude Opus** | Game design and code |

---

## Costs per Provider (per 1000 tokens)

| Provider | Input ($) | Output ($) | Best For |
|----------|-----------|------------|----------|
| **DeepSeek** | $0.0001 | $0.0002 | Code (100x cheaper) |
| **GPT-3.5 Turbo** | $0.0005 | $0.0015 | Simple tasks |
| **Claude Haiku** | $0.00025 | $0.00125 | Fast and cheap |
| **Claude Sonnet** | $0.003 | $0.015 | Balanced |
| **GPT-4 Turbo** | $0.01 | $0.03 | High quality |
| **Claude Opus** | $0.015 | $0.075 | Maximum |

**💡 Recommendation:** Use DeepSeek for code and Claude/GPT for complex tasks.

---

## Available AI Templates

| Template | Temperature | Best For |
|----------|-------------|----------|
| **Code Assistant** | 0.3 | Programming, debug |
| **Creative Writer** | 0.9 | Texts, stories |
| **Data Analyst** | 0.2 | Analysis, reports |
| **Educational Tutor** | 0.5 | Teaching, explanations |
| **Blank AI** | 0.7 | Full customization |

---

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  Chat   │  │ Editor  │  │ 3D View │  │ Media   │            │
│  │ Widget  │  │  Code   │  │  Panel  │  │ Player  │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼──────────────────┐
│                      ORCHESTRATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Token     │  │   Response   │  │   Custom AI  │           │
│  │  Optimizer   │  │    Cache     │  │   Manager    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        PROVIDERS LAYER                          │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ OpenAI │ │ Claude │ │DeepSeek│ │  Grok  │ │ Gemini │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Token Flow

```
User → [Custom AI] → No Return Limit ✅
       ↓
       [External Query] → Optimized Limit (tokens)
       ↓
       [Providers: DeepSeek/Claude/GPT/etc] → Response
       ↓
       [Cache] → Future token savings
```

---

*Document generated on 01/24/2026*  
*Maintained by: @S.V.S - Try Technology*
