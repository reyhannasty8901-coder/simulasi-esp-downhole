import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Simulasi Scaling BaSO4 & SrSO4", layout="wide")
st.title("🛢️ Simulasi Presipitasi Barium Sulfat & Stronsium Sulfat di Pipa Minyak")
st.markdown("---")

# ================= INPUT PARAMETER =================
with st.sidebar:
    st.header("⚙️ Parameter Air Formasi & Injeksi")
    ba_conc = st.number_input("Konsentrasi Ba²⁺ dalam Air Formasi (mg/L)", min_value=0.0, max_value=500.0, value=150.0, step=5.0)
    sr_conc = st.number_input("Konsentrasi Sr²⁺ dalam Air Formasi (mg/L)", min_value=0.0, max_value=300.0, value=80.0, step=5.0)
    so4_conc = st.number_input("Konsentrasi SO₄²⁻ dalam Air Laut Injeksi (mg/L)", min_value=0.0, max_value=3000.0, value=2000.0, step=50.0)
    mixing_ratio = st.slider("Rasio Air Laut Injeksi (%)", min_value=0, max_value=100, value=30, step=1)
    
    st.markdown("---")
    st.header("📏 Spesifikasi Pipa")
    pipe_diameter_mm = st.number_input("Diameter Dalam Pipa (mm)", min_value=50, max_value=300, value=150, step=10)
    pipe_length_m = st.number_input("Panjang Pipa (m)", min_value=10, max_value=1000, value=100, step=10)
    
    st.markdown("---")
    st.caption("⚡ Efisiensi pengendapan diasumsikan 98% (stoikiometris).")

# ================= PERHITUNGAN KIMIA (STOIKIOMETRI) =================
# Konstanta massa molar (g/mol)
M_Ba = 137.3
M_Sr = 87.6
M_SO4 = 96.0
M_BaSO4 = 233.4
M_SrSO4 = 183.6

# Konsentrasi setelah mixing (berdasarkan fraksi air laut)
ba_mix = ba_conc * (1 - mixing_ratio / 100.0)
sr_mix = sr_conc * (1 - mixing_ratio / 100.0)
so4_mix = so4_conc * (mixing_ratio / 100.0)

# Konversi ke mol (per Liter)
mol_ba = ba_mix / M_Ba
mol_sr = sr_mix / M_Sr
mol_so4 = so4_mix / M_SO4

# Endapan BaSO4 (prioritas, karena Ksp lebih kecil)
precip_ba_mol = min(mol_ba, mol_so4) * 0.98  # 98% efisiensi
mol_so4_remaining = mol_so4 - precip_ba_mol

# Endapan SrSO4 (menggunakan sisa sulfat)
precip_sr_mol = min(mol_sr, max(0, mol_so4_remaining)) * 0.98

# Massa endapan (mg/L)
mass_ba = precip_ba_mol * M_BaSO4  # mg/L
mass_sr = precip_sr_mol * M_SrSO4  # mg/L
total_mass = mass_ba + mass_sr

# ================= PERHITUNGAN DAMPAK KE PIPA =================
# Konversi massa total ke volume (asumsi densitas kerak ~ 4000 kg/m³ = 4 g/cm³ = 4e6 mg/m³)
# Volume per liter air = total_mass (mg) / 4e6 (mg/m³) = total_mass * 1e-6 / 4  m³
# Sederhanakan: 1 mg/L = 1e-6 kg/m3. Density 4000 kg/m3 -> Volume = mass_kg / 4000
volume_scale_m3_per_liter = (total_mass / 1e6) / 4000  # m³ per liter air
# Asumsikan total volume air yang mengalir mempengaruhi pipa adalah 1 m³ (untuk skala visual)
total_volume_scale_m3 = volume_scale_m3_per_liter * 1000  # skala ke 1 m³

