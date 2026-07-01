import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN HALAMAN STREAMLIT ---
st.set_page_config(page_title="Simulasi EMSP", layout="wide", initial_sidebar_state="collapsed")

# Menyembunyikan elemen bawaan Streamlit agar terlihat seperti web mandiri penuh
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

# --- KODE INJEKSI HTML5, CSS3, & JAVASCRIPT ---
# Seluruh logika fisika, slider, UI, dan grafik real-time dibangun di sini
html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>EMSP Simulation</title>
    <style>
        :root {
            --bg-color: #0e1117;
            --panel-bg: #1e212b;
            --text-main: #fafafa;
            --accent-cyan: #00f2fe;
            --calcite-color: #8892b0;
            --aragonite-color: #ff4b4b;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 10px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h2 { margin-top: 5px; margin-bottom: 15px; font-weight: 600; letter-spacing: 1px; }
        
        /* Container Utama */
        .main-container {
            width: 100%;
            max-width: 1200px;
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
        }
        
        /* Kanvas Utama */
        .canvas-section {
            background: var(--panel-bg);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        canvas {
            background: #12141a;
            border-radius: 8px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
            width: 100%;
            max-height: 350px;
        }
        
        /* Panel Kontrol & Dashboard */
        .control-panel {
            background: var(--panel-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        /* Toggle Switch */
        .toggle-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #262a35;
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid #3a3f50;
        }
        .switch { position: relative; display: inline-block; width: 50px; height: 26px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider-toggle {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #555; transition: .4s; border-radius: 34px;
        }
        .slider-toggle:before {
            position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px;
            background-color: white; transition: .4s; border-radius: 50%;
        }
        input:checked + .slider-toggle { background-color: var(--accent-cyan); box-shadow: 0 0 10px var(--accent-cyan); }
        input:checked + .slider-toggle:before { transform: translateX(24px); }
        
        /* Sliders */
        .slider-group { display: flex; flex-direction: column; gap: 5px; }
        .slider-group label { font-size: 0.85rem; color: #a1a1aa; display: flex; justify-content: space-between; }
        input[type=range] {
            -webkit-appearance: none; width: 100%; background: transparent; margin: 5px 0;
        }
        input[type=range]::-webkit-slider-runnable-track {
            width: 100%; height: 6px; background: #3f3f46; border-radius: 3px;
        }
        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%;
            background: var(--text-main); cursor: pointer; margin-top: -5px;
        }
        
        /* Parameter Real-Time (Progress Bars) */
        .param-box { background: #262a35; padding: 15px; border-radius: 8px; }
        .param-title { font-size: 0.9rem; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #3f3f46; padding-bottom: 5px; }
        .progress-row { margin-bottom: 8px; }
        .progress-label { font-size: 0.75rem; display: flex; justify-content: space-between; margin-bottom: 3px; }
        .progress-bar-bg { width: 100%; height: 8px; background: #18181b; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: #4caf50; width: 50%; transition: width 0.5s ease, background 0.5s ease; }
        
        /* Morfologi Box */
        .morph-box {
            text-align: center; padding: 10px; margin-top: 10px; border-radius: 8px;
            border: 2px dashed #555; transition: all 0.5s;
        }
        .morph-title { font-size: 0.8rem; color: #a1a1aa; }
        .morph-value { font-size: 1.2rem; font-weight: bold; margin-top: 5px; }
        .morph-calcite { color: var(--calcite-color); border-color: var(--calcite-color); }
        .morph-aragonite { color: var(--aragonite-color); border-color: var(--aragonite-color); }
        
        /* Legenda */
        .legend { display: flex; gap: 15px; margin-top: 10px; font-size: 0.8rem; }
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 10px; height: 10px; border-radius: 50%; }
        
        /* Grafik Mini */
        .chart-container { margin-top: 15px; height: 100px; width: 100%; background: #12141a; border-radius: 8px; }
        
        /* Footer Edukasi */
        .footer-note {
            margin-top: 20px; font-size: 0.75rem; color: #71717a; text-align: center; max-width: 900px; line-height: 1.4;
        }
    </style>
</head>
<body>

    <h2>Simulasi Electromagnetic Scale Preventer</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="300"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:#3b82f6;"></div> Ion Ca²⁺</div>
                <div class="legend-item"><div class="dot" style="background:#10b981;"></div> Ion CO₃²⁻</div>
                <div class="legend-item"><div class="dot" style="background:var(--calcite-color); border-radius:0;"></div> Scale Calcite</div>
                <div class="legend-item"><div class="dot" style="background:var(--aragonite-color); border-radius:50%;"></div> Aragonite Suspensi</div>
            </div>
            
            <div class="chart-container">
                <canvas id="chartCanvas" width="850" height="100"></canvas>
            </div>
        </div>
        
        <div class="control-panel">
            <div class="toggle-container">
                <span style="font-weight:bold; font-size:0.9rem;">Medan EMSP</span>
                <label class="switch">
                    <input type="checkbox" id="emspToggle">
                    <span class="slider-toggle"></span>
                </label>
            </div>
            
            <div class="slider-group">
                <label>Mineral Saturation <span id="valSat">50%</span></label>
                <input type="range" id="satSlider" min="10" max="100" value="50">
                
                <label>Flow Velocity <span id="valFlow">Normal</span></label>
                <input type="range" id="flowSlider" min="1" max="5" value="2.5" step="0.1">
            </div>
            
            <div class="param-box">
                <div class="param-title">Real-Time Parameters</div>
                <div class="progress-row">
                    <div class="progress-label"><span>Nucleation Rate</span><span id="txtNuc">Rendah</span></div>
                    <div class="progress-bar-bg"><div id="barNuc" class="progress-fill"></div></div>
                </div>
                <div class="progress-row">
                    <div class="progress-label"><span>Crystal Growth</span><span id="txtGro">Tinggi</span></div>
                    <div class="progress-bar-bg"><div id="barGro" class="progress-fill"></div></div>
                </div>
                <div class="progress-row">
                    <div class="progress-label"><span>Adhesion (Risk)</span><span id="txtAdh">Tinggi</span></div>
                    <div class="progress-bar-bg"><div id="barAdh" class="progress-fill"></div></div>
                </div>
            </div>
            
            <div id="morphBox" class="morph-box morph-calcite">
                <div class="morph-title">Morfologi Dominan</div>
                <div class="morph-value" id="morphValue">Calcite (Melekat)</div>
            </div>
            
            <button id="btnReset" style="background:#3f3f46; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer; margin-top:5px;">Reset Pipa</button>
        </div>
    </div>
    
    <div class="footer-note">
        <b>Catatan Ilmiah:</b> Simulasi ini merupakan ilustrasi konseptual berdasarkan mekanisme yang diusulkan dalam literatur. Electromagnetic Scale Preventer tidak menghilangkan ion penyusun kerak, melainkan memanipulasi medan elektromagnetik untuk mempercepat nukleasi dini. Hasilnya adalah formasi kristal Aragonite (bukan Calcite) yang berukuran mikroskopis, stabil melayang dalam fluida (suspended solids), dan kehilangan daya adhesi kimia untuk menempel pada dinding pipa baja.
    </div>

<script>
    // Konfigurasi Canvas
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const chartCanvas = document.getElementById('chartCanvas');
    const cCtx = chartCanvas.getContext('2d');
    
    // Elemen UI
    const toggle = document.getElementById('emspToggle');
    const satSlider = document.getElementById('satSlider');
    const flowSlider = document.getElementById('flowSlider');
    
    // Dimensi Pipa
    const pipeY = 50;
    const pipeHeight = 200;
    const pipeBottom = pipeY + pipeHeight;
    const coilX = 350;
    const coilWidth = 150;
    
    // State Variabel
    let isEMSP = false;
    let particles = [];
    let crystals = [];
    let scaleThickness = new Array(850).fill(0);
    
    // Chart Data
    let time = 0;
    let chartDataScale = [];
    let chartDataCrystals = [];
    
    // Kelas Partikel Ion
    class Ion {
        constructor() {
            this.x = Math.random() * 50; // Muncul di kiri
            this.y = pipeY + 10 + Math.random() * (pipeHeight - 20);
            this.type = Math.random() > 0.5 ? 'Ca' : 'CO3';
            this.vx = parseFloat(flowSlider.value) + (Math.random() - 0.5);
            this.vy = (Math.random() - 0.5) * 1.5;
            this.active = true;
        }
        update() {
            this.x += this.vx + parseFloat(flowSlider.value)*0.5;
            this.y += this.vy;
            // Brownian motion ringan
            this.vy += (Math.random() - 0.5) * 0.5;
            // Batas pipa (pantulan)
            let currentBottom = pipeBottom - scaleThickness[Math.floor(this.x) || 0];
            if(this.y < pipeY + 5) this.vy *= -1;
            if(this.y > currentBottom - 5) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, 2.5, 0, Math.PI*2);
            ctx.fillStyle = this.type === 'Ca' ? '#3b82f6' : '#10b981';
            ctx.fill();
        }
    }
    
    // Kelas Kristal
    class Crystal {
        constructor(x, y, isAragonite) {
            this.x = x;
            this.y = y;
            this.isAragonite = isAragonite;
            this.size = isAragonite ? 2 : 4; // Aragonite kecil, Calcite mulai agak besar
            this.vx = parseFloat(flowSlider.value) * (isAragonite ? 1.0 : 0.6); // Aragonite ringan hanyut, Calcite lambat
            this.vy = isAragonite ? (Math.random()-0.5) : 0.5; // Calcite cenderung tenggelam
            this.stuck = false;
        }
        update() {
            if (this.stuck) return;
            
            this.x += this.vx;
            this.y += this.vy;
            
            // Pertumbuhan Kristal
            if (!this.isAragonite && this.size < 12) {
                this.size += 0.05; // Calcite tumbuh membesar
                this.vy += 0.02;   // Semakin berat, makin turun
            }
            
            let floor = pipeBottom - (scaleThickness[Math.floor(this.x)] || 0);
            
            // Logika Adhesi
            if (!this.isAragonite && this.y >= floor - this.size) {
                this.stuck = true;
                this.y = floor - this.size/2;
                // Menambah ketebalan scale
                let impactX = Math.floor(this.x);
                for(let i = Math.max(0, impactX-10); i < Math.min(850, impactX+10); i++) {
                    let dist = Math.abs(impactX - i);
                    scaleThickness[i] += Math.max(0, (10 - dist) * 0.1);
                }
            } else if (this.isAragonite) {
                // Aragonite memantul dari dasar/scale
                if(this.y >= floor - 5) this.vy *= -1;
                if(this.y <= pipeY + 5) this.vy *= -1;
            }
        }
        draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            if (this.isAragonite) {
                // Aragonite (Jarum/Lonjong merah muda)
                ctx.fillStyle = 'rgba(255, 75, 75, 0.8)';
                ctx.beginPath();
                ctx.ellipse(0, 0, this.size+2, this.size, 0, 0, Math.PI*2);
                ctx.fill();
            } else {
                // Calcite (Poligon abu-abu gelap)
                ctx.fillStyle = this.stuck ? '#52525b' : 'rgba(136, 146, 176, 0.9)';
                ctx.beginPath();
                ctx.moveTo(0, -this.size);
                ctx.lineTo(this.size, 0);
                ctx.lineTo(0, this.size);
                ctx.lineTo(-this.size, 0);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();
        }
    }
    
    function drawBackground() {
        ctx.fillStyle = '#12141a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Pipa
        ctx.strokeStyle = '#4b5563';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(0, pipeY); ctx.lineTo(850, pipeY);
        ctx.moveTo(0, pipeBottom); ctx.lineTo(850, pipeBottom);
        ctx.stroke();
        
        // Panah Aliran
        ctx.fillStyle = 'rgba(255,255,255,0.05)';
        ctx.font = '60px Arial';
        ctx.fillText('»', 100, 160);
        ctx.fillText('»', 700, 160);
        
        // Kumparan (Coil) EMSP
        ctx.save();
        for(let i=0; i<=coilWidth; i+=10) {
            ctx.beginPath();
            ctx.moveTo(coilX + i, pipeY - 10);
            ctx.lineTo(coilX + i, pipeBottom + 10);
            
            if (isEMSP) {
                ctx.strokeStyle = 'rgba(0, 242, 254, 0.7)';
                ctx.lineWidth = 2;
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#00f2fe';
            } else {
                ctx.strokeStyle = '#3f3f46';
                ctx.lineWidth = 2;
                ctx.shadowBlur = 0;
            }
            ctx.stroke();
        }
        
        // Efek Gelombang Elektromagnetik Aktif
        if(isEMSP) {
            let waveOffset = (Date.now() / 200) % (Math.PI * 2);
            ctx.beginPath();
            for(let i=0; i<coilWidth; i+=5) {
                let yWave = Math.sin(i * 0.1 - waveOffset) * 20;
                if(i===0) ctx.moveTo(coilX + i, 150 + yWave);
                else ctx.lineTo(coilX + i, 150 + yWave);
            }
            ctx.strokeStyle = '#00f2fe';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
        ctx.restore();
        
        // Lapisan Scale (Kerak)
        ctx.fillStyle = '#3f3f46';
        ctx.beginPath();
        ctx.moveTo(0, pipeBottom);
        for(let i=0; i<850; i++) {
            ctx.lineTo(i, pipeBottom - scaleThickness[i]);
        }
        ctx.lineTo(850, pipeBottom);
        ctx.closePath();
        ctx.fill();
        
        // Garis batas kerak
        ctx.strokeStyle = '#71717a';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    
    function updateDashboard() {
        // Update Labels
        document.getElementById('valSat').innerText = satSlider.value + '%';
        document.getElementById('valFlow').innerText = flowSlider.value + 'x';
        
        const morphBox = document.getElementById('morphBox');
        const morphVal = document.getElementById('morphValue');
        
        const bNuc = document.getElementById('barNuc');
        const bGro = document.getElementById('barGro');
        const bAdh = document.getElementById('barAdh');
        
        if(isEMSP) {
            morphBox.className = 'morph-box morph-aragonite';
            morphVal.innerText = 'Aragonite (Hanyut)';
            
            bNuc.style.width = '90%'; bNuc.style.background = '#4caf50';
            bGro.style.width = '15%'; bGro.style.background = '#4caf50';
            bAdh.style.width = '5%';  bAdh.style.background = '#4caf50';
            
            document.getElementById('txtNuc').innerText = 'Sangat Tinggi';
            document.getElementById('txtGro').innerText = 'Rendah (Terbatas)';
            document.getElementById('txtAdh').innerText = 'Nihil / Aman';
        } else {
            morphBox.className = 'morph-box morph-calcite';
            morphVal.innerText = 'Calcite (Melekat)';
            
            bNuc.style.width = '30%'; bNuc.style.background = '#f44336';
            bGro.style.width = '85%'; bGro.style.background = '#f44336';
            bAdh.style.width = '95%'; bAdh.style.background = '#f44336';
            
            document.getElementById('txtNuc').innerText = 'Rendah (Spontan)';
            document.getElementById('txtGro').innerText = 'Tinggi (Agresif)';
            document.getElementById('txtAdh').innerText = 'Kritis (Scaling)';
        }
    }
    
    function drawCharts() {
        cCtx.fillStyle = '#12141a';
        cCtx.fillRect(0,0, chartCanvas.width, chartCanvas.height);
        
        // Grid
        cCtx.strokeStyle = '#262a35';
        cCtx.beginPath();
        cCtx.moveTo(0, 50); cCtx.lineTo(850, 50);
        cCtx.stroke();
        
        // Label
        cCtx.fillStyle = '#a1a1aa';
        cCtx.font = '10px Arial';
        cCtx.fillText('Deposit Kerak', 10, 15);
        cCtx.fillText('Populasi Aragonite', 10, 85);
        
        // Data maintenance
        let totalScale = scaleThickness.reduce((a,b)=>a+b, 0);
        let suspended = crystals.filter(c => c.isAragonite && c.x < 850).length;
        
        chartDataScale.push(totalScale / 15); 
        chartDataCrystals.push(suspended);
        if(chartDataScale.length > 850) {
            chartDataScale.shift();
            chartDataCrystals.shift();
        }
        
        // Draw Scale Line
        cCtx.strokeStyle = 'var(--calcite-color)';
        cCtx.lineWidth = 2;
        cCtx.beginPath();
        for(let i=0; i<chartDataScale.length; i++) {
            cCtx.lineTo(i, 50 - Math.min(50, chartDataScale[i]));
        }
        cCtx.stroke();
        
        // Draw Aragonite Line
        cCtx.strokeStyle = 'var(--aragonite-color)';
        cCtx.beginPath();
        for(let i=0; i<chartDataCrystals.length; i++) {
            cCtx.lineTo(i, 100 - Math.min(50, chartDataCrystals[i]));
        }
        cCtx.stroke();
    }
    
    function animate() {
        drawBackground();
        
        // Spawn Ion berdasarkan saturasi
        let spawnRate = parseInt(satSlider.value) / 100;
        if(Math.random() < spawnRate && particles.length < 150) {
            particles.push(new Ion());
        }
        
        // Update Ion & Deteksi Tabrakan (Nukleasi)
        for(let i = particles.length - 1; i >= 0; i--) {
            let p1 = particles[i];
            p1.update();
            p1.draw();
            
            // Hapus jika keluar batas
            if(p1.x > 850) {
                particles.splice(i, 1);
                continue;
            }
            
            // Deteksi tabrakan Ca dan CO3
            if(p1.active) {
                for(let j = i - 1; j >= 0; j--) {
                    let p2 = particles[j];
                    if(p2.active && p1.type !== p2.type) {
                        let dx = p1.x - p2.x;
                        let dy = p1.y - p2.y;
                        let dist = Math.sqrt(dx*dx + dy*dy);
                        
                        // Jarak tabrakan
                        if(dist < 10) {
                            // Probabilitas nukleasi
                            // Jika masuk zona coil (350-500) dan EMSP ON, probabilitas 95%
                            // Jika EMSP OFF, probabilitas 10% (lambat)
                            let inCoil = (p1.x > coilX && p1.x < coilX + coilWidth);
                            let prob = (isEMSP && inCoil) ? 0.95 : 0.05;
                            
                            if(Math.random() < prob) {
                                p1.active = false;
                                p2.active = false;
                                // Buat kristal. Jika di zona coil dan EMSP ON -> Aragonite
                                let makeAragonite = (isEMSP && inCoil);
                                crystals.push(new Crystal(p1.x, p1.y, makeAragonite));
                                break;
                            }
                        }
                    }
                }
            }
        }
        
        // Bersihkan ion yang tidak aktif
        particles = particles.filter(p => p.active);
        
        // Update Kristal
        for(let i = crystals.length - 1; i >= 0; i--) {
            let c = crystals[i];
            c.update();
            c.draw();
            if(c.x > 850 && !c.stuck) {
                crystals.splice(i, 1);
            }
        }
        
        updateDashboard();
        drawCharts();
        
        requestAnimationFrame(animate);
    }
    
    // Event Listeners
    toggle.addEventListener('change', (e) => {
        isEMSP = e.target.checked;
    });
    
    document.getElementById('btnReset').addEventListener('click', () => {
        scaleThickness = new Array(850).fill(0);
        particles = [];
        crystals = [];
        chartDataScale = [];
        chartDataCrystals = [];
    });
    
    // Mulai Animasi
    animate();
</script>
</body>
</html>
"""

# Menyuntikkan aplikasi HTML ke dalam Streamlit tanpa margin/padding berlebih
components.html(html_app, height=850, scrolling=False)
