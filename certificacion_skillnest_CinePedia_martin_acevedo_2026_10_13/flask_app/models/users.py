from flask_app.config.database import query


def find_user(user_id):
    return query("SELECT * FROM usuarios WHERE id = %s", (user_id,), fetchone=True)


def find_user_by_email(email):
    return query("SELECT * FROM usuarios WHERE email = %s", (email,), fetchone=True)


def create_user(nombre, apellido, email, password):
    return query(
        "INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)",
        (nombre, apellido, email, password),
    )
