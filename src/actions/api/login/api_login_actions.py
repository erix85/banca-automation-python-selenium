import requests
from src.utils.api_utils import ApiUtils
from src.utils.logger import get_logger

# Obtiene una instancia de logger para esta clase
logger = get_logger(__name__)


class LoginActions:
    """
    Clase para encapsular las acciones de autenticación (login) contra una API.
    """

    def __init__(self, env: str = 'qa'):
        """
        Inicializa la clase LoginActions con el entorno de API especificado.
        Args:
            env (str): El entorno de la API (ej. 'qa', 'development').
        """
        self.api_utils = ApiUtils(env)
        logger.info(f"LoginActions inicializado para el entorno: {env} con URL base: {self.api_utils.base_url}")

    def login_user(self, username: str, password: str) -> dict:

        """

        Realiza una petición POST al endpoint de login para autenticar un usuario.




        Args:

            username (str): El nombre de usuario o email del usuario.

            password (str): La contraseña del usuario.




        Returns:

            dict: La respuesta JSON de la API si la autenticación es exitosa,

                  generalmente conteniendo un token o datos del usuario.




        Raises:

            requests.exceptions.RequestException: Si la petición falla o el status code no es 2xx.

        """

        endpoint = "auth/login"  # O el endpoint real de tu API de login, ej: "v1/users/login"

        payload = {

            "username": username,

            "password": password

        }

        logger.info(f"Intentando login para el usuario: {username}")

        response = self.api_utils.post(endpoint, json_data=payload)

        # Opcional: Puedes agregar validaciones aquí si lo deseas, o manejarlas en los steps.

        # Por ejemplo, verificar si el código de estado es 200/201.

        if response.status_code in [200, 201]:

            logger.info(f"Login exitoso para el usuario: {username}. Status: {response.status_code}")

            return response.json()

        else:

            logger.error(

                f"Fallo en el login para el usuario: {username}. Status: {response.status_code}, Respuesta: {response.text}")

            response.raise_for_status()  # Lanza una excepción si el status code no es 2xx

            return {}  # Esto no se alcanzará si raise_for_status() es llamado, pero es un buen fallback.

    def get_auth_token(self, username: str, password: str) -> str | None:

        """

        Realiza el login y extrae el token de autenticación de la respuesta.




        Args:

            username (str): El nombre de usuario o email del usuario.

            password (str): La contraseña del usuario.




        Returns:

            str | None: El token de autenticación si se encuentra, None en caso contrario.

        """

        try:

            login_response = self.login_user(username, password)

            # Asume que el token viene en una clave como 'access_token' o 'token'

            token = login_response.get("access_token") or login_response.get("token")

            if token:

                logger.info("Token de autenticación obtenido exitosamente.")

                return token

            else:

                logger.warning("Login exitoso, pero no se encontró un token en la respuesta.")

                return None

        except Exception as e:

            logger.error(f"Error al obtener token para {username}: {e}")

            return None

            # Si la API tiene un endpoint para logout

    def logout_user(self, token: str) -> requests.Response:

        """

        Realiza una petición POST al endpoint de logout para cerrar la sesión.




        Args:

            token (str): El token de autenticación a invalidar.




        Returns:

            requests.Response: El objeto de respuesta de la API.

        """

        endpoint = "auth/logout"  # O el endpoint real de tu API de logout

        headers = {"Authorization": f"Bearer {token}"}

        logger.info("Intentando cerrar sesión (logout).")

        response = self.api_utils.post(endpoint, headers=headers)

        if response.status_code in [200, 204]:

            logger.info("Logout exitoso.")

        else:

            logger.error(f"Fallo en el logout. Status: {response.status_code}, Respuesta: {response.text}")

        return response
