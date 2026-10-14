from flask_app.config.database import query


class UserModel:
    @staticmethod
    def find(user_id):
        return query("SELECT * FROM usuarios WHERE id = %s", (user_id,), fetchone=True)

    @staticmethod
    def find_by_email(email):
        return query(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,),
            fetchone=True,
        )

    @staticmethod
    def create(nombre, apellido, email, password):
        return query(
            "INSERT INTO usuarios (nombre, apellido, email, password) "
            "VALUES (%s, %s, %s, %s)",
            (nombre, apellido, email, password),
        )
