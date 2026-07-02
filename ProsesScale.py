import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Simulasi Presipitasi Scale Barium", layout="wide", initial_sidebar_state="collapsed")
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
        h2 { margin: 0 0 15px 0; font-weight: 600; text-align: center; font-size: 1.5rem; color: #f8fafc; }
        
        .main-container {
            width: 100%; max-width: 1300px; display: grid; grid-template-columns: 1fr 400px; gap: 20px;
        }
        
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center;
        }
        canvas { background: #0b0f19; border-radius: 8px; width: 100%; max-width: 850px; }
        
        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 15px;
        }
        
        .control-section {
            border: 1px solid #334155; padding: 15px; border-radius: 8px; background: #1e293b;
        }
        .control-title {
            font-size: 0.95rem; font-weight: bold; color: #94a3b8; margin-bottom: 12px; border-bottom: 1px solid #475569; padding-bottom: 5px;
        }
        
        .slider-group label { font-size: 0.85rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 8px;}
        input[type=range] { width: 100%; margin: 8px 0 12px 0; accent-color: #3b82f6; }
        
        .metrics-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;
        }
        .metric-card {
            background: #0f172a; padding: 12px; border-radius: 6px; text-align: center; border: 1px solid #334155;
        }
        .metric-title { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.4rem; font-weight: bold; margin-top: 5px; color: #f8fafc; }
        .alert { color: #ef4444 !important; animation: pulse 1s infinite; }
        .safe { color: #10b981 !important; }
        
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        
        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-size: 0.85rem; padding: 12px; background: #1e293b; border-radius: 8px; margin-top:15px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 6px; font-weight: 500;}
        .dot { width: 14px; height: 14px; border-radius: 50%; }
        
        button { background:#0284c7; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px; transition: 0.3s; font-size: 1rem;}
        button:hover { background: #0369a1; }
        .btn-danger { background:#ef4444; }
        .btn-danger:hover { background: #b91c1c; }
    </style>
</head>
<body>

    <h2>Analisis Dinamis Penyumbatan Pipa Produksi</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="550"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Ion Ba²⁺</div>
                <div class="legend-item"><div class="dot" style="background:var(--sr-color);"></div> Ion Sr²⁺</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Ion SO₄²⁻</div>
                <div class="legend-item"><div class="dot" style="background:var(--scale-color); border-radius:3px;"></div> Kerak (Menumpuk)</div>
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
                <div class="control-title" style="color: #f8fafc; text-align: center;">Dasbor Sistem Operasi</div>
                
                <div style="text-align: center; padding: 10px; background: #1e293b; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-size: 0.75rem; color: #94a3b8;">SATURATION INDEX (SI)</div>
                    <div id="valSI" style="font-size: 1.8rem; font-weight: bold; color: #10b981;">0.00</div>
                    <div id="lblSIStatus" style="font-size: 0.85rem; color: #94a3b8;">Kondisi Undersaturated</div>
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
                
                <div style="margin-top: 10px; padding: 12px; background: #1e293b; border-radius: 6px; text-align: center; border: 1px solid #ef4444;">
                    <div class="metric-title" style="color: #fca5a5;">Laju Alir Fluida (Produksi)</div>
                    <div class="metric-value safe" id="valProdDrop" style="font-size: 1.8rem;">100%</div>
                </div>
            </div>
            
            <button id="btnFlush" class="btn-danger">ACID WASH (Bersihkan Pipa)</button>
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
    
    // Geometri Pipa Utama
    const cX = 425; // Titik sumbu X tengah
    const mY = 240; // Titik persimpangan Y
    const pW = 120; // Lebar pipa diperbesar agar visual kerak lebih jelas
    
    let particles = [];
    
    // Array untuk menyimpan profil ketebalan kerak di setiap titik Y
    let scaleArrL = new Array(600).fill(0); 
    let scaleArrR = new Array(600).fill(0);
    
    let totalBlockage = 0; 
    let chokeY = -1; // Titik Y di mana pipa mampet 100%
    let flashEffect = 0; 

    class Particle {
        constructor(type, startX, startY, tgtX, tgtY, isLeftFlow) {
            this.type = type;
            this.x = startX; 
            this.y = startY;
            this.isLeftFlow = isLeftFlow; 
            
            // Kalkulasi arah dari pipa cabang ke titik temu
            let dx = tgtX - startX;
            let dy = tgtY - startY;
            let angle = Math.atan2(dy, dx);
            let speed = 3 + Math.random() * 2; // Partikel lebih cepat & responsif
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            
            this.size = type === 'Scale' ? 5 : 4; // Ukuran partikel lebih tebal
            this.active = true;
            this.isStuck = false;
        }
        
        update(flowVelocity) {
            if (this.isStuck) return;
            
            // Tahap 1: Di dalam pipa cabang (atas)
            if (this.y < mY - 20) {
                // Jika pipa bawah sudah mampet total, aliran di atas juga ikut melambat parah
                if (totalBlockage >= 100) {
                    this.x += this.vx * 0.1;
                    this.y += this.vy * 0.1;
                } else {
                    this.x += this.vx; 
                    this.y += this.vy;
                }
            } 
            // Tahap 2: Di dalam pipa produksi (bawah)
            else {
                let yIdx = Math.floor(this.y);
                if (yIdx >= 550) yIdx = 549;
                
                // LOGIKA PENYUMBATAN TOTAL (CHOKE POINT)
                if (totalBlockage >= 100 && chokeY > 0 && this.y <= chokeY + 10) {
                    // Partikel berhenti bergerak karena tekanan terblokir
                    this.vy = 0;
                    this.x += (Math.random() - 0.5); // Hanya bergetar di tempat
                } else {
                    // Kecepatan meningkat akibat penyempitan (Hukum Kontinuitas), tapi turun jika hampir mampet
                    let velocityBoost = 1;
                    if (totalBlockage < 90) velocityBoost = 1 + (totalBlockage / 100) * 1.5;
                    else velocityBoost = (100 - totalBlockage) / 10;
                    
                    this.vy = (flowVelocity * 0.1) * velocityBoost + 2;
                    this.x += (Math.random() - 0.5) * 3; // Turbulensi air
                }
                
                this.y += this.vy;

                // Hitung batas dinding aktual berdasarkan tumpukan kerak
                let wallL = cX - pW/2 + scaleArrL[yIdx];
                let wallR = cX + pW/2 - scaleArrR[yIdx];
                
                // Jaga agar partikel tidak menembus kerak
                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // LOGIKA KERAK BERTUMPUK BERGERIGI
                if (this.type === 'Scale' && totalBlockage < 100) {
                    // Jika menyentuh batas dinding (yang sudah tertutup kerak)
                    if (this.x <= wallL + 5 || this.x >= wallR - 5) {
                        if (Math.random() < 0.4) { // Probabilitas menempel tinggi
                            this.isStuck = true;
                            
                            // Tumbuhkan kerak dengan profil pegunungan tajam (peak)
                            let peakHeight = Math.random() * 4 + 2;
                            let spread = 15; // Lebar sebaran kerak
                            
                            for(let i = Math.max(mY, yIdx - spread); i < Math.min(550, yIdx + spread); i++) {
                                let dist = Math.abs(yIdx - i);
                                let increment = Math.max(0, (spread - dist) * 0.2 * peakHeight);
                                
                                // Pastikan kerak dari kiri dan kanan tidak menembus garis tengah
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
                // Bentuk kotak berlian untuk partikel kerak
                ctx.fillStyle = '#f59e0b';
                ctx.moveTo(this.x, this.y - this.size);
                ctx.lineTo(this.x + this.size, this.y);
                ctx.lineTo(this.x, this.y + this.size);
                ctx.lineTo(this.x - this.size, this.y);
                ctx.fill();
            } else {
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
                if (this.type === 'Ba') ctx.fillStyle = '#3b82f6';
                else if (this.type === 'Sr') ctx.fillStyle = '#a855f7';
                else if (this.type === 'SO4') ctx.fillStyle = '#10b981';
                ctx.fill();
            }
        }
    }
    
    function drawSystem() {
        // Latar Belakang
        ctx.fillStyle = '#0b0f19'; 
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Gambar Struktur Pipa Y (Lebih Tebal)
        ctx.strokeStyle = '#475569'; 
        ctx.lineWidth = 10; 
        ctx.lineJoin = 'round';
        
        ctx.beginPath(); 
        ctx.moveTo(70, 50); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, 550);
        ctx.moveTo(780, 50); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, 550);
        ctx.moveTo(220, 50); ctx.lineTo(cX, mY - 70); ctx.lineTo(630, 50);
        ctx.stroke();
        
        // Teks Bantuan
        ctx.fillStyle = '#94a3b8'; ctx.font = '14px Arial'; ctx.textAlign = 'center';
        ctx.fillText('Air Formasi (Ba²⁺, Sr²⁺)', 140, 35);
        ctx.fillText('Air Laut Injeksi (SO₄²⁻)', 710, 35);
        
        // RENDER TUMPUKAN KERAK (Profil Gunung)
        ctx.fillStyle = '#b45309'; // Warna isi kerak
        
        // Kerak Kiri
        ctx.beginPath(); ctx.moveTo(cX - pW/2, mY);
        for(let y = mY; y <= 550; y++) ctx.lineTo(cX - pW/2 + scaleArrL[y], y);
        ctx.lineTo(cX - pW/2, 550); ctx.fill();
        
        // Kerak Kanan
        ctx.beginPath(); ctx.moveTo(cX + pW/2, mY);
        for(let y = mY; y <= 550; y++) ctx.lineTo(cX + pW/2 - scaleArrR[y], y);
        ctx.lineTo(cX + pW/2, 550); ctx.fill();

        // Garis batas luar kerak (warna lebih terang)
        ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 2;
        
        ctx.beginPath(); ctx.moveTo(cX - pW/2 + scaleArrL[mY], mY);
        for(let y = mY; y <= 550; y++) ctx.lineTo(cX - pW/2 + scaleArrL[y], y);
        ctx.stroke();
        
        ctx.beginPath(); ctx.moveTo(cX + pW/2 - scaleArrR[mY], mY);
        for(let y = mY; y <= 550; y++) ctx.lineTo(cX + pW/2 - scaleArrR[y], y);
        ctx.stroke();

        // Efek Kilat Reset
        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(239, 68, 68, ${flashEffect / 20})`;
            ctx.fillRect(0,0,850,550); 
            flashEffect--;
        }
    }
    
    function processSystem() {
        let fF = parseInt(slFlowF.value); let cBa = parseInt(slBa.value);
        let fL = parseInt(slFlowL.value); let cSO4 = parseInt(slSO4.value);
        
        let totalFlow = fF + fL;
        // Saturation Index (Disederhanakan untuk visual)
        let siValue = totalFlow > 0 ? (((fF/totalFlow)*cBa) * ((fL/totalFlow)*cSO4)) / 5000000 : 0;
        
        // Spawn Ion (Berhenti spawn jika buntu total agar tidak nge-lag)
        if (totalBlockage < 100) {
            if (fF > 0 && Math.random() < (fF / 100)) {
                let type = Math.random() > 0.25 ? 'Ba' : 'Sr';
                particles.push(new Particle(type, 140 + (Math.random() - 0.5)*50, 50, cX - 25, mY, true));
            }
            if (fL > 0 && Math.random() < (fL / 100)) {
                particles.push(new Particle('SO4', 710 + (Math.random() - 0.5)*50, 50, cX + 25, mY, false));
            }
        }
        
        // Nukleasi di Persimpangan (Tumbukan Kiri & Kanan)
        let nProb = siValue > 1 ? Math.min(siValue * 0.15, 0.9) : 0;
        
        if (nProb > 0) {
            for(let i = 0; i < particles.length; i++) {
                let p1 = particles[i];
                if(!p1.active || p1.isStuck || p1.type === 'Scale' || p1.y < mY - 20) continue;
                
                for(let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if(!p2.active || p2.isStuck || p2.type === 'Scale' || p2.y < mY - 20) continue;
                    
                    if ((p1.isLeftFlow !== p2.isLeftFlow) && p1.type !== p2.type) {
                        // Jarak deteksi tabrakan
                        if(Math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2) < 20 && Math.random() < nProb) {
                            p1.active = false; p2.active = false;
                            particles.push(new Particle('Scale', (p1.x+p2.x)/2, (p1.y+p2.y)/2, 0, 0, false));
                        }
                    }
                }
            }
        }
        return { totalFlow, siValue };
    }
    
    function updateDasbor(flowData) {
        // Cari titik mampet tertinggi (Choke Point)
        let maxBlockVal = 0;
        chokeY = -1;
        
        for (let i = mY; i <= 550; i++) {
            let localBlockage = scaleArrL[i] + scaleArrR[i];
            if (localBlockage > maxBlockVal) {
                maxBlockVal = localBlockage;
            }
            // Tentukan titik Y di mana mampet pertama kali terjadi (dari atas)
            if (localBlockage >= pW - 2 && chokeY === -1) {
                chokeY = i;
            }
        }
        
        totalBlockage = (maxBlockVal / pW) * 100;
        if (totalBlockage > 100) totalBlockage = 100;

        // Fluida terhenti drastis jika tersumbat
        let radiusSisa = 1 - (totalBlockage/100);
        let flowEff = (radiusSisa * radiusSisa) * 100;
        if (totalBlockage >= 98) flowEff = 0;
        
        // Render Teks UI
        document.getElementById('valSI').innerText = flowData.siValue.toFixed(2);
        let lblSI = document.getElementById('lblSIStatus');
        if (flowData.siValue < 0.5) { lblSI.innerText = 'Undersaturated'; lblSI.style.color = '#10b981'; }
        else if (flowData.siValue < 1.5) { lblSI.innerText = 'Saturated (Waspada)'; lblSI.style.color = '#f59e0b'; }
        else { lblSI.innerText = 'Supersaturated (Bahaya)'; lblSI.style.color = '#ef4444'; }
        
        document.getElementById('valThick').innerText = maxBlockVal.toFixed(1) + ' mm';
        
        let elBlock = document.getElementById('valBlock');
        elBlock.innerText = totalBlockage.toFixed(0) + '%';
        elBlock.className = totalBlockage > 80 ? 'metric-value alert' : (totalBlockage > 30 ? 'metric-value' : 'metric-value safe');
        if (totalBlockage > 30 && totalBlockage <= 80) elBlock.style.color = '#f59e0b';
        
        let elProd = document.getElementById('valProdDrop');
        elProd.innerText = flowEff.toFixed(0) + '%';
        elProd.className = flowEff < 20 ? 'metric-value alert' : (flowEff < 80 ? 'metric-value' : 'metric-value safe');
        if (flowEff >= 20 && flowEff < 80) elProd.style.color = '#f59e0b';
    }
    
    function animate() {
        drawSystem();
        let data = processSystem();
        
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update(data.totalFlow);
                p.draw();
                if (p.y > canvas.height + 10 && !p.isStuck) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }
        
        updateDasbor(data);
        requestAnimationFrame(animate);
    }
    
    // Fungsi ACID WASH
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

components.html(html_app, height=750, scrolling=False)
