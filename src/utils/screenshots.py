import os
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime
from ..utils.logger import get_logger  # Asegúrate de que esta importación sea correcta

# Obtén una instancia de logger específica para este módulo

logger = get_logger(__name__)
# --- Definición y Verificación del Directorio de Capturas de Pantalla ---
# Paso 1: Determinar la ruta raíz del proyecto 'vivienda'.
# Si este archivo (screenshots.py) está en 'vivienda/src/utils/',
# necesitamos subir 3 niveles para llegar a 'vivienda/'.
# 1. os.path.abspath(__file__) -> C:/.../vivienda/src/utils/screenshots.py
# 2. os.path.dirname(paso1) -> C:/.../vivienda/src/utils/
# 3. os.path.dirname(paso2) -> C:/.../vivienda/src/
# 4. os.path.dirname(paso3) -> C:/.../vivienda/  <-- ¡Esta es la raíz del proyecto!
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paso 2: Construir la ruta completa al directorio de capturas a partir de la raíz del proyecto.
# Ahora, _PROJECT_ROOT es 'vivienda/', así que simplemente añadimos 'reports/screenshots'.
_SCREENSHOTS_DIR = os.path.join(

    _PROJECT_ROOT,

    'reports',

    'screenshots'

)

# Paso 3: Verificar y crear el directorio si no existe.

# 'exist_ok=True' es crucial para evitar errores si el directorio ya existe.

if not os.path.exists(_SCREENSHOTS_DIR):

    os.makedirs(_SCREENSHOTS_DIR, exist_ok=True)

    logger.info(f"Directorio de capturas de pantalla creado: {_SCREENSHOTS_DIR}")

else:

    logger.info(f"Directorio de capturas de pantalla ya existe: {_SCREENSHOTS_DIR}")


# --- Función para Tomar Capturas de Pantalla ---


def take_screenshot(driver: WebDriver, name: str) -> str | None:
    """

    Toma una captura de pantalla del estado actual del navegador.

    Las capturas se guardan en el directorio definido por _SCREENSHOTS_DIR.

    :param driver: La instancia de WebDriver de Selenium.

    :param name: Nombre base para el archivo de la captura (sin extensión).

                 Se le añadirá un timestamp y la extensión .png.

    :return: La ruta completa del archivo de la captura si se guardó con éxito,

             o None en caso de error.

    """

    # Genera un timestamp para asegurar un nombre de archivo único

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Construye el nombre del archivo final

    file_name = f"{name}_{timestamp}.png"

    # Une el directorio base de capturas con el nombre del archivo

    file_path = os.path.join(_SCREENSHOTS_DIR, file_name)

    try:

        # Intenta guardar la captura de pantalla

        driver.save_screenshot(file_path)

        logger.info(f"Captura de pantalla guardada en: {file_path}")

        return file_path

    except Exception as e:

        # Registra cualquier error que ocurra durante el proceso

        logger.error(f"Error al tomar captura de pantalla en {file_path}: {e}")

        return None
