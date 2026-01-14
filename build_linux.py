"""
Build da aplicação para Linux
Adaptado de build_exe.py
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_application():
    print("=" * 60)
    print("BUILD AI CODE ASSISTANT - Linux Version".center(60))
    print("=" * 60)
    
    # Verificar arquivo principal
    main_file = Path("src/main.py")
    if not main_file.exists():
        print("✗ Arquivo src/main.py não encontrado!")
        return False
    
    print(f"✓ Arquivo principal: {main_file}")
    
    # Limpar builds anteriores
    print("\nLimpando builds anteriores...")
    for dir_name in ['build', 'dist_linux', '__pycache__']:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removido: {dir_name}")
    
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
    
    # Criar diretório de saída
    Path('dist_linux').mkdir(exist_ok=True)
    
    # Comando PyInstaller
    cmd = [
        'pyinstaller',
        '--name=AI_Code_Assistant_v0.3.5-alpha',
        '--windowed',
        '--onefile',
        '--clean',
        '--noupx',
        # Linux costuma usar ícones separados ou integrados de forma diferente, 
        # mas mantemos a lógica se houver um .png ou similar no futuro.
        '--distpath=build_linux_v0.3.5-alpha',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'PIL',
        'src/main.py'
    ]
    
    print(f"\nComando: {' '.join(cmd[:10])}...")
    print("\nExecutando PyInstaller...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("✓ BUILD CONCLUÍDO COM SUCESSO!".center(60))
            print("="*60)
            
            # Verificar executável (sem .exe no Linux)
            exe_path = Path('build_linux_v0.3.5-alpha') / 'AI_Code_Assistant_v0.3.5-alpha'
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                
                print(f"\n📦 Executável criado:")
                print(f"   Local: {exe_path}")
                print(f"   Tamanho: {size_mb:.2f} MB")
                
                # Garantir permissão de execução
                os.chmod(exe_path, 0o755)
                
                # Copiar recursos
                print("\n📂 Copiando recursos...")
                
                # Configurações
                if Path('config').exists():
                    config_dst = Path('build_linux_v0.3.5-alpha') / 'config'
                    if config_dst.exists():
                        shutil.rmtree(config_dst)
                    shutil.copytree('config', config_dst)
                    print("   ✓ Configurações")
                
                # README
                if Path('README.md').exists():
                    shutil.copy('README.md', 'build_linux_v0.3.5-alpha/')
                    print("   ✓ Documentação")
                
                # Assets (se existir)
                if Path('assets').exists():
                    assets_dst = Path('build_linux_v0.3.5-alpha') / 'assets'
                    if assets_dst.exists():
                        shutil.rmtree(assets_dst)
                    shutil.copytree('assets', assets_dst)
                    print("   ✓ Assets/ícones")
                
                # Criar arquivo de instruções
                create_instructions()
                
                print("\n" + "="*60)
                print("🎉 APLICAÇÃO PRONTA!".center(60))
                print("="*60)
                print("\nPara executar:")
                print(f"  ./{exe_path}")
                
                return True
            else:
                print("\n✗ Executável não encontrado após build!")
                return False
                
        else:
            print(f"\n✗ ERRO NO BUILD:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"\n✗ EXCEÇÃO: {e}")
        return False

def create_instructions():
    """Cria arquivo de instruções para Linux"""
    instructions = """🎯 AI CODE ASSISTANT - Linux Version 🎯

COMO USAR:

1. 🚀 INÍCIO RÁPIDO:
   - Abra o terminal na pasta 'dist_linux'
   - Execute: ./AI_Code_Assistant
   - Se necessário, dê permissão: chmod +x AI_Code_Assistant

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

5. 🔧 REQUISITOS:
   • Dependências de sistema (Tkinter/PyQt6) devem estar instaladas na distro.
   • Debian/Ubuntu/Mint: sudo apt install python3-tk libxcb-cursor0
   • Fedora: sudo dnf install python3-tkinter xcb-util-cursor
   • Arch: sudo pacman -S tk xcb-util-cursor

Versão: v0.3.5-alpha - Premium Build
"""
    
    with open(Path('build_linux_v0.3.5-alpha') / 'INSTRUCOES_LINUX.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)

def main():
    """Função principal"""
    print("\nIniciando build para Linux...")
    
    success = build_application()
    
    if success:
        print("\n✅ Build concluído com sucesso!")
        print("📁 Execute o aplicativo em: build_linux_v0.3.5-alpha/AI_Code_Assistant_v0.3.5-alpha")
    else:
        print("\n❌ Build falhou!")
        print("Verifique os erros acima.")

if __name__ == "__main__":
    main()
