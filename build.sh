#!/bin/bash

echo "========================================"
echo "AI Code Assistant - Build para Linux"
echo "========================================"
echo

# Ir para o diretório do script
cd "$(dirname "$0")"

# Verificar se python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: python3 não encontrado."
    exit 1
fi

# Criar ambiente virtual se não existir ou estiver quebrado
if [ ! -f "venv_linux/bin/activate" ]; then
    echo "Criando ambiente virtual (venv_linux)..."
    rm -rf venv_linux
    python3 -m venv venv_linux
fi

# Ativar venv e instalar dependências
echo "Ativando ambiente virtual e verificando dependências..."
source venv_linux/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Executar o script de build especializado para Linux
echo
echo "Iniciando processo de build..."
python build_linux.py

if [ $? -eq 0 ]; then
    echo
    echo "✓ Processo finalizado."
    deactivate
else
    echo
    echo "✗ Erro durante o build."
    deactivate
    exit 1
fi
