@echo off
chcp 65001 >nul
title Build AI Code Assistant

echo ========================================
echo AI Code Assistant - Build para Windows
echo ========================================
echo.

cd /d "%~dp0"
echo Diretório: %cd%
echo.

REM Limpar anteriores
echo Limpando builds anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q dist_windows 2>nul
del *.spec 2>nul
del *.log 2>nul

echo.
echo Criando diretórios...
mkdir dist_windows 2>nul
mkdir config 2>nul

echo.
echo Executando PyInstaller...
echo Aguarde, pode levar alguns minutos...
echo.

REM Comando PyInstaller corrigido
pyinstaller ^
  --name=AI_Code_Assistant ^
  --windowed ^
  --onefile ^
  --clean ^
  --noupx ^
  --distpath=dist_windows ^
  --hidden-import=tkinter ^
  --hidden-import=tkinter.ttk ^
  --hidden-import=tkinter.filedialog ^
  --hidden-import=tkinter.scrolledtext ^
  --hidden-import=tkinter.font ^
  src\main.py

echo.
if exist dist_windows\AI_Code_Assistant.exe (
    echo ✓ BUILD CONCLUÍDO COM SUCESSO!
    echo.
    
    for %%F in (dist_windows\AI_Code_Assistant.exe) do (
        set /a size_mb=%%~zF/1048576
        echo Executável: %%F
        echo Tamanho: !size_mb! MB
    )
    
    echo.
    echo Para testar: dist_windows\AI_Code_Assistant.exe
    echo.
    echo Pressione qualquer tecla para fechar...
) else (
    echo ✗ BUILD FALHOU!
    echo.
    echo Tente executar como administrador.
    echo.
    echo Pressione qualquer tecla para fechar...
)

pause >nul