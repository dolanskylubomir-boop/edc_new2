/**
 * Funkce pro zobrazení systémového banneru
 * @param {string} text - Text hlášení, který se má zobrazit
 */
function showSystemBanner(text = 'Stránky se připravují') {
    const banner = document.getElementById('system-banner');
    const textElement = document.getElementById('system-banner-text');

    if (banner && textElement) {
        textElement.textContent = text;
        banner.style.display = 'flex'; // Zobrazí banner
        
        // DŮLEŽITÉ: Posune obsah webu dolů, aby banner nezakryl horní menu/header
        document.body.style.paddingTop = banner.offsetHeight + 'px';
    }
}

/**
 * Funkce pro ZAVŘENÍ systémového banneru
 * Volá se pomocí onclick="closeSystemBanner()" v HTML
 */
function closeSystemBanner() {
    const banner = document.getElementById('system-banner');
    if (banner) {
        banner.style.display = 'none'; // Skryje banner
        
        // Vrátí odsazení stránky zpět na nulu
        document.body.style.paddingTop = '0px';
    }
}

// SPOUŠTĚCÍ VOLÁNÍ: Aktivuje se po načtení stránky
document.addEventListener('DOMContentLoaded', function() {
    // Zde nastavte požadovaný text hlášení
    showSystemBanner('UPOZORNĚNÍ: Tady doplnit text o odstávce atd......');
});
