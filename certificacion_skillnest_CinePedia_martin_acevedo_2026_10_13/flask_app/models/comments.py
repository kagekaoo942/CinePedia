from flask_app.config.database import query


class CommentModel:
    @staticmethod
    def for_movie(movie_id):
        return query(
            """
            SELECT comentarios.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
            FROM comentarios JOIN usuarios ON usuarios.id = comentarios.usuario_id
            WHERE pelicula_id = %s ORDER BY comentarios.id DESC
            """,
            (movie_id,),
            fetchall=True,
        )

    @staticmethod
    def create(text, movie_id, user_id):
        return query(
            "INSERT INTO comentarios (texto, pelicula_id, usuario_id) "
            "VALUES (%s, %s, %s)",
            (text, movie_id, user_id),
        )

    @staticmethod
    def delete(comment_id, user_id):
        return query(
            "DELETE FROM comentarios WHERE id = %s AND usuario_id = %s",
            (comment_id, user_id),
        )
