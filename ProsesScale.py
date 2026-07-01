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
        
        /* Dasbor Metrik */
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
        
        button { background:#ef4444; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px; transition: 0.3s;}
        button:hover { background: #b91c1c; }
    </style>
</head>
<body>

    <h2>Kinetika Presipitasi & Dinamika Transport Fluida</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="520"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Ion Ba²⁺</div>
                <div class="legend-item"><div class="dot" style="background:var(--sr-color);"></div> Ion Sr²⁺</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Ion SO₄²⁻</div>
                <div class="legend-item"><div class="dot" style="background:var(--scale-color); border-radius:2px;"></div> Kerak (Nucleated BaSO₄/SrSO₄)</div>
            </div>
        </div>
        
        <div class="control-panel">
            
            <div class="control-section">
                <div class="control-title">Fluida Formasi (Ba²⁺, Sr²⁺)</div>
                <div class="slider-group">
                    <label>Laju Alir <span id="valFlowF">50 bbl/d</span></label>
                    <input type="range" id="slFlowF" min="0" max="100" value="50">
                    <label>Konsentrasi Barium <span id="valBa">4000 ppm</span></label>
                    <input type="range" id="slBa" min="0" max="5000" value="4000" step="100">
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
                        <div class="metric-title">Tebal Kerak</div>
                        <div class="metric-value" id="valThick">0.0 mm</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Penyumbatan</div>
                        <div class="metric-value safe" id="valBlock">0%</div>
                    </div>
                </div>
                
                <div style="margin-top: 10px; padding: 10px; background: #1e293b; border-radius: 6px; text-align: center; border: 1px solid #ef4444;">
                    <div class="metric-title" style="color: #fca5a5;">Penurunan Produksi Minyak</div>
                    <div class="metric-value safe" id="valProdDrop">0%</div>
                </div>
            </div>
            
            <button id="btnFlush">ACID WASH (Reset Pipa)</button>
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
    const cX = 425; // Center X
    const mY = 250; // Mix Y
    const pW = 100; // Pipe Width Max
    
    let particles = [];
    let scaleThickL = 0; // Ketebalan kiri
    let scaleThickR = 0; // Ketebalan kanan
    let totalBlockage = 0; // Persentase
    
    class Particle {
        constructor(type, startX, startY, tgtX, tgtY, isLeftFlow) {
            this.type = type; // 'Ba', 'Sr', 'SO4', 'Scale'
            this.x = startX; this.y = startY;
            this.isLeftFlow = isLeftFlow; // true = dari formasi, false = dari laut
            
            // Perhitungan arah aliran menuju pusat campur
            let dx = tgtX - startX;
            let dy = tgtY - startY;
            let angle = Math.atan2(dy, dx);
            let speed = 2 + Math.random() * 2;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.active = true;
            this.isStuck = false;
        }
        
        update(flowVelocity) {
            if (this.isStuck) return;
            
            // Tahap 1: Aliran masuk menuju pencampuran
            if (this.y < mY - 20) {
                this.x += this.vx; this.y += this.vy;
                this.x += (Math.random() - 0.5) * 1.0; 
            } 
            // Tahap 2: Zona Campur & Aliran Bawah (Produksi)
            else {
                // Efek Bernoulli: Semakin tersumbat, fluida di tengah mengalir lebih cepat
                let velocityBoost = 1 + (totalBlockage / 100) * 1.5; 
                this.vy = (flowVelocity * 0.1) * velocityBoost + Math.random();
                
                // Hentikan jika buntu total
                if (totalBlockage >= 98 && this.type !== 'Scale') this.vy *= 0.1;
                
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 3; // Turbulensi campuran
                
                // Logika Pembatasan Dinding akibat Kerak
                let wallL = cX - pW/2 + scaleThickL;
                let wallR = cX + pW/2 - scaleThickR;
                
                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // Logika Deposisi (Scale menempel)
                if (this.type === 'Scale' && totalBlockage < 100) {
                    if (this.x <= wallL + 6) {
                        if (Math.random() < 0.15) { // Probabilitas nempel
                            this.isStuck = true;
                            if (scaleThickL < pW/2 - 2) scaleThickL += 0.25;
                        }
                    } else if (this.x >= wallR - 6) {
                        if (Math.random() < 0.15) {
                            this.isStuck = true;
                            if (scaleThickR < pW/2 - 2) scaleThickR += 0.25;
                        }
                    }
                }
            }
        }
        
        draw() {
            ctx.beginPath();
            if(this.type === 'Scale') {
                ctx.fillStyle = '#f59e0b'; // Kristal BaSO4 solid
                ctx.moveTo(this.x, this.y - 4); ctx.lineTo(this.x + 4, this.y);
                ctx.lineTo(this.x, this.y + 4); ctx.lineTo(this.x - 4, this.y);
                ctx.fill();
            } else {
                ctx.arc(this.x, this.y, 3, 0, Math.PI*2);
                if (this.type === 'Ba') ctx.fillStyle = '#3b82f6';
                else if (this.type === 'Sr') ctx.fillStyle = '#a855f7';
                else if (this.type === 'SO4') ctx.fillStyle = '#10b981';
                ctx.fill();
            }
        }
    }
    
    function drawPipes() {
        ctx.fillStyle = '#12141a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#475569'; ctx.lineWidth = 8; ctx.lineJoin = 'round';
        // Kiri
        ctx.beginPath(); ctx.moveTo(70, 50); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, 520); ctx.stroke();
        // Kanan
        ctx.beginPath(); ctx.moveTo(780, 50); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, 520); ctx.stroke();
        // Tengah
        ctx.beginPath(); ctx.moveTo(200, 50); ctx.lineTo(cX, mY - 60); ctx.lineTo(650, 50); ctx.stroke();
        
        // Label
        ctx.fillStyle = '#94a3b8'; ctx.font = '13px Arial'; ctx.textAlign = 'center';
        ctx.fillText('Air Formasi', 135, 40);
        ctx.fillText('Air Laut / Injeksi', 715, 40);
        ctx.fillText('Sumur Produksi', cX, 510);
        
        // Render Kerak (Scale Deposition)
        if (scaleThickL > 0 || scaleThickR > 0) {
            ctx.fillStyle = '#92400e'; 
            ctx.fillRect(cX - pW/2, mY, scaleThickL, 520 - mY);
            ctx.fillRect(cX + pW/2 - scaleThickR, mY, scaleThickR, 520 - mY);
            
            // Border keras untuk kerak
            ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(cX - pW/2 + scaleThickL, mY); ctx.lineTo(cX - pW/2 + scaleThickL, 520);
            ctx.moveTo(cX + pW/2 - scaleThickR, mY); ctx.lineTo(cX + pW/2 - scaleThickR, 520);
            ctx.stroke();
        }
    }
    
    function processSystem() {
        let flowF = parseInt(slFlowF.value);
        let flowL = parseInt(slFlowL.value);
        let cBa = parseInt(slBa.value);
        let cSO4 = parseInt(slSO4.value);
        
        // Kalkulasi Saturation Index (Sederhana: Konsentrasi dikali Volume fraksi)
        let totalFlow = flowF + flowL;
        let siValue = 0;
        
        if (totalFlow > 0) {
            let mixBa = (flowF / totalFlow) * cBa;
            let mixSO4 = (flowL / totalFlow) * cSO4;
            // Angka 500000 hanyalah konstanta visual agar nilai SI berkisar 0-5
            siValue = (mixBa * mixSO4) / 5000000; 
        }
        
        // Spawn Formasi (Kiri)
        if (flowF > 0 && Math.random() < (flowF / 100)) {
            let type = Math.random() > 0.25 ? 'Ba' : 'Sr'; 
            let stX = 135 + (Math.random() - 0.5) * 60;
            particles.push(new Particle(type, stX, 50, cX - 25, mY, true));
        }
        
        // Spawn Laut (Kanan)
        if (flowL > 0 && Math.random() < (flowL / 100)) {
            let stX = 715 + (Math.random() - 0.5) * 60;
            particles.push(new Particle('SO4', stX, 50, cX + 25, mY, false));
        }
        
        // Fisika Tabrakan & Nukleasi (Hanya terjadi jika SI tinggi)
        // Semakin tinggi SI, probabilitas tabrakan bereaksi semakin besar
        let nucleationProb = siValue > 1 ? Math.min(siValue * 0.15, 0.9) : 0;

        if (nucleationProb > 0) {
            for(let i = 0; i < particles.length; i++) {
                let p1 = particles[i];
                if(!p1.active || p1.isStuck || p1.type === 'Scale' || p1.y < mY - 30) continue;
                
                for(let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if(!p2.active || p2.isStuck || p2.type === 'Scale' || p2.y < mY - 30) continue;
                    
                    if ((p1.isLeftFlow !== p2.isLeftFlow) && p1.type !== p2.type) {
                        let dist = Math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2);
                        if(dist < 18 && Math.random() < nucleationProb) {
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
        // Update Labels Slider
        document.getElementById('valFlowF').innerText = slFlowF.value + ' bbl/d';
        document.getElementById('valBa').innerText = slBa.value + ' ppm';
        document.getElementById('valFlowL').innerText = slFlowL.value + ' bbl/d';
        document.getElementById('valSO4').innerText = slSO4.value + ' ppm';
        
        // Kalkulasi Penyumbatan
        totalBlockage = ((scaleThickL + scaleThickR) / pW) * 100;
        if (totalBlockage > 100) totalBlockage = 100;
        
        // Penurunan Produksi Berbanding lurus dengan kuadrat jari-jari yang tersisa (Hagen-Poiseuille)
        let radiusSisa = 1 - (totalBlockage/100);
        let prodDrop = (1 - (radiusSisa * radiusSisa)) * 100;
        
        // Update HTML Dasbor
        let valSI = document.getElementById('valSI');
        let lblSI = document.getElementById('lblSIStatus');
        
        valSI.innerText = flowData.siValue.toFixed(2);
        if (flowData.siValue < 0.5) { valSI.style.color = '#10b981'; lblSI.innerText = 'Undersaturated (Aman)'; }
        else if (flowData.siValue < 1.5) { valSI.style.color = '#f59e0b'; lblSI.innerText = 'Saturated (Waspada)'; }
        else { valSI.style.color = '#ef4444'; lblSI.innerText = 'Supersaturated (Presipitasi Masif)'; }
        
        document.getElementById('valThick').innerText = (scaleThickL + scaleThickR).toFixed(1) + ' mm';
        
        let elBlock = document.getElementById('valBlock');
        elBlock.innerText = totalBlockage.toFixed(0) + '%';
        elBlock.className = totalBlockage > 50 ? 'metric-value alert' : (totalBlockage > 20 ? 'metric-value' : 'metric-value safe');
        
        let elProd = document.getElementById('valProdDrop');
        elProd.innerText = prodDrop.toFixed(0) + '%';
        elProd.className = prodDrop > 50 ? 'metric-value alert' : (prodDrop > 20 ? 'metric-value' : 'metric-value safe');
    }
    
    function animate() {
        drawPipes();
        let flowData = processSystem();
        
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                // Beri kecepatan aliran gabungan
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
        scaleThickL = 0; scaleThickR = 0; totalBlockage = 0;
    });
    
    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=750, scrolling=False)
