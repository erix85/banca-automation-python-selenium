from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from selenium.webdriver.common.by import By  # Importar By para tipado

from ..utils.logger import logger

from ..utils.screenshots import take_screenshot


class SeleniumUtils:
    """

    Clase de utilidades para Selenium WebDriver, proporcionando métodos

    comunes de interacción con elementos y esperas.

    """

    def __init__(self, driver: WebDriver, default_timeout: int = 10):

        self.driver = driver

        self.default_timeout = default_timeout

        logger.info("Instancia de SeleniumUtils creada.")

    def _wait(self, timeout: int = None) -> WebDriverWait:

        """Retorna una instancia de WebDriverWait."""

        return WebDriverWait(self.driver, timeout if timeout is not None else self.default_timeout)

    def find_element(self, locator: tuple[By, str], timeout: int = None):

        """

        Encuentra un elemento utilizando un localizador y espera hasta que sea visible.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param timeout: Tiempo máximo de espera en segundos.

        :return: El elemento web encontrado.

        :raises TimeoutException: Si el elemento no es encontrado o visible en el tiempo.

        :raises WebDriverException: Para otros errores del WebDriver.

        """

        by_strategy, selector = locator

        try:

            element = self._wait(timeout).until(

                EC.visibility_of_element_located((by_strategy, selector))

            )

            logger.debug(f"Elemento localizado y visible: {locator}")

            return element

        except TimeoutException:

            logger.error(
                f"Tiempo de espera excedido: Elemento no visible en {timeout if timeout is not None else self.default_timeout}s para {locator}")

            take_screenshot(self.driver, f"element_not_visible_{by_strategy}_{selector}")  # Captura más específica

            raise

        except WebDriverException as e:

            logger.error(f"Error del WebDriver al buscar elemento {locator}: {e}")

            take_screenshot(self.driver, f"webdriver_error_{by_strategy}_{selector}")

            raise

    def find_elements(self, locator: tuple[By, str], timeout: int = None):

        """

        Encuentra múltiples elementos utilizando un localizador.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param timeout: Tiempo máximo de espera en segundos.

        :return: Lista de elementos web encontrados (puede estar vacía).

        :raises WebDriverException: Para otros errores del WebDriver.

        """

        by_strategy, selector = locator

        try:

            elements = self._wait(timeout).until(

                EC.presence_of_all_elements_located((by_strategy, selector))

            )

            logger.debug(f"Elementos localizados: {locator}")

            return elements

        except TimeoutException:

            logger.warning(
                f"Tiempo de espera excedido: No se encontraron elementos presentes en {timeout if timeout is not None else self.default_timeout}s para {locator}. Retornando lista vacía.")

            # No tomamos captura aquí, ya que el warning indica que la ausencia podría ser esperada

            return []

        except WebDriverException as e:

            logger.error(f"Error del WebDriver al buscar múltiples elementos {locator}: {e}")

            take_screenshot(self.driver, f"webdriver_error_multi_{by_strategy}_{selector}")

            raise

    def click_element(self, locator: tuple[By, str], timeout: int = None):

        """

        Hace clic en un elemento web después de esperar que sea clickeable.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param timeout: Tiempo máximo de espera en segundos.

        """

        by_strategy, selector = locator

        try:

            element = self._wait(timeout).until(

                EC.element_to_be_clickable((by_strategy, selector))

            )

            element.click()

            logger.info(f"Clic realizado en el elemento: {locator}")

        except TimeoutException:

            logger.error(
                f"Tiempo de espera excedido: Elemento no clickeable en {timeout if timeout is not None else self.default_timeout}s para {locator}")

            take_screenshot(self.driver, f"element_not_clickable_{by_strategy}_{selector}")

            raise

        except WebDriverException as e:

            logger.error(f"Error del WebDriver al hacer clic en elemento {locator}: {e}")

            take_screenshot(self.driver, f"webdriver_error_click_{by_strategy}_{selector}")

            raise

    def enter_text(self, locator: tuple[By, str], text: str, timeout: int = None):

        """

        Ingresa texto en un campo de entrada.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param text: El texto a ingresar.

        :param timeout: Tiempo máximo de espera en segundos.

        """

        by_strategy, selector = locator

        try:

            element = self._wait(timeout).until(

                EC.visibility_of_element_located((by_strategy, selector))

            )

            element.clear()  # Limpiar el campo antes de escribir

            element.send_keys(text)

            logger.info(f"Texto ingresado en {locator}: '{text[:50]}...'")  # Loguear solo los primeros 50 caracteres

        except TimeoutException:

            logger.error(
                f"Tiempo de espera excedido: Campo de texto no visible o no interactuable en {timeout if timeout is not None else self.default_timeout}s para {locator}")

            take_screenshot(self.driver, f"text_input_failed_{by_strategy}_{selector}")

            raise

        except WebDriverException as e:

            logger.error(f"Error del WebDriver al ingresar texto en {locator}: {e}")

            take_screenshot(self.driver, f"webdriver_error_text_{by_strategy}_{selector}")

            raise

    def get_element_text(self, locator: tuple[By, str], timeout: int = None) -> str:

        """

        Obtiene el texto de un elemento.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param timeout: Tiempo máximo de espera en segundos.

        :return: El texto del elemento.

        :raises TimeoutException: Si el elemento no es encontrado o visible.

        :raises WebDriverException: Para otros errores del WebDriver.

        """

        try:

            element = self.find_element(locator, timeout)  # Reutiliza find_element

            text = element.text

            logger.debug(f"Texto obtenido de {locator}: '{text}'")

            return text

        except Exception:  # find_element ya loguea y lanza, solo re-lanzamos

            raise

    def wait_for_element_visibility(self, locator: tuple[By, str], timeout: int = None):

        """

        Espera hasta que un elemento sea visible.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param timeout: Tiempo máximo de espera en segundos.

        :return: El elemento web visible.

        :raises TimeoutException: Si el elemento no se vuelve visible.

        :raises WebDriverException: Para otros errores del WebDriver.

        """

        by_strategy, selector = locator

        try:

            element = self._wait(timeout).until(

                EC.visibility_of_element_located((by_strategy, selector))

            )

            logger.debug(f"Elemento {locator} es visible.")

            return element

        except TimeoutException:

            logger.error(
                f"Elemento {locator} no se hizo visible en {timeout if timeout is not None else self.default_timeout}s.")

            take_screenshot(self.driver, f"element_not_visible_wait_{by_strategy}_{selector}")

            raise

        except WebDriverException as e:

            logger.error(f"Error del WebDriver al esperar visibilidad de {locator}: {e}")

            take_screenshot(self.driver, f"webdriver_error_visibility_{by_strategy}_{selector}")

            raise

    def is_element_present(self, locator: tuple[By, str], timeout: int = 5) -> bool:

        """

        Verifica si un elemento está presente en el DOM.

        No espera a que sea visible o interactuable.

        :param locator: Tupla (By.STRATEGY, "selector").

        :param timeout: Tiempo máximo de espera en segundos.

        :return: True si el elemento está presente, False en caso contrario.

        :raises WebDriverException: Para otros errores del WebDriver.

        """

        by_strategy, selector = locator

        try:

            self._wait(timeout).until(

                EC.presence_of_element_located((by_strategy, selector))

            )

            logger.debug(f"Elemento {locator} está presente en el DOM.")

            return True

        except (TimeoutException, NoSuchElementException):  # Ambos pueden ocurrir

            logger.debug(f"Elemento {locator} no está presente en el DOM dentro de {timeout}s.")

            return False

        except WebDriverException as e:

            logger.error(f"Error del WebDriver al verificar presencia de {locator}: {e}")

            take_screenshot(self.driver, f"webdriver_error_presence_{by_strategy}_{selector}")

            raise
