import json

import os

from src.utils.logger import get_logger

_common_logger = get_logger(__name__)

# Asumiendo que el directorio 'data' está un nivel arriba de 'utils'

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def read_json_data(file_path: str) -> dict:
    """

    Lee datos desde un archivo JSON.

    :param file_path: La ruta relativa o absoluta al archivo JSON dentro de la carpeta 'data'.

    :return: Un diccionario con los datos del JSON.

    :raises FileNotFoundError: Si el archivo no existe.

    :raises json.JSONDecodeError: Si el archivo JSON es inválido.

    """

    full_path = os.path.join(_DATA_DIR, file_path)

    try:

        with open(full_path, 'r', encoding='utf-8') as f:

            data = json.load(f)

            _common_logger.info(f"Datos cargados exitosamente desde: {full_path}")

            return data

    except FileNotFoundError:

        _common_logger.error(f"Error: Archivo de datos no encontrado en {full_path}")

        raise

    except json.JSONDecodeError:

        _common_logger.error(f"Error: No se pudo decodificar el JSON de {full_path}. Verifica la sintaxis.")

        raise

    except Exception as e:

        _common_logger.error(f"Error desconocido al leer JSON de {full_path}: {e}")

        raise
