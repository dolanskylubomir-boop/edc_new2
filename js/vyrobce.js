document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("priceSelect");
    for (let i = 0.25; i <= 3.00; i += 0.25) {
        let val = i.toFixed(2);
        let opt = document.createElement("option");
        opt.value = val.replace('.', ',') + " Kč";
        opt.text = opt.value;
        select.appendChild(opt);
    }

    document.getElementById("userId").addEventListener("input", e => {
        e.target.value = e.target.value.replace(/\D/g, '').substring(0, 5);
    });
});

let v_captchaResult = 0;

function checkForm() {
    const n1 = Math.floor(Math.random() * 10) + 1, n2 = Math.floor(Math.random() * 10) + 1;
    v_captchaResult = n1 + n2;
    document.getElementById("captchaQuestion").innerText = `${n1} + ${n2}`;
    
    const list = document.getElementById("summaryList");
    list.innerHTML = `<li class="list-group-item">ID: ${document.getElementById("userId").value}</li>`;
    list.innerHTML += `<li class="list-group-item">Typ: ${document.getElementById("consumptionType").value}</li>`;

    document.getElementById("energyForm").style.display = "none";
    document.getElementById("summarySection").style.display = "block";
}

function submitForm() {
    if (parseInt(document.getElementById("captchaInput").value) !== v_captchaResult) { alert("Captcha!"); return; }

    const data = {
        userId: document.getElementById("userId").value,
        email: document.getElementById("email").value,
        price: document.getElementById("priceSelect").value,
        smartMeter: document.getElementById("smartMeter").value,
        consumptionType: document.getElementById("consumptionType").value,
        consumption: document.getElementById("consumption").value
    };

    fetch('/submit-vyrobce', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(res => res.json()).then(res => { alert(res.message); location.reload(); });

}
