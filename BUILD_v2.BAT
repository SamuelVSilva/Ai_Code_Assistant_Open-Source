@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title Build AI Code Assistant v0.3.6 - Windows

echo ========================================
echo AI Code Assistant - Build para Windows
echo Versao: v0.3.6-14012026-alpha
echo ========================================
echo.

cd /d "%~dp0"
echo Diretorio: %cd%
echo.

REM Usar Python global (py launcher)
set PY_BUILD=py

echo [OK] Usando Python global: %PY_BUILD%
%PY_BUILD% --version
echo.

REM Limpar builds anteriores
echo Limpando builds anteriores...
rmdir /s /q build_windows_v0.3.6 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul
echo [OK] Limpeza concluida.
echo.

REM Criar diretorios
echo Criando estrutura de diretorios...
mkdir build 2>nul
mkdir build\temp 2>nul
mkdir build_windows_v0.3.6 2>nul
echo [OK] Diretorios criados.
echo.

echo ========================================
echo Executando PyInstaller...
echo Aguarde, pode levar alguns minutos...
echo ========================================
echo.

REM Executar build
REM Usando workpath=build\temp para evitar conflitos de cache na raiz
%PY_BUILD% -m PyInstaller --name=AI_Code_Assistant_v0.3.6 --windowed --onefile --noupx --distpath=build_windows_v0.3.6 --workpath=build\temp --add-data "config;config" --hidden-import=PyQt6 --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.sip --hidden-import=openai --hidden-import=anthropic --hidden-import=yaml --hidden-import=watchdog --hidden-import=pygments --hidden-import=pygments.lexers --hidden-import=pygments.formatters src\main.py

echo.

REM Verificar resultado
if exist "build_windows_v0.3.6\AI_Code_Assistant_v0.3.6.exe" (
    echo ========================================
    echo [OK] BUILD CONCLUIDO COM SUCESSO!
    echo ========================================
    echo.
    
    for %%F in ("build_windows_v0.3.6\AI_Code_Assistant_v0.3.6.exe") do (
        set /a size_mb=%%~zF/1048576
        echo Executavel: %%~nxF
        echo Tamanho: !size_mb! MB
    )
    echo.
    
    REM Copiar recursos
    echo Copiando recursos adicionais...
    if exist config (
        xcopy /E /I /Y config build_windows_v0.3.6\config >nul 2>&1
        echo    [OK] Configuracoes
    )
    if exist README.md (
        copy /Y README.md build_windows_v0.3.6\ >nul 2>&1
        echo    [OK] Documentacao
    )
    if exist assets (
        xcopy /E /I /Y assets build_windows_v0.3.6\assets >nul 2>&1
        echo    [OK] Assets
    )
    
    echo.
    echo ========================================
    echo APLICACAO PRONTA!
    echo ========================================
    echo.
    echo Pasta: build_windows_v0.3.6\
    echo.
    dir /b build_windows_v0.3.6\
    echo.
) else (
    echo ========================================
    echo [ERRO] BUILD FALHOU
    echo ========================================
    echo.
    echo Verifique os erros acima.
    echo.
)

echo.
echo Pressione qualquer tecla para fechar...
pause >nul