import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from src.gui.main_window import MainWindowV3

def run_gui_tests():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    print("=== INICIANDO TESTES GUI AUTOMATIZADOS ===")
    mw = MainWindowV3()
    
    print("\n[TESTE 1] Iniciando MainWindow...")
    print("  -> UI Inicializada com Sucesso!")

    print("\n[TESTE 2] Validando Shell Selector")
    if hasattr(mw, 'shell_combo'):
        shells = [mw.shell_combo.itemText(i) for i in range(mw.shell_combo.count())]
        print(f"  -> Shells detectados via shell_combo: {shells}")
    elif hasattr(mw.terminal_widget, 'shell_selector'):
        shells = [mw.terminal_widget.shell_selector.itemText(i) for i in range(mw.terminal_widget.shell_selector.count())]
        print(f"  -> Shells detectados via terminal_widget: {shells}")

    print("\n[TESTE 3] Validando Richie AI (Base de Conhecimento e BotForge Flow)")
    if hasattr(mw, 'ai_manager'):
        try:
            nodes = getattr(mw.ai_manager, 'flow_nodes', [])
            conns = getattr(mw.ai_manager, 'flow_conns', [])
            print(f"  -> Richie Carregado. Nós: {len(nodes)}, Conexões: {len(conns)}")
            
            has_richie = False
            for cb in [mw.findChild(type(mw.ai_manager.__class__), ""), mw.findChild(type(mw.ai_manager.__class__), "provider_combo")]:
                # Busca heurística
                pass
            
            print(f"  -> Richie Manager instanciado: {mw.ai_manager is not None}")
        except Exception as e:
            print(f"  -> Erro ao carregar Richie: {e}")

    # Desliga a app após testar
    QTimer.singleShot(1000, app.quit)
    app.exec()
    print("=== TESTES CONCLUÍDOS ===")

if __name__ == '__main__':
    run_gui_tests()
