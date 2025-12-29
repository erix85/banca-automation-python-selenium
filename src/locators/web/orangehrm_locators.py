from selenium.webdriver.common.by import By

class OrangeHRMLocators:
    # --- Login ---
    LOGIN_USERNAME_INPUT = (By.NAME, "username")
    LOGIN_PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(@class, 'orangehrm-login-button')]")
    FORGOT_PASSWORD_LINK = (By.XPATH, "//p[contains(@class, 'orangehrm-login-forgot-header')]")
    
    # --- Header / User Menu ---
    USER_DROPDOWN = (By.CLASS_NAME, "oxd-userdropdown-tab")
    LOGOUT_LINK = (By.XPATH, "//a[text()='Logout']")

    # --- PIM / Add Employee ---
    MENU_PIM = (By.XPATH, "//span[text()='PIM']")
    NAV_ADD_EMPLOYEE = (By.XPATH, "//a[text()='Add Employee']")
    
    FIRST_NAME_INPUT = (By.NAME, "firstName")
    MIDDLE_NAME_INPUT = (By.NAME, "middleName")
    LAST_NAME_INPUT = (By.NAME, "lastName")
    EMPLOYEE_ID_INPUT = (By.XPATH, "//label[text()='Employee Id']/../following-sibling::div//input")
    
    CREATE_LOGIN_DETAILS_SWITCH = (By.XPATH, "//div[contains(@class, 'oxd-switch-wrapper')]")
    
    USER_NAME_INPUT = (By.XPATH, "//label[normalize-space()='Username']/../following-sibling::div//input")
    USER_PASSWORD_INPUT = (By.XPATH, "//label[normalize-space()='Password']/../following-sibling::div//input")
    CONFIRM_PASSWORD_INPUT = (By.XPATH, "//label[normalize-space()='Confirm Password']/../following-sibling::div//input")
    SAVE_BUTTON = (By.XPATH, "//button[@type='submit']")
    SUCCESS_TOAST = (By.XPATH, "//div[contains(@class, 'oxd-toast-content')]")
    PROFILE_HEADER = (By.XPATH, "//h6[text()='Personal Details']")
    INPUT_FIELD_ERROR = (By.XPATH, "//span[contains(@class, 'oxd-input-field-error-message')]")

    # --- Admin / User Management (Recovery Flow) ---
    MENU_ADMIN = (By.XPATH, "//span[text()='Admin']")
    # Reutilizamos USER_NAME_INPUT para la búsqueda ya que el selector es compatible
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")
    EDIT_USER_BUTTON = (By.XPATH, "//button[.//i[contains(@class, 'bi-pencil-fill')]]")
    CHANGE_PASSWORD_CHECKBOX = (By.XPATH, "//label[contains(., 'Change Password')]/ancestor::div[contains(@class, 'oxd-input-group')]//span[contains(@class, 'oxd-checkbox-input')]")