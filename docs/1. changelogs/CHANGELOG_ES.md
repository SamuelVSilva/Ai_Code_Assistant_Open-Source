# CHANGELOG - AI Code Assistant

**Documento de Historial de Cambios**  
**Versión:** v0.4.b16-240126  
**Idioma:** Español

---

## Índice

- [Build 16 - 24/01/2026](#build-16---24012026)
- [Build 15 - 22/01/2026](#build-15---22012026)
- [Build 14 - 14/01/2026](#build-14---14012026)

---

## Build 16 - 24/01/2026

### v0.4.b16-240126 | Build 16.0 | Rev 16.0.2 | Imp C | Homologación

**Resumen:** Ajustes en los scripts de compilación y creación de instaladores.

#### 🔧 Ajustes (Rev 16.0.2)

- **Scripts de Build Actualizados**
  - `BUILD_V2.BAT` actualizado para Windows con nueva versión
  - `build.sh` actualizado para Linux con verificación de dependencias
  - Inclusión de todos los hidden imports necesarios
  - Copia automática de docs, config y models

- **Creación de Instaladores**
  - Nuevo script `CREATE_INSTALLER.BAT` para Windows (NSIS o ZIP)
  - Nuevo script `create_installer.sh` para Linux (.deb y .tar.gz)
  - Creación de accesos directos en Escritorio y Menú Inicio
  - Soporte a desinstalación limpia

- **Documentación**
  - Actualización de CHANGELOGs en PT, EN, ES

---

### v0.4.b16-240126 | Build 16.0 | Rev 16.0.1 | Imp A+ | Homologación

**Resumen:** Implementación de sistema avanzado de IAs personalizadas con entrenamiento, especialización por área y optimización de tokens.

#### ✨ Novedades (Características)

- **Sistema de IAs Personalizadas Sin Límite**
  - Las IAs personalizadas ahora devuelven respuestas completas sin truncamiento
  - Límite de tokens aplicado SOLO para consultas a proveedores externos (DeepSeek, Grok, Gemini, Claude, ChatGPT)
  - Sistema de streaming real para respuestas largas

- **Sistema de Entrenamiento Avanzado**
  - Selección de proyectos para aprendizaje de la IA
  - Modo creativo para aprendizaje libre
  - Entrenamiento local y con uso de IAs externas para consulta
  - Visualización y gestión de proyectos de entrenamiento

- **Especialización por Área de IA**
  - **Creatividad y Código**: Claude Opus
  - **Generación de Imágenes**: Gemini Nano Banana, Grok, ChatGPT
  - **Generación de Videos**: ChatGPT, Grok, Nano Banana
  - **Modelos 3D**: Meshy AI
  - **Texto a Voz**: Speechigy Studio
  - **Creación de Juegos**: Rosebud AI

- **Proveedores Especializados**
  - Nuevo sistema de enrutamiento inteligente por tipo de tarea
  - Integración con proveedores especializados por categoría
  - Fallback automático entre proveedores

#### 🚀 Mejoras

- **Streaming Real (Chunks)**
  - Respuestas mostradas en tiempo real mientras se generan
  - Mejora en la experiencia del usuario

- **Carga Diferida de Mensajes**
  - Carga bajo demanda de mensajes antiguos del chat
  - Reducción del uso de memoria

- **Virtualización de Lista de Archivos**
  - Rendimiento optimizado para proyectos grandes
  - Renderizado solo de elementos visibles

- **Optimización de Tokens**
  - Reducción del 60-80% en el consumo de tokens en consultas externas
  - Caché inteligente de respuestas
  - Compresión de contexto de código

#### 📚 Documentación

- Creación de documentaciones multilingües (PT, EN, ES)
- CHANGELOG actualizado en todos los idiomas
- TECHNOLOGIES actualizado en todos los idiomas

#### 🔧 Correcciones (Bug Fixes)

- Corrección de fuga de memoria al mantener muchos mensajes en el chat
- Corrección de hilos no finalizados al cerrar la aplicación
- Mejora en la estabilidad general del sistema

---

## Build 15 - 22/01/2026

### v0.3.b15-220126 | Build 15.0 | Rev 15.0.0 | Imp A | Homologación

**Resumen:** Introducción del sistema de IAs personalizadas y optimización de tokens.

#### ✨ Novedades

- Sistema de creación de IAs personalizadas
- Plantillas para diferentes tipos de asistentes
- Gestión de IAs (crear, editar, eliminar, exportar, importar)
- Sistema de caché de respuestas

#### 🚀 Mejoras

- Token Optimizer integrado
- Response Cache implementado
- Sistema de fallback entre proveedores

---

## Build 14 - 14/01/2026

### v0.3.6-b14-140126 | Build 14.0 | Rev 14.0.0 | Imp A | Homologación

**Resumen:** Versión alfa inicial con soporte para múltiples proveedores de IA.

#### ✨ Novedades

- Interfaz principal estilo VS Code
- Soporte para DeepSeek, OpenAI y Anthropic
- Editor de código con resaltado de sintaxis
- Terminal integrado
- Chat con IA integrado

---

## Leyenda de Versión

**Formato:** `v[VERSAO_SAAS].[bVERSAO_BUILD]-[FECHA] | Build [VERSAO_BUILD] | Rev [REVISION] | Imp [IMPORTANCIA] | [AMBIENTE]`

**Importancia:**
- **S** (Crítico): Cambio estructural
- **A** (Alta): Nueva build con funcionalidades significativas
- **B** (Media): Corrección de funcionalidades
- **C** (Baja): Ajustes de UI/UX
- **D** (Mínima): Correcciones insignificantes

---

*Documento generado el 24/01/2026*  
*Mantenido por: @S.V.S - Try Technology*
