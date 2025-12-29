import time
from selenium.webdriver.common.by import By
from src.page.web.orangehrm_page import OrangeHRMPage
from src.locators.web.orangehrm_locators import OrangeHRMLocators

class OrangeHRMAction(OrangeHRMPage):
    """
    Contiene la lógica de negocio y acciones principales para OrangeHRM.
    Hereda de OrangeHRMPage para acceso a utils y driver.
    """

    def perform_login(self, username, password):
        self.utils.enter_text(OrangeHRMLocators.LOGIN_USERNAME_INPUT, username)
        self.utils.enter_text(OrangeHRMLocators.LOGIN_PASSWORD_INPUT, password)
        self.utils.click_element(OrangeHRMLocators.LOGIN_BUTTON)

    def navigate_to_add_employee(self):
        self.utils.click_element(OrangeHRMLocators.MENU_PIM)
        self.utils.click_element(OrangeHRMLocators.NAV_ADD_EMPLOYEE)

    def fill_employee_personal_details(self, first_name, middle_name, last_name):
        self.utils.enter_text(OrangeHRMLocators.FIRST_NAME_INPUT, first_name)
        self.utils.enter_text(OrangeHRMLocators.MIDDLE_NAME_INPUT, middle_name)
        self.utils.enter_text(OrangeHRMLocators.LAST_NAME_INPUT, last_name)

    def get_employee_id(self):
        element = self.utils.find_element(OrangeHRMLocators.EMPLOYEE_ID_INPUT)
        return element.get_attribute("value")

    def activate_login_details(self):
        self.utils.click_element(OrangeHRMLocators.CREATE_LOGIN_DETAILS_SWITCH)

    def fill_login_credentials(self, username, password, confirm_password):
        self.utils.enter_text(OrangeHRMLocators.USER_NAME_INPUT, username)
        self.utils.enter_text(OrangeHRMLocators.USER_PASSWORD_INPUT, password)
        self.utils.enter_text(OrangeHRMLocators.CONFIRM_PASSWORD_INPUT, confirm_password)

    def save_employee(self):
        self.utils.click_element(OrangeHRMLocators.SAVE_BUTTON)

    def is_success_message_displayed(self):
        # Estrategia robusta: Verificar Toast O Redirección al Perfil
        if self.utils.is_element_present(OrangeHRMLocators.SUCCESS_TOAST):
            return True
        
        # Si el toast se perdió o no apareció, verificar si estamos en la página de detalles
        # Esto confirma que el guardado fue exitoso y hubo redirección.
        return self.utils.is_element_present(OrangeHRMLocators.PROFILE_HEADER)

    def is_profile_header_displayed(self):
        return self.utils.is_element_present(OrangeHRMLocators.PROFILE_HEADER)

    def perform_logout(self):
        self.utils.click_element(OrangeHRMLocators.USER_DROPDOWN)
        self.utils.click_element(OrangeHRMLocators.LOGOUT_LINK)

    def reset_password_as_admin(self, username, new_password):
        # Navegar a Admin -> User Management
        self.utils.click_element(OrangeHRMLocators.MENU_ADMIN)
        # Buscar usuario
        self.utils.enter_text(OrangeHRMLocators.USER_NAME_INPUT, username)
        self.utils.click_element(OrangeHRMLocators.SEARCH_BUTTON)
        # Editar usuario (Selector dinámico para asegurar que editamos al usuario correcto y esperar la búsqueda)
        dynamic_edit_button = (By.XPATH, f"//div[contains(@class, 'oxd-table-row') and .//div[normalize-space()='{username}']]//button[.//i[contains(@class, 'bi-pencil-fill')]]")
        self.utils.click_element(dynamic_edit_button)
        # Activar cambio de contraseña
        self.utils.click_element(OrangeHRMLocators.CHANGE_PASSWORD_CHECKBOX)
        # Pequeña espera para asegurar que los campos de contraseña se desplieguen correctamente
        time.sleep(0.5)
        # Asignar nueva clave
        self.utils.enter_text(OrangeHRMLocators.USER_PASSWORD_INPUT, new_password)
        self.utils.enter_text(OrangeHRMLocators.CONFIRM_PASSWORD_INPUT, new_password)
        self.utils.click_element(OrangeHRMLocators.SAVE_BUTTON)
        # CRÍTICO: Esperar a que aparezca el mensaje de éxito para asegurar que el cambio se procesó antes de salir
        self.utils.wait_for_element_visibility(OrangeHRMLocators.SUCCESS_TOAST)