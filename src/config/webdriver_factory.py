import os
import platform
from pathlib import Path
from selenium import webdriver
from typing import Optional, Any, Union


# Importaciones correctas para las clases Options

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


# Importaciones correctas para las clases Service de Selenium 4.x

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService


# Importaciones para el WebDriver local y remoto

from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

# Importaciones de webdriver_manager

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# Importación de excepciones de Selenium

from selenium.common.exceptions import WebDriverException, SessionNotCreatedException


# Importaciones de tu proyecto

from src.utils.logger import get_logger
from src.definitions import PROJECT_ROOT

from src.config.grid_manager import GridManager


# Obtén una instancia de logger específica para este módulo

_webdriver_factory_logger = get_logger(__name__)


class WebDriverFactory:
    """

    Clase Factory para crear instancias de WebDriver, soportando ejecución local y en Selenium Grid.

    Utiliza webdriver_manager para gestionar automáticamente los ejecutables de los navegadores locales.

    """

    def __init__(self, grid_manager: GridManager) -> None:

        if grid_manager is None:

            raise ValueError("GridManager must be provided to WebDriverFactory.")

        self.grid_manager = grid_manager

        # Usa la ruta absoluta definida en definitions.py para mayor robustez
        # Esto evita que el código se rompa si mueves este archivo de carpeta.
        self._PROJECT_ROOT = PROJECT_ROOT

        # Define la ruta de la carpeta 'drivers' del proyecto (puede ser usada como default o referencia)

        self.drivers_folder_path = self._PROJECT_ROOT / "src" / "data" / "drivers"

        _webdriver_factory_logger.info(
            f"Ruta de la carpeta 'drivers' del proyecto: {self.drivers_folder_path}"
        )

        _webdriver_factory_logger.info("WebDriverFactory inicializada.")

    def _get_browser_options(
        self,
        browser_name: str,
        headless: bool = False,
        incognito: bool = False,
        mobile_device_name: Optional[str] = None,
        page_load_strategy: str = "normal",
        locale: str = "es-CL"
    ) -> Any:
        """

        Crea y retorna un objeto de opciones de navegador (ChromeOptions, FirefoxOptions, EdgeOptions)

        basado en el nombre del navegador y si el modo headless está activo.

        """

        browser_name = browser_name.lower()

        options_obj = None

        # Configuración de carpeta de descargas centralizada en la raíz del proyecto
        download_dir = self._PROJECT_ROOT / "downloads"
        download_dir.mkdir(exist_ok=True)

        # Configuración común para navegadores basados en Chromium (Chrome y Edge)
        if browser_name in ["chrome", "edge"]:
            if browser_name == "chrome":
                options_obj = ChromeOptions()
            else:
                options_obj = EdgeOptions()

            options_obj.page_load_strategy = page_load_strategy
            options_obj.accept_insecure_certs = True
            
            # Argumentos comunes
            common_args = [
                "--ignore-certificate-errors",
                "--disable-popup-blocking",
                "--disable-notifications"
            ]
            for arg in common_args:
                options_obj.add_argument(arg)

            if locale:
                options_obj.add_argument(f"--lang={locale}")

            if incognito:
                arg = "--incognito" if browser_name == "chrome" else "-inprivate"
                options_obj.add_argument(arg)

            if mobile_device_name:
                mobile_emulation = {"deviceName": mobile_device_name}
                options_obj.add_experimental_option("mobileEmulation", mobile_emulation)
                _webdriver_factory_logger.info(f"Modo de emulación móvil activado en {browser_name}: {mobile_device_name}")

            prefs = {
                "download.default_directory": str(download_dir),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
            }
            options_obj.add_experimental_option("prefs", prefs)

            if headless:
                options_obj.add_argument("--headless=new")
                options_obj.add_argument("--disable-gpu")
                options_obj.add_argument("--window-size=1920,1080")
                if browser_name == "chrome":
                    options_obj.add_argument("--no-sandbox")
                    options_obj.add_argument("--disable-dev-shm-usage")
                
                _webdriver_factory_logger.debug(f"Opciones {browser_name} para headless aplicadas.")
            else:
                options_obj.add_argument("--start-maximized")

        elif browser_name == "firefox":

            options_obj = FirefoxOptions()

            options_obj.page_load_strategy = page_load_strategy

            options_obj.accept_insecure_certs = True  # Vital para Firefox en entornos de QA

            # Preferencias de descarga para Firefox
            options_obj.set_preference("browser.download.folderList", 2)
            options_obj.set_preference("browser.download.dir", str(download_dir))
            options_obj.set_preference("browser.download.useDownloadDir", True)
            options_obj.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf,application/octet-stream,application/vnd.ms-excel,text/csv,application/zip,application/json,text/plain")

            if locale:
                options_obj.set_preference("intl.accept_languages", locale)

            # Bloqueo de notificaciones y popups (Equivalente a los flags de Chrome)
            options_obj.set_preference("dom.webnotifications.enabled", False)
            options_obj.set_preference("dom.push.enabled", False)
            options_obj.set_preference("dom.disable_open_during_load", False) # False = Permitir popups (deshabilita el bloqueador)

            if incognito:
                options_obj.add_argument("-private")

            if headless:

                options_obj.add_argument("-headless")
                options_obj.add_argument("--width=1920")
                options_obj.add_argument("--height=1080")

                _webdriver_factory_logger.debug(
                    "Opciones Firefox para headless aplicadas."
                )

            if mobile_device_name:
                _webdriver_factory_logger.warning(f"Firefox no soporta emulación móvil nativa (mobileEmulation). Se ignorará el dispositivo: {mobile_device_name}")

        else:

            _webdriver_factory_logger.error(
                f"Navegador '{browser_name}' no soportado para la creación de opciones. No se inicializará el WebDriver."
            )
            raise ValueError(f"Navegador no soportado para opciones: {browser_name}")

        _webdriver_factory_logger.debug(
            f"Opciones finales para {browser_name}: {options_obj.to_capabilities()}"
        )

        return options_obj

    def _create_remote_driver(self, browser_name: str, options_obj) -> Optional[webdriver.Remote]:
        """Intenta crear un WebDriver remoto conectado al Grid."""
        _webdriver_factory_logger.info(
            f"Intentando inicializar WebDriver con Selenium Grid para: {browser_name}"
        )
        try:
            hub_url = self.grid_manager.get_grid_hub_url()
            driver = webdriver.Remote(
                command_executor=hub_url,
                options=options_obj,
            )
            _webdriver_factory_logger.info(
                f"WebDriver de Selenium Grid para {browser_name} creado exitosamente."
            )
            return driver
        except WebDriverException as e:
            _webdriver_factory_logger.critical(
                f"Error al conectar con Selenium Grid para {browser_name}: {e}. Intentando con WebDriver local."
            )
            return None

    def _create_manual_driver(self, browser_name: str, manual_drivers_path: Union[str, Path, None], options_obj) -> Optional[webdriver.Remote]:
        """Intenta crear un WebDriver local usando un ejecutable manual."""
        # Si no se provee ruta, usar la default del proyecto
        if not manual_drivers_path:
            manual_drivers_path = self.drivers_folder_path

        # Convierte a Path y resuelve si es relativo o absoluto automáticamente
        # Nota: Si manual_drivers_path ya es absoluto (ej. self.drivers_folder_path), 
        # pathlib ignora self._PROJECT_ROOT, lo cual es el comportamiento deseado.
        abs_manual_drivers_folder = (self._PROJECT_ROOT / manual_drivers_path).resolve()

        browser_name_lower = browser_name.lower()
        system_platform = platform.system().lower()
        ext = ".exe" if "win" in system_platform else ""
        
        # Mapeo de ejecutables para simplificar la lógica condicional
        executables = {
            "chrome": f"chromedriver{ext}",
            "firefox": f"geckodriver{ext}",
            "edge": f"msedgedriver{ext}"
        }
        
        executable_name = executables.get(browser_name_lower)
        if not executable_name:
            _webdriver_factory_logger.warning(f"No se ha definido un ejecutable manual para: {browser_name}")
            return None

        driver_exe_path = abs_manual_drivers_folder / executable_name

        if driver_exe_path.exists():
            _webdriver_factory_logger.info(f"Usando driver manual para {browser_name}: {driver_exe_path}")
            try:
                service = None
                # Convertimos Path a string porque Selenium a veces prefiere strings puros para rutas
                str_path = str(driver_exe_path)
                if browser_name_lower == "chrome":
                    service = ChromeService(executable_path=str_path)
                    return webdriver.Chrome(service=service, options=options_obj)
                elif browser_name_lower == "firefox":
                    service = FirefoxService(executable_path=str_path)
                    return webdriver.Firefox(service=service, options=options_obj)
                elif browser_name_lower == "edge":
                    service = EdgeService(executable_path=str_path)
                    return webdriver.Edge(service=service, options=options_obj)
            except WebDriverException as e:
                _webdriver_factory_logger.critical(
                    f"Error al inicializar WebDriver manual para {browser_name}: {e}", exc_info=True
                )
                raise Exception(f"Fallo al inicializar WebDriver manual: {e}")
        
        _webdriver_factory_logger.warning(
            f"Driver manual para {browser_name} NO ENCONTRADO en: {driver_exe_path}. Intentando con webdriver_manager."
        )
        return None

    def _create_manager_driver(self, browser_name: str, options_obj) -> Optional[webdriver.Remote]:
        """Crea un WebDriver local usando webdriver_manager."""
        _webdriver_factory_logger.info("Configurado para usar webdriver_manager.")
        browser_name = browser_name.lower()
        try:
            # Mapeo de configuración para evitar if/elif repetitivos (Clean Code)
            drivers_map = {
                "chrome": (ChromeService, ChromeDriverManager(chrome_type=ChromeType.GOOGLE), webdriver.Chrome),
                "firefox": (FirefoxService, GeckoDriverManager(), webdriver.Firefox),
                "edge": (EdgeService, EdgeChromiumDriverManager(), webdriver.Edge),
            }

            if browser_name in drivers_map:
                service_cls, manager_inst, driver_cls = drivers_map[browser_name]
                service = service_cls(manager_inst.install())
                driver = driver_cls(service=service, options=options_obj)
                
                _webdriver_factory_logger.info(
                    f"WebDriver para {browser_name} inicializado exitosamente usando webdriver_manager."
                )
                return driver
        except Exception as e:
            _webdriver_factory_logger.critical(
                f"Error inesperado al inicializar WebDriver para {browser_name}: {e}", exc_info=True
            )
            raise Exception(f"Fallo al inicializar WebDriver: {e}")
        return None

    def get_webdriver(
        self,
        browser_name: str,
        headless: bool = False,
        use_manual_drivers: bool = False,
        manual_drivers_path: Union[str, Path, None] = None,
        incognito: bool = False,
        mobile_device_name: Optional[str] = None,
        page_load_strategy: str = "normal",
        locale: str = "es-CL",
    ) -> webdriver.Remote:
        options_obj = self._get_browser_options(browser_name, headless, incognito, mobile_device_name, page_load_strategy, locale)
        driver = None

        # 1. Intentar Selenium Grid
        if self.grid_manager.is_grid_active():
            driver = self._create_remote_driver(browser_name, options_obj)
        
        # 2. Si no hay driver aún (Grid inactivo o falló), intentar Driver Manual
        if not driver and use_manual_drivers:
            try:
                driver = self._create_manual_driver(browser_name, manual_drivers_path, options_obj)
            except Exception as e:
                _webdriver_factory_logger.warning(
                    f"Fallo al inicializar driver manual para {browser_name}: {e}. Intentando fallback a WebDriverManager."
                )

        # 3. Fallback final: WebDriverManager
        if not driver:
            driver = self._create_manager_driver(browser_name, options_obj)

        # Configuración post-creación común (DRY)
        if driver:
            if not headless:
                driver.maximize_window()
            return driver

        # Si por alguna razón no se pudo inicializar ningún driver (ej. navegador no soportado en el bloque try)
        _webdriver_factory_logger.critical(
            f"No se pudo inicializar WebDriver para el navegador: {browser_name}"
        )

        raise Exception(
            f"No se pudo inicializar WebDriver para el navegador: {browser_name}"
        )
