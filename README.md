# CinePedia

Aplicación Flask para registrar usuarios, publicar películas y comentar.
La base de datos utilizada es MySQL y puede administrarse desde MySQL Workbench.

## Ejecutar

Desde la carpeta `certificacion_skillnest_CinePedia_martin_acevedo_2026_10_13`:

```powershell
pipenv install
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
pipenv run python server.py
```

Abre `http://127.0.0.1:5000`.

El archivo `.env` no se sube al repositorio. Contiene la clave secreta de Flask y
las credenciales de MySQL. Pipenv administra el entorno virtual y el archivo
`Pipfile.lock` fija las versiones instaladas.

Para entrar al entorno interactivo:

```powershell
pipenv shell
python server.py
```

## Funcionalidades

- Registro e inicio de sesión.
- Listado de películas para usuarios autenticados.
- Crear, editar y borrar únicamente las películas propias.
- Ver el detalle de cualquier película.
- Crear y borrar únicamente los comentarios propios.
- Cierre de sesión y protección de las páginas privadas.
