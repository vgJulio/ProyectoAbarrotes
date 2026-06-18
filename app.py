from flask import Flask, render_template, request, redirect, url_for
from models.conexion import db

app = Flask(__name__)

@app.route('/')
def inciar():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        usuario_encontrado = db.usuarios.find_one(
            {
                "usuario": usuario,
                "contraseña": contraseña
            }
        )

        if usuario_encontrado:

            if usuario_encontrado["rol"] == "cliente":
                return redirect(url_for('clienteVista'))

            elif usuario_encontrado["rol"] == "vendedor":
                return redirect(url_for('inventarioVista'))

        return "Usuario o contraseña incorrectos"

    return render_template('login.html')

@app.route('/clienteVista')
def clienteVista():
    return render_template('clienteVista.html')

@app.route('/inventarioVista')
def inventarioVista():
    productos = list(db.productos.find({}, {
        'nombre': 1,
        'precio': 1,
        'stock': 1,
        'categoria': 1,
        'descripcion': 1,
        'imagen': 1
    }))
    return render_template('inventarioVista.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)

