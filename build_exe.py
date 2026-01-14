"""
Build da aplicação para Windows
Adaptado da versão Linux (build_linux.py) - v0.3.5-alpha
Interface: PyQt6
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_application():
    print("=" * 60)
    print("BUILD AI CODE ASSISTANT - Windows Version".center(60))
    print("v0.3.5-alpha - PyQt6 Interface".center(60))
    print("=" * 60)
    
    # Verificar arquivo principal
    main_file = Path("src/main.py")
    if not main_file.exists():
        print("✗ Arquivo src/main.py não encontrado!")
        return False
    
    print(f"✓ Arquivo principal: {main_file}")
    
    # Limpar builds anteriores
    print("\nLimpando builds anteriores...")
    dirs_to_clean = [
        'build', 
        'build_windows_v0.3.5-alpha', 
        '__pycache__',
        'src/__pycache__',
        'src/gui/__pycache__',
        'src/core/__pycache__',
        'src/utils/__pycache__',
        'src/providers/__pycache__'
    ]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removido: {dir_name}")
    
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  Removido: {spec_file}")
    
    # Comando PyInstaller para PyQt6
    cmd = [
        'pyinstaller',
        '--name=AI_Code_Assistant_v0.3.5-alpha_windows',
        '--windowed',
        '--onefile',
        '--clean',
        '--noupx',
        '--distpath=build_windows_v0.3.5-alpha',
        '--add-data', 'config;config',
        '--add-data', 'src;src',
        # PyQt6 imports
        '--hidden-import', 'PyQt6',
        '--hidden-import', 'PyQt6.QtWidgets',
        '--hidden-import', 'PyQt6.QtCore',
        '--hidden-import', 'PyQt6.QtGui',
        '--hidden-import', 'PyQt6.sip',
        # Outras dependências
        '--hidden-import', 'openai',
        '--hidden-import', 'anthropic',
        '--hidden-import', 'yaml',
        '--hidden-import', 'watchdog',
        '--hidden-import', 'pygments',
        '--hidden-import', 'pygments.lexers',
        '--hidden-import', 'pygments.formatters',
        # Módulos do projeto
        '--hidden-import', 'src',
        '--hidden-import', 'src.gui',
        '--hidden-import', 'src.gui.main_window',
        '--hidden-import', 'src.gui.components',
        '--hidden-import', 'src.core',
        '--hidden-import', 'src.utils',
        '--hidden-import', 'src.providers',
        # Coletar todos os arquivos do PyQt6
        '--collect-all', 'PyQt6',
        'src/main.py'
    ]
    
    # Adicionar ícone se existir
    if Path('assets/icon.ico').exists():
        cmd.insert(7, '--icon=assets/icon.ico')
    
    print(f"\nComando PyInstaller iniciando...")
    print("Isso pode levar alguns minutos...")
    print("\n" + "-"*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("-"*60)
            print("\n" + "="*60)
            print("✓ BUILD CONCLUÍDO COM SUCESSO!".center(60))
            print("="*60)
            
            # Verificar executável
            exe_path = Path('build_windows_v0.3.5-alpha') / 'AI_Code_Assistant_v0.3.5-alpha_windows.exe'
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                
                print(f"\n📦 Executável criado:")
                print(f"   Local: {exe_path}")
                print(f"   Tamanho: {size_mb:.2f} MB")
                
                # Copiar recursos adicionais
                print("\n📂 Copiando recursos adicionais...")
                
                # Configurações (se não foram incluídas no --add-data)
                config_dst = Path('build_windows_v0.3.5-alpha') / 'config'
                if Path('config').exists() and not config_dst.exists():
                    shutil.copytree('config', config_dst)
                    print("   ✓ Configurações")
                
                # README
                if Path('README.md').exists():
                    shutil.copy('README.md', 'build_windows_v0.3.5-alpha/')
                    print("   ✓ Documentação")
                
                # Assets (se existir)
                if Path('assets').exists():
                    assets_dst = Path('build_windows_v0.3.5-alpha') / 'assets'
                    if assets_dst.exists():
                        shutil.rmtree(assets_dst)
                    shutil.copytree('assets', assets_dst)
                    print("   ✓ Assets/ícones")
                
                # Criar arquivo de instruções
                create_instructions()
                print("   ✓ Instruções")
                
                # Listar conteúdo da pasta
                print("\n📁 Conteúdo da pasta de build:")
                for item in Path('build_windows_v0.3.5-alpha').iterdir():
                    if item.is_dir():
                        print(f"   📂 {item.name}/")
                    else:
                        size_kb = item.stat().st_size / 1024
                        print(f"   📄 {item.name} ({size_kb:.1f} KB)")
                
                print("\n" + "="*60)
                print("🎉 APLICAÇÃO PRONTA!".center(60))
                print("="*60)
                print(f"\nPara executar: {exe_path}")
                
                return True
            else:
                print("\n✗ Executável não encontrado após build!")
                return False
                
        else:
            print("-"*60)
            print(f"\n✗ ERRO NO BUILD:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"\n✗ EXCEÇÃO: {e}")
        return False

def create_instructions():
    """Cria arquivo de instruções para Windows"""
    instructions = """🎯 AI CODE ASSISTANT - Windows Version v0.3.5-alpha 🎯

========================================
COMO USAR:
========================================

1. 🚀 INÍCIO RÁPIDO:
   - Execute o arquivo AI_Code_Assistant_v0.3.5-alpha_windows.exe
   - Clique em "📂 Abrir Projeto" para selecionar uma pasta
   - Navegue pelos arquivos no Explorer à esquerda
   - Converse com a IA no chat à direita

2. 📁 EXPLORER DE ARQUIVOS:
   • Clique em pastas para expandir
   • Clique em arquivos para abrir no editor
   • Botão "↻" atualiza a lista

3. ✏️ EDITOR DE CÓDIGO:
   • Edite arquivos diretamente
   • Múltiplas abas suportadas
   • Números de linha automáticos

4. 💬 CHAT COM IA:
   • Digite suas perguntas
   • Use Ctrl+Enter para enviar
   • Diferentes modelos disponíveis

========================================
REQUISITOS:
========================================
• Windows 10 ou superior recomendado
• Conexão com internet para IAs online
• Permissões de leitura/escrita para pastas de projeto

========================================
SOLUÇÃO DE PROBLEMAS:
========================================
• Se bloquear, clique direito > Propriedades > Desbloquear
• Execute como administrador se necessário
• Verifique se o antivírus não está bloqueando

========================================
INFORMAÇÕES:
========================================
Versão: v0.3.5-alpha - Premium Build
Interface: PyQt6
"""
    
    with open(Path('build_windows_v0.3.5-alpha') / 'INSTRUCOES_WINDOWS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("Iniciando build para Windows...".center(60))
    print("="*60 + "\n")
    
    success = build_application()
    
    if success:
        print("\n✅ Build concluído com sucesso!")
        print("📁 Execute o aplicativo em: build_windows_v0.3.5-alpha\\AI_Code_Assistant_v0.3.5-alpha_windows.exe")
    else:
        print("\n❌ Build falhou!")
        print("Verifique os erros acima.")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()