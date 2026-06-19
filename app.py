from flask import Flask, render_template, request, redirect, url_for, session
from models.conexion import db
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "abba123"

# =========================
# INDEX
# =========================

@app.route('/')
def iniciar():
    return render_template('index.html')


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        usuario_encontrado = db.usuarios.find_one({
            "usuario": usuario,
            "contraseña": contraseña
        })

        if usuario_encontrado:

            session["id_usuario"] = str(usuario_encontrado["_id"])
            session["usuario"] = usuario_encontrado["usuario"]
            session["rol"] = usuario_encontrado["rol"]

            if usuario_encontrado["rol"] == "cliente":
                return redirect(url_for('clienteVista'))

            elif usuario_encontrado["rol"] == "vendedor":
                return redirect(url_for('inventarioVista'))

        return "Usuario o contraseña incorrectos"

    return render_template('login.html')


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))


# =========================
# CLIENTE
# =========================

@app.route('/clienteVista')
def clienteVista():

    if "usuario" not in session:
        return redirect(url_for('login'))

    productos = list(
        db.productos.find(
            {},
            {
                "nombre": 1,
                "categoria": 1,
                "precio": 1,
                "stock": 1,
                "imagen": 1
            }
        )
    )

    return render_template(
        'clienteVista.html',
        productos=productos,
        usuario=session["usuario"]
    )


# =========================
# CARRITO
# =========================

@app.route('/agregar_carrito/<id_producto>')
def agregar_carrito(id_producto):

    producto = db.productos.find_one({
        "_id": ObjectId(id_producto)
    })

    if not producto:
        return redirect(url_for('clienteVista'))

    carrito = session.get("carrito", [])

    encontrado = False

    for item in carrito:

        if item["id_producto"] == str(producto["_id"]):

            item["cantidad"] += 1

            encontrado = True

            break

    if not encontrado:

        carrito.append({
            "id_producto": str(producto["_id"]),
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": 1
        })

    session["carrito"] = carrito

    return redirect(url_for('clienteVista'))


@app.route('/carrito')
def carrito():

    carrito = session.get("carrito", [])

    total = 0

    for item in carrito:

        total += item["precio"] * item["cantidad"]

    return render_template(
        'carrito.html',
        carrito=carrito,
        total=total
    )


# =========================
# PEDIDO
# =========================

@app.route('/confirmarPedido')
def confirmarPedido():

    carrito = session.get("carrito", [])

    if len(carrito) == 0:
        return redirect(url_for('carrito'))

    total = 0

    for item in carrito:

        total += item["precio"] * item["cantidad"]

        db.productos.update_one(
            {
                "_id": ObjectId(item["id_producto"])
            },
            {
                "$inc": {
                    "stock": -item["cantidad"]
                }
            }
        )

    db.pedidos.insert_one({

        "id_cliente": session["id_usuario"],

        "usuario_cliente": session["usuario"],

        "estado": "Pendiente",

        "productos": carrito,

        "total": total
    })

    session["carrito"] = []

    return render_template('pedidoExitoso.html')


# =========================
# MIS PEDIDOS
# =========================

@app.route('/misPedidos')
def misPedidos():

    pedidos = list(
        db.pedidos.find({
            "id_cliente": session["id_usuario"]
        })
    )

    return render_template(
        'misPedidos.html',
        pedidos=pedidos
    )


# =========================
# INVENTARIO
# =========================

@app.route('/inventarioVista')
def inventarioVista():

    productos = list(
        db.productos.find({}, {
            "nombre": 1,
            "precio": 1,
            "stock": 1,
            "categoria": 1,
            "descripcion": 1,
            "imagen": 1
        })
    )

    return render_template(
        'inventarioVista.html',
        productos=productos
    )

# =========================
# NUEVO PRODUCTO
# =========================

@app.route('/nuevoProducto', methods=['GET', 'POST'])
def nuevoProducto():

    if request.method == 'POST':

        producto = {
            "nombre": request.form['nombre'],
            "categoria": request.form['categoria'],
            "precio": float(request.form['precio']),
            "stock": int(request.form['stock']),
            "descripcion": request.form['descripcion'],
            "imagen": request.form['imagen']
        }

        db.productos.insert_one(producto)

        return redirect(url_for('inventarioVista'))

    return render_template('nuevoProducto.html')

# =========================
# NUEVO PRODUCTO
# =========================

@app.route('/editarProducto/<id>', methods=['GET', 'POST'])
def editarProducto(id):

    producto = db.productos.find_one(
        {"_id": ObjectId(id)}
    )

    if request.method == 'POST':

        db.productos.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "nombre": request.form['nombre'],
                    "categoria": request.form['categoria'],
                    "precio": float(request.form['precio']),
                    "stock": int(request.form['stock']),
                    "descripcion": request.form['descripcion'],
                    "imagen": request.form['imagen']
                }
            }
        )

        return redirect(url_for('inventarioVista'))

    return render_template(
        'editarProducto.html',
        producto=producto
    )

# =========================
# ELIMINAR PRODUCTO
# =========================

@app.route('/eliminarProducto/<id>')
def eliminarProducto(id):

    db.productos.delete_one(
        {"_id": ObjectId(id)}
    )

    return redirect(url_for('inventarioVista'))

# =========================
# VER PEDIDOS DE TODOS
# =========================

@app.route('/verPedidos')
def verPedidos():

    pedidos = list(
        db.pedidos.find()
    )

    return render_template(
        'verPedidos.html',
        pedidos=pedidos
    )

# =========================
# CAMBIAR ESTADO
# =========================

@app.route('/cambiarEstado/<id>')
def cambiarEstado(id):

    db.pedidos.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "estado": "Entregado"
            }
        }
    )

    return redirect(url_for('verPedidos'))

# =========================
# MAIN
# =========================

if __name__ == '__main__':
    app.run(debug=True)

