import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulasi A - Kinetika", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #12141c; }
    .metric-card { background-color: #1e212b; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: white; }
    .border-cyan { border-left: 4px solid #00e5ff; }
    .border-orange { border-left: 4px solid #ff9100; }
    .metric-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px;}
    .metric-value-cyan { color: #00e5ff; font-weight: bold; }
    .metric-value-orange { color: #ff9100; font-weight: bold; }
    .metric-value-white { color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.header("Simulasi A: Kinetika Kalsit vs Aragonit")

col_main, col_param = st.columns([3, 1])
with col_param:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    mineral_sat = st.slider("Supersaturasi Mineral (%)", 0, 100, 60)
    st.markdown("</div>", unsafe_allow_html=True)
    
    deposit_off = mineral_sat * 0.228
    st.markdown(f"""
        <div class='metric-card border-orange'>
            <div style='color: #a0aabf; font-size:14px;'>Sistem Konvensional (OFF)</div>
            <div class='metric-row'><span>Dominasi:</span> <span class='metric-value-orange'>Calcite (Melekat)</span></div>
            <div class='metric-row'><span>Deposit:</span> <span class='metric-value-white'>{deposit_off:.1f} mm/bln</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    deposit_on = deposit_off * 0.15 
    st.markdown(f"""
        <div class='metric-card border-cyan'>
            <div style='color: #a0aabf; font-size:14px;'>Sistem EMSP (ON)</div>
            <div class='metric-row'><span>Dominasi:</span> <span class='metric-value-cyan'>Aragonite (Tersuspensi)</span></div>
            <div class='metric-row'><span>Deposit:</span> <span class='metric-value-white'>{deposit_on:.1f} mm/bln</span></div>
        </div>
    """, unsafe_allow_html=True)

with col_main:
    fig1 = go.Figure()
    x_base = np.linspace(0, 100, 200)
    y_deposit = np.abs(np.sin(x_base/5) * np.random.normal(1, 0.2, 200) * (mineral_sat/15))
    fig1.add_trace(go.Scatter(x=x_base, y=y_deposit, fill='tozeroy', mode='none', fillcolor='rgba(255, 145, 0, 0.3)', name='Kerak Calcite'))
    fig1.add_trace(go.Scatter(x=np.random.rand(50)*100, y=np.random.rand(50)*30+10, mode='markers', marker=dict(color='#00e5ff', size=6), name='Serbuk Aragonite'))

    fig1.update_layout(
        template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450,
        xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, showticklabels=False, range=[0, 50])
    )
    st.plotly_chart(fig1, use_container_width=True)
