import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Simulasi ESP Downhole", layout="centered")
st.title("🛢️ Simulasi Interaktif: ESP Downhole")
st.markdown("Atur frekuensi motor dan kedalaman sumur untuk melihat apakah minyak berhasil dipompa ke permukaan.")

# --- MEMBUAT SLIDER INTERAKTIF (DI SIDEBAR ATAU MAIN PAGE) ---
col1, col2 = st.columns(2)
with col1:
    frekuensi_motor = st.slider('Frekuensi Motor Listrik (Hz)', min_value=30.0, max_value=70.0, value=50.0, step=1.0)
with col2:
    kedalaman_sumur = st.slider('Kedalaman Sumur (meter)', min_value=1000, max_value=3000, value=1500, step=100)

# --- LOGIKA FISIKA SEDERHANA ---
# Head proporsional dengan kuadrat frekuensi
daya_dorong_maksimal = (frekuensi_motor / 50.0)**2 * 2500  

if kedalaman_sumur > daya_dorong_maksimal:
    laju_produksi = 0
    status = f"🚨 STALL! Daya Dorong ({daya_dorong_maksimal:.0f}m) < Kedalaman ({kedalaman_sumur}m)"
    warna_status = 'red'
    st.error(status)
else:
    laju_produksi = (daya_dorong_maksimal - kedalaman_sumur) * 3.5
    status = f"✅ SISTEM MENGALIR: {laju_produksi:.0f} BPD"
    warna_status = 'green'
    st.success(status)

# --- VISUALISASI GRAFIK MATPLOTLIB ---
fig, ax = plt.subplots(figsize=(5, 7))

# Menggambar casing sumur (pipa luar)
ax.plot([0, 0], [0, -3500], color='black', linewidth=4)
ax.plot([1, 1], [0, -3500], color='black', linewidth=4)

# Animasi level fluida di dalam pipa
if laju_produksi > 0:
    ax.fill_between([0.1, 0.9], 0, -kedalaman_sumur, color='#2c7bb6', alpha=0.7, label='Minyak Naik ke Permukaan')
else:
    tinggi_fluida_naik = -kedalaman_sumur + daya_dorong_maksimal
    ax.fill_between([0.1, 0.9], tinggi_fluida_naik, -kedalaman_sumur, color='#d7191c', alpha=0.7, label='Fluida Terhenti (Stall)')
    
# Menggambar unit ESP di dasar
esp_unit = Rectangle((0.15, -kedalaman_sumur - 300), 0.7, 300, color='dimgray', label='Unit ESP')
ax.add_patch(esp_unit)

# Pengaturan tampilan
ax.set_xlim(-1, 2)
ax.set_ylim(-4000, 500)
ax.set_ylabel("Kedalaman (meter)")
ax.set_xticks([]) 
ax.legend(loc='upper right')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Garis permukaan tanah
ax.axhline(0, color='green', linewidth=2, linestyle='-')
ax.text(-0.9, 50, "Permukaan Tanah", color='green', fontweight='bold')

# Menampilkan grafik ke web Streamlit
st.pyplot(fig)
