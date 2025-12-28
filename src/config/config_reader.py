from pathlib import Path
from configparser import ConfigParser, NoSectionError, NoOptionError
from typing import Optional, Dict, Any

from src.utils.logger import get_logger
from src.definitions import PROJECT_ROOT


class ConfigReader:

    def __init__(self, config_file_path: Optional[str] = None):

        self.logger = get_logger(__name__)
        self.config = ConfigParser()

        # Si no se provee ruta, busca environment.ini en src/config usando PROJECT_ROOT
        # Esto es mas robusto que usar rutas relativas a __file__

        if config_file_path:
            self.config_file = Path(config_file_path)
        else:
            self.config_file = PROJECT_ROOT / "src" / "config" / "environment.ini"

        self._load_config()

        self.logger.info("ConfigReader inicializado y archivo de configuración cargado exitosamente.")




    def _load_config(self):

        if not self.config_file.exists():

            self.logger.error(f"Archivo de configuración no encontrado en: {self.config_file}")

            raise FileNotFoundError(f"environment.ini no encontrado en {self.config_file}")

        try:

            self.config.read(str(self.config_file))

        except Exception as e:

            self.logger.error(f"Error al leer el archivo de configuración {self.config_file}: {e}")

            raise




    def get_setting(self, section: str, option: str, default=None):

        """Generic method to get a setting, with default handling."""

        try:

            return self.config.get(section, option)

        except (NoSectionError, NoOptionError):

            if default is not None:

                self.logger.warning(f"Configuración '{option}' no encontrada en la sección '{section}'. Usando valor por defecto: {default}")

                return default

            else:

                self.logger.error(f"Configuración '{option}' no encontrada en la sección '{section}' y no se proporcionó un valor por defecto.")

                raise # Re-raise if no default and setting is missing




    def get_int_setting(self, section: str, option: str, default: int = None):

        try:

            return self.config.getint(section, option)

        except (NoSectionError, NoOptionError, ValueError):

            if default is not None:

                self.logger.warning(f"Configuración '{option}' no encontrada o no es un entero en la sección '{section}'. Usando valor por defecto: {default}")

                return default

            raise




    def get_boolean_setting(self, section: str, option: str, default: bool = None):

        try:

            return self.config.getboolean(section, option)

        except (NoSectionError, NoOptionError, ValueError):

            if default is not None:

                self.logger.warning(f"Configuración '{option}' no encontrada o no es un booleano en la sección '{section}'. Usando valor por defecto: {default}")

                return default

            raise


    def get_environment_config(self, environment_name: str) -> Dict[str, Any]:

        """
        Retorna un diccionario con todas las configuraciones para un entorno dado.
        Maneja valores por defecto si no se encuentran en el archivo INI.
        """
        if not self.config.has_section(environment_name):
            self.logger.warning(f"Sección '{environment_name}' no encontrada en environments.ini. Usando valores por defecto o vacíos.")
            return {}

        # Definición del esquema de configuración: (clave, método_de_lectura, valor_por_defecto)
        # Nota: Los valores por defecto aquí actúan como respaldo final si fallan el INI y la sección DEFAULT.
        config_schema = {
            'browser': (self.get_setting, 'chrome'),
            'headless': (self.get_boolean_setting, False),
            'wait_timeout': (self.get_int_setting, 30),
            'implicit_wait': (self.get_int_setting, 0),
            'screenshot_on_fail': (self.get_boolean_setting, True),
            'api_timeout': (self.get_int_setting, 30),
            'base_url': (self.get_setting, 'http://localhost'),
            'api_base_url': (self.get_setting, 'http://localhost:5000/api'),
            'grid_active': (self.get_boolean_setting, False),
            'grid_hub_url': (self.get_setting, 'http://localhost:4444/wd/hub'),
            'use_manual_drivers': (self.get_boolean_setting, False),
            'manual_drivers_path': (self.get_setting, ''),
        }

        config_data = {}
        for key, (method, default_val) in config_schema.items():
            config_data[key] = method(environment_name, key, default_val)
            
        return config_data