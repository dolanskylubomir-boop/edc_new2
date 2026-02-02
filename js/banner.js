// Přidejte tento JavaScript kód do vašeho hlavního skriptu (např. do <script> tagu na konci body nebo do externího souboru jako js/banner.js a načtěte ho defer)

// Funkce pro zobrazení banneru s volitelným textem
function showWarningBanner(text = 'Stránky se připravují') {
    // Kontrola, jestli uživatel banner neuzavřel dříve
    if (localStorage.getItem('warning_banner_closed') === 'true') {
        return; // Nezobrazovat, pokud byl uzavřen
    }

    const banner = document.getElementById('warning-banner');
    const textElement = document.getElementById('warning-text');

    if (banner && textElement) {
        textElement.textContent = text; // Nastavit volitelný text
        banner.style.display = 'flex'; // Zobrazit banner
    }
}

// Funkce pro uzavření banneru (a persistentní skrývání)
function closeWarningBanner() {
    const banner = document.getElementById('warning-banner');
    if (banner) {
        banner.style.display = 'none';
        localStorage.setItem('warning_banner_closed', 'true'); // Uložit do localStorage, aby se nezobrazoval znovu
    }
}

// Příklad aktivace: Volání funkce showWarningBanner() kdykoli chcete (např. po načtení stránky)
// Přidejte toto do document.addEventListener('DOMContentLoaded', ... ) nebo kamkoli potřebujete
document.addEventListener('DOMContentLoaded', function() {
    showWarningBanner('Pozor! Dne 20.20.2222 nebude dostupná laserový tok energie přes EDC a tak si nedokážete uskutečnit cestu do vesmírného parku na Mars. OMLOUVÁME SE.'); // Aktivovat s volitelným textem
});
 