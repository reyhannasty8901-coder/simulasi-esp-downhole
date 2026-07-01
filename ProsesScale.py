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
            --scale-color: #f59e0b; /* Warna Kuning Kerak */
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
            <canvas id="simCanvas" width="850" height="520"></canvas>
            
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
                    <div class="metric-title" style="color: #fca5a5;">Laju Alir Fluida</div>
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
    const cX = 425; // Center X
    const mY = 220; // Mix Y (Pipa produksi dimulai)
    const pW = 100; // Pipe Width Max
    
    let particles = [];
    let scaleArrL = new Array(521).fill(0); 
    let scaleArrR = new Array(521).fill(0);
    
    let totalBlockage = 0; 
    let flashEffect = 0; 

    class Particle {
        constructor(type, startX, startY, tgtX, tgtY, isLeftFlow) {
            this.type = type;
            this.x = startX; this.y = startY;
            this.isLeftFlow = isLeftFlow; 
            
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
            if (this.y < mY) {
                this.x += this.vx; this.y += this.vy;
            } 
            // Tahap 2: Zona Produksi Vertikal
            else {
                // LOGIKA BERHENTI JIKA TERSUMBAT TOTAL
                if (totalBlockage >= 100) {
                    this.vy = 0;
                    this.vx = 0;
                } else {
                    let velocityBoost = 1 - (totalBlockage / 100); 
                    this.vy = (flowVelocity * 0.1) * velocityBoost + 1;
                    this.x += (Math.random() - 0.5) * 2;
                }
                
                this.y += this.vy;

                // Cek dinding berdasarkan kerak
                let yIdx = Math.floor(this.y);
                if (yIdx >= 520) yIdx = 520;
                if (yIdx < 0) yIdx = 0;

                let wallL = cX - pW/2 + scaleArrL[yIdx];
                let wallR = cX + pW/2 - scaleArrR[yIdx];
                
                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // Logika Penempelan Kerak
                if (this.type === 'Scale' && totalBlockage < 100) {
                    if (this.x <= wallL + 3 || this.x >= wallR - 3) {
                        if (Math.random() < 0.3) {
                            this.isStuck = true;
                            // Menumpuk kerak
                            for(let i = Math.max(mY, yIdx-15); i < Math.min(520, yIdx+15); i++) {
                                let dist = Math.abs(yIdx - i);
                                let increment = Math.max(0, (15 - dist) * 0.08);
                                // Kerak tidak bisa melebihi tengah pipa (50px kiri + 50px kanan)
                                if (scaleArrL[i] + scaleArrR[i] < pW) {
                                    if (this.x < cX) scaleArrL[i] += increment;
                                    else scaleArrR[i] += increment;
                                }
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
                ctx.fillRect(this.x - 3, this.y - 3, 6, 6);
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
        ctx.strokeStyle = '#475569'; ctx.lineWidth = 6; ctx.lineJoin = 'round';
        
        // Outline Pipa
        ctx.beginPath(); 
        ctx.moveTo(50, 50); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, 520);
        ctx.moveTo(800, 50); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, 520);
        ctx.moveTo(150, 50); ctx.lineTo(cX, mY - 60); ctx.lineTo(700, 50);
        ctx.stroke();
        
        // Render Kerak (Warna Kuning Oranye)
        ctx.fillStyle = '#f59e0b'; 
        // Kiri
        ctx.beginPath(); ctx.moveTo(cX - pW/2, mY);
        for(let y = mY; y <= 520; y++) ctx.lineTo(cX - pW/2 + scaleArrL[y], y);
        ctx.lineTo(cX - pW/2, 520); ctx.fill();
        // Kanan
        ctx.beginPath(); ctx.moveTo(cX + pW/2, mY);
        for(let y = mY; y <= 520; y++) ctx.lineTo(cX + pW/2 - scaleArrR[y], y);
        ctx.lineTo(cX + pW/2, 520); ctx.fill();

        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(255, 255, 255, ${flashEffect / 20})`;
            ctx.fillRect(0,0,850,520); flashEffect--;
        }
    }
    
    function processSystem() {
        let fF = parseInt(slFlowF.value); let cBa = parseInt(slBa.value);
        let fL = parseInt(slFlowL.value); let cSO4 = parseInt(slSO4.value);
        
        let totalFlow = fF + fL;
        let siValue = totalFlow > 0 ? (((fF/totalFlow)*cBa) * ((fL/totalFlow)*cSO4)) / 5000000 : 0;
        
        // Spawn partikel jika tidak mampet
        if (totalBlockage < 100) {
            if (fF > 0 && Math.random() < (fF / 100)) {
                particles.push(new Particle(Math.random() > 0.2 ? 'Ba' : 'Sr', 135, 50, cX - 20, mY, true));
            }
            if (fL > 0 && Math.random() < (fL / 100)) {
                particles.push(new Particle('SO4', 715, 50, cX + 20, mY, false));
            }
        }
        
        // Nukleasi
        let nProb = siValue > 1 ? Math.min(siValue * 0.15, 0.9) : 0;
        for(let i = 0; i < particles.length; i++) {
            let p1 = particles[i];
            if(!p1.active || p1.isStuck || p1.type === 'Scale' || p1.y < mY - 10) continue;
            for(let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                if(!p2.active || p2.isStuck || p2.type === 'Scale' || p2.y < mY - 10) continue;
                if ((p1.isLeftFlow !== p2.isLeftFlow) && p1.type !== p2.type) {
                    if(Math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2) < 15 && Math.random() < nProb) {
                        p1.active = false; p2.active = false;
                        particles.push(new Particle('Scale', (p1.x+p2.x)/2, (p1.y+p2.y)/2, 0, 0, false));
                    }
                }
            }
        }
        return { totalFlow, siValue };
    }
    
    function updateDasbor(flowData) {
        let maxT = 0;
        for (let i = mY; i <= 520; i++) {
            let t = scaleArrL[i] + scaleArrR[i];
            if (t > maxT) maxT = t;
        }
        totalBlockage = (maxT / pW) * 100;
        if (totalBlockage > 100) totalBlockage = 100;

        let flowEff = Math.max(0, 100 - totalBlockage);
        
        document.getElementById('valSI').innerText = flowData.siValue.toFixed(2);
        document.getElementById('valThick').innerText = maxT.toFixed(1) + ' mm';
        document.getElementById('valBlock').innerText = totalBlockage.toFixed(0) + '%';
        document.getElementById('valProdDrop').innerText = flowEff.toFixed(0) + '%';
        
        let elProd = document.getElementById('valProdDrop');
        elProd.className = flowEff < 30 ? 'metric-value alert' : 'metric-value safe';
    }
    
    function animate() {
        drawPipes();
        let data = processSystem();
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update(data.totalFlow);
                p.draw();
                if (p.y > 530) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }
        updateDasbor(data);
        requestAnimationFrame(animate);
    }
    
    document.getElementById('btnFlush').addEventListener('click', () => {
        particles = []; scaleArrL.fill(0); scaleArrR.fill(0); totalBlockage = 0; flashEffect = 20;
    });
    
    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=750, scrolling=False)
