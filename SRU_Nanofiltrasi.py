import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Simulasi SRU Nanofiltrasi", layout="wide", initial_sidebar_state="collapsed")
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
    <title>Sulfate Removal Unit (SRU) - Nanofiltration</title>
    <style>
        :root {
            --bg: #0e1117;
            --panel: #1e212b;
            --text: #fafafa;
            --so4-color: #eab308;      /* Kuning (Sulfat) */
            --water-color: #38bdf8;    /* Biru muda (Air/NaCl) */
            --membrane-color: #2dd4bf; /* Tosca (Lapisan Poliamida) */
            --polysulfone-color: #7c8db5; /* Biru keabuan (Lapisan Polisulfon) */
            --polyester-color: #475569;   /* Abu tua (Lapisan Penyangga Poliester) */
            --foul-color: #d4d4d8;     /* Abu terang (Kerak CaSO4 / Fouling) */
            --solid-color: #b45309;    /* Cokelat (Padatan tersuspensi/biologis) */
        }
        * { box-sizing: border-box; }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        h2 { margin: 0 0 15px 0; font-weight: 600; text-align: center; font-size: 1.4rem; color: #f8fafc; }

        .main-container {
            width: 100%; max-width: 1400px; display: grid;
            grid-template-columns: minmax(0, 1fr) 360px; gap: 20px; align-items: start;
        }

        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center;
            min-width: 0;
        }
        canvas { background: #12141a; border-radius: 8px; width: 100%; height: auto; display: block; }

        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 18px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 14px;
            max-height: 940px; overflow-y: auto;
        }

        .control-section {
            border: 1px solid #334155; padding: 12px; border-radius: 8px; background: #1e293b;
        }
        .control-title {
            font-size: 0.85rem; font-weight: bold; color: #94a3b8; margin-bottom: 10px;
            border-bottom: 1px solid #475569; padding-bottom: 5px;
        }

        .slider-group label { font-size: 0.82rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 8px;}
        input[type=range] { width: 100%; margin: 5px 0 10px 0; accent-color: #38bdf8; }

        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 5px; }
        .metric-card { background: #0f172a; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #334155; }
        .metric-title { font-size: 0.68rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.4px;}
        .metric-value { font-size: 1.15rem; font-weight: bold; margin-top: 4px; color: #f8fafc; }

        .alert { color: #ef4444 !important; }
        .safe { color: #10b981 !important; }
        .warn { color: #f59e0b !important; }

        .layer-row { display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: #cbd5e1; margin-top: 6px; }
        .layer-dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
        .layer-text b { color: #f1f5f9; }

        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; font-size: 0.75rem; padding: 10px;
                  background: #1e293b; border-radius: 8px; margin-top:15px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink:0; }

        button { background:#38bdf8; color:#0f172a; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 4px; transition: 0.3s;}
        button:hover { background: #0284c7; color: white;}

        @media (max-width: 950px) {
            .main-container { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <h2>Sulfate Removal Unit (SRU) — Pre-treatment &amp; Nanofiltrasi (TFC Poliamida)</h2>

    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="1000" height="560"></canvas>

            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--water-color);"></div> Air &amp; Ion Monovalen (Na⁺, Cl⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color); border-radius:2px;"></div> Ion Sulfat Divalen (SO₄²⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--solid-color); border-radius:2px;"></div> Padatan Tersuspensi / Biologis</div>
                <div class="legend-item"><div class="dot" style="background:var(--foul-color); border-radius:2px;"></div> Kerak CaSO₄ (Scaling/Fouling)</div>
            </div>
        </div>

        <div class="control-panel">

            <div class="control-section">
                <div class="control-title">1. Kondisi Air Laut (Feed Stream)</div>
                <div class="slider-group">
                    <label>Tekanan Umpan (Feed Pressure) <span id="valPress">300 psi</span></label>
                    <input type="range" id="slPress" min="100" max="600" value="300" step="10">
                    <label>Konsentrasi Sulfat <span id="valSO4">2800 ppm</span></label>
                    <input type="range" id="slSO4" min="500" max="4000" value="2800" step="100">
                    <label>Padatan Tersuspensi &amp; Material Biologis <span id="valTurbid">Sedang</span></label>
                    <input type="range" id="slTurbid" min="0" max="100" value="40">
                </div>
            </div>

            <div class="control-section">
                <div class="control-title">2. Pre-treatment: Cartridge Filter (5,0 µm)</div>
                <div class="slider-group">
                    <label>Kondisi Filter Cartridge <span id="valFilter">Baik</span></label>
                    <input type="range" id="slFilter" min="60" max="100" value="95">
                </div>
                <div style="font-size:0.72rem; color:#94a3b8; margin-top:4px;">
                    Menyaring partikel padat, material tersuspensi &amp; biologis sebelum menyentuh membran utama.
                </div>
            </div>

            <div class="control-section">
                <div class="control-title">3. Membran Nanofiltrasi (Thin-Film Composite)</div>
                <div class="slider-group">
                    <label>Integritas Lapisan Poliamida (Pore Size) <span id="valInteg">Optimal</span></label>
                    <input type="range" id="slInteg" min="70" max="100" value="99">
                </div>
                <div class="layer-row"><div class="layer-dot" style="background:var(--membrane-color);"></div>
                    <div class="layer-text"><b>Poliamida</b> — 200 nm, pori ≈ 1 nm (lapisan aktif)</div></div>
                <div class="layer-row"><div class="layer-dot" style="background:var(--polysulfone-color);"></div>
                    <div class="layer-text"><b>Polisulfon</b> — 40 µm, pori ≈ 15 nm (lapisan tengah)</div></div>
                <div class="layer-row"><div class="layer-dot" style="background:var(--polyester-color);"></div>
                    <div class="layer-text"><b>Poliester</b> — 120 µm, pori ≈ 200 µm (penyangga)</div></div>
            </div>

            <div class="control-section" style="background: #0f172a; border-color: #475569;">
                <div class="control-title" style="color: #f8fafc;">Kinerja Sistem SRU</div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Sulfate Rejection</div>
                        <div class="metric-value safe" id="valRej">99.0%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Efisiensi Pre-treatment</div>
                        <div class="metric-value safe" id="valPretreat">100%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Kerak CaSO₄ (Fouling)</div>
                        <div class="metric-value" id="valFoul">0%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Permeate Flux</div>
                        <div class="metric-value safe" id="valFlux">100%</div>
                    </div>
                </div>
            </div>

            <button id="btnCIP">CIP (Clean-in-Place) Backwash</button>
        </div>
    </div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');

    // Palet warna asli (harus hex/rgb, Canvas TIDAK bisa membaca var(--xxx) dari CSS)
    const COLORS = {
        water: '#38bdf8',
        so4: '#eab308',
        solid: '#b45309',
        foul: '#d4d4d8',
        membrane: '#2dd4bf',
        polysulfone: '#7c8db5',
        polyester: '#475569',
        pipe: '#334155',
        label: '#94a3b8'
    };

    // Sliders
    const slPress = document.getElementById('slPress');
    const slSO4 = document.getElementById('slSO4');
    const slTurbid = document.getElementById('slTurbid');
    const slFilter = document.getElementById('slFilter');
    const slInteg = document.getElementById('slInteg');

    // --- GEOMETRI ---
    const CH_TOP = 125;      // dinding atas kanal feed
    const preStartX = 60, preEndX = 165;     // zona cartridge filter (pre-treatment)
    const mStartX = 270, mEndX = 860;        // rentang modul membran NF
    const mY = 340;                           // permukaan atas lapisan poliamida (aktif)
    const LAYER_PA = 6;      // tebal visual lapisan poliamida
    const LAYER_PS = 16;     // tebal visual lapisan polisulfon
    const LAYER_PES = 22;    // tebal visual lapisan poliester
    const permTop = mY + LAYER_PA + LAYER_PS + LAYER_PES; // atas kanal permeate
    const permBottom = 500;  // dinding bawah kanal permeate
    const foulWidth = mEndX - mStartX;

    let particles = [];
    let foulingArray = new Array(foulWidth).fill(0);

    let totalFouling = 0;
    let so4Rejected = 0, so4Passed = 0;
    let solidBlocked = 0, solidPassed = 0;
    let flashEffect = 0;

    class Particle {
        constructor(type, startX, startY) {
            this.type = type; // 'SO4' | 'Water' | 'Solid'
            this.x = startX;
            this.y = startY;

            let pressure = parseInt(slPress.value) / 300;
            this.vx = 3.5 * pressure + (Math.random() * 2);
            this.vy = (Math.random() - 0.3) * 2;

            this.size = type === 'SO4' ? 5 : (type === 'Solid' ? 4.5 : 3.5);
            this.inPermeate = false;
            this.active = true;
            this.isFouling = false;     // menempel jadi kerak di membran
            this.isFiltered = false;    // tersaring di cartridge pre-treatment
            this.passedPretreat = (type !== 'Solid'); // air & sulfat lolos begitu saja (ion terlarut)
        }

        update() {
            if (this.isFouling || this.isFiltered) return;

            let pressure = parseInt(slPress.value) / 300;
            let integrity = parseInt(slInteg.value) / 100;
            let filterCond = parseInt(slFilter.value) / 100;

            if (!this.inPermeate) {
                this.x += this.vx;
                this.y += this.vy;

                // --- TAHAP PRE-TREATMENT: Cartridge Filter 5.0 micron ---
                if (this.type === 'Solid' && !this.passedPretreat && this.x >= preStartX && this.x <= preEndX) {
                    this.passedPretreat = true;
                    let passProb = (1 - filterCond) * 0.9 + 0.03;
                    if (Math.random() < passProb) {
                        solidPassed++; // lolos, akan membebani membran nanti
                    } else {
                        solidBlocked++;
                        this.isFiltered = true;
                        this.x = preStartX + 40 + Math.random() * 40;
                        this.y = 140 + Math.random() * 30;
                        return;
                    }
                }

                // Dorongan tekanan menuju membran di sepanjang modul NF
                if (this.x > mStartX && this.x < mEndX) {
                    this.vy += 0.2 * pressure;
                } else if (this.x > mEndX) {
                    this.vy *= 0.9;
                }

                if (this.y < CH_TOP) { this.y = CH_TOP; this.vy *= -1; }

                // --- TAHAP MEMBRAN NF (menabrak lapisan poliamida aktif) ---
                if (this.x >= mStartX && this.x <= mEndX && this.y >= mY - 10 && this.y <= mY) {
                    let fIdx = Math.min(foulWidth - 1, Math.max(0, Math.floor(this.x - mStartX)));
                    let localFouling = foulingArray[fIdx] || 0;

                    if (this.type === 'SO4') {
                        // Ion sulfat (divalen, >1nm) -> ditolak berdasar ukuran & muatan
                        let passProb = (1 - integrity) + (pressure * 0.005);
                        if (Math.random() < passProb) {
                            this.inPermeate = true; this.y += 20; this.vy = 2;
                            so4Passed++;
                        } else {
                            so4Rejected++;
                            // Polarisasi konsentrasi -> kerak CaSO4 menumpuk di permukaan
                            if (Math.random() < 0.02 + (localFouling * 0.05)) {
                                this.isFouling = true;
                                this.y = mY - localFouling - 3;
                                for (let i = Math.max(0, fIdx - 10); i < Math.min(foulWidth, fIdx + 10); i++) {
                                    let dist = Math.abs(fIdx - i);
                                    if (foulingArray[i] < 30) foulingArray[i] += Math.max(0, (10 - dist) * 0.1);
                                }
                            } else {
                                this.vy = -Math.abs(this.vy) * 0.8 - (Math.random() * 2);
                            }
                        }
                    } else if (this.type === 'Solid') {
                        // Padatan yang lolos pre-treatment: jauh lebih besar dari pori membran
                        // -> hampir selalu tertahan dan mempercepat fouling secara signifikan
                        if (Math.random() < 0.9) {
                            this.isFouling = true;
                            this.y = mY - localFouling - 3;
                            for (let i = Math.max(0, fIdx - 14); i < Math.min(foulWidth, fIdx + 14); i++) {
                                let dist = Math.abs(fIdx - i);
                                if (foulingArray[i] < 30) foulingArray[i] += Math.max(0, (14 - dist) * 0.22);
                            }
                        } else {
                            this.vy = -Math.abs(this.vy) * 0.7 - (Math.random() * 2);
                        }
                    } else {
                        // Air & ion monovalen (kecil) -> lolos, dihambat oleh fouling
                        let blockProb = localFouling / 30;
                        if (Math.random() > blockProb) {
                            this.inPermeate = true; this.y += 15; this.vy = 2 + (pressure * 1.5);
                        } else {
                            this.vy = -Math.abs(this.vy) * 0.5;
                        }
                    }
                }

                if (this.x > mEndX && this.y > 230) { this.y = 230; this.vy *= -1; }
            } else {
                this.x += this.vx * 0.5;
                this.y += this.vy;
                if (this.y > permBottom) { this.y = permBottom; this.vy *= -1; }
                if (this.y < permTop) { this.y = permTop; }
            }
        }

        draw() {
            if (this.isFiltered) {
                ctx.fillStyle = COLORS.solid;
                ctx.fillRect(this.x - 3, this.y - 3, 6, 6);
                return;
            }
            if (this.isFouling) {
                ctx.fillStyle = COLORS.foul;
                ctx.fillRect(this.x - 3, this.y - 3, 6, 6);
                return;
            }

            ctx.beginPath();
            if (this.type === 'SO4') {
                ctx.fillStyle = COLORS.so4;
                ctx.rect(this.x - 4, this.y - 4, 8, 8);
            } else if (this.type === 'Solid') {
                ctx.fillStyle = COLORS.solid;
                ctx.rect(this.x - 4, this.y - 4, 8, 8);
            } else {
                ctx.fillStyle = COLORS.water;
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            }
            ctx.fill();
        }
    }

    function drawScene() {
        ctx.fillStyle = '#12141a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.lineJoin = 'round';

        // Pipa feed atas & retentate
        ctx.strokeStyle = COLORS.pipe; ctx.lineWidth = 8;
        ctx.beginPath(); ctx.moveTo(0, 100); ctx.lineTo(canvas.width - 10, 100); ctx.stroke();
        // Pipa permeate bawah
        ctx.beginPath(); ctx.moveTo(mStartX - 40, permBottom); ctx.lineTo(canvas.width - 10, permBottom); ctx.stroke();
        // Dinding vertikal pemisah kanal
        ctx.beginPath(); ctx.moveTo(mStartX - 40, permBottom); ctx.lineTo(mStartX - 40, permTop); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(mEndX + 20, permTop); ctx.lineTo(mEndX, permTop); ctx.stroke();

        // --- CARTRIDGE FILTER (Pre-treatment 5.0 micron) ---
        ctx.strokeStyle = '#eab308'; ctx.lineWidth = 3; ctx.setLineDash([4, 4]);
        ctx.strokeRect(preStartX, 100, preEndX - preStartX, 130);
        ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(234,179,8,0.06)';
        ctx.fillRect(preStartX, 100, preEndX - preStartX, 130);
        // garis mesh filter
        ctx.strokeStyle = 'rgba(234,179,8,0.4)'; ctx.lineWidth = 1;
        for (let i = 1; i < 6; i++) {
            let xx = preStartX + i * ((preEndX - preStartX) / 6);
            ctx.beginPath(); ctx.moveTo(xx, 100); ctx.lineTo(xx, 230); ctx.stroke();
        }

        // --- MEMBRAN 3 LAPIS (Thin-Film Composite Poliamida) ---
        ctx.fillStyle = COLORS.membrane;
        ctx.fillRect(mStartX, mY, mEndX - mStartX, LAYER_PA);
        ctx.fillStyle = COLORS.polysulfone;
        ctx.fillRect(mStartX, mY + LAYER_PA, mEndX - mStartX, LAYER_PS);
        ctx.fillStyle = COLORS.polyester;
        ctx.fillRect(mStartX, mY + LAYER_PA + LAYER_PS, mEndX - mStartX, LAYER_PES);

        // Render kerak CaSO4 (fouling) menumpuk DI ATAS lapisan poliamida
        if (totalFouling > 0.05) {
            ctx.fillStyle = COLORS.foul;
            ctx.beginPath(); ctx.moveTo(mStartX, mY - 2);
            for (let x = 0; x < foulWidth; x++) ctx.lineTo(mStartX + x, mY - 2 - foulingArray[x]);
            ctx.lineTo(mEndX, mY - 2); ctx.closePath(); ctx.fill();
        }

        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(56, 189, 248, ${flashEffect / 20})`;
            ctx.fillRect(mStartX, mY - 40, mEndX - mStartX, 60);
            flashEffect--;
        }

        // --- LABEL (posisi & alignment dijaga agar tidak pernah terpotong tepi kanvas) ---
        ctx.font = 'bold 14px Arial'; ctx.fillStyle = COLORS.label;
        ctx.textAlign = 'left';
        ctx.fillText('FEED (Air Laut Mentah)', 15, 92);

        ctx.font = 'bold 11px Arial'; ctx.fillStyle = '#eab308';
        ctx.fillText('PRE-TREATMENT', preStartX, 96);
        ctx.font = '10px Arial'; ctx.fillStyle = COLORS.label;
        ctx.fillText('Cartridge Filter 5.0 µm', preStartX, 245);

        ctx.font = '10px Arial'; ctx.fillStyle = COLORS.membrane;
        ctx.fillText('Poliamida (200nm, pori 1nm)', mStartX, mY - 8);

        ctx.font = 'bold 13px Arial'; ctx.fillStyle = COLORS.label;
        ctx.textAlign = 'right';
        ctx.fillText('RETENTATE (Reject SO₄²⁻)', canvas.width - 15, 92);
        ctx.fillText('PERMEATE (Air Injeksi Bersih)', canvas.width - 15, permBottom + 22);
        ctx.textAlign = 'left';
    }

    function processSystem() {
        let press = parseInt(slPress.value);
        let cSO4 = parseInt(slSO4.value);
        let turbid = parseInt(slTurbid.value);

        if (Math.random() < press / 600) {
            particles.push(new Particle('Water', 5, 150 + Math.random() * 60));
            particles.push(new Particle('Water', 5, 150 + Math.random() * 60));
            if (Math.random() < cSO4 / 5000) {
                particles.push(new Particle('SO4', 5, 150 + Math.random() * 60));
            }
            if (Math.random() < turbid / 260) {
                particles.push(new Particle('Solid', 5, 150 + Math.random() * 60));
            }
        }
    }

    function updateDashboard() {
        document.getElementById('valPress').innerText = slPress.value + ' psi';
        document.getElementById('valSO4').innerText = slSO4.value + ' ppm';

        let turbid = parseInt(slTurbid.value);
        document.getElementById('valTurbid').innerText = turbid < 30 ? 'Rendah' : (turbid < 70 ? 'Sedang' : 'Tinggi');

        let filterCond = parseInt(slFilter.value);
        let lblFilter = document.getElementById('valFilter');
        lblFilter.innerText = filterCond > 90 ? 'Baik' : (filterCond > 75 ? 'Menurun' : 'Buruk');
        lblFilter.style.color = filterCond > 90 ? '#10b981' : (filterCond > 75 ? '#f59e0b' : '#ef4444');

        let integ = parseInt(slInteg.value);
        let lblInteg = document.getElementById('valInteg');
        lblInteg.innerText = integ + '%';
        lblInteg.style.color = integ > 95 ? '#10b981' : (integ > 80 ? '#f59e0b' : '#ef4444');

        totalFouling = (foulingArray.reduce((a, b) => a + b, 0) / (foulWidth * 30)) * 100;
        if (totalFouling > 100) totalFouling = 100;

        let rejectionRate = (so4Rejected + so4Passed > 0) ? (so4Rejected / (so4Rejected + so4Passed)) * 100 : integ;
        let pretreatEff = (solidBlocked + solidPassed > 0) ? (solidBlocked / (solidBlocked + solidPassed)) * 100 : filterCond;
        let flux = 100 - totalFouling;

        let elRej = document.getElementById('valRej');
        elRej.innerText = rejectionRate.toFixed(1) + '%';
        elRej.className = 'metric-value ' + (rejectionRate > 95 ? 'safe' : (rejectionRate > 80 ? 'warn' : 'alert'));

        let elPre = document.getElementById('valPretreat');
        elPre.innerText = pretreatEff.toFixed(1) + '%';
        elPre.className = 'metric-value ' + (pretreatEff > 90 ? 'safe' : (pretreatEff > 75 ? 'warn' : 'alert'));

        let elFoul = document.getElementById('valFoul');
        elFoul.innerText = totalFouling.toFixed(1) + '%';
        elFoul.className = 'metric-value ' + (totalFouling > 60 ? 'alert' : (totalFouling > 30 ? 'warn' : 'safe'));

        let elFlux = document.getElementById('valFlux');
        elFlux.innerText = flux.toFixed(0) + '%';
        elFlux.className = 'metric-value ' + (flux > 70 ? 'safe' : (flux > 40 ? 'warn' : 'alert'));
    }

    function animate() {
        drawScene();
        processSystem();

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update();
                p.draw();
                if (p.x > canvas.width + 10) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }

        // batasi jumlah partikel agar performa stabil
        if (particles.length > 900) particles.splice(0, particles.length - 900);

        updateDashboard();
        requestAnimationFrame(animate);
    }

    document.getElementById('btnCIP').addEventListener('click', () => {
        foulingArray.fill(0);
        so4Rejected = 0; so4Passed = 0;
        solidBlocked = 0; solidPassed = 0;
        particles = particles.filter(p => !p.isFouling && !p.isFiltered);
        flashEffect = 20;
    });

    animate();
</script>
</body>
</html>
"""

# Jangan lupa bagian bawah ini sangat penting!
components.html(html_app, height=1000, scrolling=False)

# --- PENJELASAN SISTEM ---
with st.expander("ℹ️ Cara Kerja Sistem SRU (Sulfate Removal Unit)", expanded=False):
    st.markdown("""
Sistem ini bekerja melalui dua tahap penyaringan fisik dari ukuran makro ke nano:

**1. Pre-treatment (Penyaringan Awal)**
Sebelum air laut menyentuh membran utama, air harus melewati *filter cartridge* dengan ukuran pori 5,0 µm.
Tujuannya adalah membuang partikel padat kotor, padatan tersuspensi, dan material biologis, agar tidak
mempercepat penyumbatan (fouling) pada membran nanofiltrasi.

**2. Struktur Tiga Lapis Membran (Thin-Film Composite / TFC Poliamida)**
Membran nanofiltrasi terdiri dari tiga lapisan yang ditumpuk:

| Lapisan | Tebal | Ukuran Pori | Fungsi |
|---|---|---|---|
| Poliamida (film tipis, teratas) | 200 nm | ≈ 1 nm | Lapisan aktif — memisahkan berdasarkan ukuran & muatan ion |
| Polisulfon (tengah) | 40 µm | ≈ 15 nm | Lapisan pendukung mekanis |
| Poliester (penyangga bawah) | 120 µm | ≈ 200 µm | Struktur penopang utama |

**3. Mekanisme Pemisahan**
Lapisan poliamida teratas menahan ion sulfat (SO₄²⁻) dan ion divalen lain (seperti kalsium) berdasarkan
ukuran (menahan ion > 1 nm) dan muatan ion. Air murni dan ion monovalen kecil bisa menembus pori,
sementara sulfat tertahan sebagai *retentate*.

**4. Masalah Ketahanan: Kerak di Atas Membran**
Karena sulfat dan kalsium terus-menerus ditahan, ion-ion tersebut menumpuk sangat pekat di permukaan
membran — fenomena yang disebut **polarisasi konsentrasi**. Akibatnya, kalsium dan sulfat bereaksi
membentuk **kerak Kalsium Sulfat (CaSO₄)** yang menutupi pori-pori membran, menurunkan efisiensi aliran
air (*permeate flux*) dan memperpendek umur membran. Proses **CIP (Clean-in-Place) Backwash** digunakan
untuk membersihkan kerak ini secara berkala.

Coba turunkan slider **"Kondisi Filter Cartridge"** pada simulasi di atas — kamu akan lihat padatan yang
lolos pre-treatment langsung mempercepat pembentukan kerak di membran.
    """)
