import os
import importlib


from src import log


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALTAMINO_MODULES_DIR = os.path.join(BASE_DIR, "aa/modules")

def load_altamino_modules():
    for file in os.listdir(ALTAMINO_MODULES_DIR):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"src.aa.modules.{file[:-3]}"
            module = importlib.import_module(module_name)

            log.info(f"[altamino] Loaded: {module_name}")