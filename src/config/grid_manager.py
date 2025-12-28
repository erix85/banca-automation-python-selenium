import os

import requests

import time

import json




from src.utils.logger import get_logger

from src.config.config_reader import ConfigReader




# Obtén una instancia de logger específica para este módulo

_grid_manager_logger = get_logger(__name__)




class GridManager:

    """

    Gestiona la configuración y el estado del Selenium Grid.

    Asume que el Grid es gestionado externamente (ej. Docker Compose).

    """

    def __init__(self, config_reader: ConfigReader = None):

        # GridManager DEBE tener una instancia de ConfigReader para leer la configuración.

        # Esta instancia NO debe ser la misma que 'context.config_reader' de Behave

        # (ya que se inicializan en diferentes momentos o contextos si no se pasan).

        # Lo importante es que GridManager pueda OBTENER la configuración.

        # Una buena práctica es que ConfigReader sea singleton o que se le pase la instancia.

        # Por ahora, la instancia local está bien si no hay conflicto.

        if config_reader:
            self.config_reader = config_reader
        else:
            self.config_reader = ConfigReader()

        self.current_env = 'default' # Almacena el nombre del entorno actual




        _grid_manager_logger.info("GridManager inicializado. Preparado para cargar configuraciones por entorno.")




    def set_environment(self, environment_name: str):

        """

        Establece el nombre del entorno de ejecución actual para el GridManager.

        Esto NO carga la configuración, solo registra el nombre del entorno.

        Los otros métodos usarán self.config_reader y este nombre de entorno

        para obtener los valores correctos.

        """

        self.current_env = environment_name

        _grid_manager_logger.info(f"GridManager: Entorno de ejecución establecido a '{environment_name}'.")




    def is_grid_active(self) -> bool: # Este método es llamado por WebDriverFactory

        """

        Verifica si el Grid está activo para el entorno actual.

        Delega la lectura de 'grid_active' a ConfigReader, pasando el entorno actual.

        """

        env_config = self.config_reader.get_environment_config(self.current_env)

        return env_config.get('grid_active', False) # Safely get the boolean value from the dictionary




    def get_grid_hub_url(self) -> str: # Este método es llamado por check_grid_status

        """

        Obtiene la URL del Hub del Grid para el entorno actual.

        Delega la lectura de 'grid_hub_url' a ConfigReader, pasando el entorno actual.

        """
        env_config = self.config_reader.get_environment_config(self.current_env)

        return env_config.get('grid_hub_url')




    def get_base_url(self) -> str:

        """

        Obtiene la URL base de la aplicación web para el entorno actual.

        Delega la lectura de 'base_url' a ConfigReader, pasando el entorno actual.

        """

        env_config = self.config_reader.get_environment_config(self.current_env)

        _grid_manager_logger.warning("GridManager.get_base_url() no se utiliza directamente en este diseño para la URL base WEB. "

                                     "Considere obtener 'base_url' directamente de context.config_env en environment.py.")

        return env_config.get('base_url')





    def check_grid_status(self, timeout=30) -> bool:

        """

        Verifica la conectividad y el estado del Hub de Selenium Grid.

        Usa una espera activa (polling).

        """

        if not self.is_grid_active(): # This will now call the corrected is_grid_active method

            _grid_manager_logger.info("Selenium Grid no está activo para el entorno actual. Saltando la verificación de estado.")

            return False




        hub_url = self.get_grid_hub_url() # This will now call the corrected get_grid_hub_url method

        if not hub_url:

            _grid_manager_logger.error("URL del Grid Hub no definida o vacía en la configuración del entorno. No se puede verificar el estado del Grid.")

            return False




        status_url = f"{hub_url}/status"

        _grid_manager_logger.info(f"Verificando estado del Selenium Grid en: {status_url}")




        start_time = time.time()

        while time.time() - start_time < timeout:

            try:

                response = requests.get(status_url, timeout=5)

                if response.status_code == 200:

                    status_data = response.json()

                    if status_data.get('value', {}).get('ready', False):

                        _grid_manager_logger.info("Selenium Grid Hub está listo y conectado.")

                        return True

                    else:

                        _grid_manager_logger.debug(f"Selenium Grid Hub no está listo aún. Respuesta: {status_data}")

                else:

                    _grid_manager_logger.debug(

                        f"Grid Hub respondió con código de estado {response.status_code}. Contenido: {response.text[:200]}...")

            except requests.exceptions.ConnectionError:

                _grid_manager_logger.debug(f"Esperando a que Selenium Grid Hub esté disponible en {hub_url}...")

            except requests.exceptions.Timeout:

                _grid_manager_logger.warning(f"Timeout al intentar conectar con el Grid Hub en {hub_url}.")

            except json.JSONDecodeError:

                _grid_manager_logger.error(f"Error al decodificar la respuesta JSON del Grid Hub en {status_url}. Contenido: {response.text[:200]}...", exc_info=True)

            except Exception as e:

                _grid_manager_logger.error(f"Error inesperado al verificar el estado del Grid: {e}", exc_info=True)

            time.sleep(2)




        _grid_manager_logger.error(f"Selenium Grid Hub no respondió o no está listo después de {timeout} segundos.")

        return False

 