from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from mysql.connector import IntegrityError

from flask_app.models import create_user, find_user, find_user_by_email
from flask_app.config.security import check_password, hash_password


auth_bp = Blueprint("auth", __name__)


def logged_user():
    if "usuario_id" not in session:
        return None
    return find_user(session["usuario_id"])


def login_required(view):
    @wraps(view)
    def protected(*args, **kwargs):
        if logged_user() is None:
            flash("Inicia sesión para continuar.")
            return redirect(url_for("auth.index"))
        return view(*args, **kwargs)

    return protected


@auth_bp.get("/")
def index():
    if logged_user():
        return redirect(url_for("movies.home"))
    return render_template("index.html")


@auth_bp.post("/registro")
def register():
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirmation = request.form.get("confirmar_password", "")
    if not all((nombre, apellido, email, password, confirmation)):
        flash("Todos los campos del registro son obligatorios.")
    elif len(password) < 8:
        flash("La contraseña debe tener al menos 8 caracteres.")
    elif password != confirmation:
        flash("Las contraseñas no coinciden.")
    else:
        try:
            create_user(nombre, apellido, email, hash_password(password))
            flash("Registro exitoso. Ahora puedes iniciar sesión.")
        except IntegrityError:
            flash("El e-mail ya está registrado.")
    return redirect(url_for("auth.index"))


@auth_bp.post("/login")
def login():
    email = request.form.get("email", "").strip().lower()
    user = find_user_by_email(email)
    if user is None or not check_password(request.form.get("password", ""), user["password"]):
        flash("El e-mail o la contraseña son incorrectos.")
        return redirect(url_for("auth.index"))
    session.clear()
    session["usuario_id"] = user["id"]
    return redirect(url_for("movies.home"))


@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.index"))
