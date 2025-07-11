from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesaria para sesiones

DATA_FILE = 'data.json'

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Vista inicial: contraste de flujos
@app.route('/')
def vista():
    data = load_data()
    zonas = set()

    for bombas in data.values():
        if bombas and isinstance(bombas, list) and isinstance(bombas[0], dict):
            zona = bombas[0].get("ZONA")
            if zona:
                zonas.add(zona)

    return render_template('vista.html', data=data, zonas=sorted(zonas))

# Ruta del login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        if user == 'admin' and password == '1234':  # Puedes cambiar las credenciales
            session['user'] = user
            return redirect(url_for('index'))
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

# Página de gestión de pozas
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Agregar poza
@app.route('/add_poza', methods=['POST'])
def add_poza():
    if 'user' not in session:
        return redirect(url_for('login'))

    name = request.form.get('poza_name')
    zona = request.form.get('zona')

    data = load_data()

    if name and name not in data:
        data[name] = [{
            "BOMBA": "",
            "L/S": None,
            "M3/H": None,
            "FECHA": None,
            "DESTINO": "",
            "ZONA": zona
        }]
        save_data(data)

    return redirect(url_for('index'))

# Agregar bomba a poza
@app.route('/add_bomba/<poza>', methods=['POST'])
def add_bomba(poza):
    if 'user' not in session:
        return redirect(url_for('login'))

    bomba = {
        "BOMBA": request.form.get('bomba'),
        "L/S": float(request.form.get('ls', 0)) if request.form.get('ls') else None,
        "M3/H": float(request.form.get('m3h', 0)) if request.form.get('m3h') else None,
        "DESTINO": request.form.get('destino'),
        "FECHA": None
    }

    data = load_data()
    if poza in data:
        data[poza].append(bomba)
        save_data(data)

    return redirect(url_for('index'))

# Eliminar bomba
@app.route('/delete_bomba/<poza>/<int:index>', methods=['POST'])
def delete_bomba(poza, index):
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    if poza in data and 0 <= index < len(data[poza]):
        data[poza].pop(index)
        if not data[poza]:
            data.pop(poza)
        save_data(data)
    return redirect(url_for('index'))

# API para vista.html
@app.route('/poza/<poza>')
def get_poza(poza):
    data = load_data()
    return jsonify(data.get(poza, []))
@app.route('/edit_bomba/<poza>/<int:index>', methods=['POST'])
def edit_bomba(poza, index):
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()

    if poza not in data or not (0 <= index < len(data[poza])):
        return redirect(url_for('index'))

    bomba_actual = data[poza][index]

    bomba = {
        "BOMBA": request.form.get("bomba"),
        "L/S": float(request.form.get("ls", 0)) if request.form.get("ls") else None,
        "M3/H": float(request.form.get("m3h", 0)) if request.form.get("m3h") else None,
        "DESTINO": request.form.get("destino"),
        "FECHA": bomba_actual.get("FECHA")  # conserva la fecha si existe
    }

    data[poza][index] = bomba
    save_data(data)

    return redirect(url_for('index'))
@app.route('/editar_zona/<poza>', methods=['POST'])
def editar_zona(poza):
    if 'user' not in session:
        return redirect(url_for('login'))

    nueva_zona = request.form.get('zona')
    data = load_data()
    if poza in data:
        for bomba in data[poza]:
            bomba["ZONA"] = nueva_zona
        save_data(data)
    return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
