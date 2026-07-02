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
        --border: #2a2e3d;
        --text: #f4f5f7;
        --muted: #8b90a3;
        --ba-color: #3b82f6;
        --sr-color: #a855f7;
        --so4-color: #34d399;
        --baso4-color: #f5a623;
        --srso4-color: #eab308;
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
        padding: 22px 26px 34px 26px; box-shadow: 0 10px 30px rgba(0,0,0,0.45);
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
        display: flex; flex-wrap: wrap; justify-content: center; gap: 18px;
        font-size: 0.78rem; color: var(--muted); margin: 14px 0 6px 0;
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
        min-width: 40px; padding: 4px 8px; border: 1px solid var(--border);
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
        <div class="legend-item"><div class="dot" style="background:var(--sr-color);"></div> Air Formasi (Sr²⁺)</div>
        <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Air Laut (SO₄²⁻)</div>
        <div class="legend-item"><div class="dot" style="background:var(--baso4-color);"></div> Kerak BaSO₄</div>
        <div class="legend-item"><div class="dot" style="background:var(--srso4-color);"></div> Kerak SrSO₄</div>
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
    const cX = 370;
    const mergeY = 195;
    const tubeHalf = 40;
    const tubeBottom = 400;
    const leftStart  = {x: 90,  y: 95};
    const rightStart = {x: 650, y: 95};
    const tubeArmWidth = 78;

    let particles = [];
    let paused = false;
    let flashEffect = 0;

    // --- KERAK MENEMPEL DARI DINDING KIRI & KANAN, MENUMPUK KE ARAH TENGAH ---
    const arrLen = (tubeBottom - mergeY) + 10;
    let scaleArrL = new Array(arrLen).fill(0);   // ketebalan kerak dari dinding kiri
    let scaleArrR = new Array(arrLen).fill(0);   // ketebalan kerak dari dinding kanan
    let colorArrL = new Array(arrLen).fill(0);   // 0 = BaSO4 (oranye) ... 1 = SrSO4 (kuning), rata-rata tertimbang
    let colorArrR = new Array(arrLen).fill(0);

    function idxOf(y) { return Math.max(0, Math.min(arrLen - 1, Math.floor(y - mergeY))); }
    function wallLAt(y) { return cX - tubeHalf + scaleArrL[idxOf(y)]; }
    function wallRAt(y) { return cX + tubeHalf - scaleArrR[idxOf(y)]; }

    function depositWall(side, y, amount, colorVal) {
        let centerIdx = idxOf(y);
        let spread = 2 + Math.floor(Math.random() * 3);
        let arr = side === 'L' ? scaleArrL : scaleArrR;
        let carr = side === 'L' ? colorArrL : colorArrR;
        for (let i = centerIdx - spread; i <= centerIdx + spread; i++) {
            if (i < 0 || i >= arrLen) continue;
            let dist = Math.abs(i - centerIdx);
            let falloff = Math.max(0, 1 - dist / (spread + 1));
            let jitter = 0.5 + Math.random() * 1.0;
            let inc = amount * falloff * jitter;
            let cap = tubeHalf - 3;
            let newThk = Math.min(cap, arr[i] + inc);
            let added = newThk - arr[i];
            if (added > 0) {
                let totalThk = arr[i] + added;
                carr[i] = (carr[i] * arr[i] + colorVal * added) / totalThk;
                arr[i] = totalThk;
            }
        }
    }
    function maxBlockagePx() {
        let m = 0;
        for (let i = 0; i < arrLen; i++) { let v = scaleArrL[i] + scaleArrR[i]; if (v > m) m = v; }
        return m;
    }
    function blendColor(orangeRGB, yellowRGB, t) {
        let r = orangeRGB[0] + (yellowRGB[0] - orangeRGB[0]) * t;
        let g = orangeRGB[1] + (yellowRGB[1] - orangeRGB[1]) * t;
        let b = orangeRGB[2] + (yellowRGB[2] - orangeRGB[2]) * t;
        return `rgb(${r | 0},${g | 0},${b | 0})`;
    }
    const ORANGE = [245, 166, 35];
    const YELLOW = [234, 179, 8];

    class Particle {
        // type: 'Ba' | 'Sr' | 'SO4' | 'Scale'
        // scaleKind (khusus type Scale): 'BaSO4' (oranye) | 'SrSO4' (kuning)
        constructor(type, x, y, vx, vy, scaleKind) {
            this.type = type; this.x = x; this.y = y; this.vx = vx; this.vy = vy;
            this.active = true; this.scaleKind = scaleKind || null;
        }
        update() {
            if (this.type === 'Scale') {
                // Kerak jatuh PELAN & bergoyang kecil, dituntun ke dinding TERDEKAT, lalu langsung menempel
                this.vy = (this.vy || 0.9) + 0.02;
                if (this.vy > 1.3) this.vy = 1.3;
                this.y += this.vy;

                let wallL = wallLAt(this.y), wallR = wallRAt(this.y);
                let midX = (wallL + wallR) / 2;
                let towardWall = (this.x < midX) ? -1 : 1;
                this.x += towardWall * (0.5 + Math.random() * 0.5);
                this.x += (Math.random() - 0.5) * 0.5;

                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;

                if (wallR - wallL < 6) { this.active = false; return; } // pipa sudah nyaris buntu total

                if (this.x <= wallL + 3 || this.x >= wallR - 3) {
                    if (Math.random() < 0.5) {
                        let side = (this.x <= wallL + 3) ? 'L' : 'R';
                        let colorVal = this.scaleKind === 'SrSO4' ? 1 : 0;
                        depositWall(side, this.y, 0.7, colorVal);
                        this.active = false;
                    }
                }
                if (this.y > tubeBottom + 5) this.active = false;
            } else {
                // Ion Ba / Sr / SO4
                if (this.y < mergeY - 5) {
                    this.x += this.vx; this.y += this.vy;
                    this.x += (Math.random() - 0.5) * 0.6;
                } else {
                    this.vy = Math.max(this.vy, 1.4);
                    this.y += this.vy * 0.55;
                    this.x += (Math.random() - 0.5) * 1.2;
                    let wallL = wallLAt(this.y), wallR = wallRAt(this.y);
                    if (this.x < wallL) this.x = wallL;
                    if (this.x > wallR) this.x = wallR;
                    if (wallR - wallL < 6) this.vy *= 0.05; // tersumbat, aliran nyaris berhenti
                }
                if (this.y > tubeBottom + 5) this.active = false;
            }
        }
        draw() {
            ctx.beginPath();
            if (this.type === 'Scale') {
                ctx.fillStyle = this.scaleKind === 'SrSO4' ? '#eab308' : '#f5a623';
                ctx.moveTo(this.x, this.y - 4); ctx.lineTo(this.x + 4, this.y);
                ctx.lineTo(this.x, this.y + 4); ctx.lineTo(this.x - 4, this.y);
                ctx.fill();
            } else {
                ctx.arc(this.x, this.y, 3.2, 0, Math.PI * 2);
                ctx.fillStyle = this.type === 'Ba' ? '#3b82f6' : (this.type === 'Sr' ? '#a855f7' : '#34d399');
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

        capsule(leftStart,  {x: cX, y: mergeY}, tubeArmWidth, '#252838', '#3d4258');
        capsule(rightStart, {x: cX, y: mergeY}, tubeArmWidth, '#252838', '#3d4258');
        capsule({x: cX, y: mergeY - 10}, {x: cX, y: tubeBottom}, tubeHalf * 2, '#252838', '#3d4258');

        ctx.fillStyle = '#e5e7eb'; ctx.font = 'bold 12px Segoe UI'; ctx.textAlign = 'left';
        ctx.fillText('Air Formasi (Ba, Sr)', leftStart.x - 20, leftStart.y - 12);
        ctx.textAlign = 'right';
        ctx.fillText('Air Laut (SO4)', rightStart.x + 20, rightStart.y - 12);

        // kerak: dinding KIRI & KANAN menumpuk ke arah tengah (bukan dari dasar ke atas)
        for (let y = mergeY; y <= tubeBottom; y += 2) {
            let idx = idxOf(y);
            let thL = scaleArrL[idx], thR = scaleArrR[idx];
            if (thL > 0.3) {
                ctx.fillStyle = blendColor(ORANGE, YELLOW, colorArrL[idx]);
                ctx.fillRect(cX - tubeHalf, y, thL, 2.2);
            }
            if (thR > 0.3) {
                ctx.fillStyle = blendColor(ORANGE, YELLOW, colorArrR[idx]);
                ctx.fillRect(cX + tubeHalf - thR, y, thR, 2.2);
            }
        }

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
        let r = parseInt(slRasio.value);
        let kBa = parseInt(slBa.value);
        let kSO4 = parseInt(slSO4.value);
        let peakX = (kBa + kSO4) > 0 ? 100 * kBa / (kBa + kSO4) : 50;
        let peakY = (kBa / 100) * (kSO4 / 100) * 100;
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

        cctx.strokeStyle = '#262a38'; cctx.fillStyle = '#6b7086'; cctx.font = '10px Segoe UI'; cctx.textAlign = 'right';
        for (let v = 0; v <= yMax; v += 10) {
            let y = padT + h - (v / yMax) * h;
            cctx.beginPath(); cctx.moveTo(padL, y); cctx.lineTo(padL + w, y); cctx.stroke();
            cctx.fillText(v, padL - 6, y + 3);
        }

        function xPos(pct) { return padL + (pct / 100) * w; }
        function yPos(val) { return padT + h - (Math.min(val, yMax) / yMax) * h; }

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

        let mx = xPos(m.r), my = yPos(m.massa);
        cctx.beginPath(); cctx.arc(mx, my, 5, 0, Math.PI * 2);
        cctx.fillStyle = '#f5a623'; cctx.fill();
        cctx.strokeStyle = '#fff'; cctx.lineWidth = 1.5; cctx.stroke();

        cctx.fillStyle = '#f4f5f7'; cctx.font = 'bold 11px Segoe UI'; cctx.textAlign = 'center';
        cctx.fillText('Massa: ' + m.massa.toFixed(1), mx, my - 12);
    }

    function processSystem(m) {
        let spawnFormasi = (1 - m.r / 100) * (m.kBa / 100);
        let spawnSO4 = (m.r / 100) * (m.kSO4 / 100);

        if (Math.random() < spawnFormasi * 0.9) {
            let sy = leftStart.y + (Math.random() - 0.5) * 30;
            let sx = leftStart.x + (Math.random() - 0.5) * 20;
            let dx = cX - sx, dy = mergeY - sy;
            let ang = Math.atan2(dy, dx), sp = 2.2 + Math.random() * 1.4;
            let ionType = Math.random() < 0.72 ? 'Ba' : 'Sr'; // Ba dominan, Sr minoritas
            particles.push(new Particle(ionType, sx, sy, Math.cos(ang) * sp, Math.sin(ang) * sp));
        }
        if (Math.random() < spawnSO4 * 0.9) {
            let sy = rightStart.y + (Math.random() - 0.5) * 30;
            let sx = rightStart.x + (Math.random() - 0.5) * 20;
            let dx = cX - sx, dy = mergeY - sy;
            let ang = Math.atan2(dy, dx), sp = 2.2 + Math.random() * 1.4;
            particles.push(new Particle('SO4', sx, sy, Math.cos(ang) * sp, Math.sin(ang) * sp));
        }

        let nucleationProb = Math.min(m.massa / 50, 1) * 0.6;
        if (nucleationProb > 0) {
            for (let i = 0; i < particles.length; i++) {
                let p1 = particles[i];
                if (!p1.active || p1.type === 'Scale' || p1.y < mergeY - 40) continue;
                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    if (!p2.active || p2.type === 'Scale' || p2.y < mergeY - 40) continue;

                    let cation = null;
                    if (p1.type === 'SO4' && (p2.type === 'Ba' || p2.type === 'Sr')) cation = p2.type;
                    else if (p2.type === 'SO4' && (p1.type === 'Ba' || p1.type === 'Sr')) cation = p1.type;
                    if (!cation) continue;

                    let dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                    if (dist < 16 && Math.random() < nucleationProb) {
                        p1.active = false; p2.active = false;
                        let nx = (p1.x + p2.x) / 2, ny = Math.max((p1.y + p2.y) / 2, mergeY);
                        let kind = cation === 'Ba' ? 'BaSO4' : 'SrSO4';
                        particles.push(new Particle('Scale', nx, ny, 0, 0.9, kind));
                        break;
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

        let blockagePct = (maxBlockagePx() / (tubeHalf * 2)) * 100;
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
        scaleArrL.fill(0); scaleArrR.fill(0);
        colorArrL.fill(0); colorArrR.fill(0);
        flashEffect = 20;
    });

    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=1150, scrolling=False)
