from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"  # NECESARIA PARA LOGIN

# -----------------------------
# CREAR BD AUTOMÁTICAMENTE
# -----------------------------
def crear_bd():
    conn = sqlite3.connect("supermercados.db")
    cursor = conn.cursor()

    # Tabla de supermercados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supermercados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            propietario TEXT NOT NULL,
            telefono TEXT NOT NULL,
            direccion TEXT NOT NULL,
            apertura TEXT NOT NULL,
            cierre TEXT NOT NULL
        )
    """)

    # Tabla admin
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            clave TEXT NOT NULL
        )
    """)

    # Insertar admin solo si no existe
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO admin(usuario, clave) VALUES (?, ?)", ("admin", "1234"))

    conn.commit()
    conn.close()

crear_bd()

# -----------------------------
# RUTA PRINCIPAL (PÚBLICA)
# -----------------------------
@app.route("/")
def index():
    conn = sqlite3.connect("supermercados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM supermercados")
    data = cursor.fetchall()
    conn.close()
    return render_template("index.html", supermercados=data, admin=session.get("admin"))

# -----------------------------
# LOGIN ADMIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        conn = sqlite3.connect("supermercados.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE usuario=? AND clave=?", (usuario, clave))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session["admin"] = True
            return redirect("/")
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -----------------------------
# SOLO EL ADMIN AGREGA
# -----------------------------
@app.route("/agregar", methods=["POST"])
def agregar():
    if not session.get("admin"):
        return redirect("/")

    nombre = request.form["nombre"]
    propietario = request.form["propietario"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]
    apertura = request.form["apertura"]
    cierre = request.form["cierre"]

    conn = sqlite3.connect("supermercados.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO supermercados(nombre, propietario, telefono, direccion, apertura, cierre)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, propietario, telefono, direccion, apertura, cierre))
    conn.commit()
    conn.close()

    return redirect("/")

# -----------------------------
# SOLO EL ADMIN EDITA
# -----------------------------
@app.route("/editar/<int:id>")
def editar(id):
    if not session.get("admin"):
        return redirect("/")

    conn = sqlite3.connect("supermercados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM supermercados WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()
    return render_template("editar.html", supermercado=data)

# -----------------------------
# SOLO EL ADMIN ACTUALIZA
# -----------------------------
@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    if not session.get("admin"):
        return redirect("/")

    nombre = request.form["nombre"]
    propietario = request.form["propietario"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]
    apertura = request.form["apertura"]
    cierre = request.form["cierre"]

    conn = sqlite3.connect("supermercados.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE supermercados
        SET nombre=?, propietario=?, telefono=?, direccion=?, apertura=?, cierre=?
        WHERE id=?
    """, (nombre, propietario, telefono, direccion, apertura, cierre, id))
    conn.commit()
    conn.close()

    return redirect("/")

# -----------------------------
# SOLO EL ADMIN ELIMINA
# -----------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if not session.get("admin"):
        return redirect("/")

    conn = sqlite3.connect("supermercados.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supermercados WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
