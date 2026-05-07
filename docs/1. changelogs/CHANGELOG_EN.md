# CHANGELOG - AI Code Assistant

**Change History Document**  
**Version:** v0.4.b16-240126  
**Language:** English

---

## Index

- [Build 16 - 01/24/2026](#build-16---01242026)
- [Build 15 - 01/22/2026](#build-15---01222026)
- [Build 14 - 01/14/2026](#build-14---01142026)

---

## Build 16 - 01/24/2026

### v0.4.b16-240126 | Build 16.0 | Rev 16.0.2 | Imp C | Staging

**Summary:** Adjustments to build scripts and installer creation.

#### 🔧 Adjustments (Rev 16.0.2)

- **Updated Build Scripts**
  - `BUILD_V2.BAT` updated for Windows with new version
  - `build.sh` updated for Linux with dependency checking
  - Inclusion of all necessary hidden imports
  - Automatic copy of docs, config and models

- **Installer Creation**
  - New `CREATE_INSTALLER.BAT` script for Windows (NSIS or ZIP)
  - New `create_installer.sh` script for Linux (.deb and .tar.gz)
  - Desktop and Start Menu shortcut creation
  - Clean uninstall support

- **Documentation**
  - CHANGELOG updates in PT, EN, ES

---

### v0.4.b16-240126 | Build 16.0 | Rev 16.0.1 | Imp A+ | Staging

**Summary:** Implementation of advanced custom AI system with training, area specialization, and token optimization.

#### ✨ New Features

- **Unlimited Custom AI System**
  - Custom AIs now return complete responses without truncation
  - Token limit applied ONLY for external provider queries (DeepSeek, Grok, Gemini, Claude, ChatGPT)
  - Real streaming system for long responses

- **Advanced Training System**
  - Project selection for AI learning
  - Creative mode for free learning
  - Local training and with external AIs for consultation
  - Training project visualization and management

- **AI Area Specialization**
  - **Creativity and Code**: Claude Opus
  - **Image Generation**: Gemini Nano Banana, Grok, ChatGPT
  - **Video Generation**: ChatGPT, Grok, Nano Banana
  - **3D Models**: Meshy AI
  - **Text to Speech**: Speechigy Studio
  - **Game Creation**: Rosebud AI

- **Specialized Providers**
  - New intelligent routing system by task type
  - Integration with specialized providers by category
  - Automatic fallback between providers

#### 🚀 Improvements

- **Real Streaming (Chunks)**
  - Responses displayed in real-time as they are generated
  - Improved user experience

- **Lazy Loading of Messages**
  - On-demand loading of old chat messages
  - Reduced memory usage

- **File List Virtualization**
  - Optimized performance for large projects
  - Render only visible items

- **Token Optimization**
  - 60-80% reduction in token consumption for external queries
  - Smart response caching
  - Code context compression

#### 📚 Documentation

- Creation of multilingual documentation (PT, EN, ES)
- CHANGELOG updated in all languages
- TECHNOLOGIES updated in all languages

#### 🔧 Bug Fixes

- Fixed memory leak when keeping many messages in chat
- Fixed threads not terminating when closing application
- Improved overall system stability

---

## Build 15 - 01/22/2026

### v0.3.b15-220126 | Build 15.0 | Rev 15.0.0 | Imp A | Staging

**Summary:** Introduction of custom AI system and token optimization.

#### ✨ New Features

- Custom AI creation system
- Templates for different assistant types
- AI management (create, edit, delete, export, import)
- Response caching system

#### 🚀 Improvements

- Integrated Token Optimizer
- Implemented Response Cache
- Fallback system between providers

---

## Build 14 - 01/14/2026

### v0.3.6-b14-140126 | Build 14.0 | Rev 14.0.0 | Imp A | Staging

**Summary:** Initial alpha version with support for multiple AI providers.

#### ✨ New Features

- VS Code-style main interface
- Support for DeepSeek, OpenAI, and Anthropic
- Code editor with syntax highlighting
- Integrated terminal
- Integrated AI chat

---

## Version Legend

**Format:** `v[SAAS_VERSION].[bBUILD_VERSION]-[DATE] | Build [BUILD_VERSION] | Rev [REVISION] | Imp [IMPORTANCE] | [ENVIRONMENT]`

**Importance:**
- **S** (Critical): Structural change
- **A** (High): New build with significant features
- **B** (Medium): Functionality fixes
- **C** (Low): UI/UX adjustments
- **D** (Minimal): Insignificant corrections

---

*Document generated on 01/24/2026*  
*Maintained by: @S.V.S - Try Technology*
