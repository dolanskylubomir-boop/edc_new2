document.addEventListener('DOMContentLoaded', () => {
    console.log('Modern effects initializing...');
    
    // 1. Inicializace AOS (pokud ještě není)
    if (typeof AOS !== 'undefined' && typeof AOS.init === 'function') {
        AOS.init({ 
            duration: 1000, 
            once: true,
            offset: 100,
            easing: 'ease-out-cubic'
        });
    }
    
    // 2. Custom Cursor - žárovička (pouze pokud není mobil)
    if (window.innerWidth > 768) {
        initCustomCursor();
    }
    
    // 3. Parallax efekt pro hero sekci
    const heroSection = document.querySelector('.hero.parallax-hero');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.3;
            heroSection.style.transform = `translateY(${rate}px)`;
        });
    }
    
    // 4. Smooth scroll pro anchor odkazy
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 100,
                    behavior: 'smooth'
                });
                // Spustit click zvuk
                if (typeof playClick === 'function') playClick();
            }
        });
    });
    
    // 5. Hover efekty s glow
    document.querySelectorAll('.modal-trigger, .card-glow').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.boxShadow = '0 20px 40px rgba(148, 227, 194, 0.4)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.boxShadow = '';
        });
    });
});

// Funkce pro custom cursor
function initCustomCursor() {
    if (document.querySelector('.custom-cursor')) return;
    
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);
    
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Parallax efekt pro kurzor
        cursorX += (mouseX - cursorX) * 0.15;
        cursorY += (mouseY - cursorY) * 0.15;
        
        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';
        
        // Změna při hoveru
        const isOverInteractive = e.target.closest('a, button, .modal-trigger, .sub-modal-trigger, input, [role="button"]');
        
        if (isOverInteractive) {
            cursor.classList.add('cursor-hover');
            cursor.style.transform = 'translate(-50%, -50%) scale(1.5)';
        } else {
            cursor.classList.remove('cursor-hover');
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
        }
    });
}

// Globální funkce pro click zvuk
window.playClick = () => {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        
        osc.type = 'sine'; 
        osc.frequency.setValueAtTime(800, audioCtx.currentTime);
        
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        
        osc.connect(gain); 
        gain.connect(audioCtx.destination);
        osc.start(); 
        osc.stop(audioCtx.currentTime + 0.1);
    } catch (e) {
        console.log('Audio context not supported:', e);
    }
};