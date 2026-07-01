import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Simulasi Scaling BaSO4 & SrSO4", layout="wide")
st.markdown("<h1 style='text-align: center;'>🔄 Presipitasi Barium Sulfat (BaSO₄)</h1>", unsafe_allow_html=True)
st.markdown("---")

# ================= SIDEBAR INPUT =================
with st.sidebar:
    st.header("⚙️ Parameter Air Formasi & Injeksi")
    ba_conc = st.number_input("Kons. Ba²⁺ (mg/L)", min_value=0.0, max_value=500.0, value=150.0, step=5.0)
    sr_conc = st.number_input("Kons. Sr²⁺ (mg/L) [Kompetitor]", min_value=0.0, max_value=300.0, value=80.0, step=5.0)
    so4_conc = st.number_input("Kons. SO₄²⁻ di Air Laut (mg/L)", min_value=0.0, max_value=3000.0, value=2000.0, step=50.0)
    mixing_ratio = st.slider("Rasio Air Laut Injeksi (%)", min_value=0, max_value=100, value=30, step=1)
    
    st.markdown("---")
    st.header("📏 Spesifikasi Pipa")
    pipe_diameter_mm = st.number_input("Diameter Pipa (mm)", min_value=50, max_value=300, value=150, step=10)
    pipe_length_m = st.number_input("Panjang Pipa (m)", min_value=10, max_value=1000, value=100, step=10)

# ================= PERHITUNGAN KIMIA (STOIKIOMETRI) =================
M_Ba, M_Sr, M_SO4 = 137.3, 87.6, 96.0
M_BaSO4, M_SrSO4 = 233.4, 183.6

# Konsentrasi setelah pencampuran
ba_mix = ba_conc * (1 - mixing_ratio / 100.0)
sr_mix = sr_conc * (1 - mixing_ratio / 100.0)
so4_mix = so4_conc * (mixing_ratio / 100.0)

# Mol per Liter
mol_ba = ba_mix / M_Ba
mol_sr = sr_mix / M_Sr
mol_so4 = so4_mix / M_SO4

# Endapan BaSO4 (prioritas)
precip_ba_mol = min(mol_ba, mol_so4) * 0.98  # efisiensi 98%
mol_so4_remaining = mol_so4 - precip_ba_mol

# Endapan SrSO4 (menggunakan sisa sulfat)
precip_sr_mol = min(mol_sr, max(0, mol_so4_remaining)) * 0.98

# Massa endapan (mg/L)
mass_ba = precip_ba_mol * M_BaSO4
mass_sr = precip_sr_mol * M_SrSO4
total_mass = mass_ba + mass_sr

# ================= SKOR POTENSI KERAK (untuk Jarum Gauge) =================
# Skala 0 - 50, merepresentasikan tingkat keparahan pengkerakan
# Jika total_mass = 250 mg/L -> skor 50 (sangat parah)
risk_score = min(50, total_mass * 0.2)  
# Contoh: massa 25 mg/L -> skor 5, massa 125 mg/L -> skor 25, dst.

# ================= DAMPAK KE PIPA =================
r_initial = (pipe_diameter_mm / 1000) / 2
# Asumsi volume kerak menempel merata
volume_scale = (total_mass / 1e6) / 4000 * 1000  # per 1 m³ air
area_lost = volume_scale / pipe_length_m
delta_r = area_lost / (2 * np.pi * r_initial) if r_initial > 0 else 0
new_r = max(0, r_initial - delta_r)
new_diameter = new_r * 2 * 1000

# Status Pipa
if total_mass < 0.1:
    status_pipa = "✅ Aman"
    laju_kerak = "Tidak Ada"
elif new_r > 0.8 * r_initial:
    status_pipa = "⚠️ Waspada"
    laju_kerak = "Rendah"
elif new_r > 0.5 * r_initial:
    status_pipa = "🔶 Mulai Menyumbat"
    laju_kerak = "Sedang"
else:
    status_pipa = "🚨 SUMBAT KRITIS!"
    laju_kerak = "Tinggi"

# ================= LAYOUT UTAMA (MIRIP SS) =================
col1, col2 = st.columns([2, 1.5], gap="medium")

