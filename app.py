import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
from models.conexion import db
from bson import ObjectId


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

@app.route('/inventarioVista', methods=['GET', 'POST'])
def inventarioVista():
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        nombre = request.form.get('nombre')
        categoria = request.form.get('categoria')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        descripcion = request.form.get('descripcion')

        imagen_archivo = request.files.get('imagen')
        nombre_imagen = None
        
        if imagen_archivo and imagen_archivo.filename != '':
            nombre_imagen = secure_filename(imagen_archivo.filename)
            ruta_guardado = os.path.join(app.root_path, 'static', 'img', nombre_imagen)
            imagen_archivo.save(ruta_guardado)

        datos_producto = {
            'nombre': nombre,
            'categoria': categoria,
            'precio': precio,
            'stock': stock,
            'descripcion': descripcion
        }
        
        if nombre_imagen:
            datos_producto['imagen'] = nombre_imagen

        if producto_id:
            db.productos.update_one({'_id': ObjectId(producto_id)}, {'$set': datos_producto})
        else:
            db.productos.insert_one(datos_producto)
            
        return redirect(url_for('inventarioVista'))

    productos = list(db.productos.find({}, {
        'nombre': 1,
        'precio': 1,
        'stock': 1,
        'categoria': 1,
        'descripcion': 1,
        'imagen': 1
    }))
    return render_template('inventarioVista.html', productos=productos)

@app.route('/eliminar_producto/<id>', methods=['DELETE'])
def eliminar_producto(id):
    try:
        db.productos.delete_one({'_id': ObjectId(id)})
        return 'Producto eliminado', 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)

