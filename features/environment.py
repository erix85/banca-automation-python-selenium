import sys
import os
from behave import *

# Importaciones necesarias (todas deben ser absolutas)

from src.utils.logger import get_logger, setup_logging
from src.config.config_reader import ConfigReader
from src.config.webdriver_factory import WebDriverFactory
from src.config.grid_manager import GridManager
from src.utils.definitions import PROJECT_ROOT
from selenium.common.exceptions import WebDriverException

# No se usa directamente aquí, pero es buena práctica mantenerla si se usa en otro lugar

from src.utils.screenshots import take_screenshot
from src.utils.selenium_utils import SeleniumUtils
from src.actions.web.orangehrm_actions import OrangeHRMAction

logger = get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def before_all(context):
    """Se ejecuta una vez antes de todas las suites de features para configurar el entorno global."""
    # Asigna la ruta raíz del proyecto al contexto
    # es la raíz del proyecto, así que navegamos hasta ella.

    context.project_root = str(PROJECT_ROOT)

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

        # Configura el sistema de logging global al inicio

    setup_logging()

    # Asigna un logger específico para el contexto de Behave

    context.logger = get_logger('automation')
    context.logger.info("Iniciando la ejecución de pruebas del framework VIBE.")

    # --- 1. Inicializar ConfigReader ---

    # Instancia ConfigReader una sola vez y pásale la ruta correcta al archivo INI.

    config_file_path = os.path.join(context.project_root, 'src', 'config', 'environment.ini')
    context.config_reader = ConfigReader(config_file_path)
    context.logger.info("ConfigReader inicializado y archivo de configuración cargado exitosamente.")

    # --- 2. Determinar el entorno de ejecución ---
    # Prioridad: Variable de entorno del sistema (ENVIRONMENT) > userdata de Behave (-D environment=...) > 'default'
    # Usa `.lower()` para estandarizar el nombre del entorno.

    context.environment = os.environ.get('ENVIRONMENT', context.config.userdata.get('environment', 'default')).lower()
    context.logger.info(f"Entorno de ejecución seleccionado: '{context.environment}'")

    # --- 3. Cargar TODA la configuración del entorno ---
    # 'get_environment_config' de ConfigReader devuelve un diccionario
    # con todos los valores ya convertidos a sus tipos correctos (int, bool, str).

    context.config_env = context.config_reader.get_environment_config(context.environment)
    context.logger.info(f"Configuración del entorno '{context.environment}': {context.config_env}")

    # --- 4. Asignar valores comunes directamente al contexto para facilitar el acceso ---
    # Accede a los valores directamente del diccionario `context.config_env`

    context.browser_name = context.config_env.get('browser', 'chrome')
    context.is_headless = context.config_env.get('headless', False)  # Ya es booleano
    context.wait_timeout = context.config_env.get('wait_timeout', 30)  # Ya es entero
    context.implicit_wait = context.config_env.get('implicit_wait', 5)  # Ya es entero
    context.base_url = context.config_env.get('base_url')
    context.api_base_url = context.config_env.get('api_base_url')
    context.screenshot_on_fail = context.config_env.get('screenshot_on_fail', True)  # Asegúrate de que sea booleano
    context.logger.info(f"Navegador configurado: '{context.browser_name}' (Headless: {context.is_headless})")

    # --- 5. Configurar GridManager y WebDriverFactory ---

    context.grid_manager = GridManager(context.config_reader)  # Pasamos el config_reader ya inicializado
    context.grid_manager.set_environment(context.environment)  # Informa a GridManager sobre el entorno actual
    context.logger.info("GridManager inicializado. Preparado para cargar configuraciones por entorno.")
    context.webdriver_factory = WebDriverFactory(grid_manager=context.grid_manager)
    context.logger.info("WebDriverFactory inicializada.")

    if context.config_env.get('grid_active', False):  # Usa .get() para booleanos
        context.logger.info(f"Configurado para usar Selenium Grid en: {context.config_env['grid_hub_url']}")

        if not context.grid_manager.check_grid_status():
            context.logger.critical("Selenium Grid no está disponible. Las pruebas web/mobile pueden fallar.")

    else:
        context.logger.info("Selenium Grid no está configurado o no está activo para el entorno actual.")