with col1:
    # ----- GAUGE / SPEEDOMETER (BENTUK SEPERTI SS) -----
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=round(risk_score, 1),
        mode="gauge+number+delta",
        title={'text': "Potensi Kerak ↑", 'font': {'size': 24, 'color': 'black'}},
        delta={'reference': 40, 'increasing.color': "red", 'decreasing.color': "green"},
        gauge={
            'axis': {'range': [0, 50], 'tickwidth': 2, 'tickvals': [0, 10, 20, 30, 40, 50], 
                     'tickfont': {'size': 14, 'color': 'black'}},
            'bar': {'color': "#FF8C00"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 15], 'color': 'rgba(144, 238, 144, 0.7)'},   # Hijau
                {'range': [15, 35], 'color': 'rgba(255, 255, 0, 0.6)'},    # Kuning
                {'range': [35, 50], 'color': 'rgba(255, 100, 100, 0.7)'}   # Merah
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.8,
                'value': round(risk_score, 1)
            }
        }
    ))
    fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=30))
    st.plotly_chart(fig, use_container_width=True)

    # ----- BAGIAN BAWAH KOLOM KIRI: MASSA & KOMPOSISI -----
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("⚖️ Total Massa Kerak", f"{total_mass:.2f} mg/L")
    col_b.metric("🟠 Massa BaSO₄", f"{mass_ba:.2f} mg/L")
    col_c.metric("🔵 Massa SrSO₄", f"{mass_sr:.2f} mg/L")
    
    # Indikator visual kecil untuk komposisi
    if total_mass > 0.1:
        st.progress(mass_ba / total_mass if total_mass > 0 else 0, text=f"Proporsi BaSO₄: {mass_ba/total_mass*100:.1f}%")
    else:
        st.info("Belum ada endapan yang terbentuk.")

with col2:
    st.subheader("📊 Status Operasi Pipa")
    st.metric("Laju Kerak", laju_kerak)
    st.metric("Status Pipa", status_pipa)
    st.metric("Rasio Air Laut (%)", f"{mixing_ratio} %")
    st.metric("Kons. Barium Tercampur", f"{ba_mix:.1f} mg/L")
    st.metric("Kons. Sulfat Tercampur", f"{so4_mix:.1f} mg/L")
    st.metric("Diameter Pipa Tersisa", f"{new_diameter:.2f} mm", 
              delta=f"{new_diameter - pipe_diameter_mm:.2f} mm")
    
    # Estimasi dampak aliran
    if new_r > 0:
        ratio_d = new_diameter / pipe_diameter_mm
        flow_rate = ratio_d ** 4
        st.metric("Perkiraan Laju Alir Tersisa", f"{flow_rate:.1%}")
        if flow_rate < 0.3:
            st.error("🛑 **PERINGATAN:** Produksi minyak sangat terhambat! Lakukan tindakan pencegahan scaling.")
    else:
        st.error("🚫 PIPA TERSAMBAT TOTAL - MINYAK TIDAK BISA MENGALIR!")

# ================= KOTAK INFORMASI TAMBAHAN (SEPERTI DI SS) =================
st.markdown("---")
st.subheader("🔬 Detail Air Formasi & Reaksi")
info_col1, info_col2, info_col3 = st.columns(3)
info_col1.info(f"🧪 **Air Formasi (Ba²⁺)** : {ba_conc} mg/L\n\n**Air Laut (SO₄²⁻)** : {so4_conc} mg/L")
info_col2.success(f"✅ **Reaksi Prioritas**: Ba²⁺ + SO₄²⁻ → BaSO₄↓ (Oranye)\n\n🔹 **Reaksi Kompetitor**: Sr²⁺ + SO₄²⁻ → SrSO₄↓ (Biru)")
info_col3.warning(f"⚡ **Efisiensi Pengendapan**: 98% (stoikiometris)\n\n📌 **Status Akhir**: {status_pipa}")

# ================= TEST CASE SPESIAL (UNTUK MEMBUKTIKAN KE AKURATAN) =================
st.markdown("---")
st.caption(f"🧪 **Cek Logika Ekstrem**: Saat ini Rasio Air Laut = {mixing_ratio}%. Konsentrasi SO₄ tercampur = {so4_mix:.2f} mg/L. ")
if mixing_ratio == 100 and so4_conc == 0:
    st.success("🎯 **BUKTI AKURAT**: Meskipun Air Laut 100%, karena Konsentrasi Sulfat = 0, maka SO₄ tercampur = 0. Tidak ada reaksi, Massa Kerak = 0, jarum Gauge di 0, dan pipa AMAN. Inilah yang seharusnya terjadi!")
elif mixing_ratio > 0 and so4_mix == 0:
    st.success("✅ Konsentrasi Sulfat efektif = 0, sehingga tidak ada endapan BaSO₄/SrSO₄ yang terbentuk.")
else:
    st.info("🔍 Silakan coba ubah 'Rasio Air Laut' menjadi 100% dan 'Kons. SO₄' menjadi 0 untuk melihat gauge bergerak ke 0 secara otomatis.")
