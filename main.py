"""
Wrapper para Streamlit Cloud.
Streamlit Cloud ejecuta este archivo (main.py en la raiz).
El codigo real vive en app/main.py.
"""
import sys, os

_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
_entry = os.path.join(_app_dir, "main.py")

# Que los imports (helpers, loaders, ...) resuelvan desde app/
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

# Compilar y ejecutar con __file__ correcto para que
# Path(__file__).parent / "Demo_data" apunte a app/Demo_data/
with open(_entry, encoding="utf-8") as _f:
    _code = compile(_f.read(), _entry, "exec")

globals()["__file__"] = _entry
exec(_code)
