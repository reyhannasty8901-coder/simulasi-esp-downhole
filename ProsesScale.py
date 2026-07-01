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
            if (this.isSt
