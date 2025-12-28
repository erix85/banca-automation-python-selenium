from src.locators.web.autenticacion.login.login_locators import LoginPageLocators
from src.utils.selenium_utils import SeleniumUtils
from src.utils.logger import get_logger
logger = get_logger(__name__)


class LoginActions:
    """
    Clase que encapsula las acciones de alto nivel en la página de login.
    """

    def __init__(self, driver, selenium_utils: SeleniumUtils):
        self.driver = driver
        self.selenium_utils = selenium_utils
        self.locators = LoginPageLocators
        logger.info("Instancia de LoginActions creada.")

    def enter_username(self, username: str):
        """
        Ingresa el nombre de usuario en el campo correspondiente.
        """
        logger.info(f"Ingresando usuario: {username}")
        self.selenium_utils.enter_text(self.locators.USERNAME_FIELD, username)

    def enter_password(self, password: str):
        """
        Ingresa la contraseña en el campo correspondiente.
        """
        logger.info("Ingresando contraseña.")  # No loguear la contraseña por seguridad
        self.selenium_utils.enter_text(self.locators.PASSWORD_FIELD, password)  # Usar self.locators

    def click_login_button(self):
        """
        Hace clic en el botón de login.
        """
        logger.info("Haciendo clic en el botón de login.")
        self.selenium_utils.click_element(self.locators.LOGIN_BUTTON)  # Usar self.locators

    def perform_login(self, username: str, password: str):
        """
        Realiza el proceso completo de login.
        """
        logger.info(f"Intentando login con usuario: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        logger.info("Proceso de login completado.")

    def get_error_message(self) -> str:
        """
        Obtiene el texto del mensaje de error de login, si existe.
        """
        logger.info("Intentando obtener mensaje de error de login.")
        try:
            # Usamos wait_for_element_visibility directamente para asegurar que el elemento está allí
            error_element = self.selenium_utils.wait_for_element_visibility(self.locators.ERROR_MESSAGE, timeout=5)
            message = error_element.text
            logger.warning(f"Mensaje de error de login encontrado: {message}")
            return message
        except Exception:
            logger.info("No se encontró mensaje de error de login o no es visible.")
            return ""

    def is_login_successful(self) -> bool:
        """
        Verifica si el login fue exitoso.
        En el sitio 'dbankdemo.com', después de un login exitoso, la URL cambia a 'bank/main'
        y el campo de username/password desaparece.
        """
        logger.info("Verificando si el login fue exitoso.")
        # La URL después del login es http://dbankdemo.com/bank/main
        if "bank/main" in self.driver.current_url:
            logger.info("La URL ha cambiado a la esperada después del login (bank/main).")
            # Adicionalmente, verifica que el campo de usuario ya no está presente
            if not self.selenium_utils.is_element_present(self.locators.USERNAME_FIELD, timeout=2):
                logger.info("Campo de usuario no presente. Login exitoso.")
                return True
            else:
                logger.warning("Campo de usuario aún presente. Login podría no ser exitoso.")
                return False
        else:
            logger.warning(f"La URL actual ({self.driver.current_url}) no contiene 'bank/main'.")
            return False
