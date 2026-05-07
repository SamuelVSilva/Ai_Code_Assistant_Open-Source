# TECNOLOGÍAS - AI Code Assistant

**Documento de Tecnologías Utilizadas**  
**Versión:** v0.4.b16-240126  
**Idioma:** Español

---

## Índice

1. [Stack Principal](#stack-principal)
2. [Proveedores de IA](#proveedores-de-ia)
3. [Especializaciones por Área](#especializaciones-por-área)
4. [Costos por Proveedor](#costos-por-proveedor)
5. [Plantillas de IA](#plantillas-de-ia)
6. [Arquitectura](#arquitectura)

---

## Stack Principal

### Frontend/Desktop

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje principal |
| PyQt6 | 6.6+ | Interfaz gráfica |
| Pygments | 2.17+ | Resaltado de sintaxis |

### Backend/Core

| Tecnología | Versión | Uso |
|------------|---------|-----|
| tiktoken | 0.5+ | Conteo de tokens |
| requests | 2.31+ | Solicitudes HTTP |
| PyYAML | 6.0+ | Configuraciones |
| openai | 1.0+ | SDK OpenAI |
| anthropic | 0.8+ | SDK Anthropic |

---

## Proveedores de IA

### Proveedores Soportados

| Proveedor | Modelos Disponibles | Especialidad |
|-----------|---------------------|--------------|
| **OpenAI** | GPT-4 Turbo, GPT-4, GPT-3.5 Turbo | Propósito general, código |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | Análisis, creatividad, código |
| **DeepSeek** | DeepSeek Coder, DeepSeek Chat | Código (costo muy bajo) |
| **Grok** | Grok 2 | Creatividad, análisis |
| **Gemini** | Gemini Pro, Gemini Nano Banana | Multimodal, imágenes |

### Proveedores Especializados (Planificados)

| Proveedor | Especialidad | Estado |
|-----------|-------------|--------|
| **Meshy AI** | Modelos 3D | 🔜 Planificado |
| **Speechigy Studio** | Texto a Voz | 🔜 Planificado |
| **Rosebud AI** | Creación de Juegos | 🔜 Planificado |
| **Runway ML** | Generación de Video | 🔜 Planificado |

---

## Especializaciones por Área

### Creatividad, Identificación de Imágenes y Programación

| IA Recomendada | Especialidad |
|----------------|--------------|
| **Claude Opus** | Máxima calidad en análisis y creatividad |
| **Claude 3.5 Sonnet** | Código y análisis equilibrados |
| **DeepSeek Coder** | Código con bajo costo |

### Generación de Imágenes (Reales y Creativas)

| IA Recomendada | Tipo de Imagen |
|----------------|----------------|
| **Gemini Nano Banana** | Imágenes realistas |
| **Grok** | Imágenes creativas |
| **ChatGPT (DALL-E)** | Propósito general |

### Generación de Videos

| IA Recomendada | Funcionalidad |
|----------------|---------------|
| **ChatGPT (Sora)** | Video de alta calidad |
| **Grok** | Videos creativos |
| **Nano Banana** | Videos rápidos |

### Modelos 3D

| IA Recomendada | Funcionalidad |
|----------------|---------------|
| **Meshy AI** | Texto/Imagen a 3D |
| **TripoSR** | Imagen a 3D |
| **Shap-E** | Texto a 3D |

### Texto a Voz y Modelos de Voces

| IA Recomendada | Funcionalidad |
|----------------|---------------|
| **Speechigy Studio** | TTS alta calidad |
| **ElevenLabs** | Clonación de voz |
| **Coqui TTS** | TTS local |

### Creación de Juegos

| IA Recomendada | Funcionalidad |
|----------------|---------------|
| **Rosebud AI** | Juegos 2D/3D desde cero |
| **Claude Opus** | Diseño de juegos y código |

---

## Costos por Proveedor (por 1000 tokens)

| Proveedor | Input ($) | Output ($) | Mejor Para |
|-----------|-----------|------------|------------|
| **DeepSeek** | $0.0001 | $0.0002 | Código (100x más barato) |
| **GPT-3.5 Turbo** | $0.0005 | $0.0015 | Tareas simples |
| **Claude Haiku** | $0.00025 | $0.00125 | Rápido y barato |
| **Claude Sonnet** | $0.003 | $0.015 | Equilibrado |
| **GPT-4 Turbo** | $0.01 | $0.03 | Alta calidad |
| **Claude Opus** | $0.015 | $0.075 | Máximo |

**💡 Recomendación:** Use DeepSeek para código y Claude/GPT para tareas complejas.

---

## Plantillas de IA Disponibles

| Plantilla | Temperatura | Mejor Para |
|-----------|-------------|------------|
| **Asistente de Código** | 0.3 | Programación, debug |
| **Escritor Creativo** | 0.9 | Textos, historias |
| **Analista de Datos** | 0.2 | Análisis, informes |
| **Tutor Educativo** | 0.5 | Enseñanza, explicaciones |
| **IA en Blanco** | 0.7 | Personalización total |

---

## Arquitectura

### Capas del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  Chat   │  │ Editor  │  │ 3D View │  │ Media   │            │
│  │ Widget  │  │  Code   │  │  Panel  │  │ Player  │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼──────────────────┐
│                      CAPA DE ORQUESTACIÓN                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Token     │  │   Response   │  │   Custom AI  │           │
│  │  Optimizer   │  │    Cache     │  │   Manager    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                       CAPA DE PROVEEDORES                       │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ OpenAI │ │ Claude │ │DeepSeek│ │  Grok  │ │ Gemini │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Tokens

```
Usuario → [IA Personalizada] → Sin Límite de Retorno ✅
          ↓
          [Consulta Externa] → Límite Optimizado (tokens)
          ↓
          [Proveedores: DeepSeek/Claude/GPT/etc] → Respuesta
          ↓
          [Caché] → Ahorro de tokens futuros
```

---

*Documento generado el 24/01/2026*  
*Mantenido por: @S.V.S - Try Technology*
