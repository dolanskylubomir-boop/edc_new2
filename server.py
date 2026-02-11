import http.server
import socketserver
import json
import csv
import os

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_error_response(400, "Neplatná data")
            return

        # --- CESTA A: Registrace spotřebitelů + Porovnání ---
        if self.path == '/submit':
            try:
                new_email = data.get('email', '').strip().lower()
                new_ean = data.get('ean', '').strip()
                filename = 'registrace.csv'
                file_exists = os.path.isfile(filename)
                
                # Kontrola duplicit
                if file_exists:
                    with open(filename, mode='r', encoding='utf-8-sig') as file:
                        reader = csv.reader(file, delimiter=';')
                        next(reader, None)
                        for row in reader:
                            if len(row) >= 4:
                                if new_email == row[2].strip().lower() or new_ean == row[3].strip():
                                    self.send_error_response(409, "Email nebo EAN je již registrován!")
                                    return

                # Zápis spotřebitele (Sloupce A-H)
                row_to_save = [
                    data.get('timestamp'),    # A
                    data.get('price'),        # B (Cena pro porovnání)
                    data.get('email'),        # C
                    data.get('ean'),          # D
                    data.get('smartMeter'),   # E (Elektroměr pro porovnání)
                    data.get('consumptionType'), # F (Typ pro porovnání)
                    '',                       # G (Jméno - prázdné)
                    data.get('consumption')    # H (Spotřeba pro porovnání)
                ]
                
                with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')
                    if not file_exists:
                        writer.writerow(['Datum', 'Cena', 'Email', 'EAN', 'Elektromer', 'Typ', 'Jmeno', 'Spotreba'])
                    writer.writerow(row_to_save)

                # --- LOGIKA POROVNÁNÍ S VYROBCE.CSV ---
                matches = []
                if os.path.exists('vyrobce.csv'):
                    with open('vyrobce.csv', mode='r', encoding='utf-8-sig') as v_file:
                        v_reader = csv.reader(v_file, delimiter=';')
                        next(v_reader, None) # Přeskočit hlavičku
                        
                        for v_row in v_reader:
                            # 1. Kontrola sloupce H (index 7) - musí být ANO
                            if len(v_row) < 8 or v_row[7].strip().upper() != 'ANO':
                                continue
                            
                            # 2. Cena: Spotřebitel B (data['price']) vs Výrobce D (v_row[3])
                            match_price = data.get('price') == v_row[3]
                            
                            # 3. Elektroměr: Výrobce E (v_row[4]) vs Spotřebitel E (data['smartMeter'])
                            # Pokud je u výrobce "Vše (bez omezení)", je vždy shoda
                            v_smart = v_row[4].strip()
                            match_smart = (v_smart == "Vše (bez omezení)") or (v_smart == data.get('smartMeter'))
                            
                            # 4. Typ odběru: Spotřebitel F vs Výrobce F (v_row[5])
                            # Pokud je u spotřebitele "Nevím", je vždy shoda
                            s_type = data.get('consumptionType')
                            match_type = (s_type == "Nevím") or (v_row[5] == s_type)
                            
                            # 5. Spotřeba: Spotřebitel H (data['consumption']) vs Výrobce G (v_row[6])
                            # Shoda, pokud je spotřeba spotřebitele >= počáteční hodnota výrobce
                            try:
                                s_cons = float(data.get('consumption', 0))
                                v_cons_limit = float(v_row[6] if v_row[6] else 0)
                                match_cons = s_cons >= v_cons_limit
                            except:
                                match_cons = False

                            if match_price and match_smart and match_type and match_cons:
                                matches.append({
                                    'name': v_row[2],   # Jméno výrobce (Sloupec A)
                                    'email': v_row[1],  # Email výrobce (Sloupec B)
                                    'price': v_row[3],  # Cena (Sloupec D)
                                    'type': v_row[5]    # Typ (Sloupec F)
                                })

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'matches': matches}).encode('utf-8'))

            except Exception as e:
                self.send_error_response(500, f"Chyba: {e}")

        # --- CESTA B: Výrobci (Zápis od sloupce D) ---
        elif self.path == '/submit-vyrobce':
            try:
                user_id = data.get('userId', '').strip()
                email = data.get('email', '').strip().lower()
                
                with open('vyrobce.csv', mode='r', encoding='utf-8-sig') as file:
                    rows = list(csv.reader(file, delimiter=';'))

                found = False
                for i, row in enumerate(rows):
                    if len(row) >= 2 and row[0].strip() == user_id and row[1].strip().lower() == email:
                        found = True
                        while len(row) < 8: row.append("")
                        # Sloupce A, B, C se nepřepisují
                        row[3] = data.get('price')           # D
                        row[4] = data.get('smartMeter')      # E
                        row[5] = data.get('consumptionType') # F
                        row[6] = data.get('consumption')      # G
                        row[7] = "ANO"                       # H
                        rows[i] = row
                        break

                if found:
                    with open('vyrobce.csv', mode='w', newline='', encoding='utf-8-sig') as file:
                        writer = csv.writer(file, delimiter=';')
                        writer.writerows(rows)
                    self.send_success_response("Výrobce aktualizován.")
                else:
                    self.send_error_response(404, "Výrobce nenalezen.")
            except Exception as e:
                self.send_error_response(500, str(e))

    def send_error_response(self, code, message):
        self.send_response(code); self.send_header('Content-type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps({'status': 'error', 'message': message}).encode('utf-8'))

    def send_success_response(self, message):
        self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps({'status': 'success', 'message': message}).encode('utf-8'))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    httpd.serve_forever()