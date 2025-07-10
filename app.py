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
    return render_template('vista.html', pozas=data.keys())

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
    data = load_data()
    if name and name not in data:
        data[name] = []
        save_data(data)
    return redirect(url_for('index'))

# Agregar bomba a poza
@app.route('/add_bomba/<poza>', methods=['POST'])
def add_bomba(poza):
    if 'user' not in session:
        return redirect(url_for('login'))
    bomba = {
        "BOMBA": request.form.get('bomba'),
        "L/S": float(request.form.get('ls', 0)),
        "M3/H": float(request.form.get('m3h', 0))
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
