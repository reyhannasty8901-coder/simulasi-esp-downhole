import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Presipitasi Barium Sulfat (BaSO4)", layout="wide", initial_sidebar_state="collapsed")
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
<title>Presipitasi Barium Sulfat (BaSO4)</title>
<style>
    :root {
        --bg: #0e1017;
        --card: #14161f;
        --panel: #1a1d29;
        --border: #2a2e3d;
        --text: #f4f5f7;
        --muted: #8b90a3;
        --ba-color: #3b82f6;
        --so4-color: #34d399;
        --scale-color: #f5a623;
        --accent: #6366f1;
        --safe: #34d399;
        --warn: #f5a623;
        --danger: #ef4444;
    }
    * { box-sizing: border-box; }
    body {
        background: var(--bg); color: var(--text); margin: 0; padding: 18px;
        font-family: 'Segoe UI', Roboto, sans-serif;
        display: flex; justify-content: center;
    }
    .card {
        width: 100%; max-width: 800px; background: var(--card); border-radius: 18px;
        padding: 22px 26px 26px 26px; box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    }
    .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
    .header h2 { margin: 0; font-size: 1.25rem; font-weight: 600; }
    .header-buttons { display: flex; gap: 10px; }
    .icon-btn {
        width: 38px; height: 38px; border-radius: 50%; border: none; cursor: pointer;
        display: flex; align-items: center; justify-content: center; font-size: 1rem;
        color: white; background: #2a2e3d; transition: 0.2s; flex-shrink: 0;
    }
    .icon-btn:hover { filter: brightness(1.2); }
    .icon-btn.primary { background: var(--accent); }

    .canvas-wrap {
        background: #0b0c12; border-radius: 14px; padding: 10px; border: 1px solid var(--border);
    }
    canvas#simCanvas { width: 100%; height: auto; display: block; border-radius: 10px; }

    .legend {
        display: flex; flex-wrap: wrap; justify-content: center; gap: 22px;
        font-size: 0.8rem; color: var(--muted); margin: 14px 0 6px 0;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

    .chart-section { margin-top: 18px; }
    .chart-title { font-size: 0.82rem; color: var(--muted); margin-bottom: 6px; }
    canvas#chartCanvas { width: 100%; height: auto; display: block; }

    .stats-row {
        display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;
        text-align: center;
    }
    .stat-label { font-size: 0.75rem; color: #7c85f0; letter-spacing: 0.3px; margin-bottom: 4px; }
    .stat-value { font-size: 1rem; font-weight: 700; }

    .controls { margin-top: 22px; display: flex; flex-direction: column; gap: 16px; }
    .controls-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .slider-block { display: flex; align-items: center; gap: 12px; }
    .slider-block .lbl { font-size: 0.82rem; color: #c7cad6; width: 130px; flex-shrink: 0; }
    .slider-block input[type=range] { flex: 1; accent-color: var(--accent); }
    .val-box {
        min-width: 40px; padding: 4px 8px; background: #23263433; border: 1px solid var(--border);
        border-radius: 6px; text-align: center; font-size: 0.82rem; color: var(--text); background: #20222e;
    }
</style>
</head>
<body>
<div class="card">
    <div class="header">
        <h2>Presipitasi Barium Sulfat (BaSO4)</h2>
        <div class="header-buttons">
            <button id="btnPause" class="icon-btn primary" title="Jeda/Lanjut">⏸</button>
            <button id="btnReset" class="icon-btn" title="Reset">↺</button>
        </div>
    </div>

    <div class="canvas-wrap">
        <canvas id="simCanvas" width="740" height="430"></canvas>
    </div>

    <div class="legend">
        <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Air Formasi (Ba²⁺)</div>
        <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Air Laut (SO₄²⁻)</div>
        <div class="legend-item"><div class="dot" style="background:var(--scale-color);"></div> Kerak BaSO₄</div>
    </div>

    <div class="chart-section">
        <div class="chart-title">Potensi Kerak ↑</div>
        <canvas id="chartCanvas" width="740" height="150"></canvas>
    </div>

    <div class="stats-row">
        <div>
            <div class="stat-label">LAJU KERAK</div>
            <div class="stat-value" id="valLaju">Sedang</div>
        </div>
        <div>
            <div class="stat-label">STATUS PIPA</div>
            <div class="stat-value" id="valStatus">Aman</div>
        </div>
    </div>

    <div class="controls">
        <div class="controls-row">
            <div class="slider-block">
                <span class="lbl">Rasio Air Laut (%)</span>
                <input type="range" id="slRasio" min="0" max="100" value="50">
                <span class="val-box" id="valRasio">50</span>
            </div>
            <div class="slider-block">
                <span class="lbl">Kons. Barium</span>
                <input type="range" id="slBa" min="0" max="100" value="50">
                <span class="val-box" id="valBaSl">50</span>
            </div>
        </div>
        <div class="slider-block">
            <span class="lbl">Kons. Sulfat</span>
            <input type="range" id="slSO4" min="0" max="100" value="50">
            <span class="val-box" id="valSO4Sl">50</span>
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    const chartCanvas = document.getElementById('chartCanvas');
    const cctx = chartCanvas.getContext('2d');

    const slRasio = document.getElementById('slRasio');
    const slBa = document.getElementById('slBa');
    const slSO4 = document.getElementById('slSO4');
    const valRasio = document.getElementById('valRasio');
    const valBaSl = document.getElementById('valBaSl');
    const valSO4Sl = document.getElementById('valSO4Sl');

    // --- GEOMETRI PIPA BENTUK Y (KAPSUL MEMBULAT) ---
    const cX = 370;                 // pusat horizontal
    const mergeY = 195;             // titik pertemuan kedua pipa
    const tubeHalf = 40;            // setengah lebar pipa vertikal keluaran
    const tubeBottom = 400;         // dasar pipa (tempat kerak menumpuk)
    const leftStart  = {x: 90,  y: 95};
    const rightStart = {x: 650, y: 95};
    const tubeArmWidth = 78;

    let particles = [];
    // Profil tumpukan kerak di dasar pipa (kolom-kolom sepanjang lebar pipa vertikal)
    const N_COLS = 16;
    let pile = new Array(N_COLS).fill(0);
    const colWidth = (tubeHalf * 2) / N_COLS;

    let paused = false;
    let flashEffect = 0;

    function pileHeightAt(x) {
        let idx = Math.floor((x - (cX - tubeHalf)) / colWidth);
        idx = Math.max(0, Math.min(N_COLS - 1, idx));
        return pile[idx];
    }
    function depositPile(x, amount) {
        let centerIdx = Math.floor((x - (cX - tubeHalf)) / colWidth);
        let spread = 1 + Math.floor(Math.random() * 2);
        for (let i = centerIdx - spread; i <= centerIdx + spread; i++) {
            if (i < 0 || i >= N_COLS) continue;
            let dist = Math.abs(i - centerIdx);
            let falloff = Math.max(0, 1 - dist / (spread + 1));
            let jitter = 0.5 + Math.random() * 1.0;
            let inc = amount * falloff * jitter;
            let maxH = tubeBottom - mergeY - 6;
            pile[i] = Math.min(maxH, pile[i] + inc);
        }
    }
    function maxPile() { return Math.max(...pile); }
    function avgPile() { return pile.reduce((a,b)=>a+b,0) / pile.length; }

    class Particle {
        constructor(type, x, y, vx, vy) {
            this.type = type; this.x = x; this.y = y; this.vx = vx; this.vy = vy;
            this.active = true; this.settled = false;
        }
        update() {
            if (this.type === 'Ba' || this.type === 'SO4') {
                if (this.y < mergeY - 5) {
                    this.x += this.vx; this.y += this.vy;
                    this.x += (Math.random() - 0.5) * 0.6;
                } else {
                    // masuk area pencampuran / pipa vertikal, lanjut turun pelan
                    this.vy = Math.max(this.vy, 1.2);
                    this.y += this.vy * 0.6;
                    this.x += (Math.random() - 0.5) * 1.2;
                    let lim = tubeHalf - 4;
                    if (this.x < cX - lim) this.x = cX - lim;
                    if (this.x > cX + lim) this.x = cX + lim;
                    let localPileTop = tubeBottom - pileHeightAt(this.x);
                    if (this.y >= localPileTop) { this.active = false; } // terkubur kerak
                    if (this.y > tubeBottom + 5) this.active = false;
                }
            } else if (this.type === 'Scale') {
                // Kerak jatuh PELAN, sedikit bergoyang, lalu menempel ke tumpukan (tidak terus mengalir)
                this.vy = 0.9 + Math.random() * 0.3;
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 0.7;
                let lim = tubeHalf - 4;
                if (this.x < cX - lim) this.x = cX - lim;
                if (this.x > cX + lim) this.x = cX + lim;
                let localPileTop = tubeBottom - pileHeightAt(this.x);
                if (this.y >= localPileTop) {
                    depositPile(this.x, 1.1);
                    this.active = false;
                }
            }
        }
        draw() {
            ctx.beginPath();
            if (this.type === 'Scale') {
                ctx.fillStyle = '#f5a623';
                ctx.moveTo(this.x, this.y - 4); ctx.lineTo(this.x + 4, this.y);
                ctx.lineTo(this.x, this.y + 4); ctx.lineTo(this.x - 4, this.y);
                ctx.fill();
            } else {
                ctx.arc(this.x, this.y, 3.2, 0, Math.PI * 2);
                ctx.fillStyle = this.type === 'Ba' ? '#3b82f6' : '#34d399';
                ctx.fill();
            }
        }
    }

    function capsule(p1, p2, width, fill, stroke) {
        ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        ctx.lineWidth = width + 5; ctx.strokeStyle = stroke;
        ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
        ctx.lineWidth = width; ctx.strokeStyle = fill;
        ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
    }

    function drawScene() {
        ctx.fillStyle = '#0b0c12'; ctx.fillRect(0, 0, canvas.width, canvas.height);

        // pipa diagonal (kiri: air formasi, kanan: air laut)
        capsule(leftStart,  {x: cX, y: mergeY}, tubeArmWidth, '#252838', '#3d4258');
        capsule(rightStart, {x: cX, y: mergeY}, tubeArmWidth, '#252838', '#3d4258');
        // pipa vertikal keluaran
        capsule({x: cX, y: mergeY - 10}, {x: cX, y: tubeBottom}, tubeHalf * 2, '#252838', '#3d4258');

        // label
        ctx.fillStyle = '#e5e7eb'; ctx.font = 'bold 12px Segoe UI'; ctx.textAlign = 'left';
        ctx.fillText('Air Formasi (Ba)', leftStart.x - 20, leftStart.y - 12);
        ctx.textAlign = 'right';
        ctx.fillText('Air Laut (SO4)', rightStart.x + 20, rightStart.y - 12);

        // tumpukan kerak (jagged, menumpuk dari dasar pipa)
        ctx.beginPath();
        ctx.moveTo(cX - tubeHalf, tubeBottom);
        for (let i = 0; i <= N_COLS; i++) {
            let x = cX - tubeHalf + i * colWidth;
            let h = pile[Math.min(i, N_COLS - 1)];
            ctx.lineTo(x, tubeBottom - h);
        }
        ctx.lineTo(cX + tubeHalf, tubeBottom);
        ctx.closePath();
        let grad = ctx.createLinearGradient(0, tubeBottom - 170, 0, tubeBottom);
        grad.addColorStop(0, '#c9791a');
        grad.addColorStop(1, '#f5a623');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = '#ffcf7a'; ctx.lineWidth = 1.5; ctx.stroke();

        // garis putus-putus di dasar pipa (indikator outlet)
        ctx.strokeStyle = '#5a5f75'; ctx.lineWidth = 2; ctx.setLineDash([4, 5]);
        ctx.beginPath(); ctx.moveTo(cX - tubeHalf, tubeBottom + 6); ctx.lineTo(cX + tubeHalf, tubeBottom + 6); ctx.stroke();
        ctx.setLineDash([]);

        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(52, 211, 153, ${flashEffect / 20})`;
            ctx.fillRect(cX - tubeHalf, mergeY, tubeHalf * 2, tubeBottom - mergeY);
            flashEffect--;
        }
    }

    function computeMassa() {
        let r = parseInt(slRasio.value);      // % Air Laut
        let kBa = parseInt(slBa.value);
        let kSO4 = parseInt(slSO4.value);
        let peakX = (kBa + kSO4) > 0 ? 100 * kBa / (kBa + kSO4) : 50;
        let peakY = (kBa / 100) * (kSO4 / 100) * 100; // maks 100, ditampilkan s/d 50
        let massa;
        if (r <= peakX) massa = peakX > 0 ? peakY * (r / peakX) : 0;
        else massa = (100 - peakX) > 0 ? peakY * ((100 - r) / (100 - peakX)) : 0;
        return { r, kBa, kSO4, peakX, peakY, massa };
    }

    function drawChart(m) {
        cctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
        const padL = 34, padR = 14, padT = 10, padB = 14;
        const w = chartCanvas.width - padL - padR;
        const h = chartCanvas.height - padT - padB;
        const yMax = 50;

        // grid + label sumbu
        cctx.strokeStyle = '#262a38'; cctx.fillStyle = '#6b7086'; cctx.font = '10px Segoe UI'; cctx.textAlign = 'right';
        for (let v = 0; v <= yMax; v += 10) {
            let y = padT + h - (v / yMax) * h;
            cctx.beginPath(); cctx.moveTo(padL, y); cctx.lineTo(padL + w, y); cctx.stroke();
            cctx.fillText(v, padL - 6, y + 3);
        }

        function xPos(pct) { return padL + (pct / 100) * w; }
        function yPos(val) { return padT + h - (Math.min(val, yMax) / yMax) * h; }

        // triangle area (kurva potensi kerak)
        cctx.beginPath();
        cctx.moveTo(xPos(0), yPos(0));
        cctx.lineTo(xPos(m.peakX), yPos(m.peakY));
        cctx.lineTo(xPos(100), yPos(0));
        cctx.lineTo(xPos(100), padT + h);
        cctx.lineTo(xPos(0), padT + h);
        cctx.closePath();
        cctx.fillStyle = 'rgba(99,102,241,0.12)';
        cctx.fill();

        cctx.beginPath();
        cctx.moveTo(xPos(0), yPos(0));
        cctx.lineTo(xPos(m.peakX), yPos(m.peakY));
        cctx.lineTo(xPos(100), yPos(0));
        cctx.strokeStyle = '#818cf8'; cctx.lineWidth = 2; cctx.stroke();

        // marker posisi saat ini
        let mx = xPos(m.r), my = yPos(m.massa);
        cctx.beginPath(); cctx.arc(mx, my, 5, 0, Math.PI * 2);
        cctx.fillStyle = '#f5a623'; cctx.fill();
        cctx.strokeStyle = '#fff'; cctx.lineWidth = 1.5; cctx.stroke();

        cctx.fillStyle = '#f4f5f7'; cctx.font = 'bold 11px Segoe UI'; cctx.textAlign = 'center';
        cctx.fillText('Massa: ' + m.massa.toFixed(1), mx, my - 12);
    }

    function processSystem(m) {
        let spawnBa = (1 - m.r / 100) * (m.kBa / 100);
        let spawnSO4 = (m.r / 100) * (m.kSO4 / 100);

        if (Math.random() < spawnBa * 0.9) {
            let sy = leftStart.y + (Math.random() - 0.5) * 30;
            let sx = leftStart.x + (Math.random() - 0.5) * 20;
            let dx = cX - sx, dy = mergeY - sy;
            let ang = Math.atan2(dy, dx), sp = 2.2 + Math.random() * 1.4;
            particles.push(new Particle('Ba', sx, sy, Math.cos(ang) * sp, Math.sin(ang) * sp));
        }
        if (Math.random() < spawnSO4 * 0.9) {
            let sy = rightStart.y + (Math.random() - 0.5) * 30;
            let sx = rightStart.x + (Math.random() - 0.5) * 20;
            let dx = cX - sx, dy = mergeY - sy;
            let ang = Math.atan2(dy, dx), sp = 2.2 + Math.random() * 1.4;
            particles.push(new Particle('SO4', sx, sy, Math.cos(ang) * sp, Math.sin(ang) * sp));
        }

        // nukleasi: Ba + SO4 berdekatan di zona percampuran -> jadi kerak
        let nucleationProb = Math.min(m.massa / 50, 1) * 0.6;
        if (nucleationProb > 0) {
            for (let i = 0; i < particles.length; i++) {
                let p1 = particles[i];
                if (!p1.active || p1.type === 'Scale' || p1.y < mergeY - 40) continue;
                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if (!p2.active || p2.type === 'Scale' || p2.y < mergeY - 40) continue;
                    if (p1.type !== p2.type) {
                        let dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                        if (dist < 16 && Math.random() < nucleationProb) {
                            p1.active = false; p2.active = false;
                            let nx = (p1.x + p2.x) / 2, ny = Math.max((p1.y + p2.y) / 2, mergeY);
                            particles.push(new Particle('Scale', nx, ny, 0, 0));
                            break;
                        }
                    }
                }
            }
        }
    }

    function updateStats(m) {
        valRasio.innerText = m.r; valBaSl.innerText = m.kBa; valSO4Sl.innerText = m.kSO4;

        let laju = document.getElementById('valLaju');
        if (m.massa < 10) { laju.innerText = 'Rendah'; laju.style.color = 'var(--safe)'; }
        else if (m.massa < 30) { laju.innerText = 'Sedang'; laju.style.color = 'var(--warn)'; }
        else { laju.innerText = 'Tinggi'; laju.style.color = 'var(--danger)'; }

        let blockagePct = (maxPile() / (tubeBottom - mergeY - 6)) * 100;
        let status = document.getElementById('valStatus');
        if (blockagePct < 40) { status.innerText = 'Aman'; status.style.color = 'var(--safe)'; }
        else if (blockagePct < 75) { status.innerText = 'Waspada'; status.style.color = 'var(--warn)'; }
        else { status.innerText = 'Bahaya'; status.style.color = 'var(--danger)'; }
    }

    function animate() {
        let m = computeMassa();
        drawScene();
        drawChart(m);

        if (!paused) {
            processSystem(m);
            for (let i = particles.length - 1; i >= 0; i--) {
                let p = particles[i];
                if (p.active) { p.update(); } else { particles.splice(i, 1); continue; }
                if (p.y > canvas.height + 10) { particles.splice(i, 1); continue; }
            }
        }
        for (let p of particles) p.draw();

        updateStats(m);
        requestAnimationFrame(animate);
    }

    document.getElementById('btnPause').addEventListener('click', (e) => {
        paused = !paused;
        e.target.innerText = paused ? '▶' : '⏸';
    });
    document.getElementById('btnReset').addEventListener('click', () => {
        particles = [];
        pile.fill(0);
        flashEffect = 20;
    });

    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=900, scrolling=False)
