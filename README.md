# CinePedia

Aplicación Flask para registrar usuarios, publicar películas y comentar.
La base de datos utilizada es MySQL y puede administrarse desde MySQL Workbench.

## Estructura

```text
run.py
flask_app/
  config.py
  database.py
  models/
  routes/
  services/
templates/
static/
```

`run.py` solo inicia la aplicación. La configuración, la conexión a MySQL,
los modelos, las rutas y la seguridad están separados en sus propias carpetas.

## Ejecutar

Desde la carpeta `certificacion_skillnest_CinePedia_martin_acevedo_2026_10_13`:

```powershell
pipenv install
```

Si Windows indica que `pipenv` no se reconoce, ejecútalo mediante Python:

```powershell
py -m pipenv install
py -m pipenv run python run.py
```

En **Command Prompt (cmd)** usa:

```cmd
cd /d C:\Users\HP\Documents\GitHub\CinePedia\certificacion_skillnest_CinePedia_martin_acevedo_2026_10_13
py -m pipenv install
py -m pipenv run python server.py
```

Si `py -m pipenv` tampoco funciona, usa la ruta completa:

```cmd
cd /d C:\Users\HP\Documents\GitHub\CinePedia\certificacion_skillnest_CinePedia_martin_acevedo_2026_10_13
"%APPDATA%\Python\Python314\Scripts\pipenv.exe" install
"%APPDATA%\Python\Python314\Scripts\pipenv.exe" run python run.py
```

También puedes agregar la carpeta de Pipenv al `PATH` del usuario y abrir un
nuevo Command Prompt:

```text
C:\Users\HP\AppData\Roaming\Python\Python314\Scripts
```

Primero ejecuta [cinepedia.sql](./certificacion_skillnest_CinePedia_martin_acevedo_2026_10_13/cinepedia.sql)
en MySQL Workbench. Después configura `.env`:

```env
SECRET_KEY=una-clave-larga-y-privada
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=cinepedia
DB_USER=root
DB_PASSWORD=tu-clave-de-MySQL
FLASK_DEBUG=0
```

Finalmente inicia Flask:

```powershell
pipenv run python run.py
```

Abre `http://127.0.0.1:5000`.

El archivo `.env` no se sube al repositorio. Contiene la clave secreta de Flask y
las credenciales de MySQL. Pipenv administra el entorno virtual y el archivo
`Pipfile.lock` fija las versiones instaladas.

Para entrar al entorno interactivo:

```powershell
pipenv shell
python run.py
```

## Funcionalidades

- Registro e inicio de sesión.
- Listado de películas para usuarios autenticados.
- Crear, editar y borrar únicamente las películas propias.
- Ver el detalle de cualquier película.
- Crear y borrar únicamente los comentarios propios.
- Cierre de sesión y protección de las páginas privadas.
