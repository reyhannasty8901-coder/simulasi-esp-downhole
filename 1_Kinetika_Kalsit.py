"""
Simulasi A — Kinetika Kristalisasi Kalsium: Kalsit vs. Aragonit
================================================================
Memvisualisasikan hipotesis mekanisme inti Electromagnetic Scale
Preventer (E-Scale): saat medan elektromagnetik AKTIF (ON), presipitasi
CaCO3 tidak berkurang, tetapi jalur kristalisasinya bergeser dari
fasa kalsit (keras, menempel di dinding pipa) ke fasa aragonit
(butiran halus, tersuspensi dan ikut terbawa aliran).

Model yang dipakai bersifat edukatif/ilustratif, dibangun di atas dua
konsep kimia nyata supaya perilakunya masuk akal:
  1) Langelier Saturation Index (LSI) — mengukur kecenderungan CaCO3
     mengendap berdasarkan pH, suhu, kesadahan kalsium, dan alkalinitas.
  2) Aturan tahapan Ostwald — presipitasi cepat cenderung membentuk
     fasa metastabil (aragonit) lebih dulu, yang lama-kelamaan
     bertransformasi ke fasa stabil (kalsit) kecuali ada gangguan yang
     menahan transformasi tersebut — di sinilah efek medan elektromagnetik
     dihipotesiskan berperan.

Jalankan dengan:
    streamlit run simulasi_kinetika_kristalisasi.py
"""

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------
# KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------------------------
st.set_page_config(page_title="Simulasi A — Kinetika Kalsit vs Aragonit", layout="wide")

CYAN = "#00e5ff"
ORANGE = "#ff9100"
BG = "#12141c"
CARD_BG = "#1e212b"
MUTED = "#a0aabf"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    .metric-card {{
        background-color: {CARD_BG}; padding: 16px 18px; border-radius: 10px;
        margin-bottom: 14px; color: white;
    }}
    .border-cyan {{ border-left: 4px solid {CYAN}; }}
    .border-orange {{ border-left: 4px solid {ORANGE}; }}
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }}
    .metric-value-cyan {{ color: {CYAN}; font-weight: 700; }}
    .metric-value-orange {{ color: {ORANGE}; font-weight: 700; }}
    .metric-value-white {{ color: white; font-weight: 700; }}
    .metric-label {{ color: {MUTED}; font-size: 13px; }}
    .section-title {{ color: white; font-size: 15px; font-weight: 700; margin: 4px 0 10px 0; }}
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 10px 14px; border-radius: 8px; color: {MUTED}; font-size: 12.5px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧪 Simulasi A — Kinetika Kalsit vs Aragonit")
st.caption(
    "Model edukatif berbasis Langelier Saturation Index (LSI) dan aturan tahapan Ostwald · "
    "bukan hasil pengukuran lapangan"
)

# ----------------------------------------------------------------------
# FUNGSI PERHITUNGAN KIMIA
# ----------------------------------------------------------------------
def hitung_lsi(pH, suhu_c, ca_hardness_ppm, alkalinity_ppm, tds_ppm=1200.0):
    """Langelier Saturation Index — indikator kecenderungan CaCO3 mengendap.
    LSI > 0  -> supersaturasi, berpotensi membentuk kerak
    LSI ~ 0  -> setimbang
    LSI < 0  -> undersaturasi / korosif
    """
    A = (math.log10(tds_ppm) - 1) / 10
    B = -13.12 * math.log10(suhu_c + 273.15) + 34.55
    C = math.log10(max(ca_hardness_ppm, 1)) - 0.4
    D = math.log10(max(alkalinity_ppm, 1))
    pHs = (9.3 + A + B) - (C + D)
    return pH - pHs, pHs


def fraksi_kalsit(lsi, suhu_c, status_on, geser_maks=0.50):
    """Estimasi fraksi kalsit dari total CaCO3 yang terbentuk.

    Tanpa treatment (OFF): supersaturasi & suhu tinggi mempercepat
    transformasi Ostwald dari aragonit -> kalsit, sehingga fraksi kalsit
    naik seiring LSI dan suhu.

    Dengan E-Scale (ON): medan elektromagnetik dihipotesiskan menahan
    transformasi tersebut, sehingga fraksi kalsit bergeser turun (aragonit
    tetap dominan / tersuspensi).
    """
    driving = max(lsi, 0.0)
    frac_off = 0.55 + 0.06 * driving + 0.0035 * (suhu_c - 20)
    frac_off = float(np.clip(frac_off, 0.50, 0.97))

    if not status_on:
        return frac_off, frac_off

    # Efek E-Scale sedikit lebih kuat saat driving force tinggi
    # (lebih banyak inti kristal yang "terpapar" medan elektromagnetik)
    geser = geser_maks * (0.6 + 0.4 * min(driving / 2.0, 1.0))
    frac_on = float(np.clip(frac_off - geser, 0.08, 0.95))
    return frac_on, frac_off