def before_scenario(context, scenario):
    """
    Se ejecuta antes de cada escenario.
    Inicializa WebDriver o cliente API dependiendo de los tags del escenario.
    """

    context.logger.info(f"Comenzando escenario: '{scenario.name}'")
    context.driver = None  # Inicializa a None para cada escenario
    context.api_client = None  # Inicializa a None para cada escenario
    context.current_scenario_type = 'none'  # Resetea el tipo de escenario

    if 'web' in scenario.tags:

        context.logger.info(f"Escenario con tag '@web'. Inicializando WebDriver para: {context.browser_name}")

        try:
            context.driver = context.webdriver_factory.get_webdriver(
                browser_name=context.browser_name,
                headless=context.is_headless,
                use_manual_drivers=context.config_env.get('use_manual_drivers', True),
                manual_drivers_path=context.config_env.get('manual_drivers_path', '')
            )

            if not context.driver:
                raise WebDriverException(
                    "WebDriver no pudo ser inicializado por WebDriverFactory. get_webdriver retornó None.")

            # --- Configuración del Navegador ---
            context.driver.maximize_window()
            # Es buena práctica configurar el implicit wait ANTES de navegar
            context.driver.implicitly_wait(context.implicit_wait)            
            context.logger.info(f"Navegador iniciado: {context.browser_name}")

            # --- Navegación ---
            try:
                context.logger.info(f"Navegando a URL: {context.base_url}")
                context.driver.get(context.base_url)
            except WebDriverException as e:
                context.logger.critical(f"Error de conexión al navegar a {context.base_url}. El sitio puede estar caído.")
                raise e # Re-lanzar para que el bloque externo lo maneje, pero ya con log claro

            # --- Inicialización de Page Objects ---
            context.selenium_utils = SeleniumUtils(context.driver, context.wait_timeout)
            context.orangehrm_action = OrangeHRMAction(context.driver)
            context.current_scenario_type = 'web'

        except WebDriverException as e:
            context.logger.critical(f"Fallo crítico en setup WEB: {e}")
            scenario.skip(f"Setup Fallido: {e}")
            context.driver = None  # Asegurarse de que el driver sea None si falla

        except Exception as e:  # Captura cualquier otra excepción inesperada

            context.logger.critical(f"Error genérico al inicializar WebDriver para {context.browser_name}: {e}",
                                    exc_info=True)

            scenario.skip(f"Fallo inesperado al inicializar WebDriver: {e}")
            context.driver = None




    elif 'api' in scenario.tags:

        context.logger.info(
            f"Escenario con tag '@api'. Inicializando cliente API para el entorno: {context.environment}")

        try:

            # Pasa el entorno al constructor de tus acciones API

            # context.api_login_actions = ApiLoginActions(env=context.environment)
            context.current_scenario_type = 'api'
            context.logger.info(f"Cliente API (LoginActions) inicializado para entorno '{context.environment}'.")

        except Exception as e:

            context.logger.critical(f"Error al inicializar cliente API: {e}", exc_info=True)
            scenario.skip(f"Fallo al inicializar cliente API: {e}")
            context.api_client = None  # Asegúrate de que sea None si falla

    else:

        context.logger.info("El escenario no tiene tags @web o @api. No se inicializa WebDriver ni cliente API.")
        context.current_scenario_type = 'none'


def after_scenario(context, scenario):
    """
    Se ejecuta después de cada escenario.
    Cierra el WebDriver y maneja capturas de pantalla en caso de fallo para pruebas web.
    """

    context.logger.info(f"Finalizando escenario: '{scenario.name}'")

    if context.current_scenario_type == 'web':  # Usa la variable que seteamos en before_scenario

        if scenario.status == 'failed' and context.config_env.get('screenshot_on_fail', False):

            context.logger.error(f"El escenario WEB '{scenario.name}' ha FALLADO.")

            try:

                screenshot_path = take_screenshot(context.driver, scenario.name)
                context.logger.error(f"Captura de pantalla tomada en: {screenshot_path}")

            except Exception as e:

                context.logger.warning(f"No se pudo tomar captura de pantalla para '{scenario.name}': {e}",
                                       exc_info=True)

                # Cierre del WebDriver

        if hasattr(context, 'driver') and context.driver:

            try:

                context.driver.quit()
                context.logger.info(f"WebDriver cerrado para el escenario '{scenario.name}'.")

            except WebDriverException as e:

                context.logger.warning(f"Error al intentar cerrar WebDriver para '{scenario.name}': {e}", exc_info=True)

            except Exception as e:

                context.logger.warning(f"Error inesperado al cerrar WebDriver para '{scenario.name}': {e}",
                                       exc_info=True)

            finally:

                # Limpiar referencias del contexto

                context.driver = None

                context.selenium_utils = None

                context.orangehrm_action = None

        else:

            context.logger.debug(
                f"No hay WebDriver para cerrar para el escenario '{scenario.name}' (posiblemente no se inicializó o falló la inicialización).")




    elif context.current_scenario_type == 'api':

        context.logger.info(f"Escenario API '{scenario.name}' finalizado. No requiere cierre de WebDriver.")

        # Aquí puedes añadir cualquier limpieza específica para el cliente API si es necesario
        # context.api_client = None # Si es un objeto grande que necesita ser liberado explícitamente
        # Limpieza de referencias API si es necesario (generalmente no es tan crítico como WebDriver)

        if hasattr(context, 'api_login_actions'):
            context.api_login_actions = None

            # Si tu api_client fuera un objeto con recursos a cerrar, lo harías aquí

        context.api_client = None  # Para asegurarte de que quede en None si se asignó previamente




    else:  # Esto cubre 'none' o escenarios sin tags específicos

        context.logger.debug(
            f"El escenario '{scenario.name}' no tiene tags @web o @api. No se requiere limpieza especial.")

        # Registro final del escenario

    context.logger.info(f"Escenario '{scenario.name}' finalizado con estado: {scenario.status}")
    context.logger.info(f"Entorno de ejecución: {context.environment}")

    if 'web' in scenario.tags and hasattr(context, 'base_url'):

        context.logger.info(f"URL Base Web: {context.base_url}")
        context.logger.info(f"Navegador usado: {context.browser_name}")

    elif 'api' in scenario.tags and hasattr(context, 'api_base_url'):

        context.logger.info(f"URL Base API: {context.api_base_url}")

    context.logger.info("-" * 50)


def after_feature(context, feature):
    """Se ejecuta después de cada feature."""

    # Usamos context.logger si está disponible, si no, el logger global

    current_logger = context.logger if hasattr(context, 'logger') else logger
    current_logger.info(f"Feature '{feature.name}' finalizada.")


def after_all(context):
    """Se ejecuta una vez después de todas las suites de features."""

    current_logger = context.logger if hasattr(context, 'logger') else logger
    current_logger.info("Fin de la ejecución de todas las features.")
    current_logger.info("Finalizada la ejecución de pruebas del framework VIBE.")

    # No es común necesitar logging.shutdown() a menos que uses manejadores de archivos muy específicos
    # que necesiten ser cerrados explícitamente y no por el recolector de basura de Python.
