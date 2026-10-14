import hashlib
import hmac
import os
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
import mysql.connector
from mysql.connector import IntegrityError


BASE_DIR = Path(__file__).parent


def load_env_file():
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip().strip("\"'"))


load_env_file()
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError("Falta SECRET_KEY en el archivo .env.")

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return f"{salt}${password_hash}"


def check_password(password, saved_password):
    try:
        salt, expected_hash = saved_password.split("$", 1)
    except ValueError:
        return False
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "cinepedia"),
        )
    return g.db


def query(sql, params=(), fetchone=False, fetchall=False):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(sql, params)
    result = cursor.fetchone() if fetchone else cursor.fetchall() if fetchall else cursor.lastrowid
    if not fetchone and not fetchall:
        get_db().commit()
    cursor.close()
    return result


@app.teardown_appcontext
def close_db(error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    cursor = database.cursor()
    for statement in (
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS peliculas (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre TEXT NOT NULL,
            director TEXT NOT NULL,
            fecha_estreno TEXT NOT NULL,
            sinopsis TEXT NOT NULL,
            usuario_id INT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS comentarios (
            id INT PRIMARY KEY AUTO_INCREMENT,
            texto TEXT NOT NULL,
            pelicula_id INT NOT NULL,
            usuario_id INT NOT NULL,
            FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB
        """,
    ):
        cursor.execute(statement)
    cursor.close()
    database.commit()


def usuario_actual():
    if "usuario_id" not in session:
        return None
    return query("SELECT * FROM usuarios WHERE id = %s", (session["usuario_id"],), fetchone=True)


def requiere_login(view):
    @wraps(view)
    def protegida(*args, **kwargs):
        if usuario_actual() is None:
            flash("Inicia sesión para continuar.")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return protegida


def validar_pelicula(form):
    datos = {
        "nombre": form.get("nombre", "").strip(),
        "director": form.get("director", "").strip(),
        "fecha_estreno": form.get("fecha_estreno", "").strip(),
        "sinopsis": form.get("sinopsis", "").strip(),
    }
    if not all(datos.values()):
        return datos, "Todos los campos de la película son obligatorios."
    return datos, None


with app.app_context():
    init_db()


@app.get("/")
def index():
    if usuario_actual():
        return redirect(url_for("inicio"))
    return render_template("index.html")


@app.post("/registro")
def registro():
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirmar = request.form.get("confirmar_password", "")

    if not all((nombre, apellido, email, password, confirmar)):
        flash("Todos los campos del registro son obligatorios.")
    elif password != confirmar:
        flash("Las contraseñas no coinciden.")
    else:
        try:
            query(
                "INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)",
                (nombre, apellido, email, hash_password(password)),
            )
            flash("Registro exitoso. Ahora puedes iniciar sesión.")
        except IntegrityError:
            flash("El e-mail ya está registrado.")
    return redirect(url_for("index"))


@app.post("/login")
def login():
    email = request.form.get("email", "").strip().lower()
    user = query("SELECT * FROM usuarios WHERE email = %s", (email,), fetchone=True)
    if user is None or not check_password(request.form.get("password", ""), user["password"]):
        flash("El e-mail o la contraseña son incorrectos.")
        return redirect(url_for("index"))
    session.clear()
    session["usuario_id"] = user["id"]
    return redirect(url_for("inicio"))


@app.get("/inicio")
@requiere_login
def inicio():
    movies = query(
        """
        SELECT peliculas.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
        FROM peliculas JOIN usuarios ON usuarios.id = peliculas.usuario_id
        ORDER BY peliculas.id DESC
        """, fetchall=True)
    return render_template("cine.html", peliculas=movies, usuario=usuario_actual())


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/nueva_pelicula", methods=["GET", "POST"])
@requiere_login
def nueva_pelicula():
    if request.method == "POST":
        datos, error = validar_pelicula(request.form)
        if error:
            return render_template("nueva_pelicula.html", datos=datos, error=error)
        cursor = query(
            """
            INSERT INTO peliculas (nombre, director, fecha_estreno, sinopsis, usuario_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (*datos.values(), session["usuario_id"]),
        )
        return redirect(url_for("ver_pelicula", pelicula_id=cursor))
    return render_template("nueva_pelicula.html", datos={}, error=None)


@app.route("/peliculas/<int:pelicula_id>/editar", methods=["GET", "POST"])
@requiere_login
def editar_pelicula(pelicula_id):
    movie = query("SELECT * FROM peliculas WHERE id = %s", (pelicula_id,), fetchone=True)
    if movie is None:
        return "Película no encontrada", 404
    if movie["usuario_id"] != session["usuario_id"]:
        flash("Solo puedes editar tus propias películas.")
        return redirect(url_for("inicio"))
    if request.method == "POST":
        datos, error = validar_pelicula(request.form)
        if error:
            return render_template("editar_pelicula.html", pelicula=datos, error=error)
        query(
            """
            UPDATE peliculas
            SET nombre = %s, director = %s, fecha_estreno = %s, sinopsis = %s
            WHERE id = %s
            """,
            (*datos.values(), pelicula_id),
        )
        return redirect(url_for("ver_pelicula", pelicula_id=pelicula_id))
    return render_template("editar_pelicula.html", pelicula=movie, error=None)


@app.get("/peliculas/<int:pelicula_id>/borrar")
@requiere_login
def borrar_pelicula(pelicula_id):
    query(
        "DELETE FROM peliculas WHERE id = %s AND usuario_id = %s",
        (pelicula_id, session["usuario_id"]),
    )
    return redirect(url_for("inicio"))


@app.get("/peliculas/<int:pelicula_id>")
@requiere_login
def ver_pelicula(pelicula_id):
    movie = query(
        """
        SELECT peliculas.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
        FROM peliculas JOIN usuarios ON usuarios.id = peliculas.usuario_id
        WHERE peliculas.id = %s
        """,
        (pelicula_id,),
        fetchone=True)
    if movie is None:
        return "Película no encontrada", 404
    comments = query(
        """
        SELECT comentarios.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
        FROM comentarios JOIN usuarios ON usuarios.id = comentarios.usuario_id
        WHERE pelicula_id = %s ORDER BY comentarios.id DESC
        """,
        (pelicula_id,),
        fetchall=True)
    return render_template(
        "comentarios.html",
        pelicula=movie,
        comentarios=comments,
        usuario=usuario_actual(),
    )


@app.post("/peliculas/<int:pelicula_id>/comentar")
@requiere_login
def comentar(pelicula_id):
    texto = request.form.get("comentario", "").strip()
    if texto:
        query(
            "INSERT INTO comentarios (texto, pelicula_id, usuario_id) VALUES (%s, %s, %s)",
            (texto, pelicula_id, session["usuario_id"]),
        )
    return redirect(url_for("ver_pelicula", pelicula_id=pelicula_id))


@app.get("/comentarios/<int:comentario_id>/borrar")
@requiere_login
def borrar_comentario(comentario_id):
    query(
        "DELETE FROM comentarios WHERE id = %s AND usuario_id = %s",
        (comentario_id, session["usuario_id"]),
    )
    return redirect(request.referrer or url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
