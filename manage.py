# MOJIZA/manage.py

import sys
import os
import importlib
from MOJIZA.engine.engine import run_server, start_auto_reload, reload_server
import threading
import glob
from MOJIZA.engine.engine import init_db

def main():
    # Loyihaning asosiy papkasini PYTHONPATH ga qo'shish
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)

    # Ma'lumotlar bazasini boshlash
    init_db()

    # `projectpapca` ichidagi barcha .py fayllarni topish va import qilish
    pages = glob.glob(os.path.join(project_dir, 'projectpapca', '*.py'))
    for page in pages:
        module_name = os.path.splitext(os.path.basename(page))[0]
        if module_name != '__init__':
            try:
                importlib.import_module(f'projectpapca.{module_name}')
                print(f"Imported module: projectpapca.{module_name}")
            except Exception as e:
                print(f"Failed to import module projectpapca.{module_name}: {e}")

    # Serverni alohida threadda ishga tushurish
    server_thread = threading.Thread(target=run_server, args=(8000,), daemon=True)
    server_thread.start()

    # Auto-reloadni alohida threadda boshlash
    reload_thread = threading.Thread(target=start_auto_reload, args=(reload_server,), daemon=True)
    reload_thread.start()

    # Asosiy threadda hech narsa qilmaymiz
    server_thread.join()
    reload_thread.join()

if __name__ == "__main__":
    main()