def laju_deposit(fraksi_kalsit_val, lsi, k_deposit=1.35):
    """Laju penebalan kerak keras (mm/bulan) — hanya fraksi kalsit yang
    dianggap menempel permanen; aragonit diasumsikan tersuspensi & terbawa aliran."""
    driving = max(lsi, 0.0)
    potensi_total = k_deposit * (driving ** 1.3)
    return potensi_total * fraksi_kalsit_val


def kurva_avrami(t_hari, k, n=1.6):
    """Persamaan Avrami — fraksi transformasi kristal terhadap waktu (kurva-S)."""
    return 1 - np.exp(-k * np.power(np.maximum(t_hari, 0), n))


# ----------------------------------------------------------------------
# LAYOUT: PANEL INPUT (kiri/sidebar) + PANEL HASIL (kanan)
# ----------------------------------------------------------------------
col_main, col_param = st.columns([2.6, 1])

with col_param:
    st.markdown("<div class='section-title'>⚙️ Parameter Simulasi</div>", unsafe_allow_html=True)

    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    status_on = st.toggle("Status E-Scale (ON / OFF)", value=True)
    st.markdown(
        f"Status saat ini: "
        f"<span class='{'metric-value-cyan' if status_on else 'metric-value-orange'}'>"
        f"{'AKTIF (ON)' if status_on else 'NONAKTIF (OFF)'}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    suhu_c = st.slider("Suhu Air Produksi (°C)", 20, 95, 55)
    pH = st.slider("pH Air Produksi", 6.0, 9.5, 7.8, step=0.1)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Parameter lanjutan (kesadahan & alkalinitas)"):
        ca_hardness = st.slider("Kesadahan Kalsium (ppm CaCO3)", 50, 800, 320)
        alkalinity = st.slider("Alkalinitas (ppm CaCO3)", 50, 500, 210)
        tds = st.slider("TDS (ppm)", 500, 5000, 1200)

    lsi, phs = hitung_lsi(pH, suhu_c, ca_hardness, alkalinity, tds)
    frac_on, frac_off = fraksi_kalsit(lsi, suhu_c, True)  # dua-duanya dihitung utk perbandingan
    frac_kalsit_aktif, _ = fraksi_kalsit(lsi, suhu_c, status_on)
    frac_aragonit_aktif = 1 - frac_kalsit_aktif

    deposit_off = laju_deposit(frac_off, lsi)
    deposit_on = laju_deposit(frac_on, lsi)
    deposit_aktif = deposit_on if status_on else deposit_off

    st.markdown("<div class='section-title'>📊 Indeks Saturasi</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-row'><span class='metric-label'>LSI</span>
                <span class='metric-value-white'>{lsi:+.2f}</span></div>
            <div class='metric-row'><span class='metric-label'>pH Saturasi (pHs)</span>
                <span class='metric-value-white'>{phs:.2f}</span></div>
            <div class='metric-row'><span class='metric-label'>Interpretasi</span>
                <span class='metric-value-white'>{"Supersaturasi (berpotensi kerak)" if lsi > 0.2 else ("Mendekati setimbang" if lsi > -0.2 else "Undersaturasi")}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='metric-card border-orange'>
            <div class='metric-label'>Sistem Konvensional (OFF)</div>
            <div class='metric-row'><span>Dominasi</span>
                <span class='metric-value-orange'>Kalsit {frac_off*100:.0f}% (Melekat)</span></div>
            <div class='metric-row'><span>Laju Deposit</span>
                <span class='metric-value-white'>{deposit_off:.2f} mm/bln</span></div>
        </div>
        <div class='metric-card border-cyan'>
            <div class='metric-label'>Sistem E-Scale (ON)</div>
            <div class='metric-row'><span>Dominasi</span>
                <span class='metric-value-cyan'>Aragonit {(1-frac_on)*100:.0f}% (Tersuspensi)</span></div>
            <div class='metric-row'><span>Laju Deposit</span>
                <span class='metric-value-white'>{deposit_on:.2f} mm/bln</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reduksi = (1 - deposit_on / deposit_off) * 100 if deposit_off > 0 else 0
    st.markdown(
        f"""
        <div class='metric-card' style='text-align:center;'>
            <div class='metric-label'>Estimasi Reduksi Deposit Kerak Keras</div>
            <div style='font-size:28px; font-weight:800; color:{CYAN};'>{reduksi:.0f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_main:
    tab1, tab2, tab3 = st.tabs(["⚖️ Rasio Kalsit vs Aragonit", "📈 Kinetika Kristalisasi", "🔬 Sensitivitas pH & Suhu"])

    # ---- TAB 1: rasio kalsit vs aragonit (ON vs OFF) ----
    with tab1:
        fig_ratio = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "domain"}, {"type": "domain"}]],
            subplot_titles=("Sistem OFF (Konvensional)", "Sistem ON (E-Scale Aktif)"),
        )
        fig_ratio.add_trace(
            go.Pie(
                labels=["Kalsit (Keras, Menempel)", "Aragonit (Tersuspensi)"],
                values=[frac_off * 100, (1 - frac_off) * 100],
                marker=dict(colors=[ORANGE, CYAN]),
                hole=0.55,
                textinfo="label+percent",
                textfont=dict(color="white", size=11),
            ),
            row=1, col=1,
        )
        fig_ratio.add_trace(
            go.Pie(
                labels=["Kalsit (Keras, Menempel)", "Aragonit (Tersuspensi)"],
                values=[frac_on * 100, (1 - frac_on) * 100],
                marker=dict(colors=[ORANGE, CYAN]),
                hole=0.55,
                textinfo="label+percent",
                textfont=dict(color="white", size=11),
            ),
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
            Pada kondisi saat ini (pH {pH}, suhu {suhu_c}°C), total presipitasi CaCO3 tidak hilang —
            yang berubah adalah <b>jalur kristalisasinya</b>. Saat E-Scale ON, fraksi kalsit turun dari
            {frac_off*100:.0f}% menjadi {frac_on*100:.0f}%, digantikan aragonit yang tersuspensi dan
            ikut terbawa aliran alih-alih menempel di dinding pipa.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- TAB 2: kurva kinetika (kurva-S Avrami) ----
    with tab2:
        t_hari = np.linspace(0, 30, 200)
        driving = max(lsi, 0.0)
        k_off = 0.015 + 0.02 * driving + 0.001 * (suhu_c - 20)
        k_on = k_off * 0.35  # medan elektromagnetik memperlambat pertumbuhan kalsit adheren

        X_off = kurva_avrami(t_hari, max(k_off, 0.001))
        X_on = kurva_avrami(t_hari, max(k_on, 0.001))

        deposit_kumulatif_off = deposit_off * X_off
        deposit_kumulatif_on = deposit_on * X_on

        fig_kin = go.Figure()
        fig_kin.add_trace(go.Scatter(
            x=t_hari, y=deposit_kumulatif_off, mode="lines", name="OFF — Kerak Kalsit",
            line=dict(color=ORANGE, width=3), fill="tozeroy", fillcolor="rgba(255,145,0,0.15)",
        ))
        fig_kin.add_trace(go.Scatter(
            x=t_hari, y=deposit_kumulatif_on, mode="lines", name="ON — Kerak Kalsit (sisa)",
            line=dict(color=CYAN, width=3), fill="tozeroy", fillcolor="rgba(0,229,255,0.15)",
        ))
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
            Kurva mengikuti persamaan Avrami (kurva-S) untuk transformasi fasa kristal.
            Semakin landai kurva ON, semakin lambat kalsit keras terbentuk — sebagian besar
            CaCO3 tetap dalam fasa aragonit yang tersuspensi dan tidak terhitung sebagai deposit adheren.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- TAB 3: sensitivitas terhadap pH & suhu ----
    with tab3:
        colA, colB = st.columns(2)

        with colA:
            pH_range = np.linspace(6.0, 9.5, 40)
            frac_off_ph, frac_on_ph = [], []
            for p in pH_range:
                lsi_p, _ = hitung_lsi(p, suhu_c, ca_hardness, alkalinity, tds)
                fo, foff = fraksi_kalsit(lsi_p, suhu_c, True)
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
                fo, foff = fraksi_kalsit(lsi_t, t, True)
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
            Garis putus-putus menandai posisi pH/suhu yang sedang dipilih di panel kiri.
            Gunakan grafik ini untuk melihat kondisi operasi mana yang membuat efek E-Scale
            paling terasa (jarak terbesar antara kurva ON dan OFF).
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class='note-box' style='margin-top:10px;'>
    ⚠️ <b>Catatan model:</b> Simulasi ini menyederhanakan kimia larutan CaCO3 menjadi dua polimorf
    (kalsit &amp; aragonit) dan menghitung kecenderungan pengendapan lewat LSI serta kurva Avrami.
    Angka yang ditampilkan bersifat ilustratif untuk membangun intuisi mekanisme, bukan pengganti
    data hasil sampling &amp; analisis laboratorium aktual pada 4 sumur uji.
    </div>
    """,
    unsafe_allow_html=True,
)
