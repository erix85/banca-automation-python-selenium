import json
import os
from os import path
from behave import *
from src.actions.api.login.api_login_actions import LoginActions
from src.utils.logger import get_logger

logger = get_logger(__name__)
# Obtén la ruta absoluta del directorio donde se encuentra este script (api_login_steps.py)

current_dir = path.dirname(path.abspath(__file__))

# Retrocede dos niveles para llegar a la raíz del proyecto 'vivienda'
# current_dir es 'C:\FrameworkQA\Python\VIBE\vivienda\features\steps'
# os.path.dirname(current_dir) es 'C:\FrameworkQA\Python\VIBE\vivienda\features'
# os.path.dirname(os.path.dirname(current_dir)) es 'C:\FrameworkQA\Python\VIBE\vivienda'
project_root = path.dirname(path.dirname(current_dir))

# Construye la ruta completa al archivo login_credential.json
# Suponiendo que está directamente en la raíz de 'vivienda'
credentials_file_path = path.join(project_root, 'src', 'data', 'test_data', 'login_credentials.json')
# Cargar las credenciales una sola vez al inicio
try:
    with open(credentials_file_path, 'r') as f:
        ALL_CREDENTIALS = json.load(f)
    logger.info(f"Archivo de credenciales cargado desde: {credentials_file_path}")
except FileNotFoundError:
    logger.error(f"ERROR: El archivo de credenciales no se encontró en: {credentials_file_path}")
    raise  # Vuelve a lanzar el error para que la ejecución falle
except json.JSONDecodeError as e:
    logger.error(f"ERROR: El archivo de credenciales '{credentials_file_path}' no es un JSON válido: {e}")
    raise
except Exception as e:
    logger.error(f"ERROR inesperado al cargar el archivo de credenciales: {e}")
    raise


@given('un usuario con "{credential_key}" y "{credential_type}"')
def step_impl(context, credential_key, credential_type):
    # Obtener el objeto de credenciales del diccionario cargado
    user_data = ALL_CREDENTIALS.get(credential_key)

    if not user_data:
        raise ValueError(f"La clave de credencial '{credential_key}' no se encontró en login_credential.json")

        # Asignar el nombre de usuario (o Rut, si es el identificador principal)
    # Asumo que 'username' es el identificador principal, ya sea email o Rut
    context.username = user_data.get("username")
    # Manejar el tipo de credencial o identificador adicional

    if credential_type == "password_valido":
        context.password = user_data.get("password")
        logger.info(f"Credenciales de usuario cargadas (password válido): {context.username}")
    elif credential_type == "password_invalida":
        context.password = "this_is_an_invalid_password_xyz"  # Una contraseña que sabes que fallará
        logger.info(f"Credenciales de usuario cargadas (password inválido): {context.username}")
    elif credential_type == "rut":
        # Si "rut" no es la contraseña, sino un identificador adicional para el login
        # Entonces, asume que la contraseña asociada sigue siendo la válida por defecto.
        # Si el RUT es el campo de username, ya está cubierto por user_data.get("username").
        # Si es un campo adicional que se envía, necesitarías un campo 'rut' en tu JSON.
        # Por ahora, si es el identificador principal, ya está en context.username.
        # Si es un campo *adicional* a la password, debes agregarlo al payload.
        # Aquí, asumiremos que si se pasa "rut", es para usar el "username" como el RUT directo
        # y la contraseña válida asociada.
        context.password = user_data.get("password")  # Asume que necesitas la contraseña válida con el RUT
        # Si necesitas el valor literal del RUT para enviarlo en algún otro campo del payload:
        # context.user_rut = user_data.get("username") # O user_data.get("rut") si tu JSON tiene una clave 'rut' separada
        logger.info(f"Credenciales de usuario cargadas (con RUT): {context.username}")
    else:
        raise ValueError(
            f"Tipo de credencial '{credential_type}' no reconocida. Use 'password_valido', 'password_invalida' o 'rut'.")


@when('hago una solicitud POST al endpoint de login')
def step_impl(context):
    try:
        # Asegúrate de que api_login_actions esté inicializado en before_scenario
        if not hasattr(context, 'api_login_actions') or context.api_login_actions is None:
            raise Exception("LoginActions para API no fue inicializado en before_scenario.")
            # Realiza la llamada a la API usando tu clase de acciones
        context.api_response = context.api_login_actions.api_utils.post(
            endpoint="auth/login",  # Endpoint específico para esta acción
            json_data={"username": context.username, "password": context.password}
        )
        logger.info(f"Solicitud de login enviada. Status code: {context.api_response.status_code}")
    except Exception as e:
        logger.error(f"Error al realizar la solicitud POST de login: {e}", exc_info=True)
        # Puedes decidir si el escenario debe fallar o marcarse como error aquí
        assert False, f"Fallo en la solicitud de login: {e}"


@then('la respuesta de la API debe tener un codigo de estado {status_code:d}')
def step_impl(context, status_code):
    expected_status = int(status_code)  # Behave puede pasar esto como string
    logger.info(
        f"Verificando que el código de estado sea: {expected_status}. Actual: {context.api_response.status_code}")
    assert context.api_response.status_code == expected_status, \
        f"Se esperaba código de estado {expected_status}, pero se obtuvo {context.api_response.status_code}. " \
            f"Respuesta: {context.api_response.text}"


logger.info("Código de estado verificado exitosamente.")


@then('la respuesta debe contener un "{key}"')
def step_impl(context, key):
    try:
        response_json = context.api_response.json()
        logger.info(f"Verificando que la respuesta contenga la clave: '{key}'")
        assert key in response_json, f"La clave '{key}' no se encontró en la respuesta JSON."
        logger.info(f"Clave '{key}' encontrada en la respuesta JSON.")
    except json.JSONDecodeError:
        assert False, f"La respuesta no es un JSON válido: {context.api_response.text}"
    except Exception as e:
        logger.error(f"Error al verificar la clave '{key}' en la respuesta: {e}", exc_info=True)
        assert False, f"Error al verificar la clave: {e}"


@then('la respuesta debe contener un mensaje de error')
def step_impl(context):
    try:
        response_json = context.api_response.json()
        # Esto es un ejemplo, el nombre de la clave de error puede variar (ej. 'error', 'message', 'details')
        assert "error" in response_json or "message" in response_json,\
            f"La respuesta no contiene una clave de error esperada. Respuesta: {response_json}"
        logger.info("Mensaje de error encontrado en la respuesta.")

    except json.JSONDecodeError:
        assert False, f"La respuesta no es un JSON válido: {context.api_response.text}"

    except Exception as e:
        logger.error(f"Error al verificar el mensaje de error: {e}", exc_info=True)
        assert False, f"Error al verificar el mensaje de error: {e}"
