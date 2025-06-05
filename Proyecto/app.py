from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect("database2.db") as users:
        cursor = users.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TIPOCARTERA (
                CODTIPCAR INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBTIPCAR TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CARTERA (
                CODCAR INTEGER PRIMARY KEY AUTOINCREMENT,
                DESCRIPCAR TEXT NOT NULL,
                PRECIOCAR TEXT NOT NULL,
                FECHACAR TEXT NOT NULL,
                CODTIPCAR INTEGER NOT NULL,
                FOREIGN KEY (CODTIPCAR) REFERENCES TIPOCARTERA(CODTIPCAR)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USUARIO (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE TEXT NOT NULL,
                CONTRASENA TEXT NOT NULL
            )
        ''')
        # Insertar tipos de cartera si están vacíos
        cursor.execute("SELECT COUNT(*) FROM TIPOCARTERA")
        if cursor.fetchone()[0] == 0:
            tipos = [('ANDINO',), ('TRADICIONAL',), ('SELVATICO',), ('COSTEÑO',)]
            cursor.executemany("INSERT INTO TIPOCARTERA (NOMBTIPCAR) VALUES (?)", tipos)

        # Insertar usuario por defecto
        cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE NOMBRE = 'carlos'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO USUARIO (NOMBRE, CONTRASENA) VALUES (?, ?)", ('carlos', '123'))

        users.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/Login', methods=['GET', 'POST'])
def login():
    mensaje = ""
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']
        with sqlite3.connect("database2.db") as users:
            cursor = users.cursor()
            cursor.execute("SELECT * FROM USUARIO WHERE NOMBRE = ? AND CONTRASENA = ?", (nombre, contrasena))
            usuario = cursor.fetchone()
            if usuario:
                return redirect(url_for('principal'))
            else:
                mensaje = "Usuario o contraseña incorrectos"
    return render_template("Login.html", mensaje=mensaje)

@app.route('/Principal')
def principal():
    return render_template("principal.html")

@app.route('/RegistrarCartera')
def form_registro():
    with sqlite3.connect("database2.db") as users:
        cursor = users.cursor()
        cursor.execute("SELECT * FROM TIPOCARTERA")
        tipos = cursor.fetchall()
    return render_template("RegistrarCartera.html", tipos=tipos)

@app.route('/GrabarCartera', methods=['POST'])
def grabar():
    nombre = request.form['nombre']
    tipo = request.form['tipo']
    precio = request.form['precio']
    fecha = request.form['fecha']
    with sqlite3.connect("database2.db") as users:
        cursor = users.cursor()
        cursor.execute("""
            INSERT INTO CARTERA (DESCRIPCAR, PRECIOCAR, FECHACAR, CODTIPCAR)
            VALUES (?, ?, ?, ?)
        """, (nombre, precio, fecha, tipo))
        users.commit()
        cursor.execute("SELECT * FROM TIPOCARTERA")
        tipos = cursor.fetchall()
    return render_template("RegistrarCartera.html", tipos=tipos, mensaje="Se grabó el registro satisfactoriamente.")

@app.route('/ConsultarCartera')
def consultar():
    tipo = request.args.get('tipo')
    resultados = []
    with sqlite3.connect("database2.db") as users:
        cursor = users.cursor()
        cursor.execute("SELECT * FROM TIPOCARTERA")
        tipos = cursor.fetchall()
        if tipo:
            cursor.execute("""
                SELECT c.CODCAR, c.DESCRIPCAR, c.PRECIOCAR, c.FECHACAR, t.NOMBTIPCAR
                FROM CARTERA c
                JOIN TIPOCARTERA t ON c.CODTIPCAR = t.CODTIPCAR
                WHERE c.CODTIPCAR = ?
            """, (tipo,))
            resultados = cursor.fetchall()
    return render_template("ConsultarCartera.html", tipos=tipos, resultados=resultados)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

