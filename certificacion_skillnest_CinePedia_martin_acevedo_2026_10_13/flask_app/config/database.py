from flask import g
import mysql.connector

from flask_app.config.settings import DB_CONFIG


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


def query(sql, params=(), fetchone=False, fetchall=False):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(sql, params)
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = cursor.lastrowid
        get_db().commit()
    cursor.close()
    return result


def close_db(error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    cursor = database.cursor()
    statements = (
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS peliculas (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(255) NOT NULL UNIQUE,
            director TEXT NOT NULL,
            fecha_estreno DATE NOT NULL,
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
    )
    for statement in statements:
        cursor.execute(statement)
    cursor.close()
    database.commit()
