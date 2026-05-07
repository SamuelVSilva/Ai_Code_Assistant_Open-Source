#!/bin/bash
# Script de Build do AI Code Assistant para Linux
# Versao: v0.4.11-rev1.2.17-s64-060526 | homologacao

VERSION="0.4.11"
BUILD_DATE="060526"
APP_NAME="AI_Code_Assistant"
OUTPUT_DIR="AI_C_A-v0.4.11-rev1.2.17-s64_linux"
REV="1.2.17-s64"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===============================================================${NC}"
echo -e "${BLUE}   AI Code Assistant - Build para Linux${NC}"
echo -e "${BLUE}   Versao: v${VERSION}-rev${REV}-${BUILD_DATE} | homologacao${NC}"
echo -e "${BLUE}   Developer: @S.V.S - Try Technology${NC}"
echo -e "${BLUE}===============================================================${NC}"
echo ""

# Ir para o diretorio base
cd "$(dirname "$0")/.."
echo "Diretorio: $(pwd)"
echo ""

echo -e "${YELLOW}[1/7] Verificando dependências base (python3, pip, etc)...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERRO] python3 não encontrado. Instale-o com 'sudo apt install python3 python3-pip'${NC}"
    exit 1
fi
python3 --version
echo -e "${GREEN}[OK] Python encontrado.${NC}"

echo -e "${YELLOW}[2/7] Instalando libs via pip...${NC}"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt pyinstaller --quiet
echo -e "${GREEN}[OK] Dependências instaladas.${NC}"

# Verificação explícita de dependências críticas
python3 -c "import PyQt6; import requests; print('[OK] PyQt6 e requests verificados')"
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRO CRITICO] PyQt6 ou requests nao encontrados!${NC}"
    echo -e "${RED}Tente: pip3 install PyQt6 requests${NC}"
    exit 1
fi

echo -e "${YELLOW}[3/7] Limpando diretórios antigos...${NC}"
rm -rf "$OUTPUT_DIR" build dist *.spec

echo -e "${YELLOW}[4/7] Preparando ambiente...${NC}"
mkdir -p build/temp "$OUTPUT_DIR"

echo -e "${BLUE}===============================================================${NC}"
echo -e "${YELLOW}[5/7] Executando PyInstaller (Aguarde alguns minutos)...${NC}"
echo -e "${BLUE}===============================================================${NC}"

# No Linux, o separador de path pro pyinstaller é os ':' e não ';'
python3 -m PyInstaller \
    --name="${APP_NAME}_v${VERSION}" \
    --windowed \
    --onefile \
    --noupx \
    --distpath="$OUTPUT_DIR" \
    --workpath="build/temp" \
    --add-data "config:config" \
    --add-data "docs:docs" \
    --add-data "models:models" \
    --add-data "templates-modelos:templates-modelos" \
    --hidden-import=PyQt6 \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.sip \
    --hidden-import=openai \
    --hidden-import=anthropic \
    --hidden-import=yaml \
    --hidden-import=watchdog \
    --hidden-import=pygments \
    --hidden-import=pygments.lexers \
    --hidden-import=pygments.formatters \
    --hidden-import=tiktoken \
    --hidden-import=requests \
    --hidden-import=requests.adapters \
    --hidden-import=requests.models \
    --hidden-import=urllib3 \
    --hidden-import=charset_normalizer \
    --hidden-import=certifi \
    --hidden-import=idna \
    --hidden-import=aiofiles \
    --hidden-import=src.core \
    --hidden-import=src.core.richie_ai \
    --hidden-import=src.core.ai_manager \
    --hidden-import=src.core.custom_ai_manager \
    --hidden-import=src.core.training_manager \
    --hidden-import=src.core.token_optimizer \
    --hidden-import=src.core.response_cache \
    --hidden-import=src.core.project_manager \
    --hidden-import=src.core.json_flow_engine \
    --hidden-import=src.gui \
    --hidden-import=src.gui.main_window \
    --hidden-import=src.gui.dialogs \
    --hidden-import=src.gui.dialogs.create_ai_dialog \
    --hidden-import=src.gui.dialogs.training_dialog \
    --hidden-import=src.gui.dialogs.settings_window \
    --hidden-import=src.gui.dialogs.extension_store_sidebar \
    --hidden-import=src.gui.dialogs.extension_store_view \
    --hidden-import=src.providers \
    src/main.py

echo ""

if [ -f "$OUTPUT_DIR/${APP_NAME}_v${VERSION}" ]; then
    echo -e "${GREEN}===============================================================${NC}"
    echo -e "${GREEN}[6/7] BUILD LINUX CONCLUÍDO COM SUCESSO!${NC}"
    echo -e "${GREEN}===============================================================${NC}"
    
    echo -e "${YELLOW}[7/7] Copiando arquivos extras...${NC}"
    [ -d "config" ] && cp -r config "$OUTPUT_DIR/"
    [ -d "docs" ] && cp -r docs "$OUTPUT_DIR/"
    [ -d "models" ] && cp -r models "$OUTPUT_DIR/"
    [ -f "README.md" ] && cp README.md "$OUTPUT_DIR/"
    [ -f ".env.example" ] && cp .env.example "$OUTPUT_DIR/"
    mkdir -p "$OUTPUT_DIR/templates-modelos"
    
    echo "v${VERSION}-rev${REV}-${BUILD_DATE} | homologacao | LINUX" > "$OUTPUT_DIR/VERSION.txt"
    
    echo "Permissão de execução sendo aplicada no binário..."
    chmod +x "$OUTPUT_DIR/${APP_NAME}_v${VERSION}"
    
    SIZE=$(du -h "$OUTPUT_DIR/${APP_NAME}_v${VERSION}" | cut -f1)
    echo ""
    echo -e "${GREEN}Tudo pronto! Executável: $OUTPUT_DIR/${APP_NAME}_v${VERSION} (${SIZE})${NC}"
    echo "Para executar: ./$OUTPUT_DIR/${APP_NAME}_v${VERSION}"
else
    echo -e "${RED}[ERRO] A compilação falhou.${NC}"
fi
