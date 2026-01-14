"""
Build da aplicação com interface VS Code
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_application():
    print("=" * 60)
    print("BUILD AI CODE ASSISTANT - VS Code Style".center(60))
    print("=" * 60)
    
    # Verificar arquivo principal
    main_file = Path("src/main.py")
    if not main_file.exists():
        print("✗ Arquivo src/main.py não encontrado!")
        return False
    
    print(f"✓ Arquivo principal: {main_file}")
    
    # Limpar builds anteriores
    print("\nLimpando builds anteriores...")
    for dir_name in ['build', 'dist', '__pycache__']:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removido: {dir_name}")
    
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
    
    # Comando PyInstaller
    cmd = [
        'pyinstaller',
        '--name=AI_Code_Assistant',
        '--windowed',
        '--onefile',
        '--clean',
        '--noupx',
        '--icon=assets/icon.ico' if Path('assets/icon.ico').exists() else '',
        '--add-data', 'config;config',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'PIL',  # Para ícones se usar
        'src/main.py'
    ]
    
    # Remover strings vazias
    cmd = [c for c in cmd if c]
    
    print(f"\nComando: {' '.join(cmd[:10])}...")
    print("\nExecutando PyInstaller...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("✓ BUILD CONCLUÍDO COM SUCESSO!".center(60))
            print("="*60)
            
            # Verificar executável
            exe_path = Path('dist') / 'AI_Code_Assistant.exe'
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                
                print(f"\n📦 Executável criado:")
                print(f"   Local: {exe_path}")
                print(f"   Tamanho: {size_mb:.2f} MB")
                
                # Copiar recursos
                print("\n📂 Copiando recursos...")
                
                # Configurações
                if Path('config').exists():
                    config_dst = Path('dist') / 'config'
                    if config_dst.exists():
                        shutil.rmtree(config_dst)
                    shutil.copytree('config', config_dst)
                    print("   ✓ Configurações")
                
                # README
                if Path('README.md').exists():
                    shutil.copy('README.md', 'dist/')
                    print("   ✓ Documentação")
                
                # Assets (se existir)
                if Path('assets').exists():
                    assets_dst = Path('dist') / 'assets'
                    if assets_dst.exists():
                        shutil.rmtree(assets_dst)
                    shutil.copytree('assets', assets_dst)
                    print("   ✓ Assets/ícones")
                
                # Criar atalho de instruções
                create_instructions()
                
                print("\n" + "="*60)
                print("🎉 APLICAÇÃO PRONTA!".center(60))
                print("="*60)
                print("\nPara executar:")
                print(f"  {exe_path}")
                print("\nInterface disponível:")
                print("  • Explorer de arquivos (esquerda)")
                print("  • Editor de código (centro)")
                print("  • Chat com IA (direita)")
                
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
    """Cria arquivo de instruções"""
    instructions = """🎯 AI CODE ASSISTANT - VS Code Style 🎯

COMO USAR:

1. 🚀 INÍCIO RÁPIDO:
   - Execute o arquivo AI_Code_Assistant.exe
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
   • Use Ctrl+Enter para enviar rapidamente
   • Selecione diferentes IAs no menu
   • Botões para anexar arquivos e limpar chat

5. ⚙️ COMANDOS DISPONÍVEIS:
   /analyze    - Analisar código atual
   /generate   - Gerar novo código
   /explain    - Explicar código selecionado
   /refactor   - Sugerir melhorias
   /test       - Criar testes unitários

6. 🔧 CONFIGURAÇÃO:
   • Adicione chaves de API em config/settings.json
   • Personalize tema e cores
   • Configure provedores de IA

7. 🛠️ SOLUÇÃO DE PROBLEMAS:
   • Se bloquear, clique direito > Propriedades > Desbloquear
   • Verifique permissões de arquivo
   • Confirme conexão com internet para IAs online

📞 SUPORTE:
   Em caso de problemas, verifique a documentação
   ou entre em contato com o desenvolvedor.

Versão: 1.0.0 - VS Code Style Interface
"""
    
    with open(Path('dist') / 'INSTRUCOES.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)

def main():
    """Função principal"""
    print("\nIniciando build da interface VS Code Style...")
    
    success = build_application()
    
    if success:
        print("\n✅ Build concluído com sucesso!")
        print("📁 Execute o aplicativo em: dist\\AI_Code_Assistant.exe")
    else:
        print("\n❌ Build falhou!")
        print("Verifique os erros acima.")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()