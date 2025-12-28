Feature: Inicio Sesión de Cliente VIBE

  Como cliente del Banco Estado

  Quiero iniciar mi sesión en el portal web VIBE

  Para poder navegar por la sesion de usuario


  @web

  Scenario:Inicio de sesion con credenciales validas

    Given estoy en la pagina web BE

    When ingreso mi rut "usuario_valido"

    And ingreso mi clave en linea

    And presiono el boton inciar sesion