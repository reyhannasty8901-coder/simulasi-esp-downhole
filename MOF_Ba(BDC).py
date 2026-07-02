import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulasi Adsorpsi MOF Ba-BDC + PCA", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 0.5rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Chemisorption Ba-BDC MOF + PCA</title>
    <style>
        :root {
            --bg: #0e1117;
            --panel: #1e212b;
            --text: #fafafa;
            --ba-color: #3b82f6;    /* Barium */
            --so4-color: #eab308;   /* Sulfat */
            --oh-color: #ec4899;    /* Hidroksida */
            --cl-color: #94a3b8;    /* Klorida (kompetitor, tidak terikat) */
            --poly-color: #334155;  /* Matriks Polimer */
            --pca-color: #22d3ee;   /* Ligan PCA (aksen) */
        }
        * { box-sizing: border-box; }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        .main-container {
            width: 100%; max-width: 1400px; display: grid; grid-template-columns: minmax(0,1fr) 380px; gap: 15px;
        }
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; gap: 10px;
            min-width: 0;
        }
        canvas { background: #0b0f19; border-radius: 8px; width: 100%; height: auto; display: block; }

        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px;
            max-height: 880px; overflow-y: auto;
        }
        .control-section { border: 1px solid #334155; padding: 12px; border-radius: 8px; background: #1e293b; }
        .control-title { font-size: 0.85rem; font-weight: bold; color: #94a3b8; margin-bottom: 8px; border-bottom: 1px solid #475569; padding-bottom: 5px; }

        .slider-group label { font-size: 0.8rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 5px;}
        input[type=range] { width: 100%; margin: 5px 0 10px 0; accent-color: #3b82f6; }

        select { width: 100%; padding: 8px; background: #0f172a; color: white; border: 1px solid #475569; border-radius: 6px; font-weight: bold; margin-bottom: 8px; outline: none; }
        select option { background: #0f172a; color: #f1f5f9; }

        .mech-info { font-size: 0.74rem; color: #cbd5e1; line-height: 1.5; background: #0f172a; border: 1px solid #164e63; border-radius: 6px; padding: 8px 10px; margin-top: 4px; }
        .mech-info b { color: #67e8f9; }
        .mech-info.hidden { display: none; }

        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }
        .metric-card { background: #0f172a; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #334155; }
        .metric-title { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.2rem; font-weight: bold; margin-top: 3px; color: #f8fafc; }

        .alert { color: #ef4444 !important; }
        .safe { color: #10b981 !important; }
        .warn { color: #f59e0b !important; }

        .badge { font-size: 0.72rem; text-align:center; padding: 6px; border-radius: 6px; margin-top: 8px; font-weight: 600; display:none; }
        .badge.on { background: rgba(34,211,238,0.12); color: #67e8f9; border: 1px solid #164e63; display:block; }

        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; font-size: 0.74rem; padding: 10px; background: #1e293b; border-radius: 8px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink:0; }

        button { background:#dc2626; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 5px; transition: 0.2s;}
        button:hover { background: #b91c1c; }
    </style>
</head>
<body>

    <h3 style="margin: 0 0 10px 0; color: #f1f5f9; text-align:center;">Visualisasi Mikroskopis: Adsorpsi MOF Ba-BDC &amp; Rekayasa Ligan PCA</h3>

    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="900" height="440"></canvas>

            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Sisi Aktif MOF (Ba²⁺)</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Ion Sulfat (SO₄²⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--oh-color);"></div> Ion Hidroksida (OH⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--cl-color);"></div> Ion Klorida (Cl⁻, kompetitor)</div>
                <div class="legend-item"><div class="dot" style="background:var(--poly-color); border-radius:2px;"></div> Matriks / Kerangka Ligan</div>
            </div>
        </div>

        <div class="control-panel">

            <div class="control-section" style="border-color: #3b82f6;">
                <div class="control-title" style="color: #60a5fa;">Desain Material Adsorben</div>
                <select id="selMOFType">
                    <option value="raw">Serbuk MOF Ba-BDC Asli (Jurnal Teoritis)</option>
                    <option value="pca">MOF Ba-BDC + PCA (Ligan Heteroleptik)</option>
                </select>
                <div class="mech-info" id="infoRaw">
                    Kerangka homoleptik Ba–BDC murni. Ion barium relatif terekspos, sehingga rentan diserang
                    OH⁻ pada air laut basa, dan node kristal dapat lepas ketika turbulensi aliran tinggi.
                </div>
                <div class="mech-info hidden" id="infoPCA">
                    <b>Sintesis heteroleptik</b> — PCA (Pikolilsianoasetamida) berkoordinasi bersama BDC pada
                    pusat Ba²⁺. Gugus donor nitrogen (piridin &amp; siano) berpotensi memberi
                    <b>perlindungan sterik</b> terhadap serangan OH⁻/H₂O, membentuk jaringan multi-titik yang
                    <b>lebih kaku</b> terhadap turbulensi, sekaligus memodulasi sisi aktif untuk
                    <b>afinitas &amp; selektivitas sulfat</b> yang lebih baik dibanding Cl⁻. <i>(Efek berbasis
                    hipotesis rekayasa ligan — bukan jaminan mutlak.)</i>
                </div>
                <div class="badge" id="badgeShield">🛡️ Perlindungan sterik aktif — OH⁻ sebagian besar dibelokkan</div>
            </div>

            <div class="control-section">
                <div class="control-title">Kondisi Lingkungan (Mekanika &amp; Kimia)</div>
                <div class="slider-group">
                    <label>Tekanan Laju Alir Air (Turbulensi) <span id="valFlow">Sedang</span></label>
                    <input type="range" id="slFlow" min="1" max="100" value="30">

                    <label>Tingkat Keasaman (pH Air) <span id="valPH">pH 2 (Asam)</span></label>
                    <input type="range" id="slPH" min="2" max="10" value="2" step="1">
                </div>
            </div>

            <div class="control-section" style="background: #0f172a; border-color: #475569;">
                <div class="control-title" style="color: #f8fafc; text-align:center;">DASHBOARD TERMODINAMIKA &amp; KINERJA</div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Kapasitas Adsorpsi (q_max)</div>
                        <div class="metric-value" id="valCap" style="color: #eab308;">0.0 mg/g</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Energi Adsorpsi (E)</div>
                        <div class="metric-value" id="valEnergy" style="color: #60a5fa;">0.0 kJ/mol</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Integritas Struktur 3D</div>
                        <div class="metric-value safe" id="valInteg">100%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Efisiensi Removal</div>
                        <div class="metric-value safe" id="valEff">100%</div>
                    </div>
                </div>
            </div>

            <button id="btnReset">SINTESIS ULANG MOF (Reset)</button>
        </div>
    </div>

<script>
    const canvas = document.getElementById('simCanvas'); const ctx = canvas.getContext('2d');

    // Palet warna asli (Canvas TIDAK bisa membaca var(--xxx) dari CSS, harus hex/rgb literal)
    const COLORS = {
        ba: '#3b82f6',
        so4: '#eab308',
        oh: '#ec4899',
        cl: '#94a3b8',
        poly: '#334155',
        pipe: '#334155',
        label: '#64748b',
        link: 'rgba(148, 163, 184, 0.3)',
        linkPCA: 'rgba(34, 211, 238, 0.35)'
    };

    const selMOFType = document.getElementById('selMOFType');
    const slFlow = document.getElementById('slFlow');
    const slPH = document.getElementById('slPH');
    const infoRaw = document.getElementById('infoRaw');
    const infoPCA = document.getElementById('infoPCA');
    const badgeShield = document.getElementById('badgeShield');

    const CW = canvas.width, CH = canvas.height;
    const zoneStartX = Math.round(CW * 0.40);
    const zoneEndX = Math.round(CW * 0.76);
    const zoneStartY = 85, zoneEndY = CH - 80;

    let mofNodes = [];
    let particles = [];
    let captureCount = 0;
    let initialNodes = 0;

    function isPCA() { return selMOFType.value === 'pca'; }

    function initMOF() {
        mofNodes = []; particles = []; captureCount = 0;
        let spacing = 36;

        for (let x = zoneStartX; x <= zoneEndX; x += spacing) {
            for (let y = zoneStartY; y <= zoneEndY; y += spacing) {
                let offsetX = (y % (spacing * 2) === 0) ? 0 : spacing / 2;
                if (x + offsetX <= zoneEndX) {
                    mofNodes.push({
                        x: x + offsetX, y: y,
                        state: 0, // 0: Kosong (Ba murni), 1: Terikat Sulfat, 2: Terblokir OH-
                        active: true,
                        baseX: x + offsetX, baseY: y
                    });
                }
            }
        }
        initialNodes = mofNodes.length;
        updateInfoPanels();
    }

    function updateInfoPanels() {
        infoRaw.classList.toggle('hidden', isPCA());
        infoPCA.classList.toggle('hidden', !isPCA());
    }

    class Particle {
        constructor(type) {
            this.type = type; // 'SO4' | 'OH' | 'Cl'
            this.x = 10 + Math.random() * 50;
            this.y = zoneStartY - 15 + Math.random() * (zoneEndY - zoneStartY + 30);

            let flow = parseInt(slFlow.value) / 10;
            this.vx = (flow * 0.8) + Math.random() * 2 + 1;
            this.vy = (Math.random() - 0.5) * 1.5;
            this.size = type === 'SO4' ? 4 : (type === 'Cl' ? 3.5 : 3);
            this.active = true;
        }

        update() {
            if (!this.active) return;

            this.x += this.vx;
            this.y += this.vy;

            if (this.y < zoneStartY - 25) { this.y = zoneStartY - 25; this.vy *= -1; }
            if (this.y > zoneEndY + 25) { this.y = zoneEndY + 25; this.vy *= -1; }

            // Klorida adalah kompetitor pasif: ukuran hidratnya tidak cocok dengan pori MOF,
            // jadi selalu lolos tanpa berinteraksi (menggambarkan selektivitas terhadap sulfat).
            if (this.type === 'Cl') return;

            if (this.x > zoneStartX - 30 && this.x < zoneEndX + 30) {
                this.x += (Math.random() - 0.5);

                // Radius interaksi sedikit lebih besar pada PCA -> modulasi sisi aktif
                let captureRadius = isPCA() ? 13.5 : 12;

                for (let i = 0; i < mofNodes.length; i++) {
                    let node = mofNodes[i];
                    if (!node.active || node.state !== 0) continue;

                    let dist = Math.sqrt((this.x - node.x) ** 2 + (this.y - node.y) ** 2);
                    if (dist < captureRadius) {
                        if (this.type === 'SO4') {
                            node.state = 1; this.active = false; captureCount++;
                            spawnEnergyFlash(node.x, node.y);
                            break;
                        } else if (this.type === 'OH') {
                            // Perlindungan sterik PCA: probabilitas OH- berhasil memblokir jauh lebih kecil
                            let blockProb = isPCA() ? 0.06 : 0.6;
                            if (Math.random() < blockProb) {
                                node.state = 2; this.active = false; break;
                            } else {
                                this.vy *= -1.4; this.vx *= 0.6; // dibelokkan / gagal menyerang
                            }
                        }
                    }
                }
            }
        }

        draw() {
            if (!this.active) return;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.type === 'SO4' ? COLORS.so4 : (this.type === 'OH' ? COLORS.oh : COLORS.cl);
            ctx.fill();
        }
    }

    let energyFlashes = [];
    function spawnEnergyFlash(x, y) {
        let baseEnergy = isPCA() ? (16.0 + Math.random()) : (15.0 + Math.random());
        energyFlashes.push({ x: x, y: y, radius: 2, alpha: 1.0, energy: baseEnergy.toFixed(1) });
    }

    function renderSystem() {
        ctx.fillStyle = '#0b0f19'; ctx.fillRect(0, 0, CW, CH);

        let pca = isPCA();

        ctx.strokeStyle = COLORS.pipe; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(0, 48); ctx.lineTo(CW, 48); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, CH - 30); ctx.lineTo(CW, CH - 30); ctx.stroke();

        ctx.fillStyle = COLORS.label; ctx.font = '12px Arial'; ctx.textAlign = 'left';
        ctx.fillText('Aliran Fluida Formasi / Air Laut', 15, 36);

        // Matriks / kerangka ligan tambahan tervisualisasi hanya untuk varian PCA
        if (pca) {
            ctx.fillStyle = 'rgba(34, 211, 238, 0.06)';
            ctx.fillRect(zoneStartX - 15, zoneStartY - 20, (zoneEndX - zoneStartX) + 30, (zoneEndY - zoneStartY) + 40);
            ctx.strokeStyle = 'rgba(34, 211, 238, 0.18)'; ctx.lineWidth = 1;
            for (let i = zoneStartX; i <= zoneEndX; i += 18) {
                ctx.beginPath(); ctx.moveTo(i, zoneStartY - 20); ctx.lineTo(i, zoneEndY + 20); ctx.stroke();
            }
            ctx.font = 'bold 11px Arial'; ctx.fillStyle = '#67e8f9'; ctx.textAlign = 'center';
            ctx.fillText('Jaringan Heteroleptik Ba-BDC + PCA', (zoneStartX + zoneEndX) / 2, zoneStartY - 26);
            ctx.textAlign = 'left';
        } else {
            ctx.font = 'bold 11px Arial'; ctx.fillStyle = '#64748b'; ctx.textAlign = 'center';
            ctx.fillText('Kerangka Ba-BDC (Homoleptik)', (zoneStartX + zoneEndX) / 2, zoneStartY - 26);
            ctx.textAlign = 'left';
        }

        // Kerusakan struktural akibat turbulensi: jauh lebih jarang terjadi pada varian PCA
        // (jaringan multi-titik lebih kaku / structural rigidity)
        let flowRate = parseInt(slFlow.value);
        if (flowRate > 40) {
            let ripProb = pca ? (flowRate / 1000) * 0.12 : (flowRate / 1000);
            if (Math.random() < ripProb) {
                let activeNodes = mofNodes.filter(n => n.active);
                if (activeNodes.length > 0) {
                    let ripNode = activeNodes[Math.floor(Math.random() * activeNodes.length)];
                    ripNode.active = false;
                }
            }
        }

        // Ligan penghubung antar node (jarak koneksi lebih jauh pada PCA -> jaringan lebih rapat/kaku)
        let linkDist = pca ? 46 : 40;
        ctx.strokeStyle = pca ? COLORS.linkPCA : COLORS.link;
        ctx.lineWidth = pca ? 1.8 : 1.2;
        for (let i = 0; i < mofNodes.length; i++) {
            let n1 = mofNodes[i];
            if (!n1.active) continue;

            // Getar fisik jika aliran sangat kuat, jauh lebih teredam pada PCA (kerangka kaku)
            let jitterFactor = pca ? 0.15 : 1;
            if (flowRate > 50) {
                n1.x = n1.baseX + (Math.random() - 0.5) * (flowRate / 20) * jitterFactor;
                n1.y = n1.baseY + (Math.random() - 0.5) * (flowRate / 20) * jitterFactor;
            } else {
                n1.x = n1.baseX; n1.y = n1.baseY;
            }

            for (let j = i + 1; j < mofNodes.length; j++) {
                let n2 = mofNodes[j];
                if (!n2.active) continue;
                let dist = Math.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2);
                if (dist < linkDist) {
                    ctx.beginPath(); ctx.moveTo(n1.x, n1.y); ctx.lineTo(n2.x, n2.y); ctx.stroke();
                }
            }
        }

        // Node Barium (sisi aktif)
        for (let i = 0; i < mofNodes.length; i++) {
            let n = mofNodes[i];
            if (!n.active) continue;

            ctx.beginPath();
            if (n.state === 0) {
                ctx.arc(n.x, n.y, 4, 0, Math.PI * 2); ctx.fillStyle = COLORS.ba; ctx.fill();
            } else if (n.state === 1) {
                ctx.arc(n.x, n.y, 6, 0, Math.PI * 2); ctx.fillStyle = COLORS.so4; ctx.fill();
                ctx.beginPath(); ctx.arc(n.x, n.y, 3, 0, Math.PI * 2); ctx.fillStyle = COLORS.ba; ctx.fill();
            } else if (n.state === 2) {
                ctx.arc(n.x, n.y, 5, 0, Math.PI * 2); ctx.fillStyle = COLORS.oh; ctx.fill();
            }
        }

        // Efek energi termodinamika saat presipitasi terjadi
        for (let i = energyFlashes.length - 1; i >= 0; i--) {
            let f = energyFlashes[i];
            ctx.beginPath(); ctx.arc(f.x, f.y, f.radius, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(234, 179, 8, ${f.alpha})`; ctx.lineWidth = 2; ctx.stroke();
            f.radius += 0.5; f.alpha -= 0.05;
            if (f.alpha <= 0) {
                energyFlashes.splice(i, 1);
            } else {
                ctx.fillStyle = `rgba(255,255,255, ${f.alpha})`; ctx.font = '9px Arial';
                ctx.fillText(f.energy + ' kJ', f.x + 8, f.y - 8);
            }
        }
    }

    function spawnIons() {
        let flow = parseInt(slFlow.value);
        let ph = parseInt(slPH.value);

        if (Math.random() < flow / 100) particles.push(new Particle('SO4'));

        let ohProb = 0;
        if (ph > 7) ohProb = (ph - 7) * 0.1;
        else if (ph > 4) ohProb = 0.02;
        if (Math.random() < ohProb * (flow / 30)) particles.push(new Particle('OH'));

        // Klorida berlimpah di air laut (kompetitor non-selektif), muncul cukup sering
        if (Math.random() < flow / 55) particles.push(new Particle('Cl'));
    }

    function updateDashboard() {
        let flow = parseInt(slFlow.value);
        let ph = parseInt(slPH.value);
        let pca = isPCA();

        document.getElementById('valFlow').innerText = flow < 40 ? 'Rendah/Aman' : (flow > 70 ? 'Sangat Tinggi (Merusak)' : 'Keras (Turbulen)');
        document.getElementById('valPH').innerText = `pH ${ph} ` + (ph < 6 ? '(Asam)' : (ph > 7 ? '(Basa/Banyak OH⁻)' : '(Netral)'));

        let activeNodes = mofNodes.filter(n => n.active);
        let boundSO4 = mofNodes.filter(n => n.active && n.state === 1).length;
        let blockedOH = mofNodes.filter(n => n.active && n.state === 2).length;

        let structuralIntegrity = initialNodes > 0 ? (activeNodes.length / initialNodes) * 100 : 100;

        // Bonus kapasitas ringan pada PCA: merepresentasikan modulasi sisi aktif / afinitas sulfat
        let capBonus = pca ? 1.12 : 1.0;
        let qMaxCurrent = initialNodes > 0 ? (boundSO4 / initialNodes) * 549.5 * capBonus : 0;

        let lostCapacity = initialNodes > 0 ? ((blockedOH + (initialNodes - activeNodes.length)) / initialNodes) * 100 : 0;
        let eff = Math.max(0, 100 - lostCapacity);

        let currentEnergy = boundSO4 > 0 ? (pca ? (16.0 + Math.random()) : (15.0 + Math.random())).toFixed(1) : "0.0";

        document.getElementById('valCap').innerText = qMaxCurrent.toFixed(1) + ' mg/g';
        document.getElementById('valEnergy').innerText = currentEnergy + ' kJ/mol';

        let elInteg = document.getElementById('valInteg');
        elInteg.innerText = structuralIntegrity.toFixed(0) + '%';
        elInteg.className = 'metric-value ' + (structuralIntegrity > 80 ? 'safe' : (structuralIntegrity > 50 ? 'warn' : 'alert'));

        let elEff = document.getElementById('valEff');
        elEff.innerText = eff.toFixed(0) + '%';
        elEff.className = 'metric-value ' + (eff > 80 ? 'safe' : (eff > 50 ? 'warn' : 'alert'));

        badgeShield.classList.toggle('on', pca && ph > 7);
    }

    function loop() {
        renderSystem();
        spawnIons();

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.update(); p.draw();
            if (p.x > CW + 10 || !p.active) particles.splice(i, 1);
        }
        if (particles.length > 700) particles.splice(0, particles.length - 700);

        updateDashboard();
        requestAnimationFrame(loop);
    }

    selMOFType.addEventListener('change', () => { updateInfoPanels(); initMOF(); });
    document.getElementById('btnReset').addEventListener('click', initMOF);

    initMOF();
    loop();
</script>
</body>
</html>
"""

components.html(html_app, height=880, scrolling=False)

with st.expander("ℹ️ Mekanisme Ligan PCA (Pikolilsianoasetamida) pada MOF Ba-BDC", expanded=False):
    st.markdown("""
Ligan PCA berpotensi meningkatkan performa MOF Ba-BDC melalui tiga jalur mekanisme (bersifat hipotesis
rekayasa material, belum tentu bekerja identik di kondisi nyata tanpa validasi eksperimen):

**1. Stabilitas Hidrolitik (Ketahanan terhadap Air Laut)**
MOF berbasis barium murni rentan terhadap lingkungan basa (pH air laut) yang dapat meruntuhkan kerangka
kristal. PCA memiliki sisi donor nitrogen (cincin piridin & gugus siano) yang, ketika berkoordinasi
bersama BDC pada Ba²⁺ (sintesis heteroleptik), berpotensi menciptakan **efek penutup sterik** di sekitar
logam pusat — mempersulit molekul air atau ion OH⁻ untuk menyerang ikatan koordinasi logam-ligan.

**2. Kerangka yang Lebih Kaku (Structural Rigidity)**
Dengan PCA sebagai ligan pendamping, ikatan tambahan lewat atom nitrogen (selain oksigen karboksilat
BDC) dapat membentuk jaringan koordinasi multi-titik tiga dimensi yang lebih kaku secara mekanis —
mempertahankan porositas material meski berada di bawah tekanan operasional/turbulensi tinggi dalam
unit SRU industri.

**3. Modulasi Sisi Aktif untuk Selektivitas Sulfat**
Gugus amida dan siano pada PCA dapat berfungsi sebagai sisi aktif tambahan yang berinteraksi secara
spesifik dengan anion sulfat lewat ikatan hidrogen/elektrostatik. Modulasi ligan ini berpotensi membentuk
pori dengan ukuran yang lebih sesuai untuk ion sulfat terhidrasi, meningkatkan selektivitas dibanding
ion lain yang berlimpah di air laut seperti klorida (Cl⁻).

Coba bandingkan **"Serbuk MOF Ba-BDC Asli"** vs **"MOF Ba-BDC + PCA"** pada slider pH tinggi (basa) dan
laju alir tinggi (turbulen) di simulasi atas — perhatikan perbedaan pada Integritas Struktur dan
Efisiensi Removal.
    """)
