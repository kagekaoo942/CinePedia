from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from flask_app.models import CommentModel, MovieModel
from flask_app.controllers.auth import logged_user, login_required


movies_bp = Blueprint("movies", __name__)


def movie_data(form):
    data = {
        "nombre": form.get("nombre", "").strip(),
        "director": form.get("director", "").strip(),
        "fecha_estreno": form.get("fecha_estreno", "").strip(),
        "sinopsis": form.get("sinopsis", "").strip(),
    }
    if not all(data.values()):
        return data, "Todos los campos de la película son obligatorios."
    if any(len(value) < 3 for value in data.values()):
        return data, "Todos los campos deben tener al menos 3 caracteres."
    return data, None


@movies_bp.get("/inicio")
@login_required
def home():
    return render_template(
        "cine.html",
        peliculas=MovieModel.all_with_authors(),
        usuario=logged_user(),
    )


@movies_bp.route("/nueva_pelicula", methods=["GET", "POST"])
@login_required
def new_movie():
    if request.method == "GET":
        return render_template("nueva_pelicula.html", datos={}, error=None)
    data, error = movie_data(request.form)
    if error:
        return render_template("nueva_pelicula.html", datos=data, error=error)
    if MovieModel.name_used(data["nombre"]):
        return render_template(
            "nueva_pelicula.html",
            datos=data,
            error="Ya existe una película con ese nombre.",
        )
    movie_id = MovieModel.create(data, session["usuario_id"])
    return redirect(url_for("movies.view_movie", pelicula_id=movie_id))


@movies_bp.route("/peliculas/<int:pelicula_id>/editar", methods=["GET", "POST"])
@login_required
def edit_movie(pelicula_id):
    movie = MovieModel.find(pelicula_id)
    if movie is None:
        return "Película no encontrada", 404
    if movie["usuario_id"] != session["usuario_id"]:
        flash("Solo puedes editar tus propias películas.")
        return redirect(url_for("movies.home"))
    if request.method == "GET":
        return render_template("editar_pelicula.html", pelicula=movie, error=None)
    data, error = movie_data(request.form)
    if error:
        return render_template("editar_pelicula.html", pelicula=data, error=error)
    if MovieModel.name_used(data["nombre"], pelicula_id):
        return render_template(
            "editar_pelicula.html",
            pelicula=data,
            error="Ya existe una película con ese nombre.",
        )
    MovieModel.update(pelicula_id, data)
    return redirect(url_for("movies.view_movie", pelicula_id=pelicula_id))


@movies_bp.get("/peliculas/<int:pelicula_id>/borrar")
@login_required
def remove_movie(pelicula_id):
    MovieModel.delete(pelicula_id, session["usuario_id"])
    return redirect(url_for("movies.home"))


@movies_bp.get("/peliculas/<int:pelicula_id>")
@login_required
def view_movie(pelicula_id):
    movie = MovieModel.find_with_author(pelicula_id)
    if movie is None:
        return "Película no encontrada", 404
    return render_template(
        "comentarios.html",
        pelicula=movie,
        comentarios=CommentModel.for_movie(pelicula_id),
        usuario=logged_user(),
    )


@movies_bp.post("/peliculas/<int:pelicula_id>/comentar")
@login_required
def add_comment(pelicula_id):
    movie = MovieModel.find(pelicula_id)
    if movie is None:
        return "Película no encontrada", 404
    if movie["usuario_id"] == session["usuario_id"]:
        flash("No puedes comentar tu propia película.")
        return redirect(url_for("movies.view_movie", pelicula_id=pelicula_id))
    text = request.form.get("comentario", "").strip()
    if text:
        CommentModel.create(text, pelicula_id, session["usuario_id"])
    return redirect(url_for("movies.view_movie", pelicula_id=pelicula_id))


@movies_bp.get("/comentarios/<int:comentario_id>/borrar")
@login_required
def remove_comment(comentario_id):
    CommentModel.delete(comentario_id, session["usuario_id"])
    return redirect(request.referrer or url_for("movies.home"))
