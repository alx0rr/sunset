import os
import yaml

_locales: dict = {}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_locales(path: str = "res/locales") -> None:
    full_path = os.path.join(BASE_DIR, path)
    for fname in os.listdir(full_path):
        if fname.endswith(".yml"):
            lang = fname.replace(".yml", "")
            with open(os.path.join(full_path, fname), encoding="utf-8") as f:
                _locales[lang] = yaml.safe_load(f)

def t(code: str, lang: str = "en") -> str:
    data = _locales.get(lang) or _locales.get("en", {})
    for key in code.split("."):
        if not isinstance(data, dict):
            return code
        data = data.get(key, {})
    return data if isinstance(data, str) else code

def get_langs_list() -> list[str]:
    return list(_locales.keys())