import streamlit as st
import streamlit.components.v1 as components

# --- PENGATURAN TEMA HALAMAN ---
st.set_page_config(page_title="Simulasi ESP Downhole", layout="centered")

st.markdown("<h2 style='text-align: center;'>🛢️ Simulasi Pompa ESP (Downhole)</h2>", unsafe_allow_html=True)

# --- SLIDER INTERAKTIF PYTHON ---
col1, col2 = st.columns(2)
with col1:
    frekuensi_motor = st.slider('Frekuensi Motor (Hz)', 30, 70, 50)
with col2:
    kedalaman_sumur = st.slider('Kedalaman Sumur (m)', 1000, 3000, 2000)

# --- LOGIKA FISIKA ---
daya_dorong_maksimal = (frekuensi_motor / 50.0)**2 * 2500  

if kedalaman_sumur > daya_dorong_maksimal:
    laju_produksi = 0
    st.error(f"🚨 STALL! Daya Dorong ({daya_dorong_maksimal:.0f}m) kalah dari Kedalaman ({kedalaman_sumur}m)")
else:
    laju_produksi = (daya_dorong_maksimal - kedalaman_sumur) * 3.5
    st.success(f"✅ SISTEM MENGALIR | Laju Produksi: {laju_produksi:.0f} BPD")

# --- ANIMASI HTML5 CANVAS & JAVASCRIPT ---
# Kita injeksikan nilai laju_produksi dari Python ke dalam variabel JavaScript
html_animasi = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        background-color: #0e1117; /* Warna gelap khas Streamlit */
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0;
        font-family: sans-serif;
    }}
    .sim-container {{
        position: relative;
        width: 250px;
        height: 450px;
        background-color: #1e1e24;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        overflow: hidden;
    }}
    canvas {{
        display: block;
    }}
</style>
</head>
<body>

<div class="sim-container">
    <canvas id="espCanvas" width="250" height="450"></canvas>
</div>

<script>
    const canvas = document.getElementById('espCanvas');
    const ctx = canvas.getContext('2d');
    
    // Ambil data dari Python
    let laju = {laju_produksi}; 
    let frekuensi = {frekuensi_motor};
    let kedalaman = {kedalaman_sumur};
    
    let partikelArray = [];
    
    // Kelas Partikel (Titik Biru)
    class Partikel {{
        constructor() {{
            this.x = Math.random() * 80 + 85; // Muncul di tengah pipa
            this.y = 330; // Mulai dari atas pompa
            this.radius = Math.random() * 4 + 2;
            // Kecepatan partikel bergantung pada laju produksi
            this.speed = (Math.random() * 2 + 1.5) * (laju / 1000); 
            this.opacity = Math.random() * 0.5 + 0.5;
        }}
        
        update() {{
            this.y -= this.speed; // Bergerak ke atas
        }}
        
        draw() {{
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(59, 130, 246, ${{this.opacity}})`; // Warna biru
            ctx.fill();
        }}
    }}
    
    function gambarLatar() {{
        // Gambar Pipa Luar (Casing)
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(70, 0); ctx.lineTo(70, 450);
        ctx.moveTo(180, 0); ctx.lineTo(180, 450);
        ctx.stroke();
        
        // Kotak PUMP
        ctx.fillStyle = '#475569';
        ctx.fillRect(72, 340, 106, 40);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 12px Arial';
        ctx.fillText('PUMP', 105, 365);
        
        // Kotak MOTOR
        ctx.fillStyle = '#334155';
        ctx.fillRect(72, 385, 106, 50);
        ctx.fillStyle = 'white';
        ctx.fillText('MOTOR', 103, 415);
        
        // Teks Kedalaman
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px Arial';
        ctx.fillText('0 m (Permukaan)', 160, 20);
        ctx.fillText(`${{kedalaman}} m (Dasar)`, 160, 430);
    }}
    
    function jalankanAnimasi() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        gambarLatar();
        
        // Jika ada laju produksi, buat gelembung baru
        if (laju > 0) {{
            // Semakin tinggi laju, semakin banyak partikel yang muncul
            let intensitas = Math.floor(laju / 500);
            for(let i=0; i<intensitas; i++) {{
                if(Math.random() < 0.3) partikelArray.push(new Partikel());
            }}
        }}
        
        // Update dan gambar semua partikel
        for (let i = 0; i < partikelArray.length; i++) {{
            partikelArray[i].update();
            partikelArray[i].draw();
        }}
        
        // Hapus partikel yang sudah keluar dari atas layar agar memori tidak penuh
        partikelArray = partikelArray.filter(p => p.y > -20);
        
        requestAnimationFrame(jalankanAnimasi);
    }}
    
    jalankanAnimasi();
</script>

</body>
</html>
"""

# Menampilkan HTML di dalam Streamlit
components.html(html_animasi, height=470)
