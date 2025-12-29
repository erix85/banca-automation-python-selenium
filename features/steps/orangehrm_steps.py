import time
from behave import given, when, then, step
from src.utils.logger import logger

@given('que navego a la página de login de OrangeHRM')
def step_impl(context):
    # La navegación ya ocurre en before_scenario, pero aseguramos estar en la URL correcta
    context.driver.get(context.base_url)
    logger.info("Navegando explícitamente a la página de login.")

@when('inicio sesión como administrador')
def step_impl(context):
    # Usamos la clase OrangeHRMAction refactorizada
    context.orangehrm_action.perform_login("Admin", "admin123")
    logger.info("Login realizado con credenciales de Administrador.")

@when('navego al módulo PIM opción Agregar Empleado')
def step_impl(context):
    context.orangehrm_action.navigate_to_add_employee()

@when('ingreso los datos personales del empleado')
def step_impl(context):
    for row in context.table:
        context.orangehrm_action.fill_employee_personal_details(
            first_name=row['primer_nombre'],
            middle_name=row['segundo_nombre'],
            last_name=row['apellido']
        )

@when('capturo el ID de empleado generado para futura referencia')
def step_impl(context):
    emp_id = context.orangehrm_action.get_employee_id()
    context.generated_employee_id = emp_id
    logger.info(f"ID de empleado capturado: {emp_id}")

@when('activo la opción de crear detalles de login')
def step_impl(context):
    context.orangehrm_action.activate_login_details()

@when('ingreso las credenciales y estado del usuario')
def step_impl(context):
    if not hasattr(context, 'user_map'):
        context.user_map = {}

    for row in context.table:
        original_username = row['nombre_usuario']
        # Generar nombre de usuario único para evitar duplicados en ejecuciones repetidas
        new_username = f"{original_username}_{int(time.time())}"
        context.user_map[original_username] = new_username

        context.orangehrm_action.fill_login_credentials(
            username=new_username,
            password=row['password'],
            confirm_password=row['confirmar_password']
        )
        # El estado se maneja por defecto como Enabled en el Page Object por simplicidad,
        # pero podríamos extenderlo usando row['estado']

@when('guardo el registro del nuevo empleado')
def step_impl(context):
    context.orangehrm_action.save_employee()

@then('el sistema debería confirmar que el empleado fue guardado exitosamente')
def step_impl(context):
    # Verificamos la presencia del Toast de éxito o la redirección al perfil
    assert context.orangehrm_action.is_success_message_displayed(), "No se mostró el mensaje de éxito."
    logger.info("Empleado guardado exitosamente.")

@then('debería ver los detalles del perfil del empleado creado')
def step_impl(context):
    assert context.orangehrm_action.is_profile_header_displayed(), "No se redirigió a la página de detalles del empleado."

@step('cierro la sesión actual')
def step_impl(context):
    context.orangehrm_action.perform_logout()
    logger.info("Sesión cerrada exitosamente.")

@when('inicio sesión con el usuario "{username}" y clave "{password}"')
def step_impl(context, username, password):
    # Si tenemos un usuario dinámico mapeado, lo usamos en lugar del estático
    if hasattr(context, 'user_map') and username in context.user_map:
        username = context.user_map[username]

    context.orangehrm_action.perform_login(username, password)
    logger.info(f"Login realizado con usuario: {username}")

@when('el administrador restablece la contraseña del usuario "{username}" a "{new_password}"')
def step_impl(context, username, new_password):
    # Si tenemos un usuario dinámico mapeado, lo usamos para buscarlo en la tabla de Admin
    if hasattr(context, 'user_map') and username in context.user_map:
        username = context.user_map[username]

    context.orangehrm_action.reset_password_as_admin(username, new_password)
    logger.info(f"Contraseña restablecida para {username} por el administrador.")
