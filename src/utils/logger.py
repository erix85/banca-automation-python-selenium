import logging

import logging.config

import os

import sys

# Determinar la ruta raíz del proyecto 'vivienda'.

# logger.py está en src/utils/, por lo que subimos tres niveles para llegar a 'vivienda'.

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directorio donde se guardarán los archivos de log dentro de la raíz del proyecto

# Asegúrate de que 'logs' exista en la raíz de 'vivienda/'

_LOGS_DIR = os.path.join(_PROJECT_ROOT, 'reports', 'logs')

# Asegurarse de que el directorio de logs exista antes de intentar configurar el logging

if not os.path.exists(_LOGS_DIR):
    os.makedirs(_LOGS_DIR, exist_ok=True)

# Nombre del archivo de log principal y su ruta completa

_LOG_FILE_NAME = 'automation.log'

_FULL_LOG_FILE_PATH = os.path.join(_LOGS_DIR, _LOG_FILE_NAME)

# --- Configuración de Logging embebida directamente en este módulo ---

# Este diccionario define cómo se comportarán los loggers, handlers y formatters.

LOGGING_CONFIG = {

    'version': 1,  # Versión del esquema de configuración (siempre 1 para las versiones actuales)

    'disable_existing_loggers': False,
    # No deshabilitar otros loggers que puedan existir (ej. de librerías de terceros)

    'formatters': {

        'standardFormatter': {  # Un formateador estándar para mensajes de log

            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',

            'datefmt': '%Y-%m-%d %H:%M:%S'

        },

    },

    'handlers': {

        'consoleHandler': {  # Un handler para mostrar logs en la consola

            'class': 'logging.StreamHandler',

            'level': 'INFO',  # Mostrar mensajes de INFO o superior en consola

            'formatter': 'standardFormatter',

            'stream': 'ext://sys.stdout',  # Dirigir la salida a la consola estándar

        },

        'fileHandler': {  # Un handler para guardar logs en un archivo rotatorio

            'class': 'logging.handlers.RotatingFileHandler',

            'level': 'DEBUG',  # Guardar mensajes de DEBUG o superior en el archivo

            'formatter': 'standardFormatter',

            'filename': _FULL_LOG_FILE_PATH,  # Ruta completa al archivo de log

            'mode': 'a',  # Abrir el archivo en modo append (añadir al final)

            'maxBytes': 10485760,  # Tamaño máximo del archivo de log antes de rotar (10 MB)

            'backupCount': 5,  # Número de archivos de respaldo a mantener

            'encoding': 'utf-8'  # Codificación del archivo de log

        },

    },

    'loggers': {

        '': {  # Configuración para el logger raíz (root logger)

            'level': 'INFO',  # Nivel por defecto para mensajes que no tienen un logger específico

            'handlers': ['consoleHandler', 'fileHandler'],  # Enviar mensajes a consola y archivo

            'propagate': True  # Por defecto, los mensajes se propagan a loggers superiores

        },

        'automation': {  # Tu logger específico para los mensajes del framework de automatización

            'level': 'DEBUG',  # Nivel de detalle para este logger (DEBUG o superior)

            'handlers': ['consoleHandler', 'fileHandler'],  # Enviar mensajes a consola y archivo

            'qualname': 'automation',  # Nombre explícito del logger

            'propagate': False  # NO propagar este logger al root, ya que ya tiene sus propios handlers

        },

    },

    # La sección 'root' es redundante si el logger con nombre '' ya está definido en 'loggers'.

    # Se incluye aquí para completar el ejemplo, pero en la práctica, solo una de las dos es necesaria.

    'root': {

        'level': 'INFO',

        'handlers': ['consoleHandler', 'fileHandler']

    }

}


# --- Fin de la Configuración de Logging embebida ---


def setup_logging():
    """

    Configura el sistema de logging utilizando un diccionario de configuración embebido.

    Este método se encarga de aplicar la configuración de logging definida en LOGGING_CONFIG.

    """

    try:

        # Aquí es donde se aplica la configuración del diccionario al módulo logging

        logging.config.dictConfig(LOGGING_CONFIG)

        # Una vez configurado, obtenemos el logger 'automation' para registrar el éxito

        logging.getLogger('automation').info(
            f"Configuración de logging cargada con éxito desde el diccionario embebido. Logs guardados en: {_FULL_LOG_FILE_PATH}")

    except Exception as e:

        # En caso de cualquier error durante la carga de la configuración,

        # se imprime un mensaje de error y se recurre a una configuración básica de respaldo.

        print(f"ERROR CRÍTICO: No se pudo cargar la configuración de logging. "

              f"Usando configuración básica de respaldo. Error: {e}", file=sys.stderr)

        # Define una ruta para el log de respaldo en caso de fallo crítico

        fallback_log_path = os.path.join(_LOGS_DIR, 'fallback_automation_error.log')

        # Configuración básica de respaldo, con un handler de consola y un handler de archivo

        logging.basicConfig(

            level=logging.INFO,

            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

            handlers=[

                logging.StreamHandler(sys.stdout),  # Salida a la consola

                logging.FileHandler(fallback_log_path, mode='a', encoding='utf-8')  # Salida a un archivo

            ]

        )

        # Registra un mensaje de error usando el logger de respaldo

        logging.getLogger('automation').error(
            "Configuración de logging básica de respaldo activada debido a un error crítico.")


def get_logger(name: str):
    """

    Obtiene una instancia de logger.

    :param name: El nombre del logger (generalmente __name__ del módulo que llama a esta función).

    :return: Una instancia de logging.Logger ya configurada.

    """

    # Esta verificación asegura que el logging esté configurado si aún no lo está.

    # Es una medida de seguridad, ya que setup_logging() se llama al importar este módulo.

    if not logging.getLogger().handlers:
        setup_logging()

    return logging.getLogger(name)


# --- Punto de entrada para la configuración del logging ---

# Esta línea se ejecuta una vez cuando el módulo 'logger.py' es importado.

# Asegura que el sistema de logging esté listo inmediatamente para ser usado por cualquier otra parte del framework.

setup_logging()

# --- Exportar una instancia de logger ---

# Se exporta una instancia del logger 'automation' para facilitar su uso.

# Otros módulos pueden importar 'logger' directamente desde 'src.utils.logger'.

logger = get_logger('automation')
