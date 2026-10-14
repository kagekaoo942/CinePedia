from flask_app.config.database import query


class MovieModel:
    @staticmethod
    def all_with_authors():
        return query(
            """
            SELECT peliculas.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
            FROM peliculas JOIN usuarios ON usuarios.id = peliculas.usuario_id
            ORDER BY peliculas.id DESC
            """,
            fetchall=True,
        )

    @staticmethod
    def find(movie_id):
        return query("SELECT * FROM peliculas WHERE id = %s", (movie_id,), fetchone=True)

    @staticmethod
    def find_with_author(movie_id):
        return query(
            """
            SELECT peliculas.*, CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS autor
            FROM peliculas JOIN usuarios ON usuarios.id = peliculas.usuario_id
            WHERE peliculas.id = %s
            """,
            (movie_id,),
            fetchone=True,
        )

    @staticmethod
    def name_used(name, movie_id=None):
        sql = "SELECT id FROM peliculas WHERE LOWER(nombre) = LOWER(%s)"
        params = [name]
        if movie_id is not None:
            sql += " AND id <> %s"
            params.append(movie_id)
        return query(sql, tuple(params), fetchone=True) is not None

    @staticmethod
    def create(data, user_id):
        return query(
            """
            INSERT INTO peliculas (nombre, director, fecha_estreno, sinopsis, usuario_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (*data.values(), user_id),
        )

    @staticmethod
    def update(movie_id, data):
        return query(
            """
            UPDATE peliculas
            SET nombre = %s, director = %s, fecha_estreno = %s, sinopsis = %s
            WHERE id = %s
            """,
            (*data.values(), movie_id),
        )

    @staticmethod
    def delete(movie_id, user_id):
        return query(
            "DELETE FROM peliculas WHERE id = %s AND usuario_id = %s",
            (movie_id, user_id),
        )
