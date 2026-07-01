import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Simulasi Presipitasi Akurat", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

# --- KODE INJEKSI HTML5 & JAVASCRIPT ---
html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Simulasi Presipitasi Barium & Stronsium Sulfat</title>
    <style>
        :root {
            --bg: #0e1117;
            --panel: #1e212b;
            --text: #fafafa;
            --ba-color: #3b82f6;   /* Biru */
            --sr-color: #a855f7;   /* Ungu */
            --so4-color: #10b981;  /* Hijau */
            --scale-color: #f59e0b; /* Orange/Kerak */
        }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        h2 { margin: 0 0 15px 0; font-weight: 600; text-align: center; font-size: 1.5rem; }
        
        .main-container {
            width: 100%; max-width: 1200px; display: grid; grid-template-columns: 1fr 350px; gap: 20px;
        }
        
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center;
        }
        canvas { background: #12141a; border-radius: 8px; width: 100%; max-width: 800px; }
        
        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 15px;
        }
        
        .slider-group label { font-size: 0.85rem; color: #a1a1aa; display: flex; justify-content: space-between; margin-top: 10px;}
        input[type=range] { width: 100%; margin: 8px 0; accent-color: #3b82f6; }
        
        .dashboard-box { background: #262a35; padding: 15px; border-radius: 8px; text-align: center;}
        .status-clogged { color: #ef4444; font-weight: bold; font-size: 1.2rem; animation: blink 1s infinite; }
        .status-warning { color: #f59e0b; font-weight: bold; font-size: 1.2rem; }
        .status-safe { color: #10b981; font-weight: bold; font-size: 1.2rem; }
        
        @keyframes blink { 50% { opacity: 0.5; } }
        
        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-size: 0.8rem; padding: 10px; background: #262a35; border-radius: 8px; margin-top:10px; width: 100%;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        
        button { background:#3f3f46; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px;}
        button:hover { background: #52525b; }
    </style>
</head>
<body>

    <h2>Analisis Dinamis Penyumbatan Pipa (Scale Clogging)</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="800" height="500"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Air Formasi (Ba²⁺)</div>
                <div class="legend-item"><div class="dot" style="background:var(--sr-color);"></div> Air Formasi (Sr²⁺)</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Air Laut (SO₄²⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--scale-color); border-radius:2px;"></div> Kerak (BaSO₄ / SrSO₄)</div>
            </div>
        </div>
        
        <div class="control-panel">
            <h4 style="margin:0; border-bottom:1px solid #444; padding-bottom:10px; text-align:center;">Parameter Fluida</h4>
            
            <div class="slider-group">
                <label>Rasio Injeksi Air Laut <span id="valRasio">50%</span></label>
                <input type="range" id="slRasio" min="0" max="100" value="50">
                <div style="font-size: 0.7rem; color: #71717a; text-align: right;">*(Air Formasi = <span id="valFormasi">50%</span>)*</div>
                
                <label>Kons. Sulfat (Air Laut) <span id="valSO4">100%</span></label>
                <input type="range" id="slSO4" min="0" max="100" value="100">
                <div style="font-size: 0.7rem; color: #71717a; text-align: right;">*(0% = Simulasi SRU Aktif)*</div>

                <label>Kons. Ba/Sr (Air Formasi) <span id="valBa">100%</span></label>
                <input type="range" id="slBa" min="0" max="100" value="100">
            </div>
            
            <div class="dashboard-box">
                <div style="font-size: 0.85rem; color: #a1a1aa; margin-bottom: 5px;">Status Pipa Produksi</div>
                <div id="lblStatus" class="status-safe">Aman (Mengalir)</div>
                
                <div style="display:flex; justify-content: space-between; margin-top: 15px; font-size: 0.8rem; border-top: 1px solid #444; padding-top: 10px;">
                    <span>Ketebalan Kerak:</span>
                    <span id="valThick" style="font-weight: bold; color: var(--scale-color);">0 mm</span>
                </div>
            </div>
            
            <button id="btnFlush">Flush Pipa (Reset)</button>
        </div>
    </div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    
    const slRasio = document.getElementById('slRasio');
    const slSO4 = document.getElementById('slSO4');
    const slBa = document.getElementById('slBa');
    
    // Geometri Pipa Y-Shape
    const centerX = 400;
    const mixY = 250;
    const pipeWidth = 80;
    
    let particles = [];
    let scaleThickness = 0; // Ketebalan kerak di dinding pipa (0 s/d 40)
    let isClogged = false;
    
    class Particle {
        constructor(type, startX, startY, tgtX, tgtY) {
            this.type = type; // 'Ba', 'Sr', 'SO4', 'Scale'
            this.x = startX;
            this.y = startY;
            this.tgtX = tgtX;
            this.tgtY = tgtY;
            
            // Kecepatan menuju titik temu (mixY)
            let angle = Math.atan2(tgtY - startY, tgtX - startX);
            let speed = 2 + Math.random() * 1.5;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.active = true;
            this.isStuck = false;
        }
        
        update() {
            if (this.isStuck) return;
            
            // Gerakan sebelum titik temu
            if (this.y < mixY) {
                this.x += this.vx;
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 1.5; // Brownian
            } else {
                // Jatuh vertikal di pipa produksi
                if(isClogged && this.type !== 'Scale') {
                    // Jika buntu, partikel melambat dan berhenti
                    this.vy *= 0.8;
                } else {
                    this.vy = 3 + Math.random() * 2;
                }
                
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 2;
                
                // Batas dinding pipa (menyempit karena kerak)
                let leftWall = centerX - pipeWidth/2 + scaleThickness;
                let rightWall = centerX + pipeWidth/2 - scaleThickness;
                
                if (this.x < leftWall) this.x = leftWall;
                if (this.x > rightWall) this.x = rightWall;
                
                // Logika Scale Menempel
                if (this.type === 'Scale' && !isClogged) {
                    // Probabilitas menempel di dinding
                    if (this.x <= leftWall + 5 || this.x >= rightWall - 5) {
                        if(Math.random() < 0.1) {
                            this.isStuck = true;
                            if (scaleThickness < pipeWidth/2 - 5) {
                                scaleThickness += 0.2; // Kerak bertambah tebal
                            }
                        }
                    }
                }
            }
        }
        
        draw() {
            ctx.beginPath();
            if(this.type === 'Scale') {
                ctx.fillStyle = '#f59e0b';
                ctx.rect(this.x - 3, this.y - 3, 6, 6);
                ctx.fill();
            } else {
                ctx.arc(this.x, this.y, 3, 0, Math.PI*2);
                if (this.type === 'Ba') ctx.fillStyle = '#3b82f6';
                if (this.type === 'Sr') ctx.fillStyle = '#a855f7';
                if (this.type === 'SO4') ctx.fillStyle = '#10b981';
                ctx.fill();
            }
        }
    }
    
    function drawBackground() {
        ctx.fillStyle = '#12141a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#4b5563'; ctx.lineWidth = 6;
        ctx.lineJoin = 'round';
        
        // Outline Pipa Y
        ctx.beginPath();
        // Kiri Luar
        ctx.moveTo(50, 50); ctx.lineTo(centerX - pipeWidth/2, mixY); ctx.lineTo(centerX - pipeWidth/2, 500);
        ctx.stroke();
        
        ctx.beginPath();
        // Kanan Luar
        ctx.moveTo(750, 50); ctx.lineTo(centerX + pipeWidth/2, mixY); ctx.lineTo(centerX + pipeWidth/2, 500);
        ctx.stroke();
        
        ctx.beginPath();
        // Tengah Dalam
        ctx.moveTo(150, 50); ctx.lineTo(centerX, mixY - 50); ctx.lineTo(650, 50);
        ctx.stroke();
        
        // Label Air
        ctx.fillStyle = '#a1a1aa'; ctx.font = '14px Arial'; ctx.textAlign = 'center';
        ctx.fillText('Air Formasi (Ba²⁺, Sr²⁺)', 150, 40);
        ctx.fillText('Air Laut Injeksi (SO₄²⁻)', 650, 40);
        
        // Gambar Kerak (Scale) yang menempel
        if (scaleThickness > 0) {
            ctx.fillStyle = '#b45309'; // Warna kerak solid
            // Kerak Kiri
            ctx.fillRect(centerX - pipeWidth/2, mixY, scaleThickness, 500 - mixY);
            // Kerak Kanan
            ctx.fillRect(centerX + pipeWidth/2 - scaleThickness, mixY, scaleThickness, 500 - mixY);
            
            // Texture Kerak
            ctx.strokeStyle = '#92400e'; ctx.lineWidth = 1;
            ctx.beginPath();
            for(let y=mixY; y<500; y+=10) {
                ctx.moveTo(centerX - pipeWidth/2, y); ctx.lineTo(centerX - pipeWidth/2 + scaleThickness, y + 5);
                ctx.moveTo(centerX + pipeWidth/2, y); ctx.lineTo(centerX + pipeWidth/2 - scaleThickness, y + 5);
            }
            ctx.stroke();
        }
    }
    
    function spawnParticles() {
        if (isClogged) return; // Jika tersumbat, aliran berhenti
        
        let rasioLaut = parseInt(slRasio.value) / 100;
        let rasioFormasi = 1 - rasioLaut;
        
        let konsSO4 = parseInt(slSO4.value) / 100;
        let konsBa = parseInt(slBa.value) / 100;
        
        // SPAWN KIRI (Air Formasi)
        // Jumlah bergantung pada % Air Formasi dikali Konsentrasi Ba/Sr
        let spawnKiri = rasioFormasi * konsBa;
        if (Math.random() < spawnKiri * 0.8) {
            let startX = 100 + (Math.random() - 0.5) * 50;
            let type = Math.random() > 0.3 ? 'Ba' : 'Sr'; // 70% Ba, 30% Sr
            particles.push(new Particle(type, startX, 50, centerX - 20, mixY));
        }
        
        // SPAWN KANAN (Air Laut)
        // Jumlah bergantung pada % Air Laut dikali Konsentrasi Sulfat
        let spawnKanan = rasioLaut * konsSO4;
        if (Math.random() < spawnKanan * 0.8) {
            let startX = 700 + (Math.random() - 0.5) * 50;
            particles.push(new Particle('SO4', startX, 50, centerX + 20, mixY));
        }
    }
    
    function processCollisions() {
        for(let i = 0; i < particles.length; i++) {
            let p1 = particles[i];
            if(!p1.active || p1.isStuck || p1.type === 'Scale') continue;
            
            // Tabrakan hanya relevan jika partikel sudah mencapai titik temu (mixY)
            if (p1.y > mixY - 30) {
                for(let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if(!p2.active || p2.isStuck || p2.type === 'Scale') continue;
                    
                    // Cek tabrakan antara Ba/Sr dengan SO4
                    if ((p1.type === 'Ba' || p1.type === 'Sr') && p2.type === 'SO4' || 
                        (p2.type === 'Ba' || p2.type === 'Sr') && p1.type === 'SO4') {
                        
                        let dist = Math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2);
                        if(dist < 15) { // Radius reaksi
                            p1.active = false;
                            p2.active = false;
                            // Menjadi Kerak (Scale)
                            particles.push(new Particle('Scale', (p1.x+p2.x)/2, (p1.y+p2.y)/2, 0, 0));
                            break;
                        }
                    }
                }
            }
        }
    }
    
    function updateUI() {
        let rLaut = slRasio.value;
        document.getElementById('valRasio').innerText = rLaut + '%';
        document.getElementById('valFormasi').innerText = (100 - rLaut) + '%';
        document.getElementById('valSO4').innerText = slSO4.value + '%';
        document.getElementById('valBa').innerText = slBa.value + '%';
        
        // Status Pipa
        document.getElementById('valThick').innerText = (scaleThickness * 2).toFixed(1) + ' mm';
        
        let lblStatus = document.getElementById('lblStatus');
        if (scaleThickness > 35) {
            isClogged = true;
            lblStatus.innerText = 'TERSUMBAT TOTAL!';
            lblStatus.className = 'status-clogged';
        } else if (scaleThickness > 15) {
            isClogged = false;
            lblStatus.innerText = 'WASPADA (Penyempitan)';
            lblStatus.className = 'status-warning';
        } else {
            isClogged = false;
            lblStatus.innerText = 'Aman (Mengalir)';
            lblStatus.className = 'status-safe';
        }
    }
    
    function animate() {
        drawBackground();
        spawnParticles();
        processCollisions();
        
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update();
                p.draw();
                // Hapus jika keluar layar bawah
                if (p.y > canvas.height && !p.isStuck) {
                    particles.splice(i, 1);
                }
            } else {
                particles.splice(i, 1);
            }
        }
        
        updateUI();
        requestAnimationFrame(animate);
    }
    
    document.getElementById('btnFlush').addEventListener('click', () => {
        particles = [];
        scaleThickness = 0;
        isClogged = false;
    });
    
    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=750, scrolling=False)
