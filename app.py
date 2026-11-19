from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'taskmaster.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS tareas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    area TEXT NOT NULL,
                    prioridad TEXT NOT NULL,
                    estado TEXT NOT NULL)''')
    conn.commit()

HTML_TASKMASTER = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskMaster Pro</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
</head>
<body class="container" style="padding-top: 20px;">
    <h2>TaskMaster Pro - Control de Pendientes</h2>
    <p><small>Gestión rápida de tareas, áreas y prioridades</small></p>
    <hr>

    <section>
        <form action="/agregar" method="POST">
            <div class="grid">
                <input type="text" name="titulo" required placeholder="Descripción de la tarea o pendiente">
                <input type="text" name="area" required placeholder="Área o proyecto (Ej. Operaciones, Logística)">
            </div>
            <div class="grid">
                <select name="prioridad" required>
                    <option value="Media" selected>Prioridad: Media</option>
                    <option value="Alta">Prioridad: Alta</option>
                    <option value="Baja">Prioridad: Baja</option>
                </select>
                <select name="estado" required>
                    <option value="Pendiente" selected>Estado: Pendiente</option>
                    <option value="En curso">Estado: En curso</option>
                    <option value="Completada">Estado: Completada</option>
                </select>
            </div>
            <button type="submit" style="background-color: #006341; border: none;">Agregar Tarea</button>
        </form>
    </section>

    <section style="margin-top: 30px;">
        <h3>Lista de Tareas Registradas</h3>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tarea</th>
                    <th>Área</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
                {% for t in tareas %}
                <tr>
                    <td>#{{ t.id }}</td>
                    <td><strong>{{ t.titulo }}</strong></td>
                    <td>{{ t.area }}</td>
                    <td>{{ t.prioridad }}</td>
                    <td><strong>{{ t.estado }}</strong></td>
                    <td>
                        <form action="/avanzar/{{ t.id }}" method="POST" style="margin: 0;">
                            <button type="submit" class="outline" style="padding: 4px 10px; font-size: 0.8rem;">Cambiar Estado</button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6" style="text-align: center;">No hay tareas registradas todavía.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
</body>
</html>
"""

@app.route('/')
def inicio():
    try:
        conn = get_db()
        tareas = conn.execute('SELECT * FROM tareas ORDER BY id DESC').fetchall()
        conn.close()
    except Exception:
        tareas = []
    return render_template_string(HTML_TASKMASTER, tareas=tareas)

@app.route('/agregar', methods=['POST'])
def agregar():
    try:
        titulo = request.form.get('titulo', 'Sin título').strip()
        area = request.form.get('area', 'General').strip()
        prioridad = request.form.get('prioridad', 'Media').strip()
        estado = request.form.get('estado', 'Pendiente').strip()

        conn = get_db()
        conn.execute(
            'INSERT INTO tareas (titulo, area, prioridad, estado) VALUES (?, ?, ?, ?)',
            (titulo, area, prioridad, estado)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    return redirect(url_for('inicio'))

@app.route('/avanzar/<int:tarea_id>', methods=['POST'])
def avanzar(tarea_id):
    orden_estados = {'Pendiente': 'En curso', 'En curso': 'Completada', 'Completada': 'Pendiente'}
    try:
        conn = get_db()
        actual = conn.execute('SELECT estado FROM tareas WHERE id = ?', (tarea_id,)).fetchone()
        if actual:
            nuevo_estado = orden_estados.get(actual['estado'], 'Pendiente')
            conn.execute('UPDATE tareas SET estado = ? WHERE id = ?', (nuevo_estado, tarea_id))
            conn.commit()
        conn.close()
    except Exception:
        pass

    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
