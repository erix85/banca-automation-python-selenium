import os
from pathlib import Path

# Ruta absoluta al directorio donde reside este archivo (config)
CONFIG_DIR = Path(__file__).resolve().parent

# Ruta absoluta a la carpeta src
SRC_DIR = CONFIG_DIR.parent

# Ruta absoluta a la raíz del proyecto (home)
PROJECT_ROOT = SRC_DIR.parent