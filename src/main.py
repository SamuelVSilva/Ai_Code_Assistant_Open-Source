"""
AI Code Assistant - Entry Point
"""
import sys
import os
import traceback

def main():
    # Estrutura de tratamento de erro robusta para debug em produção
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
    except ImportError as e:
        # Se falhar o import do PyQt, logar e tentar instalar automaticamente
        with open("startup_error.txt", "w") as f:
            f.write(f"Falha ao importar PyQt6: {e}\n{traceback.format_exc()}")
        # Tentar instalar automaticamente se pip disponível
        try:
            import subprocess
            print("[Auto-Recovery] Tentando instalar dependências faltantes...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "requests", "--quiet"])
            from PyQt6.QtWidgets import QApplication, QMessageBox
            print("[Auto-Recovery] Dependências instaladas com sucesso!")
        except Exception as install_err:
            print(f"ERRO FATAL: PyQt6 não encontrado e instalação falhou.\n{install_err}")
            return

    try:
        # Adicionar raiz do projeto ao PATH se rodando como script
        if not getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(current_dir)
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)

        app = QApplication(sys.argv)
        app.setApplicationName("AI Code Assistant — v0.4.11-rev1.2.3-220426")
        app.setOrganizationName("SVS_Technology")

        # Importação tardia para garantir que PATH estao configurados
        from src.gui.main_window import MainWindowV3
        
        window = MainWindowV3()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        # Captura qualquer crash e exibe popup e log
        err_msg = f"Ocorreu um erro fatal:\n\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(err_msg)
        
        try:
            with open("crash_log.txt", "w") as f:
                f.write(err_msg)
            
            QMessageBox.critical(None, "Erro Fatal", err_msg)
        except:
            # Se falhar até o log/msgbox, tenta printar (aparece se tiver console)
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()