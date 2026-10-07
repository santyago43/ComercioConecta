@echo off
REM iniciar.bat - Script de lanzamiento para ComercioConecta
REM Este batch file inicia simultáneamente la API Flask y el frontend Streamlit
REM del proyecto ComercioConecta. Gestiona la creación del entorno virtual,
REM instalación de dependencias y lanzamiento de ambos servicios en ventanas separadas.
REM Guarda este archivo en el directorio comercioconecta/ y haz doble clic para ejecutar.

echo Iniciando ComercioConecta...
echo.

REM Verificar que existe el entorno virtual
if not exist .venv (
    echo Entorno virtual no encontrado. Creando uno nuevo...
    python -m venv .venv
)

REM Activar entorno virtual
call .venv\Scripts\activate

REM Instalar dependencias si es necesario
pip install -r requirements.txt

echo.
echo Lanzando API en http://127.0.0.1:5000
echo Lanzando Frontend en http://localhost:8501
echo.
echo NOTA: Se abriran dos ventanas. Cierre cualquiera para terminar la aplicacion.
echo.

REM Iniciar API en ventana separada
start "API - ComercioConecta" .venv\Scripts\python.exe api.py

REM Esperar un momento para que la API inicie
ping -n 4 127.0.0.1 > nul

REM Iniciar frontend en ventana separada
start "Frontend - ComercioConecta" .venv\Scripts\streamlit.exe run frontend/app.py

echo.
echo Ambos procesos se han iniciado.
echo Para detenerlos, cierre las ventanas de API y Frontend.
echo.