"""
Simulasi A — Analisis Komparatif: Pembentukan Kerak & EMSP
============================================================
Visualisasi pipa/partikel yang menunjukkan hipotesis mekanisme inti
Electromagnetic Scale Preventer (E-Scale / EMSP): saat medan
elektromagnetik AKTIF (ON), presipitasi CaCO3 tidak berkurang, tetapi
jalur kristalisasinya bergeser dari fasa kalsit (keras, menempel di
dinding pipa) ke fasa aragonit (butiran halus, tersuspensi terbawa
aliran).

Model kimia yang dipakai (tidak berubah dari versi sebelumnya, hanya
ditambah parameter laju alir):
  1) Langelier Saturation Index (LSI) — kecenderungan CaCO3 mengendap
     berdasarkan pH, suhu, kesadahan kalsium, dan alkalinitas.
  2) Aturan tahapan Ostwald — presipitasi cepat cenderung membentuk
     fasa metastabil (aragonit) lebih dulu, yang lama-kelamaan
     bertransformasi ke fasa stabil (kalsit) kecuali ada gangguan yang
     menahan transformasi tersebut (medan elektromagnetik).
  3) Persamaan Avrami — kurva-S pertumbuhan kristal terhadap waktu.
  4) Waktu tinggal (residence time) di zona kumparan — laju alir yang
     lebih rendah memberi waktu kontak lebih lama dengan medan, sehingga
     efek pergeseran fasa lebih kuat; laju alir tinggi memperlemah efeknya.

  5) Animasi real-time — posisi partikel dianimasikan dengan pola rerun
     Streamlit (loop "frame -> sleep -> st.rerun()"), sehingga ion/kristal
     terlihat benar-benar mengalir sepanjang pipa alih-alih gambar statis.
     Kecepatan animasi mengikuti parameter Laju Alir.

Jalankan dengan:
    streamlit run simulasi_kinetika_kristalisasi_v3.py
"""

import math
import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------
# KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------------------------
st.set_page_config(page_title="Analisis Komparatif: Pembentukan Kerak & EMSP", layout="wide")

