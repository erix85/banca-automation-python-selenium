from src.utils.selenium_utils import SeleniumUtils

class OrangeHRMPage:
    """
    Clase Base de Página para OrangeHRM.
    Inicializa las utilidades de Selenium y provee acceso al driver.
    """
    def __init__(self, driver):
        self.driver = driver
        self.utils = SeleniumUtils(driver)

    def get_utils(self):
        return self.utils