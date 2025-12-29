# Automatizacin Web Selenium Behave

Este proyecto es un framework de automatización de pruebas End-to-End (E2E) robusto y escalable, construido con **Python**, **Selenium WebDriver** y **Behave** (BDD).

Está diseñado siguiendo patrones de diseño modernos como **Page Object Model (POM)**, **Factory Pattern** para la gestión de drivers, y una arquitectura modular separada en capas (Configuración, Acciones, Páginas, Localizadores).

## 🚀 Características Principales

*   **BDD (Behavior Driven Development):** Pruebas escritas en lenguaje natural (Gherkin).
*   **Multi-Navegador:** Soporte para Chrome, Firefox y Edge.
*   **Gestión de Drivers:** Uso de `webdriver-manager` para gestión automática y soporte para **Selenium Grid**.
*   **Entornos Configurables:** Fácil cambio entre QA, DEV, PROD mediante archivo `.ini`.
*   **Reportería Avanzada:** Integración con **Allure Reports** para gráficos y detalles de ejecución.
*   **Logs y Screenshots:** Sistema de logging detallado y capturas de pantalla automáticas en caso de fallo.
*   **CI/CD Ready:** Configuración lista para GitHub Actions.

## 📋 Requisitos Previos

*   **Python 3.10+** instalado.
*   **Java (JDK 8+)** (Opcional, solo necesario si deseas visualizar reportes de Allure localmente).
*   Navegadores web instalados (Google Chrome, Firefox o Edge).

## 🛠️ Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd banca-automation-python-selenium
    ```

2.  **Crear un entorno virtual (Recomendado):**
    *   Windows:
        ```bash
        python -m venv env
        .\env\Scripts\activate
        ```
    *   Mac/Linux:
        ```bash
        python3 -m venv env
        source env/bin/activate
        ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuración del Entorno

El archivo principal de configuración es `src/config/environment.ini`. Aquí puedes definir las URLs base, timeouts y configuraciones del navegador para cada entorno.

**Ejemplo de `environment.ini`:**
```ini
[DEFAULT]
browser = chrome
headless = False
wait_timeout = 10
screenshot_on_fail = True

[qa]
base_url = https://qa.orangehrmlive.com

[production]
base_url = https://opensource-demo.orangehrmlive.com
```

## ▶️ Ejecución de Pruebas

El framework utiliza `behave` como ejecutor de pruebas. Asegúrate de tener el entorno virtual activado.

### 1. Ejecución Básica (Entorno Default)
Ejecuta todos los escenarios disponibles usando la configuración `[DEFAULT]`.
```bash
behave
```

### 2. Seleccionar un Entorno Específico
Para ejecutar pruebas contra un entorno definido en el `.ini` (ej. `qa`), usa el parámetro `-D`:
```bash
behave -D environment=qa
```

### 3. Filtrar por Tags
Ejecuta solo los escenarios marcados con una etiqueta específica (ej. `@web`, `@login`, `@api`).
```bash
behave --tags=@web
```

### 4. Modo Headless (Sin interfaz gráfica)
Puedes forzar el modo headless mediante una variable de entorno (útil para CI/CD) o modificando el `.ini`.
*   **Windows (PowerShell):**
    ```powershell
    $env:HEADLESS="true"; behave
    ```
*   **Linux/Mac:**
    ```bash
    HEADLESS=true behave
    ```

## 📊 Generación de Reportes (Allure)

Este framework está configurado para generar reportes ricos con Allure.

### 1. Ejecutar pruebas generando resultados
Este comando ejecuta las pruebas y guarda los resultados en crudo en la carpeta `allure-results`.
```bash
behave -f allure_behave.formatter:AllureFormatter -o allure-results ./features
```

### 2. Visualizar el reporte (Localmente)
Si tienes Allure instalado en tu máquina, puedes levantar un servidor web temporal para ver los resultados:
```bash
allure serve allure-results
```

> **Nota:** En el pipeline de CI/CD (GitHub Actions), este reporte se genera y publica automáticamente en GitHub Pages.

## 📂 Estructura del Proyecto

```text
banca-automation-python-selenium/
├── features/               # Archivos .feature (Gherkin) y Steps
│   ├── steps/              # Definición de pasos (Step Definitions)
│   └── web/                # Features organizados por módulo
├── src/
│   ├── actions/            # Lógica de negocio (acciones sobre páginas)
│   ├── config/             # Lectura de configuración y Factory de WebDriver
│   ├── locators/           # Centralización de selectores (XPaths, IDs)
│   ├── pages/              # Page Objects (interacción pura con Selenium)
│   └── utils/              # Utilidades (Logger, Screenshots, Selenium Wrappers)
├── reports/                # Logs y capturas de pantalla generados
├── ci.yml                  # Flujo de trabajo de GitHub Actions
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación del proyecto
```

## 🤖 Integración Continua (CI/CD)

El proyecto incluye un archivo `.github/workflows/ci.yml` (o en la raíz `ci.yml`) que configura un pipeline en GitHub Actions.

**Flujo automático:**
1.  Se activa al hacer **Push** o **Pull Request** a la rama `main`.
2.  Instala Python y dependencias.
3.  Ejecuta `flake8` para análisis estático.
4.  Ejecuta los tests en modo **Headless**.
5.  Genera el reporte de Allure.
6.  Despliega el reporte en **GitHub Pages**.