CYAN = "#00e5ff"
ORANGE = "#ff9100"
BLUE = "#3b82f6"
GREEN = "#10b981"
BG = "#12141c"
CARD_BG = "#1e212b"
CARD_BG2 = "#242836"
MUTED = "#a0aabf"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    .metric-card {{
        background-color: {CARD_BG}; padding: 14px 18px; border-radius: 10px;
        margin-bottom: 12px; color: white;
    }}
    .border-cyan {{ border-left: 4px solid {CYAN}; }}
    .border-orange {{ border-left: 4px solid {ORANGE}; }}
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }}
    .metric-value-cyan {{ color: {CYAN}; font-weight: 700; }}
    .metric-value-orange {{ color: {ORANGE}; font-weight: 700; }}
    .metric-value-white {{ color: white; font-weight: 700; }}
    .metric-label {{ color: {MUTED}; font-size: 13px; }}
    .section-title {{ color: white; font-size: 16px; font-weight: 700; margin: 2px 0 10px 0; }}
    .legend-row {{ display: flex; gap: 22px; flex-wrap: wrap; align-items: center;
        background-color: {CARD_BG}; padding: 12px 16px; border-radius: 10px; margin-top: 8px; }}
    .legend-item {{ display: flex; align-items: center; gap: 7px; font-size: 12.5px; color: white; white-space: nowrap; }}
    .legend-dot {{ width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex-shrink: 0; }}
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 12px 16px; border-radius: 8px; color: {MUTED}; font-size: 12px; line-height: 1.55;
    }}
    .progress-label {{ color: white; font-size: 13px; margin-bottom: 2px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2 style='text-align:center; color:white;'>Analisis Komparatif: Pembentukan Kerak &amp; EMSP</h2>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# FUNGSI PERHITUNGAN KIMIA (sama seperti versi sebelumnya + faktor laju alir)
# ----------------------------------------------------------------------
def hitung_lsi(pH, suhu_c, ca_hardness_ppm, alkalinity_ppm, tds_ppm=1200.0):
    """Langelier Saturation Index. LSI>0 -> supersaturasi/berpotensi kerak."""
    A = (math.log10(tds_ppm) - 1) / 10
    B = -13.12 * math.log10(suhu_c + 273.15) + 34.55
    C = math.log10(max(ca_hardness_ppm, 1)) - 0.4
    D = math.log10(max(alkalinity_ppm, 1))
    pHs = (9.3 + A + B) - (C + D)
    return pH - pHs, pHs


def faktor_waktu_tinggal(laju_alir_ms, panjang_kumparan_m=1.5, referensi_s=1.5):
    """Waktu kontak air dengan medan elektromagnetik di zona kumparan.
    Laju alir rendah -> waktu tinggal lebih lama -> efek EMSP lebih kuat."""
    residence_time_s = panjang_kumparan_m / max(laju_alir_ms, 0.05)
    return float(np.clip(residence_time_s / referensi_s, 0.2, 1.3))


def fraksi_kalsit(lsi, suhu_c, status_on, dwell_factor=1.0, geser_maks=0.50):
    """Estimasi fraksi kalsit dari total CaCO3 yang terbentuk.
    OFF: transformasi Ostwald aragonit->kalsit berjalan penuh (fungsi LSI & suhu).
    ON : medan elektromagnetik menahan transformasi, besarnya efek dimodulasi
         oleh waktu tinggal air di zona kumparan (dwell_factor)."""
    driving = max(lsi, 0.0)
    frac_off = 0.55 + 0.06 * driving + 0.0035 * (suhu_c - 20)
    frac_off = float(np.clip(frac_off, 0.50, 0.97))

    if not status_on:
        return frac_off, frac_off

    geser = geser_maks * (0.6 + 0.4 * min(driving / 2.0, 1.0)) * dwell_factor
    frac_on = float(np.clip(frac_off - geser, 0.08, 0.95))
    return frac_on, frac_off


def laju_deposit(fraksi_kalsit_val, lsi, k_deposit=1.35):
    """Laju penebalan kerak keras (mm/bulan) — hanya fraksi kalsit dianggap
    menempel permanen; aragonit tersuspensi & terbawa aliran."""
    driving = max(lsi, 0.0)
    potensi_total = k_deposit * (driving ** 1.3)
    return potensi_total * fraksi_kalsit_val


def kurva_avrami(t_hari, k, n=1.6):
    return 1 - np.exp(-k * np.power(np.maximum(t_hari, 0), n))


def label_saturasi(lsi):
    if lsi > 1.0:
        return "Tinggi", ORANGE
    if lsi > 0.2:
        return "Sedang", "#ffb703"
    if lsi > -0.2:
        return "Setimbang", CYAN
    return "Rendah", "#6ee7b7"


def label_risiko(lsi, frac_kalsit_aktif):
    skor = max(lsi, 0) * frac_kalsit_aktif
    if skor > 1.1:
        return "Kritis", "#ff5252"
    if skor > 0.5:
        return "Waspada", ORANGE
    return "Aman", "#6ee7b7"


# ----------------------------------------------------------------------
# PARTIKEL PERSISTEN (agar animasi mengalir mulus antar-frame, bukan
# posisi acak ulang tiap frame)
# ----------------------------------------------------------------------
N_PARTIKEL = 56
TRANSISI_ABU = "#94a3b8"


def ambil_basis_partikel(kunci, seed, n=N_PARTIKEL):
    """Membuat (atau mengambil dari cache session_state) posisi dasar
    partikel: posisi awal di sepanjang pipa, jitter radial saat fase ion,
    dan target posisi akhir saat fase kalsit/aragonit. Hanya dibuat ulang
    saat tombol Reset ditekan (seed berubah)."""
    cache_key = f"basis_{kunci}"
    seed_key = f"seed_{kunci}"
    if cache_key not in st.session_state or st.session_state.get(seed_key) != seed:
        rng = np.random.default_rng(seed)
        sisi = rng.choice([-1, 1], n)
        st.session_state[cache_key] = dict(
            base_x=rng.uniform(0, 10, n),
            y_ion=rng.uniform(-0.85, 0.85, n),
            parity=rng.integers(0, 2, n),          # 0 -> Ca2+, 1 -> CO3 2-
            rank=rng.random(n),                    # ambang deterministik utk rasio kalsit:aragonit
            y_final_kalsit=sisi * rng.uniform(0.65, 0.95, n),
            y_final_arag=rng.uniform(-0.55, 0.55, n),
        )
        st.session_state[seed_key] = seed
    return st.session_state[cache_key]


def buat_figur_pipa_animasi(basis, frame, kecepatan, frac_kalsit_val, status_on, judul):
    """Satu frame animasi: ion mengalir dari kiri, melewati zona kumparan
    (berubah warna netral = sedang bertransformasi), lalu keluar sebagai
    kalsit (kotak oranye, menempel dekat dinding) atau aragonit
    (bulat cyan, tersuspensi di tengah aliran)."""
    n = N_PARTIKEL
    x = (basis["base_x"] + frame * kecepatan) % 10.0
    is_kalsit = basis["rank"] < frac_kalsit_val
    y_final = np.where(is_kalsit, basis["y_final_kalsit"], basis["y_final_arag"])

    fase_ion = x < 3.0
    fase_transisi = (x >= 3.0) & (x < 5.0)
    t = np.clip((x - 3.0) / 2.0, 0, 1)

    y = np.where(fase_ion, basis["y_ion"],
                 np.where(fase_transisi, basis["y_ion"] * (1 - t) + y_final * t, y_final))

    warna_ion = np.where(basis["parity"] == 0, BLUE, GREEN)
    warna = np.where(fase_ion, warna_ion,
                      np.where(fase_transisi, TRANSISI_ABU,
                               np.where(is_kalsit, ORANGE, CYAN)))
    simbol = np.where(fase_ion | fase_transisi, "circle",
                       np.where(is_kalsit, "square", "circle"))
    ukuran = np.where(fase_ion | fase_transisi, 6, np.where(is_kalsit, 10, 6))

    fig = go.Figure()

    # zona kumparan
    fig.add_shape(type="rect", x0=3.0, x1=5.0, y0=-1, y1=1,
                  fillcolor=("rgba(0,229,255,0.10)" if status_on else "rgba(255,255,255,0.04)"),
                  line=dict(width=0))
    if status_on:
        x_wave = np.linspace(3.05, 4.95, 60)
        y_wave = 0.55 * np.sin(x_wave * 14 - frame * 0.35)
        fig.add_trace(go.Scatter(x=x_wave, y=y_wave, mode="lines",
                                  line=dict(color=CYAN, width=2),
                                  showlegend=False, hoverinfo="skip"))

    # dinding pipa
    fig.add_shape(type="line", x0=0, x1=10, y0=1, y1=1, line=dict(color="#3a4150", width=2))
    fig.add_shape(type="line", x0=0, x1=10, y0=-1, y1=-1, line=dict(color="#3a4150", width=2))

    # satu trace, warna/simbol/ukuran per-titik -> partikel mengalir mulus
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers",
        marker=dict(color=warna, size=ukuran, symbol=simbol, opacity=0.9,
                    line=dict(width=0)),
        showlegend=False, hoverinfo="skip",
    ))

    fig.update_layout(
        title=dict(text=judul, font=dict(size=12.5, color="white"), x=0.01, xanchor="left"),
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=190, margin=dict(t=32, b=6, l=6, r=6),
        xaxis=dict(range=[0, 10], showgrid=False, showticklabels=False, zeroline=False, fixedrange=True),
        yaxis=dict(range=[-1.15, 1.15], showgrid=False, showticklabels=False, zeroline=False, fixedrange=True),
        uirevision="tetap",  # cegah reset zoom/hover state antar-frame
    )
    return fig


