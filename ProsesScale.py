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
        
        button { background:#0284c7; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px; transition: 0.3s;}
        button:hover { background: #0369a1; }
        .btn-danger { background:#ef4444; }
        .btn-danger:hover { background: #b91c1c; }
        .flush-toast {
            position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
            background: #10b981; color: #06281c; font-weight: bold; padding: 8px 16px;
            border-radius: 6px; opacity: 0; transition: opacity 0.4s; pointer-events: none;
            font-size: 0.85rem;
        }
        .flush-toast.show { opacity: 1; }
    </style>
</head>
<body>

    <h2>Kinetika Presipitasi & Dinamika Transport Fluida</h2>
    
    <div class="main-container">
        <div class="canvas-section" style="position: relative;">
            <div id="flushToast" class="flush-toast">✅ Pipa berhasil dibersihkan (Acid Wash)</div>
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
                        <div class="metric-title">Max Tebal Kerak</div>
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
            
            <button id="btnFlush" class="btn-danger">🧹 ACID WASH (Bersihkan Pipa)</button>
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
    const mY = 250; // Mix Y (awal zona pencampuran/pipa produksi)
    const pW = 100; // Pipe Width Max
    const pipeBottom = 520;
    
    let particles = [];
    // ARRAY KETEBALAN KERAK SEPANJANG PIPA (Index = Koordinat Y)
    let scaleArrL = new Array(600).fill(0); 
    let scaleArrR = new Array(600).fill(0);
    
    let totalBlockage = 0; // Persentase maksimum di sepanjang pipa
    let flashEffect = 0; // Animasi saat reset

    // Menumpuk kerak sebagai "medan pegunungan" yang bergerigi/tidak rata,
    // bukan lengkungan halus — meniru tampilan referensi (gray jagged terrain).
    function depositTerrain(arr, centerIdx, amount) {
        let width = 4 + Math.floor(Math.random() * 8); // lebar gundukan 4-11 px, acak tiap deposit (mirip puncak pegunungan)
        for (let i = centerIdx - width; i <= centerIdx + width; i++) {
            if (i < mY || i >= 600) continue;
            let dist = Math.abs(i - centerIdx);
            let falloff = Math.max(0, 1 - dist / (width + 1));
            let jaggedJitter = 0.5 + Math.random() * 1.0; // bikin puncak tidak rata seperti pegunungan
            let inc = amount * falloff * jaggedJitter;
            if (arr[i] + inc < pW/2 - 1) arr[i] += inc;
            else arr[i] = pW/2 - 1;
        }
    }
    
    class Particle {
        constructor(type, startX, startY, tgtX, tgtY, isLeftFlow) {
            this.type = type; // 'Ba', 'Sr', 'SO4', 'Scale'
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
            // PARTIKEL 'Scale' LANGSUNG DIANGGAP SUDAH BERADA DI DALAM PIPA PRODUKSI,
            // sehingga selalu memakai logika deposisi (tahap 2), bukan logika terbang menuju target lama.
            this.inPipe = (type === 'Scale');
            if (this.inPipe && this.y < mY) this.y = mY;
        }
        
        update(flowVelocity) {
            if (this.isStuck) return;
            
            // Tahap 1: Aliran masuk menuju zona pencampuran (hanya untuk ion, bukan kerak)
            if (!this.inPipe && this.y < mY - 20) {
                this.x += this.vx; this.y += this.vy;
                this.x += (Math.random() - 0.5) * 1.0; 
                if (this.y >= mY - 20) this.inPipe = true;
            } 
            // Tahap 2: Zona Campur & Pipa Produksi (vertikal ke bawah)
            else {
                this.inPipe = true;

                // Deteksi lebar pipa efektif di titik ini (setelah tersumbat kerak)
                let yIdx = Math.floor(this.y);
                if (yIdx < mY) yIdx = mY;
                if (yIdx >= 600) yIdx = 599;

                let localBlock = scaleArrL[yIdx] + scaleArrR[yIdx];
                let localRatio = Math.max(0, 1 - (localBlock / pW)); // 1 = lancar, 0 = buntu total

                // Semakin sempit pipa di titik ini, semakin lambat alirannya (efek tersumbat nyata)
                let baseSpeed = (flowVelocity * 0.08) + 0.4;
                this.vy = baseSpeed * Math.max(localRatio, 0.03) + Math.random() * 0.4;

                // Dinding bergerigi sesuai ketebalan kerak yang sudah menumpuk
                let wallL = cX - pW/2 + scaleArrL[yIdx];
                let wallR = cX + pW/2 - scaleArrR[yIdx];

                if (this.type === 'Scale') {
                    // Kerak TIDAK terus mengalir mengikuti arus seperti ion — ia hanya
                    // melayang PELAN turun sambil "dituntun" mendekati dinding terdekat,
                    // lalu segera MENEMPEL PERMANEN (mirip referensi: bergerigi & bertahap).
                    this.vy *= 0.35; // jatuh jauh lebih lambat daripada ion
                    let midX = (wallL + wallR) / 2;
                    let towardWall = (this.x < midX) ? -1 : 1;
                    this.x += towardWall * (0.5 + Math.random() * 0.6); // dituntun pelan ke dinding
                    this.x += (Math.random() - 0.5) * 0.6; // sedikit getaran acak, bukan aliran deras
                } else {
                    this.x += (Math.random() - 0.5) * 3;
                }

                this.y += this.vy;

                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // Logika Deposisi: begitu kerak menyentuh dinding, ia LANGSUNG menyatu
                // menjadi bagian medan (terrain) yang bergerigi lalu hilang dari daftar
                // partikel aktif — sehingga tidak ada tumpukan kerak "mengambang" tanpa henti.
                if (this.type === 'Scale' && localRatio > 0.02) {
                    if (this.x <= wallL + 3 || this.x >= wallR - 3) {
                        if (Math.random() < 0.5) {
                            this.isStuck = true;
                            this.active = false; // langsung menyatu ke medan, bukan menumpuk sbg partikel
                            let arr = (this.x <= wallL + 3) ? scaleArrL : scaleArrR;
                            depositTerrain(arr, yIdx, 0.6); // pertambahan kecil = penumpukan bertahap/pelan
                        }
                    }
                }

                // Jika pipa sudah nyaris buntu total (>=97%), aliran ion praktis berhenti,
                // memberi kesan pipa benar-benar tersumbat.
                if (totalBlockage >= 97 && this.type !== 'Scale') {
                    this.vy *= 0.05;
                }
            }
        }
        
        draw() {
            ctx.beginPath();
            if(this.type === 'Scale') {
                ctx.fillStyle = '#f59e0b';
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
        ctx.beginPath(); ctx.moveTo(70, 50); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, pipeBottom); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(780, 50); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, pipeBottom); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(200, 50); ctx.lineTo(cX, mY - 60); ctx.lineTo(650, 50); ctx.stroke();
        
        ctx.fillStyle = '#94a3b8'; ctx.font = '13px Arial'; ctx.textAlign = 'center';
        ctx.fillText('Air Formasi', 135, 40); ctx.fillText('Air Laut / Injeksi', 715, 40); ctx.fillText('Sumur Produksi', cX, 510);
        
        // Render Kerak Dinamis (terus terakumulasi, hanya hilang saat Acid Wash)
        ctx.fillStyle = '#92400e'; 
        ctx.beginPath(); ctx.moveTo(cX - pW/2, mY);
        for(let y = mY; y <= pipeBottom; y++) ctx.lineTo(cX - pW/2 + scaleArrL[y], y);
        ctx.lineTo(cX - pW/2, pipeBottom); ctx.fill();
        
        ctx.beginPath(); ctx.moveTo(cX + pW/2, mY);
        for(let y = mY; y <= pipeBottom; y++) ctx.lineTo(cX + pW/2 - scaleArrR[y], y);
        ctx.lineTo(cX + pW/2, pipeBottom); ctx.fill();
        
        // Garis batas kerak
        ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(cX - pW/2 + scaleArrL[mY], mY);
        for(let y = mY; y <= pipeBottom; y++) ctx.lineTo(cX - pW/2 + scaleArrL[y], y);
        ctx.stroke();
        
        ctx.beginPath(); ctx.moveTo(cX + pW/2 - scaleArrR[mY], mY);
        for(let y = mY; y <= pipeBottom; y++) ctx.lineTo(cX + pW/2 - scaleArrR[y], y);
        ctx.stroke();

        // Titik tersumbat total (choke point) ditandai merah berkedip
        if (totalBlockage >= 90) {
            let chokeY = mY;
            let maxV = -1;
            for (let y = mY; y <= pipeBottom; y++) {
                let v = scaleArrL[y] + scaleArrR[y];
                if (v > maxV) { maxV = v; chokeY = y; }
            }
            ctx.strokeStyle = `rgba(239,68,68,${0.5 + 0.5*Math.sin(Date.now()/150)})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(cX - pW/2 + scaleArrL[chokeY] - 4, chokeY);
            ctx.lineTo(cX + pW/2 - scaleArrR[chokeY] + 4, chokeY);
            ctx.stroke();
        }

        // Animasi kilat hijau saat baru saja di-flush/reset
        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(16, 185, 129, ${flashEffect / 20})`;
            ctx.fillRect(cX - pW/2, mY, pW, pipeBottom - mY);
            flashEffect--;
        }
    }
    
    function processSystem() {
        let flowF = parseInt(slFlowF.value); let cBa = parseInt(slBa.value);
        let flowL = parseInt(slFlowL.value); let cSO4 = parseInt(slSO4.value);
        
        let totalFlow = flowF + flowL;
        let siValue = 0;
        
        if (totalFlow > 0) {
            let mixBa = (flowF / totalFlow) * cBa;
            let mixSO4 = (flowL / totalFlow) * cSO4;
            siValue = (mixBa * mixSO4) / 5000000; 
        }
        
        // Laju kemunculan partikel ion juga sedikit dihambat bila pipa sudah hampir buntu,
        // merepresentasikan tekanan balik (backpressure) dari sumbatan.
        let spawnDamping = totalBlockage >= 90 ? 0.3 : 1;

        if (flowF > 0 && Math.random() < (flowF / 100) * spawnDamping) {
            let type = Math.random() > 0.25 ? 'Ba' : 'Sr'; 
            particles.push(new Particle(type, 135 + (Math.random() - 0.5) * 60, 50, cX - 25, mY, true));
        }
        
        if (flowL > 0 && Math.random() < (flowL / 100) * spawnDamping) {
            particles.push(new Particle('SO4', 715 + (Math.random() - 0.5) * 60, 50, cX + 25, mY, false));
        }
        
        let nucleationProb = siValue > 1 ? Math.min(siValue * 0.08, 0.55) : 0;
        if (nucleationProb > 0) {
            for(let i = 0; i < particles.length; i++) {
                let p1 = particles[i];
                if(!p1.active || p1.isStuck || p1.type === 'Scale' || p1.y < mY - 20) continue;
                
                for(let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if(!p2.active || p2.isStuck || p2.type === 'Scale' || p2.y < mY - 20) continue;
                    
                    if ((p1.isLeftFlow !== p2.isLeftFlow) && p1.type !== p2.type) {
                        let dist = Math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2);
                        if(dist < 20 && Math.random() < nucleationProb) {
                            p1.active = false; p2.active = false;
                            particles.push(new Particle('Scale', (p1.x+p2.x)/2, Math.max((p1.y+p2.y)/2, mY), 0, 0, false));
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
        
        // Cari titik penyumbatan maksimum (choke point) di sepanjang pipa
        let maxBlockagePoint = 0;
        for (let i = mY; i <= pipeBottom; i++) {
            let localBlockage = scaleArrL[i] + scaleArrR[i];
            if (localBlockage > maxBlockagePoint) maxBlockagePoint = localBlockage;
        }
        
        totalBlockage = (maxBlockagePoint / pW) * 100;
        if (totalBlockage > 100) totalBlockage = 100;
        
        let radiusSisa = 1 - (totalBlockage/100);
        let prodDrop = (1 - (radiusSisa * radiusSisa)) * 100;
        
        let valSI = document.getElementById('valSI');
        let lblSI = document.getElementById('lblSIStatus');
        
        valSI.innerText = flowData.siValue.toFixed(2);
        if (flowData.siValue < 0.5) { valSI.style.color = '#10b981'; lblSI.innerText = 'Undersaturated (Aman)'; }
        else if (flowData.siValue < 1.5) { valSI.style.color = '#f59e0b'; lblSI.innerText = 'Saturated (Waspada)'; }
        else { valSI.style.color = '#ef4444'; lblSI.innerText = 'Supersaturated (Presipitasi Masif)'; }
        
        document.getElementById('valThick').innerText = maxBlockagePoint.toFixed(1) + ' mm';
        
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
        // Reset seluruh variabel: kerak, partikel, dan indikator penyumbatan
        particles = [];
        scaleArrL.fill(0);
        scaleArrR.fill(0);
        totalBlockage = 0;
        flashEffect = 20; // Trigger animasi kilat hijau

        // Tampilkan notifikasi singkat bahwa pipa sudah dibersihkan
        let toast = document.getElementById('flushToast');
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 1800);
    });
    
    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=750, scrolling=False)
