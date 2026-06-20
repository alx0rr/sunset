import os
import importlib


from src import log


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TG_MODULES_DIR = os.path.join(BASE_DIR, "telegram/modules")
ALTAMINO_MODULES_DIR = os.path.join(BASE_DIR, "altamino/modules")


def load_tg_modules(app):
    for file in os.listdir(TG_MODULES_DIR):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"src.telegram.modules.{file[:-3]}"
            module = importlib.import_module(module_name)

            log.info(f"[tg] Loaded: {module_name}")


def load_altamino_modules():
    for file in os.listdir(ALTAMINO_MODULES_DIR):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"src.altamino.modules.{file[:-3]}"
            module = importlib.import_module(module_name)

            log.info(f"[altamino] Loaded: {module_name}")