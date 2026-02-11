document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("priceSelect");
    for (let i = 0.25; i <= 3.00; i += 0.25) {
        let val = i.toFixed(2);
        let text = val.replace('.', ',') + " Kč";
        let opt = document.createElement("option");
        opt.value = text; opt.text = text;
        select.appendChild(opt);
    }

    document.getElementById("ean").addEventListener("input", e => {
        e.target.value = e.target.value.replace(/\D/g, '').substring(0, 18);
    });
});

let captchaResult = 0;

function validateEAN(ean) {
    if (!/^\d{18}$/.test(ean) || !ean.startsWith("8591824")) return false;
    const dist = parseInt(ean.substring(7, 10));
    if (dist < 1 || dist > 8) return false;
    let sum = 0;
    for (let i = 0; i < 17; i++) {
        sum += (i % 2 === 0) ? parseInt(ean[i]) * 3 : parseInt(ean[i]);
    }
    return ((10 - (sum % 10)) % 10) === parseInt(ean[17]);
}

function checkForm() {
    const ean = document.getElementById("ean").value;
    if (!validateEAN(ean)) { alert("❌ EAN kód je neplatný!"); return; }
    
    const fields = [
        { label: "Cena", val: document.getElementById("priceSelect").value },
        { label: "EAN", val: ean },
        { label: "Odběr", val: document.getElementById("consumption").value + " kWh" }
    ];
    
    const list = document.getElementById("summaryList");
    list.innerHTML = "";
    fields.forEach(f => list.innerHTML += `<li class="list-group-item"><strong>${f.label}:</strong> ${f.val}</li>`);

    const n1 = Math.floor(Math.random() * 10) + 1, n2 = Math.floor(Math.random() * 10) + 1;
    captchaResult = n1 + n2;
    document.getElementById("captchaQuestion").innerText = `${n1} + ${n2}`;

    document.getElementById("energyForm").style.display = "none";
    document.getElementById("summarySection").style.display = "block";
}

// Nahraďte funkci submitForm ve vašem formscript.js touto verzí:
function submitForm() {
    if (!document.getElementById("legalConsent").checked || parseInt(document.getElementById("captchaInput").value) !== captchaResult) {
        alert("⚠️ Zkontrolujte prosím souhlas s podmínkami a výsledek příkladu."); 
        return;
    }

    const data = {
        price: document.getElementById("priceSelect").value,
        email: document.getElementById("email").value,
        ean: document.getElementById("ean").value,
        smartMeter: document.getElementById("smartMeter").value,
        consumptionType: document.getElementById("consumptionType").value,
        consumption: document.getElementById("consumption").value,
        timestamp: new Date().toLocaleString('cs-CZ')
    };

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(async res => {
        const result = await res.json();
        const summary = document.getElementById("summarySection");
        
        if (res.ok) {
            summary.innerHTML = `<h3 class="text-success mb-4">✅ Registrace úspěšná</h3>`;
            
            if (result.matches && result.matches.length > 0) {
                summary.innerHTML += `
                    <div class="alert alert-info">
                        <h5>Nalezené shody s výrobci (${result.matches.length}):</h5>
                        <p class="small">Seznam výrobců splňujících vaše požadavky (jméno ze sloupce C):</p>
                        
                        <div style="max-height: 250px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 8px; background: white;" class="p-2 mb-3 shadow-sm">
                            <div class="list-group list-group-flush">
                                ${result.matches.map(m => `
                                    <div class="list-group-item py-3">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1 text-primary fw-bold">${m.name}</h6>
                                            <span class="badge bg-success">${m.price}</span>
                                        </div>
                                        <p class="mb-1 small">Email: <strong>${m.email}</strong></p>
                                        <small class="text-muted">Typ objektu: ${m.type}</small>
                                    </div>
                                `).join('')}
                            </div>
                        </div>

                        <button class="btn btn-primary btn-sm w-100 mb-2" onclick='downloadMatches(${JSON.stringify(result.matches)})'>
                            📥 Stáhnout seznam kontaktů (.txt)
                        </button>
                    </div>`;
            } else {
                summary.innerHTML += `
                    <div class="alert alert-warning">
                        <h5>Nenalezena žádná okamžitá shoda</h5>
                        <p>Vaše požadavky jsme uložili. Jakmile se objeví vhodný výrobce, budeme vás informovat.</p>
                    </div>`;
            }
            summary.innerHTML += `<button class="btn btn-secondary w-100 mt-2" onclick="location.reload()">Zavřít a zpět</button>`;
        } else {
            alert("❌ Chyba: " + result.message);
        }
    })
    .catch(err => alert("❌ Chyba spojení se serverem."));
}

// Funkce pro generování a stažení TXT souboru
function downloadMatches(matches) {
    let text = "VÝSLEDKY PÁROVÁNÍ - ENERGETICKÁ KOMUNITA\n";
    text += "========================================\n\n";
    
    matches.forEach((m, i) => {
        text += `${i + 1}. VÝROBCE: ${m.name}\n`;
        text += `   Email: ${m.email}\n`;
        text += `   Cena: ${m.price}\n`;
        text += `   Typ: ${m.type}\n`;
        text += "----------------------------------------\n";
    });

    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'nalezene_shody.txt';
    a.click();
    window.URL.revokeObjectURL(url);
}
