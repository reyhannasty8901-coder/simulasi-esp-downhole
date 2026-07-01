import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulasi EMSP Lanjut", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>EMSP Advanced Simulation</title>
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
            background-color: var(--bg-color); color: var(--text-main);
            font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        h2 { margin: 0 0 10px 0; font-weight: 600; text-align: center; }
        
        .main-container {
            width: 100%; max-width: 1400px; display: grid; grid-template-columns: 1fr 350px; gap: 15px;
        }
        
        .canvas-section {
            background: var(--panel-bg); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 10px;
        }
        canvas {
            background: #12141a; border-radius: 8px; width: 100%;
        }
        
        .control-panel {
            background: var(--panel-bg); border-radius: 12px; padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 15px;
        }
        
        .slider-group label { font-size: 0.85rem; color: #a1a1aa; display: flex; justify-content: space-between; }
        input[type=range] { width: 100%; margin: 8px 0; }
        
        .dashboard-box { background: #262a35; padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent-cyan); }
        .dash-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9rem; }
        .dash-val { font-weight: bold; }
        
        .legend { display: flex; justify-content: center; gap: 15px; font-size: 0.8rem; padding: 10px; background: #262a35; border-radius: 8px;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        
        .footer-note { margin-top: 15px; font-size: 0.75rem; color: #71717a; text-align: center; line-height: 1.4; }
    </style>
</head>
<body>

    <h2>Analisis Komparatif: Pembentukan Kerak & EMSP</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="900" height="420"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:#3b82f6;"></div> Ion Ca²⁺</div>
                <div class="legend-item"><div class="dot" style="background:#10b981;"></div> Ion CO₃²⁻</div>
                <div class="legend-item"><div class="dot" style="background:var(--calcite-color); border-radius:2px;"></div> Calcite (Kerak Melekat)</div>
                <div class="legend-item"><div class="dot" style="background:var(--aragonite-color); border-radius:50%;"></div> Aragonite (Tersuspensi)</div>
            </div>
            
            <canvas id="chartCanvas" width="900" height="150"></canvas>
        </div>
        
        <div class="control-panel">
            <h4 style="margin:0; border-bottom:1px solid #444; padding-bottom:10px;">Parameter Sistem</h4>
            
            <div class="slider-group">
                <label>Mineral Saturation <span id="valSat">50%</span></label>
                <input type="range" id="satSlider" min="10" max="100" value="50">
                
                <label>Flow Velocity <span id="valFlow">2.5 m/s</span></label>
                <input type="range" id="flowSlider" min="1" max="5" value="2.5" step="0.1">
            </div>
            
            <div class="dashboard-box">
                <div class="dash-row"><span>Supersaturation:</span> <span class="dash-val" id="lblSuper">Medium</span></div>
                <div class="dash-row"><span>Scale Risk:</span> <span class="dash-val" id="lblRisk" style="color:#ff4b4b;">Kritis</span></div>
            </div>
            
            <div class="dashboard-box" style="border-left-color: #8892b0;">
                <h5 style="margin:0 0 10px 0; color:#a1a1aa;">Sistem Konvensional (OFF)</h5>
                <div class="dash-row"><span>Morfologi:</span> <span class="dash-val">Calcite</span></div>
                <div class="dash-row"><span>Deposit:</span> <span class="dash-val" id="valDepOff">0 mm</span></div>
            </div>
            
            <div class="dashboard-box" style="border-left-color: var(--accent-cyan);">
                <h5 style="margin:0 0 10px 0; color:#a1a1aa;">Sistem EMSP (ON)</h5>
                <div class="dash-row"><span>Morfologi:</span> <span class="dash-val">Aragonite</span></div>
                <div class="dash-row"><span>Deposit:</span> <span class="dash-val" id="valDepOn">0 mm</span></div>
            </div>
            
            <button id="btnReset" style="background:#3f3f46; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">Reset Pipa & Grafik</button>
        </div>
    </div>
    
    <div class="footer-note">
        <b>Catatan Ilmiah:</b> Simulasi ini membandingkan mekanisme kristalisasi secara konseptual. Pada sistem tanpa alat (Atas), tabrakan ion di kondisi supersaturasi memicu pembentukan Calcite yang agresif tumbuh dan melekat di dinding pipa. Saat EMSP aktif (Bawah), medan elektromagnetik menginduksi laju nukleasi masif. Ion yang telah melewati medan elektromagnetik secara eksklusif dipaksa membentuk kristal Aragonite mikroskopis yang kehilangan daya adhesi dan tetap berada dalam fase suspensi (<i>suspended solids</i>), sehingga secara efektif mencegah pertumbuhan deposit kerak baru.
    </div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const chartCanvas = document.getElementById('chartCanvas');
    const cCtx = chartCanvas.getContext('2d');
    
    const satSlider = document.getElementById('satSlider');
    const flowSlider = document.getElementById('flowSlider');
    
    // Konfigurasi Pipa (Atas = OFF, Bawah = ON)
    const p1Y = 30, p1H = 150, p1Bottom = p1Y + p1H;
    const p2Y = 240, p2H = 150, p2Bottom = p2Y + p2H;
    const coilX = 350, coilW = 150;
    
    let sysOff = { ions: [], crystals: [], scale: new Array(900).fill(0) };
    let sysOn = { ions: [], crystals: [], scale: new Array(900).fill(0) };
    
    let chartDepOff = [], chartDepOn = [], chartAragOn = [];
    
    class Ion {
        constructor(isSysOn) {
            this.sys = isSysOn;
            this.x = Math.random() * 50;
            this.y = (isSysOn ? p2Y : p1Y) + 10 + Math.random() * (p1H - 20);
            this.type = Math.random() > 0.5 ? 'Ca' : 'CO3';
            this.vx = parseFloat(flowSlider.value) * 0.8 + (Math.random() - 0.5);
            this.vy = (Math.random() - 0.5) * 1.5;
            this.active = true;
        }
        update() {
            let flow = parseFloat(flowSlider.value);
            this.x += this.vx + flow * 0.3;
            this.y += this.vy;
            this.vy += (Math.random() - 0.5) * 0.8; // Gerakan Brownian
            
            let floor = (this.sys ? p2Bottom : p1Bottom) - ((this.sys ? sysOn.scale[Math.floor(this.x)||0] : sysOff.scale[Math.floor(this.x)||0]) || 0);
            let ceil = (this.sys ? p2Y : p1Y) + 5;
            
            if(this.y < ceil) { this.y = ceil; this.vy *= -1; }
            if(this.y > floor - 5) { this.y = floor - 5; this.vy *= -1; }
        }
        draw() {
            ctx.beginPath(); ctx.arc(this.x, this.y, 2.5, 0, Math.PI*2);
            ctx.fillStyle = this.type === 'Ca' ? '#3b82f6' : '#10b981';
            ctx.fill();
        }
    }
    
    class Crystal {
        constructor(x, y, isAragonite, isSysOn) {
            this.sys = isSysOn;
            this.x = x; this.y = y;
            this.isArag = isAragonite;
            this.size = isAragonite ? 1.5 : 3;
            this.vx = parseFloat(flowSlider.value) * (isAragonite ? 1.1 : 0.7);
            this.vy = isAragonite ? (Math.random()-0.5) : 1.0;
            this.stuck = false;
        }
        update() {
            if (this.stuck) return;
            this.x += this.vx; this.y += this.vy;
            
            // Calcite (bukan Aragonite) tumbuh semakin besar dan berat
            if (!this.isArag && this.size < 12) {
                this.size += parseFloat(satSlider.value) * 0.001; 
                this.vy += 0.05; 
            }
            
            let floor = (this.sys ? p2Bottom : p1Bottom) - ((this.sys ? sysOn.scale[Math.floor(this.x)||0] : sysOff.scale[Math.floor(this.x)||0]) || 0);
            let ceil = (this.sys ? p2Y : p1Y) + 5;
            
            // Logika pengendapan kerak (Hanya untuk Calcite)
            if (!this.isArag && this.y >= floor - this.size) {
                this.stuck = true; this.y = floor - this.size/2;
                let impactX = Math.floor(this.x);
                let tgtScale = this.sys ? sysOn.scale : sysOff.scale;
                for(let i = Math.max(0, impactX-12); i < Math.min(900, impactX+12); i++) {
                    tgtScale[i] += Math.max(0, (12 - Math.abs(impactX - i)) * 0.08);
                }
            } else if (this.isArag) {
                // Aragonite melayang dan memantul halus
                if(this.y >= floor - 5) this.vy *= -1;
                if(this.y <= ceil) this.vy *= -1;
            }
        }
        draw() {
            ctx.save(); ctx.translate(this.x, this.y);
            if (this.isArag) {
                // Render Aragonite: Kecil, lonjong, merah muda
                ctx.fillStyle = 'rgba(255, 75, 75, 0.9)';
                ctx.beginPath(); ctx.ellipse(0, 0, this.size+3, this.size, 0, 0, Math.PI*2); ctx.fill();
            } else {
                // Render Calcite: Besar, poligon bersudut, abu-abu
                ctx.fillStyle = this.stuck ? '#52525b' : 'rgba(136, 146, 176, 0.9)';
                ctx.beginPath();
                ctx.moveTo(0, -this.size); ctx.lineTo(this.size, 0); ctx.lineTo(0, this.size); ctx.lineTo(-this.size, 0);
                ctx.closePath(); ctx.fill();
            }
            ctx.restore();
        }
    }
    
    function drawPipe(y, isON) {
        ctx.strokeStyle = '#4b5563'; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(900, y); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, y+150); ctx.lineTo(900, y+150); ctx.stroke();
        
        ctx.fillStyle = 'rgba(255,255,255,0.03)'; ctx.font = '50px Arial';
        ctx.fillText('»', 100, y + 90); ctx.fillText('»', 750, y + 90);
        
        ctx.fillStyle = '#a1a1aa'; ctx.font = '12px Arial';
        ctx.fillText(isON ? 'EMSP: ON (Aragonite Mode)' : 'EMSP: OFF (Calcite Mode)', 10, y - 8);
        
        ctx.save();
        for(let i=0; i<=coilW; i+=10) {
            ctx.beginPath(); ctx.moveTo(coilX + i, y - 10); ctx.lineTo(coilX + i, y + 160);
            if (isON) {
                ctx.strokeStyle = 'rgba(0, 242, 254, 0.6)'; ctx.lineWidth = 2;
                ctx.shadowBlur = 10; ctx.shadowColor = '#00f2fe';
            } else {
                ctx.strokeStyle = '#2d323e'; ctx.lineWidth = 2; ctx.shadowBlur = 0;
            }
            ctx.stroke();
        }
        if(isON) {
            let waveOffset = (Date.now() / 150) % (Math.PI * 2);
            ctx.beginPath();
            for(let i=0; i<coilW; i+=5) {
                let yWave = Math.sin(i * 0.1 - waveOffset) * 25;
                if(i===0) ctx.moveTo(coilX + i, y + 75 + yWave);
                else ctx.lineTo(coilX + i, y + 75 + yWave);
            }
            ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5; ctx.stroke();
        }
        ctx.restore();
        
        let tgtScale = isON ? sysOn.scale : sysOff.scale;
        ctx.fillStyle = '#3f3f46'; ctx.beginPath(); ctx.moveTo(0, y+150);
        for(let i=0; i<900; i++) ctx.lineTo(i, y+150 - tgtScale[i]);
        ctx.lineTo(900, y+150); ctx.closePath(); ctx.fill();
        ctx.strokeStyle = '#71717a'; ctx.lineWidth = 1; ctx.stroke();
    }
    
    function processSystem(sysObj, isON) {
        let sat = parseInt(satSlider.value);
        let spawnRate = sat / 100;
        
        if(Math.random() < spawnRate && sysObj.ions.length < (isON ? 120 : 150)) {
            sysObj.ions.push(new Ion(isON));
        }
        
        for(let i = sysObj.ions.length - 1; i >= 0; i--) {
            let p1 = sysObj.ions[i];
            p1.update(); p1.draw();
            if(p1.x > 900) { sysObj.ions.splice(i, 1); continue; }
            
            if(p1.active) {
                for(let j = i - 1; j >= 0; j--) {
                    let p2 = sysObj.ions[j];
                    if(p2.active && p1.type !== p2.type) {
                        let dist = Math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2);
                        if(dist < 12) {
                            let inCoil = (p1.x >= coilX && p1.x <= coilX + coilW);
                            let passedCoil = (p1.x >= coilX); // Ion telah memasuki/melewati zona elektromagnetik
                            
                            let prob = (isON && inCoil) ? 0.95 : (sat/200); 
                            
                            if(Math.random() < prob) {
                                p1.active = false; p2.active = false;
                                // PERBAIKAN LOGIKA: Jika EMSP ON dan fluida telah melalui zona kumparan, HANYA terbentuk Aragonite
                                let isArag = (isON && passedCoil);
                                sysObj.crystals.push(new Crystal(p1.x, p1.y, isArag, isON));
                                break;
                            }
                        }
                    }
                }
            }
        }
        sysObj.ions = sysObj.ions.filter(p => p.active);
        
        for(let i = sysObj.crystals.length - 1; i >= 0; i--) {
            let c = sysObj.crystals[i];
            c.update(); c.draw();
            if(c.x > 900 && !c.stuck) sysObj.crystals.splice(i, 1);
        }
    }
    
    function updateUI() {
        let sat = parseInt(satSlider.value);
        document.getElementById('valSat').innerText = sat + '%';
        document.getElementById('valFlow').innerText = flowSlider.value + ' m/s';
        
        let lblSuper = document.getElementById('lblSuper');
        let lblRisk = document.getElementById('lblRisk');
        
        if(sat < 30) { lblSuper.innerText = 'Rendah'; lblSuper.style.color = '#10b981'; lblRisk.innerText = 'Aman'; lblRisk.style.color = '#10b981'; }
        else if(sat < 70) { lblSuper.innerText = 'Sedang'; lblSuper.style.color = '#f59e0b'; lblRisk.innerText = 'Waspada'; lblRisk.style.color = '#f59e0b'; }
        else { lblSuper.innerText = 'Tinggi'; lblSuper.style.color = '#ff4b4b'; lblRisk.innerText = 'Kritis'; lblRisk.style.color = '#ff4b4b'; }
        
        let depOff = sysOff.scale.reduce((a,b)=>a+b, 0) / 900;
        let depOn = sysOn.scale.reduce((a,b)=>a+b, 0) / 900;
        document.getElementById('valDepOff').innerText = depOff.toFixed(1) + ' mm';
        document.getElementById('valDepOn').innerText = depOn.toFixed(1) + ' mm';
        
        chartDepOff.push(depOff);
        chartDepOn.push(depOn);
        chartAragOn.push(sysOn.crystals.filter(c => c.isArag && c.x < 900).length / 2);
        
        if(chartDepOff.length > 900) { chartDepOff.shift(); chartDepOn.shift(); chartAragOn.shift(); }
    }
    
    function drawCharts() {
        cCtx.fillStyle = '#12141a'; cCtx.fillRect(0,0, chartCanvas.width, chartCanvas.height);
        cCtx.strokeStyle = '#262a35'; cCtx.beginPath(); cCtx.moveTo(0, 75); cCtx.lineTo(900, 75); cCtx.stroke();
        
        cCtx.fillStyle = '#a1a1aa'; cCtx.font = '11px Arial';
        cCtx.fillText('Pertumbuhan Kerak (OFF)', 10, 20);
        cCtx.fillText('Suspensi Aragonite (ON)', 10, 95);
        
        cCtx.lineWidth = 2.5;
        // Line OFF (Scale)
        cCtx.strokeStyle = 'var(--calcite-color)'; cCtx.beginPath();
        for(let i=0; i<chartDepOff.length; i++) cCtx.lineTo(i, 75 - Math.min(75, chartDepOff[i]*1.5)); cCtx.stroke();
        // Line ON (Aragonite)
        cCtx.strokeStyle = 'var(--aragonite-color)'; cCtx.beginPath();
        for(let i=0; i<chartAragOn.length; i++) cCtx.lineTo(i, 150 - Math.min(75, chartAragOn[i]*2)); cCtx.stroke();
    }
    
    function animate() {
        ctx.fillStyle = '#12141a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawPipe(p1Y, false); processSystem(sysOff, false);
        drawPipe(p2Y, true); processSystem(sysOn, true);
        
        updateUI(); drawCharts();
        requestAnimationFrame(animate);
    }
    
    document.getElementById('btnReset').addEventListener('click', () => {
        sysOff = { ions: [], crystals: [], scale: new Array(900).fill(0) };
        sysOn = { ions: [], crystals: [], scale: new Array(900).fill(0) };
        chartDepOff = []; chartDepOn = []; chartAragOn = [];
    });
    
    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=900, scrolling=False)
