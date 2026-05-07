@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title Build AI Code Assistant v0.4.9 - Windows

echo ===============================================================
echo    AI Code Assistant - Build para Windows
echo    Versao: V0.4.9-rev19.0.3-070426 ^| Homologacao
echo    Developer: @S.V.S - Try Technology
echo ===============================================================
echo.
REM Limpar builds com nomes zumbis que ficaram travados no sistema de arquivos
for /d %%D in (build_windows_v*) do (
    rmdir /s /q "%%D" 2>nul
)

REM Definir variaveis de versao limpas
set VERSION=0.4.9
set BUILD_DATE=070426
set APP_NAME=AI_Code_Assistant
set OUTPUT_DIR=build_windows_v%VERSION%_%RANDOM%

cd /d "%~dp0.."
echo Diretorio: %cd%
echo.

REM Fechar processos do app que possam estar rodando para evitar File Lock
echo [0/8] Encerrando processos abertos do AI Code Assistant...
taskkill /F /IM "%APP_NAME%_v%VERSION%.exe" /T 2>nul
taskkill /F /IM "%APP_NAME%.exe" /T 2>nul
REM Espera 2 segundos para o SO liberar handles e arquivos
timeout /t 2 /nobreak >nul
echo.


REM Verificar Python
set PY_BUILD=py
echo [1/8] Verificando Python...
%PY_BUILD% --version
if %errorlevel% neq 0 (
    set PY_BUILD=python
    %PY_BUILD% --version
    if !errorlevel! neq 0 (
        echo [ERRO] Python nao encontrado. Instale Python 3.11+.
        pause
        exit /b 1
    )
)
echo [OK] Python encontrado.
echo.

REM Instalar/Atualizar dependencias
echo [2/8] Verificando e instalando dependencias...
%PY_BUILD% -m pip install --upgrade pip --quiet
%PY_BUILD% -m pip install -r requirements.txt pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [AVISO] Algumas dependencias podem nao ter sido instaladas.
)
echo [OK] Dependencias verificadas.
echo.

REM Limpar builds anteriores
echo [3/8] Limpando builds anteriores...
rmdir /s /q %OUTPUT_DIR% 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul
echo [OK] Limpeza concluida.
echo.

REM Criar diretorios
echo [4/8] Criando estrutura de diretorios...
mkdir build 2>nul
mkdir build\temp 2>nul
mkdir %OUTPUT_DIR% 2>nul
echo [OK] Diretorios criados.
echo.

echo ===============================================================
echo [5/8] Executando PyInstaller...
echo Aguarde, pode levar alguns minutos...
echo ===============================================================
echo.

REM Executar build com todos os imports necessarios
%PY_BUILD% -m PyInstaller ^
    --name=%APP_NAME%_v%VERSION% ^
    --windowed ^
    --onefile ^
    --noupx ^
    --distpath=%OUTPUT_DIR% ^
    --workpath=build\temp ^
    --add-data "config;config" ^
    --add-data "docs;docs" ^
    --add-data "models;models" ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=openai ^
    --hidden-import=anthropic ^
    --hidden-import=yaml ^
    --hidden-import=watchdog ^
    --hidden-import=pygments ^
    --hidden-import=pygments.lexers ^
    --hidden-import=pygments.formatters ^
    --hidden-import=tiktoken ^
    --hidden-import=aiofiles ^
    src\main.py

if %errorlevel% neq 0 (
    echo.
    echo ===============================================================
    echo [ERRO FATAL] O PyInstaller encontrou um erro e nao conseguiu compilar.
    echo Certifique-se de que nenhum terminal ou aplicativo externo esteja
    echo bloqueando os arquivos da pasta '%OUTPUT_DIR%'.
    echo ===============================================================
    pause
    exit /b %errorlevel%
)

echo.

REM Verificar resultado
if exist "%OUTPUT_DIR%\%APP_NAME%_v%VERSION%.exe" (
    echo ===============================================================
    echo [6/8] BUILD CONCLUIDO COM SUCESSO!
    echo ===============================================================
    echo.
    
    for %%F in ("%OUTPUT_DIR%\%APP_NAME%_v%VERSION%.exe") do (
        set /a size_mb=%%~zF/1048576
        echo Executavel: %%~nxF
        echo Tamanho: !size_mb! MB
    )
    echo.
    
    REM Copiar recursos adicionais
    echo [7/8] Copiando recursos adicionais...
    
    if exist config ( xcopy /E /I /Y config %OUTPUT_DIR%\config >nul 2>&1 )
    if exist docs ( xcopy /E /I /Y docs %OUTPUT_DIR%\docs >nul 2>&1 )
    if exist models ( xcopy /E /I /Y models %OUTPUT_DIR%\models >nul 2>&1 )
    if exist README.md ( copy /Y README.md %OUTPUT_DIR%\ >nul 2>&1 )
    if exist .env.example ( copy /Y .env.example %OUTPUT_DIR%\ >nul 2>&1 )
    mkdir %OUTPUT_DIR%\templates-modelos 2>nul
    echo [OK] Pasta templates-modelos criada para persistencia de IAs.
    
    REM Criar arquivo de versao
    echo V%VERSION%-rev19.0.3-%BUILD_DATE% > %OUTPUT_DIR%\VERSION.txt
    
    echo [8/8] Finalizacao.
    echo.
    echo ===============================================================
    echo APLICACAO PRONTA PARA DISTRIBUICAO!
    echo Pasta: %OUTPUT_DIR%\
    echo ===============================================================
    echo.
) else (
    echo ===============================================================
    echo [ERRO] BUILD FALHOU
    echo ===============================================================
    echo.
)

pause