# Pengurangan diameter pipa
r_initial_m = (pipe_diameter_mm / 1000) / 2
# Anggap kerak menempel merata di sepanjang pipa. Volume kerak = pi * (R² - r²) * L
# Luas penampang yang hilang = volume / L
area_lost = total_volume_scale_m3 / pipe_length_m  # m²
# Pengurangan jari-jari (approximation: area_lost ≈ 2 * pi * R * delta_r)
delta_r = area_lost / (2 * np.pi * r_initial_m) if r_initial_m > 0 else 0
new_r = max(0, r_initial_m - delta_r)
new_diameter_mm = new_r * 2 * 1000

# Status Pipa
if new_r > 0.9 * r_initial_m:
    status_pipa = "✅ Aman"
    status_color = "green"
elif new_r > 0.7 * r_initial_m:
    status_pipa = "⚠️ Waspada (Mulai Menyumbat)"
    status_color = "orange"
else:
    status_pipa = "🚨 SUMBAT KRITIS / Minyak Tersumbat!"
    status_color = "red"

# Dampak terhadap Pressure Drop (ΔP ≈ 1/D^5) dan Flow Rate (Q ≈ D^4)
if new_r > 0:
    ratio_d = new_diameter_mm / pipe_diameter_mm
    delta_p_ratio = (1 / ratio_d) ** 5
    flow_rate_ratio = ratio_d ** 4
else:
    delta_p_ratio = float('inf')
    flow_rate_ratio = 0

# ================= OUTPUT & VISUALISASI =================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🧪 Hasil Analisis Kimia Air")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Konsentrasi Ba²⁺ tercampur", f"{ba_mix:.1f} mg/L")
    col_b.metric("Konsentrasi Sr²⁺ tercampur", f"{sr_mix:.1f} mg/L")
    col_c.metric("Konsentrasi SO₄²⁻ tercampur", f"{so4_mix:.1f} mg/L")
    
    st.subheader("⚖️ Massa Endapan yang Terbentuk (per Liter Air)")
    col_d, col_e, col_f = st.columns(3)
    col_d.metric("Massa BaSO₄ ↓", f"{mass_ba:.2f} mg/L", delta="Prioritas")
    col_e.metric("Massa SrSO₄ ↓", f"{mass_sr:.2f} mg/L", delta="Kompetitor")
    col_f.metric("**Total Massa Kerak**", f"{total_mass:.2f} mg/L", delta="Jika > 0 mulai scaling")

    # Chart batang
    fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
    labels = ['BaSO₄', 'SrSO₄']
    values = [mass_ba, mass_sr]
    colors = ['#FF8C00', '#1E90FF']  # Oranye untuk Ba, Biru untuk Sr
    bars = ax_bar.bar(labels, values, color=colors, edgecolor='black')
    ax_bar.set_ylabel('Massa Endapan (mg/L)')
    ax_bar.set_title('Komposisi Kerak Berdasarkan Jenis Ion')
    for bar, val in zip(bars, values):
        ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}', ha='center', va='bottom')
    st.pyplot(fig_bar)

with col2:
    st.subheader("📉 Status Operasional Pipa")
    st.metric("Diameter Pipa Tersisa", f"{new_diameter_mm:.2f} mm", delta=f"{new_diameter_mm - pipe_diameter_mm:.1f} mm")
    st.metric("Perubahan Pressure Drop (ΔP)", f"{delta_p_ratio:.2f} x lipat" if delta_p_ratio < 100 else "~ TAK TERHINGGA (Sumbat)", delta="Naik" if delta_p_ratio > 1 else "Normal")
    st.metric("Perubahan Laju Alir (Q)", f"{flow_rate_ratio:.2%}", delta="Turun" if flow_rate_ratio < 1 else "Normal")
    
    st.markdown(f"### 🔴 Status Pipa: {status_pipa}")
    st.progress(min(1.0, new_r / r_initial_m), text=f"Tersisa {new_r / r_initial_m:.1%} kapasitas aliran")

