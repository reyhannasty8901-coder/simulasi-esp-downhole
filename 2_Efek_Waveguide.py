import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulasi B - Waveguide", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #12141c; }
    .metric-card { background-color: #1e212b; padding: 15px; border-radius: 8px; color: white; border-left: 4px solid #00e5ff;}
    </style>
""", unsafe_allow_html=True)

st.header("Simulasi B: Efek Waveguide Fluida (Downhole)")

c1, c2 = st.columns([1, 2])
with c1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    water_cut = st.slider("Water Cut (%)", 10, 99, 90)
    salinity = st.slider("Salinitas (ppm TDS)", 5000, 50000, 35000)
    esp_depth = st.number_input("Kedalaman Pompa ESP (m)", value=1500, step=100)
    st.markdown("</div>", unsafe_allow_html=True)
    st.info("Fluida sumur dengan salinitas dan water cut tinggi bertindak sebagai kabel penghantar (waveguide) yang sangat baik untuk gelombang elektromagnetik ke arah downhole.")

with c2:
    depths = np.linspace(0, 2500, 100)
    attenuation = 0.005 * (((100 - water_cut) / 100) * 8 + (10000 / salinity))
    signal = 100 * np.exp(-attenuation * depths)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=signal, y=depths, mode='lines', line=dict(color='#00e5ff', width=3), fill='tozerox'))
    fig2.add_hline(y=esp_depth, line_dash="dash", line_color="#ff9100", annotation_text=f"Intake ESP ({esp_depth}m)")
    
    fig2.update_layout(
        template='plotly_dark', plot_bgcolor='#1e212b', paper_bgcolor='rgba(0,0,0,0)', height=450,
        xaxis_title="Kekuatan Sinyal Elektromagnetik (%)", yaxis_title="Kedalaman Sumur (meter)",
        yaxis=dict(autorange="reversed") 
    )
    st.plotly_chart(fig2, use_container_width=True)
