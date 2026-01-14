@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo AI Code Assistant - Build para Windows
echo ========================================

REM Obter o diretório onde este script está
set "SCRIPT_DIR=%~dp0"
echo Script directory: %SCRIPT_DIR%

REM Mudar para o diretório do script
cd /d "%SCRIPT_DIR%"
echo Current directory: %cd%

REM Verificar se estamos no diretório correto
if not exist src\main.py (
    echo.
    echo ERRO: Arquivo src\main.py nao encontrado!
    echo Certifique-se de que esta na raiz do projeto.
    echo.
    pause
    exit /b 1
)

echo.
echo Verificando estrutura do projeto...
if exist src\main.py echo ✓ src\main.py encontrado
if exist config\ echo ✓ Pasta config encontrada
if exist requirements.txt echo ✓ requirements.txt encontrado

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist build_windows rmdir /s /q build_windows 2>nul
if exist dist_windows rmdir /s /q dist_windows 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
del /q *.spec 2>nul
del /q *.log 2>nul

echo.
echo Criando diretórios...
if not exist build_windows mkdir build_windows
if not exist dist_windows mkdir dist_windows
if not exist config mkdir config
if not exist logs mkdir logs

echo.
echo Verificando config/settings.yaml...
if not exist config\settings.yaml (
    echo Criando config/settings.yaml...
    (
    echo app:
    echo   name: "AI Code Assistant"
    echo   version: "1.0.0"
    echo 
    echo ai:
    echo   default_provider: "openai"
    ) > config\settings.yaml
    echo ✓ config/settings.yaml criado
)

echo.
echo Executando PyInstaller...
echo Este processo pode levar alguns minutos...
echo.

REM Executar PyInstaller diretamente (sem desativar Windows Defender)
pyinstaller ^
  --name=AI_Code_Assistant ^
  --windowed ^
  --onefile ^
  --distpath=dist ^
  --workpath=build ^
  --clean ^
  --noupx ^
  src\main.py

if errorlevel 1 (
    echo.
    echo ERRO: PyInstaller falhou!
    echo.
    echo Tentando metodo alternativo...
    call :alternate_build
    if errorlevel 1 (
        pause
        exit /b 1
    )
)

echo.
echo Verificando executável...
if exist dist\AI_Code_Assistant.exe (
    echo ✓ Executavel criado com sucesso!
    
    REM Mover para dist_windows
    move dist\AI_Code_Assistant.exe dist_windows\ >nul 2>&1
    if exist dist_windows\AI_Code_Assistant.exe (
        for %%F in (dist_windows\AI_Code_Assistant.exe) do (
            set /a size=%%~zF/1048576
            echo ✓ Movido para: dist_windows\AI_Code_Assistant.exe
            echo ✓ Tamanho: !size! MB
        )
    )
    
    REM Copiar arquivos adicionais
    echo.
    echo Copiando arquivos adicionais...
    if exist config xcopy config dist_windows\config /E /I /Y >nul 2>&1 && echo ✓ Configuracoes copiadas
    if exist README.md copy README.md dist_windows\ >nul 2>&1 && echo ✓ README.md copiado
    if exist requirements.txt copy requirements.txt dist_windows\ >nul 2>&1 && echo ✓ requirements.txt copiado
    
    echo.
    echo ========================================
    echo BUILD CONCLUIDO COM SUCESSO!
    echo ========================================
    echo.
    echo Executavel criado em: dist_windows\AI_Code_Assistant.exe
    echo.
    echo Para testar, execute: dist_windows\AI_Code_Assistant.exe
    echo.
    echo NOTA: Se o Windows Defender bloquear:
    echo 1. Clique direito no executavel
    echo 2. Escolha "Propriedades"
    echo 3. Na aba "Geral", marque "Desbloquear"
    echo 4. Clique em "Aplicar" e "OK"
    echo.
    
) else (
    echo ✗ Executavel nao foi criado!
    echo.
    echo Verificando se ha arquivo .spec...
    if exist AI_Code_Assistant.spec (
        echo Tentando build usando arquivo .spec...
        pyinstaller --clean AI_Code_Assistant.spec
        if exist dist\AI_Code_Assistant.exe (
            move dist\AI_Code_Assistant.exe dist_windows\ >nul
            echo ✓ Executavel criado via .spec
        )
    )
)

echo.
echo Limpando arquivos temporarios...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
del /q *.spec 2>nul
del /q *.log 2>nul

echo.
echo ========================================
echo PROCESSO CONCLUIDO
echo ========================================
pause
exit /b 0

:alternate_build
echo.
echo Metodo alternativo: Build simples...
echo.
REM Metodo mais simples
pyinstaller --name=AI_Code_Assistant --windowed --onefile --clean src\main.py
if errorlevel 1 (
    echo ✗ Metodo alternativo falhou!
    exit /b 1
)
exit /b 0