# ----------------------------------------------------------------------
# STATE UNTUK TOMBOL RESET (mengacak ulang posisi partikel)
# ----------------------------------------------------------------------
if "seed_pipa" not in st.session_state:
    st.session_state.seed_pipa = 0
if "frame" not in st.session_state:
    st.session_state.frame = 0

# ----------------------------------------------------------------------
# LAYOUT UTAMA: VISUALISASI (kiri) + PARAMETER (kanan)
# ----------------------------------------------------------------------
col_viz, col_param = st.columns([1.55, 1])

# ---------------- PANEL PARAMETER (dihitung dulu agar tersedia utk viz) ----------------
with col_param:
    st.markdown("<div class='section-title'>Parameter Sistem</div>", unsafe_allow_html=True)

    status_on = st.toggle("Status EMSP (ON / OFF)", value=True)
    suhu_c = st.slider("Suhu Air Produksi (°C)", 20, 95, 55)
    pH = st.slider("pH Air Produksi", 6.0, 9.5, 7.8, step=0.1)
    laju_alir = st.slider("Laju Alir (m/s)", 0.2, 5.0, 2.5, step=0.1)

    with st.expander("Parameter lanjutan (kesadahan & alkalinitas)"):
        ca_hardness = st.slider("Kesadahan Kalsium (ppm CaCO3)", 50, 800, 320)
        alkalinity = st.slider("Alkalinitas (ppm CaCO3)", 50, 500, 210)
        tds = st.slider("TDS (ppm)", 500, 5000, 1200)

    # --- hitung semua turunan kimia ---
    lsi, phs = hitung_lsi(pH, suhu_c, ca_hardness, alkalinity, tds)
    dwell = faktor_waktu_tinggal(laju_alir)
    frac_on, frac_off = fraksi_kalsit(lsi, suhu_c, True, dwell_factor=dwell)
    frac_kalsit_aktif, _ = fraksi_kalsit(lsi, suhu_c, status_on, dwell_factor=dwell)

    deposit_off = laju_deposit(frac_off, lsi)
    deposit_on = laju_deposit(frac_on, lsi)

    sat_label, sat_color = label_saturasi(lsi)
    risk_label, risk_color = label_risiko(lsi, frac_kalsit_aktif)

    st.markdown(
        f"""
        <div class='metric-card border-cyan'>
            <div class='metric-row'><span class='metric-label'>Saturasi Mineral</span>
                <span style='color:{sat_color}; font-weight:700;'>{sat_label} (LSI {lsi:+.2f})</span></div>
            <div class='metric-row'><span class='metric-label'>Scale Risk</span>
                <span style='color:{risk_color}; font-weight:700;'>{risk_label}</span></div>
            <div class='metric-row'><span class='metric-label'>Waktu Tinggal di Kumparan</span>
                <span class='metric-value-white'>{dwell:.2f}× (relatif)</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='metric-card border-orange'>
            <div class='metric-label'>Sistem Konvensional (OFF)</div>
            <div class='metric-row'><span>Morfologi</span>
                <span class='metric-value-orange'>Kalsit ({frac_off*100:.0f}%)</span></div>
            <div class='metric-row'><span>Deposit</span>
                <span class='metric-value-white'>{deposit_off:.1f} mm/bln</span></div>
        </div>
        <div class='metric-card border-cyan'>
            <div class='metric-label'>Sistem EMSP (ON)</div>
            <div class='metric-row'><span>Morfologi</span>
                <span class='metric-value-cyan'>Aragonit ({(1-frac_on)*100:.0f}%)</span></div>
            <div class='metric-row'><span>Deposit</span>
                <span class='metric-value-white'>{deposit_on:.1f} mm/bln</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reduksi = (1 - deposit_on / deposit_off) * 100 if deposit_off > 0 else 0
    st.markdown(
        f"""
        <div class='metric-card' style='text-align:center;'>
            <div class='metric-label'>Estimasi Reduksi Deposit Kerak Keras</div>
            <div style='font-size:26px; font-weight:800; color:{CYAN};'>{reduksi:.0f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Reset Pipa & Grafik", use_container_width=True):
        st.session_state.seed_pipa += 1
        st.session_state.frame = 0

# ---------------- PANEL VISUALISASI PIPA (ANIMASI REAL-TIME) ----------------
with col_viz:
    kontrol_a, kontrol_b = st.columns([1, 1])
    with kontrol_a:
        animasi_aktif = st.toggle("▶️ Animasi Real-Time", value=False, key="animate_flag")
    with kontrol_b:
        kecepatan_anim = st.select_slider(
            "Kecepatan", options=["0.5×", "1×", "2×"], value="1×", key="speed_mult",
        )

    basis_off = ambil_basis_partikel("off", st.session_state.seed_pipa)
    basis_on = ambil_basis_partikel("on", st.session_state.seed_pipa + 1000)

    # kecepatan dasar mengikuti laju alir (fisis) + pengali kecepatan tampilan
    mult = {"0.5×": 0.5, "1×": 1.0, "2×": 2.0}[kecepatan_anim]
    kecepatan_frame = (0.08 + laju_alir * 0.10) * mult

    slot_off = st.empty()
    slot_on = st.empty()

    frame = st.session_state.get("frame", 0)
    fig_off = buat_figur_pipa_animasi(basis_off, frame, kecepatan_frame, frac_off, False, "EMSP: OFF (Calcite Mode)")
    fig_on = buat_figur_pipa_animasi(basis_on, frame, kecepatan_frame, frac_on, True, "EMSP: ON (Aragonite Mode)")
    slot_off.plotly_chart(fig_off, use_container_width=True, config={"displayModeBar": False}, key="pipa_off")
    slot_on.plotly_chart(fig_on, use_container_width=True, config={"displayModeBar": False}, key="pipa_on")

    st.markdown(
        f"""
        <div class='legend-row'>
            <div class='legend-item'><span class='legend-dot' style='background:{BLUE};'></span>Ion Ca²⁺</div>
            <div class='legend-item'><span class='legend-dot' style='background:{GREEN};'></span>Ion CO₃²⁻</div>
            <div class='legend-item'><span class='legend-dot' style='background:{ORANGE};'></span>Calcite (Kerak Melekat)</div>
            <div class='legend-item'><span class='legend-dot' style='background:{CYAN};'></span>Aragonite (Tersuspensi)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='progress-label' style='margin-top:14px;'>Perkembangan Kerak (OFF)</div>", unsafe_allow_html=True)
    st.progress(frac_off, text=f"{frac_off*100:.0f}% menuju kerak keras")

    st.markdown("<div class='progress-label' style='margin-top:8px;'>Suspensi Aragonit (ON)</div>", unsafe_allow_html=True)
    st.progress(1 - frac_on, text=f"{(1-frac_on)*100:.0f}% tersuspensi & terbawa aliran")

# ----------------------------------------------------------------------
# ANALISIS LANJUTAN (mempertahankan seluruh output versi sebelumnya)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:22px;'>Analisis Lanjutan</div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["⚖️ Rasio Kalsit vs Aragonit", "📈 Kinetika Kristalisasi", "🔬 Sensitivitas pH & Suhu"])

with tab1:
    fig_ratio = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Sistem OFF (Konvensional)", "Sistem ON (EMSP Aktif)"),
    )
    fig_ratio.add_trace(
        go.Pie(labels=["Kalsit (Keras, Menempel)", "Aragonit (Tersuspensi)"],
               values=[frac_off * 100, (1 - frac_off) * 100],
               marker=dict(colors=[ORANGE, CYAN]), hole=0.55,
               textinfo="label+percent", textfont=dict(color="white", size=11)),
        row=1, col=1,
    )
    fig_ratio.add_trace(
        go.Pie(labels=["Kalsit (Keras, Menempel)", "Aragonit (Tersuspensi)"],
               values=[frac_on * 100, (1 - frac_on) * 100],
               marker=dict(colors=[ORANGE, CYAN]), hole=0.55,
               textinfo="label+percent", textfont=dict(color="white", size=11)),
        row=1, col=2,
    )
    fig_ratio.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=420, showlegend=False, margin=dict(t=60, b=20, l=10, r=10),
    )
    fig_ratio.update_annotations(font=dict(color="white", size=13))
    st.plotly_chart(fig_ratio, use_container_width=True)
    st.markdown(
        f"""
        <div class='note-box'>
        Pada kondisi saat ini (pH {pH}, suhu {suhu_c}°C, laju alir {laju_alir} m/s), total presipitasi
        CaCO3 tidak hilang — yang berubah adalah <b>jalur kristalisasinya</b>. Saat EMSP ON, fraksi kalsit
        turun dari {frac_off*100:.0f}% menjadi {frac_on*100:.0f}%, digantikan aragonit yang tersuspensi
        dan ikut terbawa aliran alih-alih menempel di dinding pipa.
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab2:
    t_hari = np.linspace(0, 30, 200)
    driving = max(lsi, 0.0)
    k_off = 0.015 + 0.02 * driving + 0.001 * (suhu_c - 20)
    k_on = k_off * 0.35 * (1.3 - 0.3 * dwell)  # dwell rendah -> k_on mendekati k_off

    X_off = kurva_avrami(t_hari, max(k_off, 0.001))
    X_on = kurva_avrami(t_hari, max(k_on, 0.001))

    deposit_kumulatif_off = deposit_off * X_off
    deposit_kumulatif_on = deposit_on * X_on

    fig_kin = go.Figure()
    fig_kin.add_trace(go.Scatter(x=t_hari, y=deposit_kumulatif_off, mode="lines", name="OFF — Kerak Kalsit",
                                  line=dict(color=ORANGE, width=3), fill="tozeroy", fillcolor="rgba(255,145,0,0.15)"))
    fig_kin.add_trace(go.Scatter(x=t_hari, y=deposit_kumulatif_on, mode="lines", name="ON — Kerak Kalsit (sisa)",
                                  line=dict(color=CYAN, width=3), fill="tozeroy", fillcolor="rgba(0,229,255,0.15)"))
    fig_kin.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=430, margin=dict(t=30, b=10, l=10, r=10),
        xaxis_title="Waktu Operasi (hari)", yaxis_title="Deposit Kalsit Kumulatif (mm)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="white")),
    )
    st.plotly_chart(fig_kin, use_container_width=True)
    st.markdown(
        """
        <div class='note-box'>
        Kurva mengikuti persamaan Avrami (kurva-S) untuk transformasi fasa kristal. Laju alir yang lebih
        rendah memperbesar waktu kontak dengan medan elektromagnetik (dwell factor), membuat kurva ON
        makin landai dibanding kurva OFF.
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab3:
    colA, colB = st.columns(2)

    with colA:
        pH_range = np.linspace(6.0, 9.5, 40)
        frac_off_ph, frac_on_ph = [], []
        for p in pH_range:
            lsi_p, _ = hitung_lsi(p, suhu_c, ca_hardness, alkalinity, tds)
            fo, foff = fraksi_kalsit(lsi_p, suhu_c, True, dwell_factor=dwell)
            frac_off_ph.append(foff * 100)
            frac_on_ph.append(fo * 100)

        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=pH_range, y=frac_off_ph, mode="lines", name="OFF", line=dict(color=ORANGE, width=3)))
        fig_ph.add_trace(go.Scatter(x=pH_range, y=frac_on_ph, mode="lines", name="ON", line=dict(color=CYAN, width=3)))
        fig_ph.add_vline(x=pH, line_dash="dash", line_color="white", opacity=0.4)
        fig_ph.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=380, margin=dict(t=40, b=10, l=10, r=10), title="Fraksi Kalsit vs pH",
            xaxis_title="pH", yaxis_title="Fraksi Kalsit (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, font=dict(color="white")),
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    with colB:
        suhu_range = np.linspace(20, 95, 40)
        frac_off_t, frac_on_t = [], []
        for t in suhu_range:
            lsi_t, _ = hitung_lsi(pH, t, ca_hardness, alkalinity, tds)
            fo, foff = fraksi_kalsit(lsi_t, t, True, dwell_factor=dwell)
            frac_off_t.append(foff * 100)
            frac_on_t.append(fo * 100)

        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=suhu_range, y=frac_off_t, mode="lines", name="OFF", line=dict(color=ORANGE, width=3)))
        fig_t.add_trace(go.Scatter(x=suhu_range, y=frac_on_t, mode="lines", name="ON", line=dict(color=CYAN, width=3)))
        fig_t.add_vline(x=suhu_c, line_dash="dash", line_color="white", opacity=0.4)
        fig_t.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=380, margin=dict(t=40, b=10, l=10, r=10), title="Fraksi Kalsit vs Suhu",
            xaxis_title="Suhu (°C)", yaxis_title="Fraksi Kalsit (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, font=dict(color="white")),
        )
        st.plotly_chart(fig_t, use_container_width=True)

    st.markdown(
        """
        <div class='note-box'>
        Garis putus-putus menandai posisi pH/suhu yang sedang dipilih di panel kanan. Gunakan grafik ini
        untuk melihat kondisi operasi mana yang membuat efek EMSP paling terasa (jarak terbesar antara
        kurva ON dan OFF).
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# CATATAN ILMIAH (footer)
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class='note-box' style='margin-top:16px;'>
    ⚠️ <b>Catatan Model:</b> Simulasi ini menyederhanakan kimia larutan CaCO3 menjadi dua polimorf utama
    (kalsit &amp; aragonit) dan mengaitkan kecenderungan pengendapan dengan Langelier Saturation Index (LSI),
    aturan tahapan Ostwald untuk transformasi fasa metastabil→stabil, persamaan Avrami untuk kinetika
    pertumbuhan, dan waktu tinggal di zona kumparan sebagai proksi kekuatan paparan medan elektromagnetik.
    Posisi &amp; jumlah partikel pada visualisasi pipa bersifat ilustratif (mengikuti proporsi hasil
    perhitungan), bukan simulasi dinamika fluida sebenarnya. Angka yang ditampilkan membantu membangun
    intuisi mekanisme, bukan pengganti data hasil sampling &amp; analisis laboratorium aktual pada 4 sumur uji.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# MESIN ANIMASI REAL-TIME
# ----------------------------------------------------------------------
# Pola standar animasi di Streamlit: seluruh skrip dijalankan ulang tiap
# frame lewat st.rerun(), dengan jeda singkat (time.sleep) di antaranya.
# Widget lain (slider, toggle) tetap responsif karena diproses ulang di
# awal skrip pada setiap rerun. Animasi berhenti otomatis begitu toggle
# "Animasi Real-Time" dimatikan.
if st.session_state.get("animate_flag", False):
    st.session_state.frame = st.session_state.get("frame", 0) + 1
    time.sleep(0.06)
    st.rerun()
