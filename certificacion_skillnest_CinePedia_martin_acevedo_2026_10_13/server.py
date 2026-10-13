from flask import Flask, render_template


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/nueva_pelicula")
def nueva_pelicula():
    return render_template("nueva_pelicula.html")


if __name__ == "__main__":
    app.run(debug=True)