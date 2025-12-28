from selenium.webdriver.common.by import By


class LoginPageLocators:
    """ Clase que contiene los localizadores (By, selector) para los elementos de la página de login."""
    USERNAME_FIELD = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_FIELD = (By.NAME, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
