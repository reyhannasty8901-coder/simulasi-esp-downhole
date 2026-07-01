import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Simulasi Presipitasi Skala Industri", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

# --- KODE INJEKSI HTML5 & JAVASCRIPT ---
html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Kinetika Presipitasi Scale Barium Sulfat</title>
    <style>
        :root {
            --bg: #0e1117;
            --panel: #1e212b;
            --text: #fafafa;
            --ba-color: #3b82f6;   
            --sr-color: #a855f7;   
            --so4-color: #10b981;  
            --scale-color: #f59e0b; 
        }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        h2 { margin: 0 0 15px 0; font-weight: 600; text-align: center; font-size: 1.4rem; color: #e2e8f0; }
        
        .main-container {
            width: 100%; max-width: 1300px; display: grid; grid-template-columns: 1fr 380px; gap: 20px;
        }
        
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center;
        }
        /* Tinggi Canvas disesuaikan agar proporsional dan tidak terpotong */
        canvas { background: #12141a; border-radius: 8px; width: 100%; max-width: 850px; }
        
        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 15px;
            height: 100%; overflow-y: auto;
        }
        
        .control-section {
            border: 1px solid #334155; padding: 12px; border-radius: 8px; background: #1e293b;
        }
        .control-title {
            font-size: 0.9rem; font-weight: bold; color: #94a3b8; margin-bottom: 10px; border-bottom: 1px solid #475569; padding-bottom: 5px;
        }
        
        .slider-group label { font-size: 0.85rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 8px;}
        input[type=range] { width: 100%; margin: 5px 0 10px 0; accent-color: #3b82f6; }
        
        .metrics-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 5px;
        }
        .metric-card {
            background: #0f172a; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #334155;
        }
        .metric-title { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.2rem; font-weight: bold; margin-top: 5px; color: #f8fafc; }
        .alert { color: #ef4444 !important; animation: pulse 1s infinite; }
        .safe { color: #10b981 !important; }
        
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        
        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-size: 0.8rem; padding: 10px; background: #1e293b; border-radius: 8px; margin-top:15px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        
        button { background:#0284c7; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px; transition: 0.3s;}
        button:hover { background: #0369a1; }
        .btn-danger { background:#ef4444; }
        .btn-danger:hover { background: #b91c1c; }
    </style>
</head>
<body>

    <h2>Analisis Dinamis Penyumbatan Pipa Produksi</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="500"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Ion Ba²⁺</div>
                <div class="legend-item"><div class="dot" style="background:var(--sr-color);"></div> Ion Sr²⁺</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Ion SO₄²⁻</div>
                <div class="legend-item"><div class="dot" style="background:var(--scale-color); border-radius:2px;"></div> Kerak (Menumpuk)</div>
            </div>
        </div>
        
        <div class="control-panel">
            
            <div class="control-section">
                <div class="control-title">Fluida Formasi (Ba²⁺, Sr²⁺)</div>
                <div class="slider-group">
                    <label>Laju Alir <span id="valFlowF">50 bbl/d</span></label>
                    <input type="range" id="slFlowF" min="0" max="100" value="50">
                    <label>Konsentrasi Barium <span id="valBa">4500 ppm</span></label>
                    <input type="range" id="slBa" min="0" max="5000" value="4500" step="100">
                </div>
            </div>
            
            <div class="control-section">
                <div class="control-title">Air Injeksi (SO₄²⁻)</div>
                <div class="slider-group">
                    <label>Laju Alir <span id="valFlowL">50 bbl/d</span></label>
                    <input type="range" id="slFlowL" min="0" max="100" value="50">
                    <label>Konsentrasi Sulfat <span id="valSO4">28000 ppm</span></label>
                    <input type="range" id="slSO4" min="0" max="30000" value="28000" step="500">
                </div>
            </div>
            
            <div class="control-section" style="background: #0f172a; border-color: #475569;">
                <div class="control-title" style="color: #f8fafc;">Dasbor Sistem Operasi</div>
                
                <div style="text-align: center; padding: 10px; background: #1e293b; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-size: 0.75rem; color: #94a3b8;">SATURATION INDEX (SI)</div>
                    <div id="valSI" style="font-size: 1.5rem; font-weight: bold; color: #10b981;">0.0</div>
                    <div id="lblSIStatus" style="font-size: 0.8rem; color: #94a3b8;">Kondisi Undersaturated</div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Max Tebal Kerak</div>
                        <div class="metric-value" id="valThick">0.0 mm</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Penyumbatan</div>
                        <div class="metric-value safe" id="valBlock">0%</div>
                    </div>
                </div>
                
                <div style="margin-top: 10px; padding: 10px; background: #1e293b; border-radius: 6px; text-align: center; border: 1px solid #ef4444;">
                    <div class="metric-title" style="color: #fca5a5;">Laju Alir Fluida (Produksi)</div>
                    <div class="metric-value safe" id="valProdDrop">100%</div>
                </div>
            </div>
            
            <button id="btnFlush" class="btn-danger">ACID WASH (Reset Pipa)</button>
        </div>
    </div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    
    // Sliders
    const slFlowF = document.getElementById('slFlowF');
    const slBa = document.getElementById('slBa');
    const slFlowL = document.getElementById('slFlowL');
    const slSO4 = document.getElementById('slSO4');
    
    // Geometry
    const cX = 425; // Sumbu Tengah
    const mY = 220; // Titik persimpangan Y
    const pW = 120; // Lebar pipa diperbesar
    
    let particles = [];
    
    // ARRAY KETEBALAN KERAK SEPANJANG PIPA
    let scaleArrL = new Array(600).fill(0); 
    let scaleArrR = new Array(600).fill(0);
    
    let totalBlockage = 0; 
    let chokeY = -1; // Titik sumbat 100%
    let flashEffect = 0; 
    
    class Particle {
        constructor(type, startX, startY, tgtX, tgtY, isLeftFlow) {
            this.type = type; 
            this.x = startX; this.y = startY;
            this.isLeftFlow = isLeftFlow; 
            
            let dx = tgtX - startX;
            let dy = tgtY - startY;
            let angle = Math.atan2(dy, dx);
            let speed = 3 + Math.random() * 2;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            
            this.size = type === 'Scale' ? 4 : 3;
            this.active = true;
            this.isStuck = false; // Kalau true, partikel disembunyikan dan diubah jadi dinding
        }
        
        update(flowVelocity) {
            if (this.isStuck) return;
            
            // Tahap 1: Aliran masuk menuju pencampuran
            if (this.y < mY) {
                // Berhenti mengalir jika buntu
                if (totalBlockage >= 100) {
                    this.vx *= 0.5; this.vy *= 0.5;
                }
                this.x += this.vx; this.y += this.vy;
            } 
            // Tahap 2: Zona Produksi Vertikal
            else {
                // Deteksi indeks dinding
                let yIdx = Math.floor(this.y);
                if (yIdx >= 499) yIdx = 499;

                // LOGIKA PENYUMBATAN TOTAL
                if (totalBlockage >= 100 && chokeY > 0 && this.y <= chokeY + 10) {
                    this.vy = 0; // Berhenti sama sekali
                    this.x += (Math.random() - 0.5); // Getar getar air mampet
                } else {
                    let velocityBoost = 1;
                    if (totalBlockage < 95) velocityBoost = 1 + (totalBlockage / 100) * 1.5; 
                    else velocityBoost = (100 - totalBlockage) / 5; // Melambat tajam saat hampir mampet
                    
                    this.vy = (flowVelocity * 0.1) * velocityBoost + 2;
                    this.x += (Math.random() - 0.5) * 3; // Turbulensi
                }
                
                this.y += this.vy;
                
                let wallL = cX - pW/2 + scaleArrL[yIdx];
                let wallR = cX + pW/2 - scaleArrR[yIdx];
                
                // Jaga partikel tidak tembus kerak
                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // LOGIKA PENUMPUKAN KERAK (Super Agresif)
                if (this.type === 'Scale' && totalBlockage < 100) {
                    // Jarak deteksi dinding diperlebar agar cepat numpuk
                    if (this.x <= wallL + 8) {
                        this.isStuck = true; 
                        // Tambah ketebalan lokal membentuk gunung
                        for(let i = Math.max(mY, yIdx-20); i < Math.min(500, yIdx+20); i++) {
                            let dist = Math.abs(yIdx - i);
                            let increment = Math.max(0, (20 - dist) * 0.15); // Tumbuh cepat
                            if (scaleArrL[i] + scaleArrR[i] < pW) scaleArrL[i] += increment;
                        }
                    } else if (this.x >= wallR - 8) {
                        this.isStuck = true;
                        for(let i = Math.max(mY, yIdx-20); i < Math.min(500, yIdx+20); i++) {
                            let dist = Math.abs(yIdx - i);
                            let increment = Math.max(0, (20 - dist) * 0.15);
                            if (scaleArrL[i] + scaleArrR[i] < pW) scaleArrR[i] += increment;
                        }
                    }
                }
            }
        }
        
        draw() {
            if (this.isStuck) return; // Jangan gambar partikel yang sudah jadi kerak, biarkan Canvas yang gambar keraknya
            
            ctx.beginPath();
            if(this.type === 'Scale') {
                ctx.fillStyle = '#f59e0b';
                ctx.rect(this.x - 3, this.y - 3, 6, 6);
            } else {
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
                if (this.type === 'Ba') ctx.fillStyle = '#3b82f6';
                else if (this.type === 'Sr') ctx.fillStyle = '#a855f7';
                else if (this.type === 'SO4') ctx.fillStyle = '#10b981';
            }
            ctx.fill();
        }
    }
    
    function drawPipes() {
        ctx.fillStyle = '#12141a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#475569'; ctx.lineWidth = 8; ctx.lineJoin = 'round';
        
        // Pipa Outline
        ctx.beginPath(); ctx.moveTo(60, 40); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, 500); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(790, 40); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, 500); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(200, 40); ctx.lineTo(cX, mY - 60); ctx.lineTo(650, 40); ctx.stroke();
        
        ctx.fillStyle = '#94a3b8'; ctx.font = '13px Arial'; ctx.textAlign = 'center';
        ctx.fillText('Air Formasi (Ba²⁺, Sr²⁺)', 140, 30);
        ctx.fillText('Air Laut Injeksi (SO₄²⁻)', 710, 30);
        
        // RENDER KERAK DINAMIS SOLID
        ctx.fillStyle = '#f59e0b'; // Warna Kuning Emas Solid
        
        // Kerak Kiri
        ctx.beginPath(); ctx.moveTo(cX - pW/2, mY);
        for(let y = mY; y <= 500; y++) ctx.lineTo(cX - pW/2 + scaleArrL[y], y);
        ctx.lineTo(cX - pW/2, 500); ctx.fill();
        
        // Kerak Kanan
        ctx.beginPath(); ctx.moveTo(cX + pW/2, mY);
        for(let y = mY; y <= 500; y++) ctx.lineTo(cX + pW/2 - scaleArrR[y], y);
        ctx.lineTo(cX + pW/2, 500); ctx.fill();

        // Animasi Flash Reset
        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(16, 185, 129, ${flashEffect / 20})`;
            ctx.fillRect(0,0,850,500);
            flashEffect--;
        }
    }
    
    function processSystem() {
        let flowF = parseInt(slFlowF.value); let cBa = parseInt(slBa.value);
        let flowL = parseInt(slFlowL.value); let cSO4 = parseInt(slSO4.value);
        
        let totalFlow = flowF + flowL;
        let siValue = totalFlow > 0 ? (((fF/totalFlow)*cBa) * ((fL/totalFlow)*cSO4)) / 4000000 : 0; // Lebih sensitif
        
        // Spawn Ion (Stop kalau buntu)
        if (totalBlockage < 100) {
            if (flowF > 0 && Math.random() < (flowF / 100)) {
                let type = Math.random() > 0.25 ? 'Ba' : 'Sr'; 
                particles.push(new Particle(type, 135 + (Math.random() - 0.5)*60, 40, cX - 25, mY, true));
            }
            if (flowL > 0 && Math.random() < (flowL / 100)) {
                particles.push(new Particle('SO4', 715 + (Math.random() - 0.5)*60, 40, cX + 25, mY, false));
            }
        }
        
        // Nukleasi
        let nucleationProb = siValue > 1 ? Math.min(siValue * 0.2, 0.95) : 0; // Lebih cepat bereaksi
        if (nucleationProb > 0) {
            for(let i = 0; i < particles.length; i++) {
                let p1 = particles[i];
                if(!p1.active || p1.isStuck || p1.type === 'Scale' || p1.y < mY - 30) continue;
                
                for(let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if(!p2.active || p2.isStuck || p2.type === 'Scale' || p2.y < mY - 30) continue;
                    
                    if ((p1.isLeftFlow !== p2.isLeftFlow) && p1.type !== p2.type) {
                        let dist = Math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2);
                        if(dist < 20 && Math.random() < nucleationProb) {
                            p1.active = false; p2.active = false;
                            particles.push(new Particle('Scale', (p1.x+p2.x)/2, (p1.y+p2.y)/2, 0, 0, false));
                            break;
                        }
                    }
                }
            }
        }
        return { totalFlow, siValue };
    }
    
    function updateDasbor(flowData) {
        document.getElementById('valFlowF').innerText = slFlowF.value + ' bbl/d';
        document.getElementById('valBa').innerText = slBa.value + ' ppm';
        document.getElementById('valFlowL').innerText = slFlowL.value + ' bbl/d';
        document.getElementById('valSO4').innerText = slSO4.value + ' ppm';
        
        // Cari titik penyumbatan maksimum (Choke Point)
        let maxBlockVal = 0;
        chokeY = -1;
        for (let i = mY; i <= 500; i++) {
            let totalAtY = scaleArrL[i] + scaleArrR[i];
            if (totalAtY > maxBlockVal) maxBlockVal = totalAtY;
            if (totalAtY >= pW - 3 && chokeY === -1) chokeY = i; // Titik sumbat pertama
        }
        
        totalBlockage = (maxBlockVal / pW) * 100;
        if (totalBlockage > 100) totalBlockage = 100;
        
        // Kalkulasi efisiensi fluida
        let radiusSisa = 1 - (totalBlockage/100);
        let prodDrop = (radiusSisa * radiusSisa) * 100;
        if (totalBlockage >= 98) prodDrop = 0;
        
        // Update UI HTML
        let valSI = document.getElementById('valSI');
        let lblSI = document.getElementById('lblSIStatus');
        
        valSI.innerText = flowData.siValue.toFixed(2);
        if (flowData.siValue < 0.5) { valSI.style.color = '#10b981'; lblSI.innerText = 'Undersaturated (Aman)'; }
        else if (flowData.siValue < 1.5) { valSI.style.color = '#f59e0b'; lblSI.innerText = 'Saturated (Waspada)'; }
        else { valSI.style.color = '#ef4444'; lblSI.innerText = 'Supersaturated (Bahaya)'; }
        
        document.getElementById('valThick').innerText = maxBlockVal.toFixed(1) + ' mm';
        
        let elBlock = document.getElementById('valBlock');
        elBlock.innerText = totalBlockage.toFixed(0) + '%';
        elBlock.className = totalBlockage > 80 ? 'metric-value alert' : (totalBlockage > 30 ? 'metric-value' : 'metric-value safe');
        if (totalBlockage > 30 && totalBlockage <= 80) elBlock.style.color = '#f59e0b';
        
        let elProd = document.getElementById('valProdDrop');
        if (totalBlockage >= 98) {
            elProd.innerText = '0% (TERSUMBAT)';
            elProd.className = 'metric-value alert';
        } else {
            elProd.innerText = prodDrop.toFixed(0) + '%';
            elProd.className = prodDrop < 30 ? 'metric-value alert' : (prodDrop < 80 ? 'metric-value' : 'metric-value safe');
            if (prodDrop >= 30 && prodDrop < 80) elProd.style.color = '#f59e0b';
        }
    }
    
    function animate() {
        drawPipes();
        let flowData = processSystem();
        
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update(flowData.totalFlow);
                p.draw();
                if (p.y > canvas.height + 10 && !p.isStuck) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }
        
        updateDasbor(flowData);
        requestAnimationFrame(animate);
    }
    
    document.getElementById('btnFlush').addEventListener('click', () => {
        particles = [];
        scaleArrL.fill(0);
        scaleArrR.fill(0);
        totalBlockage = 0;
        chokeY = -1;
        flashEffect = 20; 
    });
    
    animate();
</script>
</body>
</html>
"""

# Tinggi dinaikkan ke 850 agar dijamin tidak terpotong!
components.html(html_app, height=850, scrolling=False)
