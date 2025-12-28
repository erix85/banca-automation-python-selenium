import json
import time
from behave import given, when, then
from pathlib import Path
from src.locators.web.autenticacion.login.login_locators import LoginPageLocators
from src.actions.web.autenticacion.login.login_actions import LoginActions
from src.utils.logger import get_logger
import os

logger = get_logger(__name__)


# --- Ruta a las credenciales de login (usando context.project_root) ---
# NO DEFINIR _LOGIN_CREDENTIALS_PATH directamente aquí con una ruta estática.
# Es mejor pasarla a través del contexto o configurarla de forma relativa al project_root.
# Por ejemplo, si tus credenciales están en 'vivienda/src/data/credentials.json'
# Lo leeremos dinámicamente.

def read_json_data(file_path):
    """Lee datos de un archivo JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

    # --- Implementación de los pasos ---


@given(u'estoy en la pagina web BE')
def step_impl(context):
    """

    Navega a la página de login.

    La URL base se obtiene del entorno configurado en `environment.py`.

    """

    logger.info(f"Navegando a la página de login en: {context.base_url}")
    context.driver.get(context.base_url)
    logger.info(f"ya estoy en la pagina web")

    try:

        # Usa la instancia de selenium_utils que se pasó a login_actions en environment.py

        context.login_actions.selenium_utils.wait_for_element_visibility(
            LoginPageLocators.USERNAME_FIELD, timeout=context.config_env['wait_timeout']

        )

        logger.info("Campo de usuario visible, página de login cargada.")

    except Exception as e:

        logger.error(f"El campo de usuario no se hizo visible en la página de login: {e}", exc_info=True)
        raise  # Re-lanza la excepción para que el escenario falle


@when(u'ingreso mi rut "{user_profile}"')
def step_impl(context, user_profile):
    """

    Lee las credenciales del perfil de usuario especificado desde el JSON

    y guarda el usuario y la contraseña en el contexto. Luego ingresa el RUT.

    """

    logger.info(f"Leyendo credenciales para el perfil: '{user_profile}'")

    # Construir la ruta al archivo JSON de credenciales usando context.project_root
    # Asegúrate de que este path coincida con donde realmente está tu archivo credentials.json
    # Por ejemplo, si está en C:\FrameworkQA\Python\VIBE\vivienda\src\data\credentials.json

    credentials_file_path = os.path.join(context.project_root, 'src', 'data', 'test_data', 'login_credentials.json')

    try:

        all_login_data = read_json_data(credentials_file_path)

    except FileNotFoundError:

        logger.error(f"Archivo de credenciales no encontrado en: {credentials_file_path}")

        raise

    except json.JSONDecodeError:

        logger.error(
            f"Error al parsear el JSON de credenciales en: {credentials_file_path}. Verifica la sintaxis del JSON.",
            exc_info=True)

        raise

    except Exception as e:

        logger.error(f"Error inesperado al leer el archivo JSON {credentials_file_path}: {e}", exc_info=True)

        raise

    if user_profile not in all_login_data:
        logger.error(

            f"Perfil de usuario '{user_profile}' no encontrado en el archivo JSON. Claves disponibles: {list(all_login_data.keys())}")

        raise ValueError(f"Perfil de usuario '{user_profile}' no encontrado en el archivo JSON.")

    user_data = all_login_data[user_profile]
    context.current_username = user_data.get('username')
    context.current_password = user_data.get('password')

    if not hasattr(context, 'login_actions') or context.login_actions is None:
        raise AttributeError("context.login_actions no está inicializado. Revisa tu setup en environment.py.")

    if context.current_username:
        context.login_actions.enter_username(context.current_username)
        logger.info(f"RUT ingresado para '{user_profile}': {context.current_username}")

    else:

        logger.warning(f"No se encontró 'username' para el perfil '{user_profile}' en el archivo JSON.")


@when(u'ingreso mi clave en linea')
def step_impl(context):
    """

    Ingresa la contraseña obtenida del perfil de usuario previamente cargado.

    """

    if not hasattr(context, 'current_password') or context.current_password is None:
        raise AttributeError(

            "Contraseña no encontrada en el contexto. Asegúrate de que el paso 'ingreso mi rut...' se ejecutó primero y que la contraseña está en el JSON.")

    if not hasattr(context, 'login_actions') or context.login_actions is None:
        raise AttributeError("context.login_actions no está inicializado. Revisa tu setup en environment.py.")

    context.login_actions.enter_password(context.current_password)

    logger.info("Contraseña en línea ingresada.")


@when(u'presiono el boton inciar sesion')
def step_impl(context):
    """

    Presiona el botón de iniciar sesión.

    """

    if not hasattr(context, 'login_actions') or context.login_actions is None:
        raise AttributeError("context.login_actions no está inicializado. Revisa tu setup en environment.py.")

    context.login_actions.click_login_button()

    logger.info("Botón de iniciar sesión presionado.")

# @then(u'I should be logged in successfully')

# def step_impl(context):

#     """

#     Verifica que el usuario ha iniciado sesión con éxito.

#     Esto puede ser comprobando la URL, la presencia de un elemento en la página de inicio, etc.

#     """

#     if not hasattr(context, 'web_login_actions') or context.web_login_actions is None:

#         raise AttributeError("context.web_login_actions no está inicializado. Revisa tu setup en environment.py.")


#     # Ejemplo: Verificar si la URL ha cambiado a una esperada después del login

#     # O verificar la visibilidad de un elemento en la página post-login

#     expected_url_after_login = "http://dbankdemo.com/bank/home" # Reemplaza con la URL real


#     # Puedes implementar la verificación dentro de web_login_actions o aquí directamente

#     if context.driver.current_url != expected_url_after_login:

#         logger.error(f"URL actual '{context.driver.current_url}' no coincide con la URL esperada post-login '{expected_url_after_login}'.")

#         # Aquí podrías añadir una captura de pantalla de la página actual antes de fallar

#         raise AssertionError(f"Fallo en el login: La URL no es la esperada después del login. Actual: {context.driver.current_url}")


#     # O verificar la presencia de un elemento específico de la página de inicio

#     # try:

#     #     context.web_login_actions.selenium_utils.wait_for_element_visibility(HomePageLocators.WELCOME_MESSAGE, timeout=context.config_env['wait_timeout'])

#     #     logger.info("Mensaje de bienvenida o elemento de la página de inicio visible.")

#     # except Exception as e:

#     #     logger.error(f"No se encontró el mensaje de bienvenida o elemento de la página de inicio: {e}")

#     #     raise AssertionError("No se pudo verificar el login exitoso (elemento no encontrado).")


#     logger.info("Login exitoso verificado.")
