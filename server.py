from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import io

app = Flask(__name__)

# Nastavení databáze (SQLite pro začátek)
# Pro Azure SQL doplnit řádek pro připojení na server, nezapomenout kurva  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local_test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DEFINICE TABULEK (MODELŮ) ---

class Registrace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    price = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    ean = db.Column(db.String(50), unique=True, nullable=False)
    smart_meter = db.Column(db.String(50))
    consumption_type = db.Column(db.String(50))
    consumption = db.Column(db.Float)

class Vyrobce(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Toto je tvoje userId
    user_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120))
    name = db.Column(db.String(100))
    price = db.Column(db.String(20))
    smart_meter = db.Column(db.String(50))
    consumption_type = db.Column(db.String(50))
    consumption_limit = db.Column(db.Float)
    active = db.Column(db.String(10), default="NE")

# Vytvoření databáze (spustí se při prvním startu)
with app.app_context():
    db.create_all()

# --- ENDPOINTY ---

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    
    # Kontrola duplicity (Email nebo EAN)
    exists = Registrace.query.filter((Registrace.email == data.get('email')) | (Registrace.ean == data.get('ean'))).first()
    if exists:
        return jsonify({'status': 'error', 'message': 'Email nebo EAN je již registrován!'}), 409

    # Uložení do SQL
    nova_registrace = Registrace(
        timestamp=data.get('timestamp'),
        price=data.get('price'),
        email=data.get('email').strip().lower(),
        ean=data.get('ean').strip(),
        smart_meter=data.get('smartMeter'),
        consumption_type=data.get('consumptionType'),
        consumption=float(data.get('consumption', 0))
    )
    db.session.add(nova_registrace)
    db.session.commit()

    # Logika porovnání (Hledání v tabulce Vyrobce)
    matches = []
    vyrobci = Vyrobce.query.filter_by(active='ANO').all()
    
    for v in vyrobci:
        match_price = data.get('price') == v.price
        match_smart = (v.smart_meter == "Vše (bez omezení)") or (v.smart_meter == data.get('smartMeter'))
        match_type = (data.get('consumptionType') == "Nevím") or (v.consumption_type == data.get('consumptionType'))
        match_cons = float(data.get('consumption', 0)) >= (v.consumption_limit or 0)

        if match_price and match_smart and match_type and match_cons:
            matches.append({
                'name': v.name,
                'email': v.email,
                'price': v.price,
                'type': v.consumption_type
            })

    return jsonify({'status': 'success', 'matches': matches})

@app.route('/download-csv')
def download_csv():
    # Vygenerování CSV z databáze 
    registrace = Registrace.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Datum', 'Cena', 'Email', 'EAN', 'Elektromer', 'Typ', 'Spotreba'])
    
    for r in registrace:
        writer.writerow([r.timestamp, r.price, r.email, r.ean, r.smart_meter, r.consumption_type, r.consumption])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='export_registrace.csv'
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
