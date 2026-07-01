import streamlit as st
import streamlit.components.v1 as components

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="Simulasi Pencampuran & Scaling", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

# --- INJEKSI CORE SIMULATOR HTML5 & JS ---
html_app = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Kinetika Pencampuran & Presipitasi Scale</title>
    <style>
        :root {
            --bg: #0e1117;
            --panel: #1e212b;
            --text: #fafafa;
            --so4-color: #eab308;  /* Kuning */
            --ba-color: #3b82f6;   /* Biru */
            --sr-color: #a855f7;   /* Ungu */
            --scale-color: #ea580c; /* Oranye Gelap / Coklat */
        }
        body {
            background-color: var(--bg); color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 10px;
            display: flex; flex-direction: column; align-items: center;
        }
        h2 { margin: 0 0 15px 0; font-weight: 600; text-align: center; color: #f8fafc; font-size: 1.5rem;}
        
        .main-container {
            width: 100%; max-width: 1300px; display: grid; grid-template-columns: 1fr 380px; gap: 20px;
        }
        
        .canvas-section {
            background: var(--panel); border-radius: 12px; padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center;
        }
        canvas { background: #0b0f19; border-radius: 8px; width: 100%; max-width: 850px; }
        
        .control-panel {
            background: var(--panel); border-radius: 12px; padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 15px;
        }
        
        .control-section {
            border: 1px solid #334155; padding: 12px; border-radius: 8px; background: #1e293b;
        }
        .control-title {
            font-size: 0.9rem; font-weight: bold; color: #94a3b8; margin-bottom: 10px; border-bottom: 1px solid #475569; padding-bottom: 5px; text-align: center;
        }
        
        .slider-group label { font-size: 0.85rem; color: #cbd5e1; display: flex; justify-content: space-between; margin-top: 8px;}
        input[type=range] { width: 100%; margin: 8px 0; accent-color: #3b82f6; }
        
        .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-size: 0.85rem; padding: 12px; background: #1e293b; border-radius: 8px; margin-top:15px; width: 100%; border: 1px solid #334155;}
        .legend-item { display: flex; align-items: center; gap: 6px; font-weight: 500;}
        .dot { width: 14px; height: 14px; border-radius: 50%; }
        
        /* Dasbor Metrik */
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
        .metric-card {
            background: #0f172a; padding: 12px; border-radius: 6px; text-align: center; border: 1px solid #334155;
        }
        .metric-title { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 1.4rem; font-weight: bold; margin-top: 5px; color: #f8fafc; }
        
        button { background:#ef4444; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; width: 100%; margin-top: 10px; transition: 0.3s;}
        button:hover { background: #b91c1c; }
    </style>
</head>
<body>

    <h2>Visualisasi Dinamis: Pencampuran Fluida & Deposisi Scale</h2>
    
    <div class="main-container">
        <div class="canvas-section">
            <canvas id="simCanvas" width="850" height="520"></canvas>
            
            <div class="legend">
                <div class="legend-item"><div class="dot" style="background:var(--so4-color);"></div> Ion Sulfat (SO₄²⁻)</div>
                <div class="legend-item"><div class="dot" style="background:var(--ba-color);"></div> Ion Barium (Ba²⁺)</div>
                <div class="legend-item"><div class="dot" style="background:var(--sr-color);"></div> Ion Stronsium (Sr²⁺)</div>
                <div class="legend-item"><div class="dot" style="background:var(--scale-color); border-radius:3px;"></div> Kerak (Menempel)</div>
            </div>
        </div>
        
        <div class="control-panel">
            
            <div class="control-section" style="border-left: 4px solid var(--so4-color);">
                <div class="control-title">Pipa Kiri (Injeksi Sulfat)</div>
                <div class="slider-group">
                    <label>Laju Aliran (Flow Rate) <span id="valFlowL">50%</span></label>
                    <input type="range" id="slFlowL" min="0" max="100" value="50">
                </div>
            </div>
            
            <div class="control-section" style="border-left: 4px solid var(--ba-color);">
                <div class="control-title">Pipa Kanan (Air Formasi)</div>
                <div class="slider-group">
                    <label>Laju Aliran (Flow Rate) <span id="valFlowR">50%</span></label>
                    <input type="range" id="slFlowR" min="0" max="100" value="50">
                </div>
            </div>
            
            <div class="control-section" style="background: #0f172a; border-color: #475569;">
                <div class="control-title" style="color: #f8fafc;">Status Pipa Utama (Bawah)</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Ketebalan Kerak</div>
                        <div class="metric-value" id="valThick" style="color: var(--scale-color);">0.0 mm</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Penyumbatan</div>
                        <div class="metric-value" id="valBlock">0%</div>
                    </div>
                </div>
            </div>
            
            <button id="btnFlush">Bersihkan Pipa (Reset)</button>
        </div>
    </div>

<script>
    const canvas = document.getElementById('simCanvas');
    const ctx = canvas.getContext('2d');
    
    // Sliders
    const slFlowL = document.getElementById('slFlowL');
    const slFlowR = document.getElementById('slFlowR');
    
    // Geometri Pipa Y-Shape
    const cX = 425; // Center X (Titik temu)
    const mY = 220; // Titik persimpangan Y
    const pW = 100; // Lebar pipa bawah
    
    let particles = [];
    let scaleThickL = 0; // Ketebalan kerak di dinding kiri
    let scaleThickR = 0; // Ketebalan kerak di dinding kanan
    let totalBlockage = 0; 
    
    class Particle {
        constructor(type, startX, startY, tgtX, tgtY) {
            this.type = type; // 'SO4', 'Ba', 'Sr', 'Scale'
            this.x = startX; this.y = startY;
            
            // Hitung arah gerak menuju persimpangan tengah
            let angle = Math.atan2(tgtY - startY, tgtX - startX);
            let speed = 2.5 + Math.random() * 2;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            
            this.size = type === 'Scale' ? 4 : 3.5; // Scale sedikit lebih besar
            this.active = true; 
            this.isStuck = false;
        }
        
        update(flowRate) {
            if (this.isStuck) return;
            
            // Fase 1: Mengalir dari cabang pipa atas menuju tengah
            if (this.y < mY - 15) {
                this.x += this.vx; 
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 1.5; // Efek turbulensi ringan
            } 
            // Fase 2: Mengalir ke bawah di pipa utama
            else {
                // Kecepatan aliran ke bawah
                this.vy = (flowRate * 0.1) + 2 + Math.random();
                
                // Jika pipa buntu total (100%), aliran berhenti
                if (totalBlockage >= 98 && this.type !== 'Scale') this.vy *= 0.1;
                
                this.y += this.vy;
                this.x += (Math.random() - 0.5) * 3; 
                
                // Batas dinding pipa (menyempit seiring tumbuhnya kerak)
                let wallL = cX - pW/2 + scaleThickL;
                let wallR = cX + pW/2 - scaleThickR;
                
                if (this.x < wallL) this.x = wallL;
                if (this.x > wallR) this.x = wallR;
                
                // Logika Penempelan Kerak (Hanya partikel 'Scale' yang bisa menempel)
                if (this.type === 'Scale' && totalBlockage < 95) {
                    // Cek tabrakan dengan dinding kiri atau kanan
                    if (this.x <= wallL + 5) {
                        if (Math.random() < 0.2) { // 20% peluang menempel saat menyentuh dinding
                            this.isStuck = true;
                            if (scaleThickL < pW/2 - 2) scaleThickL += 0.3; // Kerak bertambah
                        }
                    } else if (this.x >= wallR - 5) {
                        if (Math.random() < 0.2) {
                            this.isStuck = true;
                            if (scaleThickR < pW/2 - 2) scaleThickR += 0.3;
                        }
                    }
                }
            }
        }
        
        draw() {
            ctx.beginPath();
            if (this.type === 'Scale') {
                // Gambar Kerak (Kotak/Kristal)
                ctx.fillStyle = 'var(--scale-color)';
                ctx.rect(this.x - this.size, this.y - this.size, this.size*2, this.size*2);
            } else {
                // Gambar Ion (Lingkaran)
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
                if (this.type === 'SO4') ctx.fillStyle = 'var(--so4-color)';
                else if (this.type === 'Ba') ctx.fillStyle = 'var(--ba-color)';
                else if (this.type === 'Sr') ctx.fillStyle = 'var(--sr-color)';
            }
            ctx.fill();
        }
    }
    
    function drawPipes() {
        ctx.fillStyle = '#0b0f19'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#334155'; ctx.lineWidth = 8; ctx.lineJoin = 'round';
        
        // Pipa Kiri (Sulfat)
        ctx.beginPath(); ctx.moveTo(60, 40); ctx.lineTo(cX - pW/2, mY); ctx.lineTo(cX - pW/2, 520); ctx.stroke();
        // Pipa Kanan (Ba/Sr)
        ctx.beginPath(); ctx.moveTo(790, 40); ctx.lineTo(cX + pW/2, mY); ctx.lineTo(cX + pW/2, 520); ctx.stroke();
        // Celah Tengah (V-Shape atas)
        ctx.beginPath(); ctx.moveTo(180, 40); ctx.lineTo(cX, mY - 50); ctx.lineTo(670, 40); ctx.stroke();
        
        // Teks Label Pipa
        ctx.fillStyle = '#94a3b8'; ctx.font = '14px Arial'; ctx.textAlign = 'center'; fontWeight = 'bold';
        ctx.fillText('PIPA KIRI', 120, 35);
        ctx.fillText('(Sulfat)', 120, 55);
        ctx.fillText('PIPA KANAN', 730, 35);
        ctx.fillText('(Ba²⁺ / Sr²⁺)', 730, 55);
        
        // Render Tumpukan Kerak di Pipa Utama
        if (scaleThickL > 0 || scaleThickR > 0) {
            ctx.fillStyle = '#9a3412'; // Warna dasar kerak
            
            // Kerak Kiri
            ctx.fillRect(cX - pW/2, mY, scaleThickL, 520 - mY);
            // Kerak Kanan
            ctx.fillRect(cX + pW/2 - scaleThickR, mY, scaleThickR, 520 - mY);
            
            // Garis Luar Kerak (Batas dengan air)
            ctx.strokeStyle = 'var(--scale-color)'; ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(cX - pW/2 + scaleThickL, mY); ctx.lineTo(cX - pW/2 + scaleThickL, 520);
            ctx.moveTo(cX + pW/2 - scaleThickR, mY); ctx.lineTo(cX + pW/2 - scaleThickR, 520);
            ctx.stroke();
        }
    }
    
    function processSystem() {
        let fL = parseInt(slFlowL.value);
        let fR = parseInt(slFlowR.value);
        let totalFlow = fL + fR;
        
        // Spawn Ion KIRI (Sulfat)
        if (fL > 0 && Math.random() < (fL / 100)) {
            let stX = 120 + (Math.random() - 0.5) * 50;
            particles.push(new Particle('SO4', stX, 60, cX - 25, mY));
        }
        
        // Spawn Ion KANAN (Ba / Sr)
        if (fR > 0 && Math.random() < (fR / 100)) {
            let type = Math.random() > 0.3 ? 'Ba' : 'Sr'; 
            let stX = 730 + (Math.random() - 0.5) * 50;
            particles.push(new Particle(type, stX, 60, cX + 25, mY));
        }
        
        // Proses Tabrakan & Nukleasi (Hanya saat mereka bertemu di persimpangan tengah)
        for(let i = 0; i < particles.length; i++) {
            let p1 = particles[i];
            // Abaikan jika p1 sudah menempel, sudah jadi kerak, atau belum sampai tengah
            if(!p1.active || p1.isStuck || p1.type === 'Scale' || p1.y < mY - 30) continue;
            
            for(let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                if(!p2.active || p2.isStuck || p2.type === 'Scale' || p2.y < mY - 30) continue;
                
                // Jika Sulfat (Kiri) bertemu Ba/Sr (Kanan)
                if ((p1.type === 'SO4' && (p2.type === 'Ba' || p2.type === 'Sr')) || 
                    (p2.type === 'SO4' && (p1.type === 'Ba' || p1.type === 'Sr'))) {
                    
                    let dist = Math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2);
                    
                    // Jarak tabrakan (Radius Reaksi)
                    if(dist < 15) { 
                        p1.active = false; p2.active = false;
                        // Ubah menjadi partikel Kerak (Scale)
                        particles.push(new Particle('Scale', (p1.x+p2.x)/2, (p1.y+p2.y)/2, 0, 0));
                        break;
                    }
                }
            }
        }
        
        return totalFlow;
    }
    
    function updateDasbor() {
        document.getElementById('valFlowL').innerText = slFlowL.value + '%';
        document.getElementById('valFlowR').innerText = slFlowR.value + '%';
        
        // Kalkulasi Persentase Penyumbatan
        totalBlockage = ((scaleThickL + scaleThickR) / pW) * 100;
        if (totalBlockage > 100) totalBlockage = 100;
        
        document.getElementById('valThick').innerText = (scaleThickL + scaleThickR).toFixed(1) + ' mm';
        
        let elBlock = document.getElementById('valBlock');
        elBlock.innerText = totalBlockage.toFixed(0) + '%';
        
        if (totalBlockage > 60) elBlock.style.color = '#ef4444'; // Merah (Bahaya)
        else if (totalBlockage > 20) elBlock.style.color = '#f59e0b'; // Kuning (Waspada)
        else elBlock.style.color = '#10b981'; // Hijau (Aman)
    }
    
    function animate() {
        drawPipes();
        let currentFlow = processSystem();
        
        for(let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            if (p.active) {
                p.update(currentFlow);
                p.draw();
                // Hapus partikel yang sudah lolos ke bawah layar
                if (p.y > canvas.height + 10 && !p.isStuck) particles.splice(i, 1);
            } else {
                particles.splice(i, 1);
            }
        }
        
        updateDasbor();
        requestAnimationFrame(animate);
    }
    
    // Tombol Reset Kerak
    document.getElementById('btnFlush').addEventListener('click', () => {
        particles = [];
        scaleThickL = 0; scaleThickR = 0; totalBlockage = 0;
    });
    
    animate();
</script>
</body>
</html>
"""

components.html(html_app, height=750, scrolling=False)
