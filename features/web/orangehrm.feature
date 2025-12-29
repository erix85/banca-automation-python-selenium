Feature: Gestión de Empleados (PIM) en OrangeHRM

  Como administrador de recursos humanos
  Quiero registrar nuevos empleados y asignarles credenciales de acceso
  Para que puedan ingresar al sistema OrangeHRM

  @web
  Scenario: Crear un nuevo empleado con credenciales de usuario activas
    Given que navego a la página de login de OrangeHRM
    When inicio sesión como administrador
    And navego al módulo PIM opción Agregar Empleado
    And ingreso los datos personales del empleado
      | primer_nombre | segundo_nombre | apellido |
      | Juan          | Andres         | Perez    |
    And capturo el ID de empleado generado para futura referencia
    And activo la opción de crear detalles de login
    And ingreso las credenciales y estado del usuario
      | nombre_usuario | password    | confirmar_password | estado  |
      | juan.perez.qa  | Password123 | Password123        | Enabled |
    And guardo el registro del nuevo empleado
    Then el sistema debería confirmar que el empleado fue guardado exitosamente
    And debería ver los detalles del perfil del empleado creado
    And cierro la sesión actual
    When inicio sesión con el usuario "juan.perez.qa" y clave "Password123"
    And cierro la sesión actual
    When inicio sesión como administrador
    And el administrador restablece la contraseña del usuario "juan.perez.qa" a "NewPass456!"
    And cierro la sesión actual
    When inicio sesión con el usuario "juan.perez.qa" y clave "NewPass456!"
    And cierro la sesión actual

