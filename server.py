import http.server
import socketserver
import json
import csv
import os

# Azure dynamicky přiděluje port, na kterém aplikace musí běžet
PORT = int(os.environ.get('PORT', 8000))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        """Obsluhuje stahování souborů a zobrazení stránek."""
        # TAJNÁ CESTA: Pro stažení nasbíraných dat
        if self.path == '/download-csv':
            filename = 'registrace.csv'
            if os.path.exists(filename):
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                # attachment zajistí, že se soubor v prohlížeči začne stahovat
                self.send_header('Content-Disposition', 'attachment; filename="export_registrace.csv"')
                self.end_headers()
                with open(filename, 'rb') as file:
                    self.wfile.write(file.read())
                return
            else:
                self.send_error_response(404, "Soubor s registracemi zatím neexistuje.")
                return

        # Standardní chování: Pokud uživatel přijde na web, ukáže se index.html
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Obsluhuje odesílání formulářů z webu."""
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
                
                # Kontrola duplicit v registracích
                if file_exists:
                    with open(filename, mode='r', encoding='utf-8-sig') as file:
                        reader = csv.reader(file, delimiter=';')
                        next(reader, None)
                        for row in reader:
                            if len(row) >= 4:
                                if new_email == row[2].strip().lower() or new_ean == row[3].strip():
                                    self.send_error_response(409, "Email nebo EAN je již registrován!")
                                    return

                # Zápis nového spotřebitele do CSV
                row_to_save = [
                    data.get('timestamp'), 
                    data.get('price'), 
                    data.get('email'), 
                    data.get('ean'), 
                    data.get('smartMeter'), 
                    data.get('consumptionType'), 
                    '', # Jméno prázdné
                    data.get('consumption')
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
                        next(v_reader, None)
                        
                        for v_row in v_reader:
                            if len(v_row) < 8 or v_row[7].strip().upper() != 'ANO':
                                continue
                            
                            # Kontroly (Cena, Elektroměr, Typ, Spotřeba)
                            match_price = data.get('price') == v_row[3]
                            v_smart = v_row[4].strip()
                            match_smart = (v_smart == "Vše (bez omezení)") or (v_smart == data.get('smartMeter'))
                            s_type = data.get('consumptionType')
                            match_type = (s_type == "Nevím") or (v_row[5] == s_type)
                            
                            try:
                                s_cons = float(data.get('consumption', 0))
                                v_cons_limit = float(v_row[6] if v_row[6] else 0)
                                match_cons = s_cons >= v_cons_limit
                            except:
                                match_cons = False

                            if match_price and match_smart and match_type and match_cons:
                                matches.append({
                                    'name': v_row[2],
                                    'email': v_row[1],
                                    'price': v_row[3],
                                    'type': v_row[5]
                                })

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'matches': matches}).encode('utf-8'))

            except Exception as e:
                self.send_error_response(500, f"Chyba: {e}")

        # --- CESTA B: Výrobci (Aktualizace dat) ---
        elif self.path == '/submit-vyrobce':
            try:
                user_id = data.get('userId', '').strip()
                email = data.get('email', '').strip().lower()
                
                if not os.path.exists('vyrobce.csv'):
                    self.send_error_response(404, "Soubor vyrobce.csv neexistuje.")
                    return

                with open('vyrobce.csv', mode='r', encoding='utf-8-sig') as file:
                    rows = list(csv.reader(file, delimiter=';'))

                found = False
                for i, row in enumerate(rows):
                    if len(row) >= 2 and row[0].strip() == user_id and row[1].strip().lower() == email:
                        found = True
                        while len(row) < 8: row.append("")
                        row[3] = data.get('price')
                        row[4] = data.get('smartMeter')
                        row[5] = data.get('consumptionType')
                        row[6] = data.get('consumption')
                        row[7] = "ANO"
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
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'error', 'message': message}).encode('utf-8'))

    def send_success_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'success', 'message': message}).encode('utf-8'))

# Spuštění serveru
if __name__ == "__main__":
    # "0.0.0.0" je nutné pro Azure, aby byl web dostupný zvenčí
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
        print(f"Azure server běží na portu {PORT}...")
        httpd.serve_forever()