# ================= VISUALISASI PENAMPANG PIPA =================
st.markdown("---")
st.subheader("📐 Visualisasi Penampang Pipa (Tampak Depan)")

fig_pipe, ax_pipe = plt.subplots(figsize=(5, 5))
# Buat lingkaran luar (dinding pipa)
outer_circle = patches.Circle((0, 0), r_initial_m, edgecolor='black', facecolor='none', linewidth=3, label='Dinding Pipa')
ax_pipe.add_patch(outer_circle)

# Buat lingkaran dalam (area aliran tersisa)
if new_r > 0.001:
    inner_color = 'lightgreen' if new_r > 0.9 * r_initial_m else 'orange' if new_r > 0.7 * r_initial_m else 'red'
    inner_circle = patches.Circle((0, 0), new_r, edgecolor='darkgray', facecolor=inner_color, alpha=0.7, label='Area Aliran Tersisa')
    ax_pipe.add_patch(inner_circle)
else:
    st.warning("Pipa telah tersumbat total!")

# Gambar kerak (cincin antara r_initial dan new_r)
if new_r < r_initial_m:
    # Buat cincin kerak dengan warna campuran (orange dan biru)
    # Kita buat 2 sektor untuk menunjukkan komposisi BaSO4 (orange) dan SrSO4 (biru)
    # Sederhana: plot annulus dengan warna gradient atau split
    # Method: plot ring dengan warna orange untuk bagian Ba, biru untuk Sr
    # Kita split secara visual menjadi 2 bagian (180 derajat masing-masing)
    theta = np.linspace(0, 2*np.pi, 100)
    # Untuk BaSO4 (0-180 derajat)
    wedge1 = patches.Wedge((0,0), r_initial_m, 0, 180, width=r_initial_m-new_r, facecolor='#FF8C00', edgecolor='black', alpha=0.8, label='Kerak BaSO₄')
    wedge2 = patches.Wedge((0,0), r_initial_m, 180, 360, width=r_initial_m-new_r, facecolor='#1E90FF', edgecolor='black', alpha=0.8, label='Kerak SrSO₄')
    ax_pipe.add_patch(wedge1)
    ax_pipe.add_patch(wedge2)

# Set aspek dan batas
ax_pipe.set_aspect('equal')
ax_pipe.set_xlim(-r_initial_m*1.2, r_initial_m*1.2)
ax_pipe.set_ylim(-r_initial_m*1.2, r_initial_m*1.2)
ax_pipe.set_title('Penampang Pipa & Tebal Kerak')
ax_pipe.legend(loc='upper left')
ax_pipe.grid(False)
st.pyplot(fig_pipe)

# ================= KESIMPULAN AKHIR =================
st.markdown("---")
st.subheader("📝 Interpretasi / Rekomendasi")

if total_mass < 0.01:
    st.success("✅ **Tidak terjadi pengendapan signifikan.** Pipa aman dari scaling BaSO₄/SrSO₄.")
else:
    st.warning("⚠️ **Terjadi pengendapan!** Perhatikan penurunan diameter pipa.")
    if status_pipa == "🚨 SUMBAT KRITIS / Minyak Tersumbat!":
        st.error("🛑 **BAHAYA!** Pipa hampir tersumbat total. Produksi minyak terhambat. Lakukan acidizing atau squeeze inhibitor segera!")
    else:
        st.info("📌 **Saran:** Kurangi rasio injeksi air laut, atau gunakan inhibitor scale (seperti DTPA) untuk mencegah presipitasi lebih lanjut.")

# ================= PENTING! CEK LOGIKA =================
st.markdown("---")
st.caption(f"🔬 **Cek Logika**: Saat ini Rasio Air Laut = {mixing_ratio}%. Konsentrasi SO4 tercampur = {so4_mix:.1f} mg/L. Jika nilai ini 0, maka BaSO4 & SrSO4 = 0. (Sesuai dengan teori kimia).")
