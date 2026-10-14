from flask_app.config.database import query


def comments_for_movie(movie_id):
    return query(
        """
        SELECT comentarios.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
        FROM comentarios JOIN usuarios ON usuarios.id = comentarios.usuario_id
        WHERE pelicula_id = %s ORDER BY comentarios.id DESC
        """,
        (movie_id,),
        fetchall=True,
    )


def create_comment(text, movie_id, user_id):
    return query(
        "INSERT INTO comentarios (texto, pelicula_id, usuario_id) VALUES (%s, %s, %s)",
        (text, movie_id, user_id),
    )


def delete_comment(comment_id, user_id):
    return query(
        "DELETE FROM comentarios WHERE id = %s AND usuario_id = %s",
        (comment_id, user_id),
    )
