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
            --so4-color: #eab308;  /* Kuning (Sulfate) */
            --water-color: #38bdf8; /* Biru Muda (Air/NaCl) */
            --membrane-color: #2dd4bf; /* Tosca (Membran NF) */
            --foul-color: #a1a1aa; /* Abu-abu (Fouling) */
        }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        h2 { margin: 0 0 15px 0; font-weight: 600; text-align: center; font-size: 1.5rem; color: #f8fafc; }
        
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
        input[type=range] { width: 100%; margin: 5px 0 10px 0; accent-color: #38bdf8; }
        
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 5px; }
        .metric-card { background: #0f172a; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #334155; }
        .metric-title { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.3rem; font-weight: bold; margin-top: 5px; color: #f8fafc; }
        
        .alert { color: #ef4444 !important; }
        .safe { color: #10b981 !important; }
        .warn { color: #f59e0b !important; }
        
        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-size: 0.8rem; padding: 10px; background: #1e293b; border-radius: 8px; margin-top:15px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        
        button { background:#38bdf8; color:#0f172a; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px; transition: 0.3s;}
        button:hover { background: #0284c7; color: white;}
    </style>
</head>
<body>

    <h2>Unit Presipitasi: Nanofiltration (Sulfate Removal)</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="500"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--water-color);"></div> Air & Ion Monovalen (Na⁺, Cl⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--so4-color); border-radius:2px;"></div> Ion Sulfat Divalen (SO₄²⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--foul-color); border-radius:2px;"></div> Fouling (Penyumbatan Membran)</div>
            </div>
        </div>
        
        <div class="control-panel">
            
            <div class="control-section">
                <div class="control-title">Kondisi Air Laut (Feed Stream)</div>
                <div class="slider-group">
                    <label>Tekanan Umpan (Feed Pressure) <span id="valPress">300 psi</span></label>
                    <input type="range" id="slPress" min="100" max="600" value="300" step="10">
                    <label>Konsentrasi Sulfat <span id="valSO4">2800 ppm</span></label>
                    <input type="range" id="slSO4" min="500" max="4000" value="2800" step="100">
                </div>
            </div>
            
            <div class="control-section">
                <div class="control-title">Kondisi Membran Nanofiltrasi</div>
                <div class="slider-group">
                    <label>Integritas Membran (Pore Size) <span id="valInteg">Optimal</span></label>
                    <input type="range" id="slInteg" min="70" max="100" value="99">
                </div>
            </div>
            
            <div class="control-section" style="background: #0f172a; border-color: #475569;">
                <div class="control-title" style="color: #f8fafc;">Kinerja Sistem SRU</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Sulfate Rejection</div>
                        <div class="metric-value safe" id="valRej">99.0%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Kondisi Fouling</div>
                        <div class="metric-value" id="valFoul">0%</div>
                    </div>
                </div>
                
                <div style="margin-top: 10px; padding: 10px; background: #1e293b; border-radius: 6px; text-align: center; border: 1px solid #38bdf8;">
                    <div class="metric-title" style="color: #bae6fd;">Produksi Air Injeksi (Permeate Flux)</div>
                    <div class="metric-value safe" id="valFlux">100%</div>
                </div>
            </div>
            
            <button id="btnCIP">CIP (Clean-in-Place) Backwash</button>
        </div>
    </div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    
    // Sliders
    const slPress = document.getElementById('slPress');
    const slSO4 = document.getElementById('slSO4');
    const slInteg = document.getElementById('slInteg');
    
    // Geometry
    const mStartX = 200; // Membran mulai
    const mEndX = 750;   // Membran berakhir
    const mY = 250;      // Posisi Y Membran
    
    let particles = [];
    let foulingArray = new Array(550).fill(0); // Array Fouling dari X: 200 ke 750
    
    let totalFouling = 0;
    let so4Rejected = 0;
    let so4Passed = 0;
    let flashEffect = 0;
    
    class Particle {
        constructor(type, startX, startY) {
            this.type = type; // 'SO4' or 'Water'
            this.x = startX; 
            this.y = startY;
            
            // Laju awal (Horizontal dominant karena aliran Feed)
            let pressure = parseInt(slPress.value) / 300;
            this.vx = 4 * pressure + (Math.random() * 2);
            this.vy = (Math.random() - 0.2) * 2; // Sedikit acak vertikal
            
            this.size = type === 'SO4' ? 5 : 3.5; 
            this.inPermeate = false; 
            this.active = true;
            this.isFouling = false; // Menjadi kerak membran
        }
        
        update() {
            if (this.isFouling) return;
            
            let pressure = parseInt(slPress.value) / 300;
            let integrity = parseInt(slInteg.value) / 100;
            
            // Tahap 1: Di atas membran (Retentate/Feed Channel)
            if (!this.inPermeate) {
                this.x += this.vx;
                this.y += this.vy;
                
                // Efek dorongan tekanan ke bawah menuju membran
                if (this.x > mStartX && this.x < mEndX) {
                    this.vy += 0.2 * pressure; 
                } else if (this.x > mEndX) {
                    this.vy *= 0.9; // Hilang tekanan downdraft setelah lewat membran
                }
                
                // Batas atas dinding pipa
                if (this.y < 120) { this.y = 120; this.vy *= -1; }
                
                // MENABRAK MEMBRAN (Cross-flow filtration)
                if (this.x >= mStartX && this.x <= mEndX && this.y >= mY - 10 && this.y <= mY) {
                    let fIdx = Math.floor(this.x - mStartX);
                    let localFouling = foulingArray[fIdx] || 0;
                    
                    if (this.type === 'SO4') {
                        // Ion Sulfat berukuran besar -> Probabilitas ditolak sangat tinggi
                        let passProb = (1 - integrity) + (pressure * 0.005); // Tekanan tinggi maksa ion lewat jika membran bocor
                        
                        if (Math.random() < passProb) {
                            this.inPermeate = true; this.y += 20; this.vy = 2; // Jebol
                            so4Passed++;
                        } else {
                            so4Rejected++;
                            // Fouling (Concentration Polarization)
                            if (Math.random() < 0.02 + (localFouling * 0.05)) {
                                this.isFouling = true;
                                this.y = mY - localFouling - 3;
                                // Menambah kerak membran
                                for(let i = Math.max(0, fIdx-10); i < Math.min(550, fIdx+10); i++) {
                                    let dist = Math.abs(fIdx - i);
                                    if(foulingArray[i] < 30) foulingArray[i] += Math.max(0, (10 - dist) * 0.1);
                                }
                            } else {
                                this.vy = -Math.abs(this.vy) * 0.8 - (Math.random() * 2); // Memantul & tersapu aliran cross-flow
                            }
                        }
                    } else {
                        // Air dan Ion Monovalen (Ukurannya kecil)
                        let blockProb = localFouling / 30; // Fouling menghalangi fluks air
                        if (Math.random() > blockProb) {
                            this.inPermeate = true; this.y += 15; this.vy = 2 + (pressure * 1.5);
                        } else {
                            this.vy = -Math.abs(this.vy) * 0.5; // Memantul karena tertutup fouling
                        }
                    }
                }
                
                // Lewat dari membran (Masuk ke Reject/Retentate line)
                if (this.x > mEndX && this.y > 220) {
                    this.y = 220; this.vy *= -1;
                }
            } 
            // Tahap 2: Di bawah membran (Permeate Channel)
            else {
                this.x += this.vx * 0.5; 
                this.y += this.vy;
                if (this.y > 380) { this.y = 380; this.vy *= -1; }
            }
        }
        
        draw() {
            if (this.isFouling) {
                ctx.fillStyle = 'var(--foul-color)';
                ctx.fillRect(this.x - 3, this.y - 3, 6, 6);
                return;
            }
            
            ctx.beginPath();
            if(this.type === 'SO4') {
                ctx.fillStyle = 'var(--so4-color)';
                ctx.rect(this.x - 4, this.y - 4, 8, 8); // Sulfat kotak kuning besar
            } else {
                ctx.fillStyle = 'var(--water-color)';
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2); // Air bulat biru kecil
            }
            ctx.fill();
        }
    }
    
    function drawMembraneSystem() {
        ctx.fillStyle = '#12141a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 8; ctx.lineJoin = 'round';
        
        // Pipa Feed Atas
        ctx.beginPath(); ctx.moveTo(0, 110); ctx.lineTo(mEndX + 100, 110); ctx.stroke();
        // Pipa Permeate Bawah
        ctx.beginPath(); ctx.moveTo(mStartX - 20, 390); ctx.lineTo(mEndX + 100, 390); ctx.stroke();
        // Dinding Vertikal Pemisah
        ctx.beginPath(); ctx.moveTo(mStartX - 20, 390); ctx.lineTo(mStartX - 20, mY); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(mEndX + 100, mY); ctx.lineTo(mEndX, mY); ctx.stroke();
        
        // Teks Label Pipa
        ctx.fillStyle = '#94a3b8'; ctx.font = 'bold 16px Arial'; 
        ctx.fillText('FEED (Air Laut Mentah)', 20, 100);
        ctx.fillText('RETENTATE (Reject SO₄²⁻)', mEndX + 5, 100);
        ctx.fillText('PERMEATE (Air Injeksi Bersih)', mEndX - 100, 415);
        
        // RENDER MEMBRAN NANOFILTRASI (Garis Putus-putus Tosca)
        ctx.strokeStyle = 'var(--membrane-color)';
        ctx.lineWidth = 6;
        ctx.setLineDash([15, 8]); // Efek pori-pori
        ctx.beginPath(); ctx.moveTo(mStartX, mY); ctx.lineTo(mEndX, mY); ctx.stroke();
        ctx.setLineDash([]); // Reset
        
        // Render Fouling (Penumpukan di atas membran)
        if (totalFouling > 0) {
            ctx.fillStyle = 'var(--foul-color)';
            ctx.beginPath(); ctx.moveTo(mStartX, mY - 2);
            for(let x = 0; x < 550; x++) ctx.lineTo(mStartX + x, mY - 2 - foulingArray[x]);
            ctx.lineTo(mEndX, mY - 2); ctx.fill();
        }
        
        if (flashEffect > 0) {
            ctx.fillStyle = `rgba(56, 189, 248, ${flashEffect / 20})`; // Kilat biru bersih
            ctx.fillRect(mStartX, mY-40, 550, 60); 
            flashEffect--;
        }
    }
    
    function processSystem() {
        let press = parseInt(slPress.value);
        let cSO4 = parseInt(slSO4.value);
        
        // Laju Injeksi (Tergantung Tekanan)
        if (Math.random() < press / 600) {
            // Spawn Air
            particles.push(new Particle('Water', 10, 130 + Math.random()*50));
            particles.push(new Particle('Water', 10, 130 + Math.random()*50));
            // Spawn Sulfat (Tergantung konsentrasi slider)
            if (Math.random() < cSO4 / 5000) {
                particles.push(new Particle('SO4', 10, 130 + Math.random()*50));
            }
        }
    }
    
    function updateDasbor() {
        document.getElementById('valPress').innerText = slPress.value + ' psi';
        document.getElementById('valSO4').innerText = slSO4.value + ' ppm';
        
        let integ = parseInt(slInteg.value);
        let lblInteg = document.getElementById('valInteg');
        lblInteg.innerText = integ + '%';
        if(integ > 95) lblInteg.style.color = '#10b981';
        else if (integ > 80) lblInteg.style.color = '#f59e0b';
        else lblInteg.style.color = '#ef4444';
        
        // Kalkulasi Fouling
        totalFouling = (foulingArray.reduce((a,b)=>a+b, 0) / (550 * 30)) * 100;
        if(totalFouling > 100) totalFouling = 100;
        
        // Kalkulasi Sulfate Rejection
        let rejectionRate = 100;
        if (so4Rejected + so4Passed > 0) {
            rejectionRate = (so4Rejected / (so4Rejected + so4Passed)) * 100;
        } else {
            rejectionRate = integ; // Default
        }
        
        // Kalkulasi Permeate Flux (Kinerja Air Tembus)
        let flux = (100 - totalFouling); 
        
        // Update UI Text
        let elRej = document.getElementById('valRej');
        elRej.innerText = rejectionRate.toFixed(1) + '%';
        elRej.className = rejectionRate > 95 ? 'metric-value safe' : (rejectionRate > 80 ? 'metric-value warn' : 'metric-value alert');
        
        let elFoul = document.getElementById('valFoul');
        elFoul.innerText = totalFouling.toFixed(1) + '%';
        elFoul.className = totalFouling > 60 ? 'metric-value alert' : (totalFouling > 30 ? 'metric-value warn' : 'metric-value safe');
        
        let elFlux = document.getElementById('valFlux');
        elFlux.innerText = flux.toFixed(0) + '%';
        elFlux.className = flux > 70 ? 'metric-value safe' : (flux > 40 ? 'metric-value warn' : 'metric-value alert');
    }
    
    function animate() {
        drawMembraneSystem();
        processSystem();
        
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update();
                p.draw();
                // Hapus jika sudah melewati layar kanan
                if (p.x > canvas.width + 10) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }
        
        updateDasbor();
        requestAnimationFrame(animate);
    }
    
    // Tombol Backwash (CIP - Clean In Place)
    document.getElementById('btnCIP').addEventListener('click', () => {
        foulingArray.fill(0);
        so4Rejected = 0; so4Passed = 0; // Reset metrik agar hitungan akurat lagi
        // Ubah partikel fouling yang nyangkut jadi air biasa atau hilangkan
        particles = particles.filter(p => !p.isFouling); 
        flashEffect = 20; 
    });
    
    animate();
</script>
</body>
</html>
"""

# Jangan lupa bagian bawah ini sangat penting!
components.html(html_app, height=850, scrolling=False)
