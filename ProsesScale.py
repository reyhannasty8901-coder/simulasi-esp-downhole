import streamlit as st
import streamlit.components.v1 as components

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="Simulator Scale Lapangan", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 0.5rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

# --- INJEKSI CORE SIMULATOR ---
html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Advanced Scale Crystallization & Remediation Simulator</title>
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        .main-container {
            width: 100%; max-width: 1400px; display: grid; grid-template-columns: 1fr 380px; gap: 15px;
        }
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; gap: 12px;
        }
        canvas { background: #0b0f19; border-radius: 8px; width: 100%; }
        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px;
        }
        .control-section {
            border: 1px solid #334155; padding: 10px; border-radius: 8px; background: #1e293b;
        }
        .control-title {
            font-size: 0.85rem; font-weight: bold; color: #94a3b8; margin-bottom: 8px; border-bottom: 1px solid #475569; padding-bottom: 4px;
        }
        .slider-group label { font-size: 0.8rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 4px;}
        input[type=range] { width: 100%; margin: 4px 0; accent-color: #3b82f6; }
        
        /* Dashboard Styling */
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }
        .metric-card {
            background: #0f172a; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #334155;
        }
        .metric-title { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.15rem; font-weight: bold; margin-top: 3px; }
        
        /* Action Buttons */
        .btn-prime { background: #0284c7; color: white; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 5px; transition: 0.2s; }
        .btn-prime:hover { background: #0369a1; }
        .btn-danger { background: #dc2626; color: white; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 5px; transition: 0.2s; }
        .btn-danger:hover { background: #b91c1c; }
        
        .alert { color: #ef4444; animation: pulse 1s infinite; }
        .safe { color: #10b981; }
        @keyframes pulse { 50% { opacity: 0.5; } }
        .footer-note { margin-top: 10px; font-size: 0.75rem; color: #64748b; text-align: center; max-width: 1100px; }
    </style>
</head>
<body>

    <h3 style="margin: 0 0 10px 0; font-weight: 600; color: #f1f5f9;">Simulasi Kinetika Deposition & Remediasi Kerak (Scale)</h3>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="380"></canvas>
            <canvas id="chartCanvas" width="850" height="130"></canvas>
        </div>
        
        <div class="control-panel">
            <div class="control-section">
                <div class="control-title">Kondisi Aliran & Prekursor</div>
                <div class="slider-group">
                    <label>Laju Air Formasi <span id="lblFlowF">50 bbl/d</span></label>
                    <input type="range" id="slFlowF" min="0" max="100" value="50">
                    <label>Konsentrasi Ba²⁺/Sr²⁺ <span id="lblBa">3500 ppm</span></label>
                    <input type="range" id="slBa" min="0" max="5000" value="3500" step="100">
                    <label>Laju Air Injeksi Laut <span id="lblFlowL">50 bbl/d</span></label>
                    <input type="range" id="slFlowL" min="0" max="100" value="50">
                    <label>Konsentrasi Sulfat (SO₄²⁻) <span id="lblSO4">24000 ppm</span></label>
                    <input type="range" id="slSO4" min="0" max="30000" value="24000" step="500">
                </div>
            </div>
            
            <div class="control-section" style="background: #0f172a; border-color: #334155;">
                <div class="control-title" style="color: #f8fafc; text-align: center;">DASHBOARD PARAMETER SUMUR</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Waktu Operasi</div>
                        <div class="metric-value" id="mTime" style="color: #67e8f9;">0.0 Hari</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Saturation Index</div>
                        <div class="metric-value" id="mSI">0.0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Max Tebal Kerak</div>
                        <div class="metric-value" id="mThick" style="color: var(--scale-color);">0.0 mm</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Penyumbatan</div>
                        <div class="metric-value" id="mBlock">0%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Pressure Drop</div>
                        <div class="metric-value" id="mDp">15.0 psi</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Volume Kerak</div>
                        <div class="metric-value" id="mVol" style="color: #e2e8f0;">0.00 m³</div>
                    </div>
                </div>
                
                <div style="margin-top: 8px; padding: 8px; background: #1e293b; border-radius: 6px; text-align: center; border: 1px solid #0284c7;">
                    <div class="metric-title" style="color: #38bdf8;">Laju Alir Produksi Minyak</div>
                    <div class="metric-value" id="mProd" style="color: #10b981; font-size: 1.3rem;">100%</div>
                </div>
            </div>
            
            <div class="control-section">
                <div class="control-title">Intervensi Lapangan / Remediasi</div>
                <button id="btnPigging" class="btn-prime">⚙️ PIGGING & CHEMICAL REMOVAL</button>
                <button id="btnReset" class="btn-danger">🔄 RESET SIMULASI</button>
            </div>
        </div>
    </div>
    
    <div class="footer-note">
        <b>Mekanisme Dinamis Lapangan:</b> Aliran produksi minyak melandai secara non-linear mengikuti penyempitan diameter pipa berdasarkan hukum *Hagen-Poiseuille* ($Q \propto r^4$). Penyempitan pipa memicu peningkatan tahanan aliran (*Pressure Drop / $\Delta P$*). Proses *Pigging* mekanis dan *Chemical Wash* (penyuntikan asam/chelating agent) mengembalikan geometri internal pipa ke kondisi awal secara instan.
    </div>

<script>
    const canvas = document.getElementById('simCanvas'); const ctx = canvas.getContext('2d');
    const chartCanvas = document.getElementById('chartCanvas'); const cCtx = chartCanvas.getContext('2d');
    
    // Sliders & Buttons
    const slFlowF = document.getElementById('slFlowF'); const slBa = document.getElementById('slBa');
    const slFlowL = document.getElementById('slFlowL'); const slSO4 = document.getElementById('slSO4');
    const btnPigging = document.getElementById('btnPigging'); const btnReset = document.getElementById('btnReset');
    
    // Data Geometri & Simulasi
    const cX = 425, mY = 160, pW = 80;
    let particles = [];
    let scaleArray = new Array(850).fill(0); // Profile ketebalan sepanjang pipa bawah
    let simTicks = 0;
    let historyTime = [], historyThick = [];
    let showPigEffect = 0; // Timer untuk efek kilatan pigging
    
    class Particle {
        constructor(type, x, y, tx, ty, isLeft) {
            this.type = type; this.x = x; this.y = y; this.tx = tx; this.ty = ty; this.isLeft = isLeft;
            let angle = Math.atan2(ty - y, tx - x);
            let speed = 2 + Math.random() * 2;
            this.vx = Math.cos(angle) * speed; this.vy = Math.sin(angle) * speed;
            this.size = type === 'Scale' ? 2 : 3;
            this.active = true; this.stuck = false;
        }
        update(totalFlow, siValue) {
            if (this.stuck) return;
            
            if (this.y < mY) {
                this.x += this.vx; this.y += this.vy;
            } else {
                // Aliran pipa produksi bawah
                let avgBlock = (scaleArray.reduce((a,b)=>a+b,0) / 850) / (pW/2);
                let speedMultiplier = 1 + (avgBlock * 2); // Efek venturi / penyempitan kecepatan meningkat
                this.vy = (totalFlow * 0.08) * speedMultiplier + Math.random() * 0.5;
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 2; // Turbulensi
                
                let idxX = Math.floor(this.x);
                let currentScaleL = scaleArray[idxX] || 0;
                let currentScaleR = scaleArray[idxX] || 0;
                let wallL = cX - pW/2 + currentScaleL;
                let wallR = cX + pW/2 - currentScaleR;
                
                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // Pertumbuhan Kristal saat mengalir bebas di kondisi Supersaturasi
                if (this.type === 'Scale' && siValue > 1 && this.size < 8) {
                    this.size += 0.03 * siValue;
                }
                
                // Deposisi Kerak pada dinding pipa
                if (this.type === 'Scale') {
                    if (this.x <= wallL + 4 || this.x >= wallR - 4) {
                        if (Math.random() < 0.2) {
                            this.stuck = true;
                            // Tambah ketebalan lokal berbentuk persebaran gauss kecil
                            for(let i = Math.max(0, idxX-15); i < Math.min(850, idxX+15); i++) {
                                let d = Math.abs(idxX - i);
                                scaleArray[i] += Math.max(0, (15 - d) * 0.03);
                                if(scaleArray[i] > pW/2 - 3) scaleArray[i] = pW/2 - 3; // Batas buntu total
                            }
                        }
                    }
                }
            }
        }
        draw() {
            ctx.beginPath();
            if (this.type === 'Scale') {
                ctx.fillStyle = 'var(--scale-color)';
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
            } else {
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
                ctx.fillStyle = this.type === 'Ba' ? 'var(--ba-color)' : (this.type === 'Sr' ? 'var(--sr-color)' : 'var(--so4-color)');
            }
            ctx.fill();
        }
    }

    function drawSystemPipes() {
        ctx.fillStyle = '#0b0f19'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 6; ctx.lineJoin = 'round';
        
        // Render Struktur Kisi Jalur Pipa Y
        ctx.beginPath();
        ctx.moveTo(60, 40); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, 380);
        ctx.moveTo(790, 40); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, 380);
        ctx.moveTo(180, 40); ctx.lineTo(cX, mY - 40); ctx.lineTo(670, 40);
        ctx.stroke();
        
        // Render Massa Kerak Melekat (Scale Layer)
        ctx.fillStyle = '#b45309';
        ctx.beginPath(); ctx.moveTo(cX - pW/2, mY);
        for(let y=mY; y<=380; y++) ctx.lineTo(cX - pW/2 + scaleArray[y], y);
        ctx.lineTo(cX - pW/2, 380); ctx.fill();
        
        ctx.beginPath(); ctx.moveTo(cX + pW/2, mY);
        for(let y=mY; y<=380; y++) ctx.lineTo(cX + pW/2 - scaleArray[y], y);
        ctx.lineTo(cX + pW/2, 380); ctx.fill();
        
        // Garis batas internal kerak dinamis
        ctx.strokeStyle = 'var(--scale-color)'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(cX - pW/2 + scaleArray[mY], mY);
        for(let y=mY; y<=380; y++) ctx.lineTo(cX - pW/2 + scaleArray[y], y);
        ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cX + pW/2 - scaleArray[mY], mY);
        for(let y=mY; y<=380; y++) ctx.lineTo(cX + pW/2 - scaleArray[y], y);
        ctx.stroke();

        // Efek Kilatan Visual saat Pigging Aktif
        if(showPigEffect > 0) {
            ctx.fillStyle = `rgba(14, 165, 233, ${showPigEffect / 20})`;
            ctx.fillRect(cX - pW/2, mY, pW, 380-mY);
            showPigEffect--;
        }
    }

    function runKineticsEngine() {
        let fF = parseInt(slFlowF.value); let cBa = parseInt(slBa.value);
        let fL = parseInt(slFlowL.value); let cSO4 = parseInt(slSO4.value);
        let totalFlow = fF + fL;
        
        // Kalkulasi Saturation Index & Waktu Eksponensial
        let siValue = totalFlow > 0 ? ((fF / totalFlow) * cBa * (fL / totalFlow) * cSO4) / 4500000 : 0;
        simTicks += (totalFlow > 0) ? 0.05 : 0;
        let simDays = simTicks;

        // Injeksi Partikel Baru dari Hulu Sumur
        if (fF > 0 && Math.random() < (fF/100)) {
            let type = Math.random() > 0.25 ? 'Ba' : 'Sr';
            particles.push(new Particle(type, 120 + (Math.random()-0.5)*50, 40, cX - 20, mY, true));
        }
        if (fL > 0 && Math.random() < (fL/100)) {
            particles.push(new Particle('SO4', 730 + (Math.random()-0.5)*50, 40, cX + 20, mY, false));
        }

        // Deteksi Tumbukan Ion -> Pembentukan Inti Kristal (Nukleasi)
        let probNuc = siValue > 1 ? Math.min(siValue * 0.12, 0.85) : 0;
        if (probNuc > 0) {
            for(let i=0; i<particles.length; i++) {
                let p1 = particles[i];
                if (!p1.active || p1.stuck || p1.type === 'Scale' || p1.y < mY - 15) continue;
                for(let j=i+1; j<particles.length; j++) {
                    let p2 = particles[j];
                    if (!p2.active || p2.stuck || p2.type === 'Scale') continue;
                    if (p1.isLeft !== p2.isLeft && p1.type !== p2.type) {
                        if (Math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2) < 14 && Math.random() < probNuc) {
                            p1.active = false; p2.active = false;
                            particles.push(new Particle('Scale', (p1.x+p2.x)/2, (p1.y+p2.y)/2, 0, 0, false));
                            break;
                        }
                    }
                }
            }
        }
        return { totalFlow, siValue, simDays };
    }

    function drawHistoryChart() {
        cCtx.fillStyle = '#0b0f19'; cCtx.fillRect(0,0, chartCanvas.width, chartCanvas.height);
        cCtx.strokeStyle = '#1e293b'; cCtx.lineWidth = 1;
        cCtx.beginPath(); cCtx.moveTo(0, 65); cCtx.lineTo(850, 65); cCtx.stroke(); // Garis Tengah
        
        cCtx.fillStyle = '#64748b'; cCtx.font = '10px Arial';
        cCtx.fillText('Tren Ketebalan Kerak Maksimum vs Waktu Operasi', 10, 15);

        if(historyThick.length < 2) return;
        cCtx.strokeStyle = 'var(--scale-color)'; cCtx.lineWidth = 2.5;
        cCtx.beginPath();
        for(let i=0; i<historyThick.length; i++) {
            let xPos = (i / 900) * 850;
            let yPos = 120 - (historyThick[i] / (pW/2)) * 100;
            if(i===0) cCtx.moveTo(xPos, yPos); else cCtx.lineTo(xPos, yPos);
        }
        cCtx.stroke();
    }

    function updateDashboardMetrics(data) {
        document.getElementById('lblFlowF').innerText = slFlowF.value + ' bbl/d';
        document.getElementById('lblBa').innerText = slBa.value + ' ppm';
        document.getElementById('lblFlowL').innerText = slFlowL.value + ' bbl/d';
        document.getElementById('lblSO4').innerText = slSO4.value + ' ppm';
        
        document.getElementById('mTime').innerText = data.simDays.toFixed(1) + ' Hari';
        
        let mSI = document.getElementById('mSI'); mSI.innerText = data.siValue.toFixed(2);
        if(data.siValue < 0.5) { mSI.className = 'metric-value safe'; }
        else if(data.siValue < 1.5) { mSI.className = 'metric-value'; mSI.style.color='#f59e0b'; }
        else { mSI.className = 'metric-value alert'; }

        // Hitung Parameter Lapangan Riil
        let maxThick = Math.max(...scaleArray);
        let blockPercent = (maxThick / (pW / 2)) * 100;
        if(blockPercent > 100) blockPercent = 100;
        
        // Penurunan produksi mengikuti r^4 (Hagen-Poiseuille)
        let rRatio = 1 - (blockPercent / 100);
        let prodEfficiency = Math.pow(rRatio, 4) * 100;
        let prodLoss = 100 - prodEfficiency;
        
        // Tahanan Aliran / Pressure Drop (Meningkat eksponensial saat menyempit)
        let pressureDrop = 15.0 + (blockPercent / (100.1 - blockPercent)) * 250;
        
        // Estimasi akumulasi volume kerak terendah
        let scaleVol = (scaleArray.reduce((a,b)=>a+b, 0) * 0.0001);

        document.getElementById('mThick').innerText = (maxThick * 0.5).toFixed(1) + ' mm';
        
        let mBlock = document.getElementById('mBlock'); mBlock.innerText = blockPercent.toFixed(0) + '%';
        mBlock.className = blockPercent > 60 ? 'metric-value alert' : 'metric-value';
        
        document.getElementById('mDp').innerText = pressureDrop.toFixed(0) + ' psi';
        document.getElementById('mVol').innerText = scaleVol.toFixed(3) + ' m³';
        
        let mProd = document.getElementById('mProd'); mProd.innerText = prodEfficiency.toFixed(0) + '%';
        mProd.className = prodEfficiency < 40 ? 'metric-value alert' : 'metric-value safe';

        // Rekam Histori Grafik
        if(Math.random() < 0.2) {
            historyThick.push(maxThick);
            if(historyThick.length > 900) historyThick.shift();
        }
    }

    function loop() {
        drawSystemPipes();
        let data = runKineticsEngine();
        
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update(data.totalFlow, data.siValue);
                p.draw();
                if(p.y > 390 && !p.stuck) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }
        
        updateDashboardMetrics(data);
        drawHistoryChart();
        requestAnimationFrame(loop);
    }

    // LISTENER AKSI TOMBOL REMEDIASI
    btnPigging.addEventListener('click', () => {
        // Aksi Pigging menyapu/menghancurkan lapisan kerak kembali ke nol
        scaleArray.fill(0);
        showPigEffect = 20; // Triger efek animasi pencucian
    });

    btnReset.addEventListener('click', () => {
        scaleArray.fill(0); particles = []; simTicks = 0; historyThick = [];
    });

    loop();
</script>
</body>
</html>
"""

# Render ke Frame Utama Streamlit
components.html(html_app, height=600, scrolling=False)
