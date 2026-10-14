CREATE DATABASE IF NOT EXISTS cinepedia
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cinepedia;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS peliculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    director VARCHAR(255) NOT NULL,
    fecha_estreno DATE NOT NULL,
    sinopsis TEXT NOT NULL,
    usuario_id INT NOT NULL,
    CONSTRAINT uk_peliculas_nombre UNIQUE (nombre),
    CONSTRAINT fk_peliculas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    texto TEXT NOT NULL,
    pelicula_id INT NOT NULL,
    usuario_id INT NOT NULL,
    CONSTRAINT fk_comentarios_pelicula
        FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE,
    CONSTRAINT fk_comentarios_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;
