import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulasi Adsorpsi MOF Ba-BDC", layout="wide", initial_sidebar_state="collapsed")
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
    <title>Chemisorption Ba-BDC MOF</title>
    <style>
        :root {
            --bg: #0e1117;
            --panel: #1e212b;
            --text: #fafafa;
            --ba-color: #3b82f6;   /* Barium */
            --so4-color: #eab308;  /* Sulfat */
            --oh-color: #ec4899;   /* Hidroksida */
            --poly-color: #334155; /* Matriks Polimer */
        }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        .main-container {
            width: 100%; max-width: 1350px; display: grid; grid-template-columns: 1fr 380px; gap: 15px;
        }
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; gap: 10px;
        }
        canvas { background: #0b0f19; border-radius: 8px; width: 100%; }
        
        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px;
        }
        .control-section { border: 1px solid #334155; padding: 12px; border-radius: 8px; background: #1e293b; }
        .control-title { font-size: 0.85rem; font-weight: bold; color: #94a3b8; margin-bottom: 8px; border-bottom: 1px solid #475569; padding-bottom: 5px; }
        
        .slider-group label { font-size: 0.8rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 5px;}
        input[type=range] { width: 100%; margin: 5px 0 10px 0; accent-color: #3b82f6; }
        
        select { width: 100%; padding: 8px; background: #0f172a; color: white; border: 1px solid #475569; border-radius: 6px; font-weight: bold; margin-bottom: 10px; outline: none; }
        
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }
        .metric-card { background: #0f172a; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #334155; }
        .metric-title { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.25rem; font-weight: bold; margin-top: 3px; color: #f8fafc; }
        
        .alert { color: #ef4444 !important; }
        .safe { color: #10b981 !important; }
        .warn { color: #f59e0b !important; }
        
        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; font-size: 0.75rem; padding: 10px; background: #1e293b; border-radius: 8px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        
        button { background:#dc2626; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 5px; transition: 0.2s;}
        button:hover { background: #b91c1c; }
    </style>
</head>
<body>

    <h3 style="margin: 0 0 10px 0; color: #f1f5f9;">Visualisasi Mikroskopis: Adsorpsi MOF Ba-BDC & Tantangan Operasional</h3>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="420"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Sisi Aktif MOF (Ba²⁺)</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Ion Sulfat (SO₄²⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--oh-color);"></div> Ion Hidroksida (OH⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--poly-color); border-radius:2px;"></div> Matriks Polimer Membran</div>
            </div>
        </div>
        
        <div class="control-panel">
            
            <div class="control-section" style="border-color: #3b82f6;">
                <div class="control-title" style="color: #60a5fa;">Desain Material Adsorben</div>
                <select id="selMOFType">
                    <option value="raw">Serbuk MOF Asli (Jurnal Teoritis)</option>
                    <option value="composite">Membran Komposit (Upgrade Rekayasa)</option>
                </select>
            </div>

            <div class="control-section">
                <div class="control-title">Kondisi Lingkungan (Mekanika & Kimia)</div>
                <div class="slider-group">
                    <label>Tekanan Laju Alir Air (Turbulensi) <span id="valFlow">Sedang</span></label>
                    <input type="range" id="slFlow" min="1" max="100" value="30">
                    
                    <label>Tingkat Keasaman (pH Air) <span id="valPH">pH 2 (Asam)</span></label>
                    <input type="range" id="slPH" min="2" max="10" value="2" step="1">
                </div>
            </div>
            
            <div class="control-section" style="background: #0f172a; border-color: #475569;">
                <div class="control-title" style="color: #f8fafc; text-align:center;">DASHBOARD TERMODINAMIKA & KINERJA</div>
                
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
    
    const selMOFType = document.getElementById('selMOFType');
    const slFlow = document.getElementById('slFlow');
    const slPH = document.getElementById('slPH');
    
    // Grid MOF (3D Orthorhombic representation)
    let mofNodes = [];
    let particles = [];
    let captureCount = 0;
    let initialNodes = 0;
    
    function initMOF() {
        mofNodes = []; particles = []; captureCount = 0;
        let isComposite = selMOFType.value === 'composite';
        
        // Membangun matriks jaringan MOF Ba-BDC
        let startX = 350, endX = 650;
        let startY = 80, endY = 340;
        let spacing = 35;
        
        for (let x = startX; x <= endX; x += spacing) {
            for (let y = startY; y <= endY; y += spacing) {
                // Posisi sedikit zigzag untuk meniru struktur kristal
                let offsetX = (y % (spacing*2) === 0) ? 0 : spacing/2;
                if (x + offsetX <= endX) {
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
    }
    
    class Particle {
        constructor(type) {
            this.type = type; // 'SO4' or 'OH'
            this.x = 10 + Math.random() * 50;
            this.y = 80 + Math.random() * 260;
            
            let flow = parseInt(slFlow.value) / 10;
            this.vx = (flow * 0.8) + Math.random() * 2 + 1;
            this.vy = (Math.random() - 0.5) * 1.5;
            this.size = type === 'SO4' ? 4 : 3;
            this.active = true;
        }
        
        update() {
            if (!this.active) return;
            
            let flow = parseInt(slFlow.value) / 10;
            this.x += this.vx;
            this.y += this.vy;
            
            // Pantulan dinding pipa atas bawah
            if (this.y < 60) { this.y = 60; this.vy *= -1; }
            if (this.y > 360) { this.y = 360; this.vy *= -1; }
            
            // Memasuki zona MOF
            if (this.x > 320 && this.x < 680) {
                this.x += (Math.random() - 0.5); // Efek menembus pori
                
                // Deteksi interaksi dengan sisi aktif (Ba)
                for (let i = 0; i < mofNodes.length; i++) {
                    let node = mofNodes[i];
                    if (!node.active || node.state !== 0) continue;
                    
                    let dist = Math.sqrt((this.x - node.x)**2 + (this.y - node.y)**2);
                    if (dist < 12) {
                        let isComposite = selMOFType.value === 'composite';
                        
                        if (this.type === 'SO4') {
                            // Chemisorption Presipitasi terjadi
                            node.state = 1; this.active = false; captureCount++;
                            drawEnergyFlash(node.x, node.y);
                            break;
                        } else if (this.type === 'OH') {
                            // Jika MOF Asli, OH- memblokir situs (interferensi basa)
                            if (!isComposite) {
                                if (Math.random() < 0.6) {
                                    node.state = 2; this.active = false; break;
                                }
                            } else {
                                // Jika MOF Modifikasi, menolak OH-
                                this.vy *= -1.5; this.vx *= 0.5; // Terlempar
                            }
                        }
                    }
                }
            }
        }
        
        draw() {
            if (!this.active) return;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
            ctx.fillStyle = this.type === 'SO4' ? 'var(--so4-color)' : 'var(--oh-color)';
            ctx.fill();
        }
    }
    
    let energyFlashes = [];
    function drawEnergyFlash(x, y) {
        energyFlashes.push({x: x, y: y, radius: 2, alpha: 1.0});
    }
    
    function renderSystem() {
        ctx.fillStyle = '#0b0f19'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        let isComposite = selMOFType.value === 'composite';
        
        // Pipa Saluran
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(0, 50); ctx.lineTo(850, 50); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, 370); ctx.lineTo(850, 370); ctx.stroke();
        
        ctx.fillStyle = '#64748b'; ctx.font = '12px Arial';
        ctx.fillText('Aliran Fluida Formasi / Air Laut', 20, 40);
        
        // Render Matriks Polimer Jika Komposit
        if (isComposite) {
            ctx.fillStyle = 'rgba(51, 65, 85, 0.4)';
            ctx.fillRect(330, 60, 340, 300);
            ctx.strokeStyle = '#475569'; ctx.lineWidth = 1;
            for(let i=330; i<=670; i+=20) {
                ctx.beginPath(); ctx.moveTo(i, 60); ctx.lineTo(i, 360); ctx.stroke();
            }
        }
        
        // Dinamika Kerusakan Struktur MOF oleh Turbulensi
        let flowRate = parseInt(slFlow.value);
        if (!isComposite && flowRate > 40) {
            // MOF serbuk hancur terbawa arus kuat
            if (Math.random() < (flowRate / 1000)) {
                let activeNodes = mofNodes.filter(n => n.active);
                if (activeNodes.length > 0) {
                    let ripNode = activeNodes[Math.floor(Math.random() * activeNodes.length)];
                    ripNode.active = false;
                }
            }
        }
        
        // Render Ligan Tereftalat (Garis penghubung)
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)'; ctx.lineWidth = 1.5;
        for (let i = 0; i < mofNodes.length; i++) {
            let n1 = mofNodes[i];
            if (!n1.active) continue;
            
            // Getar fisik jika aliran sangat kuat (Hanya powder)
            if (!isComposite && flowRate > 50) {
                n1.x = n1.baseX + (Math.random() - 0.5) * (flowRate/20);
                n1.y = n1.baseY + (Math.random() - 0.5) * (flowRate/20);
            } else {
                n1.x = n1.baseX; n1.y = n1.baseY; // Stabil
            }

            for (let j = i + 1; j < mofNodes.length; j++) {
                let n2 = mofNodes[j];
                if (!n2.active) continue;
                let dist = Math.sqrt((n1.x-n2.x)**2 + (n1.y-n2.y)**2);
                if (dist < 40) {
                    ctx.beginPath(); ctx.moveTo(n1.x, n1.y); ctx.lineTo(n2.x, n2.y); ctx.stroke();
                }
            }
        }
        
        // Render Node Barium (Sisi Aktif)
        for (let i = 0; i < mofNodes.length; i++) {
            let n = mofNodes[i];
            if (!n.active) continue;
            
            ctx.beginPath();
            if (n.state === 0) {
                ctx.arc(n.x, n.y, 4, 0, Math.PI*2); ctx.fillStyle = 'var(--ba-color)';
            } else if (n.state === 1) {
                // Chemisorption (Ba terikat SO4)
                ctx.arc(n.x, n.y, 6, 0, Math.PI*2); ctx.fillStyle = 'var(--so4-color)';
                ctx.fill(); ctx.beginPath(); ctx.arc(n.x, n.y, 3, 0, Math.PI*2); ctx.fillStyle = 'var(--ba-color)';
            } else if (n.state === 2) {
                // Terblokir basa (OH-)
                ctx.arc(n.x, n.y, 5, 0, Math.PI*2); ctx.fillStyle = 'var(--oh-color)';
            }
            ctx.fill();
        }
        
        // Render Efek Energi Termodinamika (15.0 - 16.0 kJ/mol)
        for(let i=energyFlashes.length-1; i>=0; i--) {
            let f = energyFlashes[i];
            ctx.beginPath(); ctx.arc(f.x, f.y, f.radius, 0, Math.PI*2);
            ctx.strokeStyle = `rgba(234, 179, 8, ${f.alpha})`; ctx.lineWidth = 2; ctx.stroke();
            f.radius += 0.5; f.alpha -= 0.05;
            if (f.alpha <= 0) energyFlashes.splice(i, 1);
            else {
                ctx.fillStyle = `rgba(255,255,255, ${f.alpha})`; ctx.font = '9px Arial';
                ctx.fillText('15.5 kJ', f.x + 8, f.y - 8);
            }
        }
    }
    
    function spawnIons() {
        let flow = parseInt(slFlow.value);
        let ph = parseInt(slPH.value);
        
        // Peluang SO4 muncul sebanding dengan flow
        if (Math.random() < flow / 100) particles.push(new Particle('SO4'));
        
        // Basa (pH > 7) memunculkan ion Hidroksida (OH-) yang sangat mengganggu
        let ohProb = 0;
        if (ph > 7) ohProb = (ph - 7) * 0.1;
        else if (ph > 4) ohProb = 0.02;
        
        if (Math.random() < ohProb * (flow/30)) particles.push(new Particle('OH'));
    }
    
    function updateDashboard() {
        let flow = parseInt(slFlow.value);
        let ph = parseInt(slPH.value);
        
        document.getElementById('valFlow').innerText = flow < 40 ? 'Rendah/Aman' : (flow > 70 ? 'Sangat Tinggi (Merusak)' : 'Keras (Turbulen)');
        document.getElementById('valPH').innerText = `pH ${ph} ` + (ph < 6 ? '(Asam)' : (ph > 7 ? '(Basa/Banyak OH⁻)' : '(Netral)'));
        
        // Perhitungan Kapasitas (Maksimal Teori = 549.5 mg/g)
        let activeNodes = mofNodes.filter(n => n.active);
        let boundSO4 = mofNodes.filter(n => n.active && n.state === 1).length;
        let blockedOH = mofNodes.filter(n => n.active && n.state === 2).length;
        
        let structuralIntegrity = (activeNodes.length / initialNodes) * 100;
        let qMaxCurrent = (boundSO4 / initialNodes) * 549.5; 
        
        // Efisiensi penangkapan
        let eff = 100;
        let lostCapacity = ((blockedOH + (initialNodes - activeNodes.length)) / initialNodes) * 100;
        eff = Math.max(0, 100 - lostCapacity);
        
        // Indikator Energi
        let currentEnergy = boundSO4 > 0 ? (15.0 + Math.random()).toFixed(1) : "0.0";
        
        // Terapkan ke HTML
        document.getElementById('valCap').innerText = qMaxCurrent.toFixed(1) + ' mg/g';
        document.getElementById('valEnergy').innerText = currentEnergy + ' kJ/mol';
        
        let elInteg = document.getElementById('valInteg');
        elInteg.innerText = structuralIntegrity.toFixed(0) + '%';
        elInteg.className = structuralIntegrity > 80 ? 'metric-value safe' : 'metric-value alert';
        
        let elEff = document.getElementById('valEff');
        elEff.innerText = eff.toFixed(0) + '%';
        elEff.className = eff > 80 ? 'metric-value safe' : (eff > 50 ? 'metric-value warn' : 'metric-value alert');
    }
    
    function loop() {
        renderSystem();
        spawnIons();
        
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.update(); p.draw();
            if (p.x > 860 || !p.active) particles.splice(i, 1);
        }
        
        updateDashboard();
        requestAnimationFrame(loop);
    }
    
    selMOFType.addEventListener('change', initMOF);
    document.getElementById('btnReset').addEventListener('click', initMOF);
    
    initMOF();
    loop();
</script>
</body>
</html>
"""

components.html(html_app, height=780, scrolling=False)
