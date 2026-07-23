"""
Kalkulator Interaktif — Kecepatan Alir Fluida & Waktu Tempuh (Residence Time)
================================================================================
Alat bantu interaktif untuk menghitung kecepatan alir fluida di dalam
tubing dan waktu tempuhnya dari kedalaman sumur (MD) hingga ke
permukaan/flowline -- dipakai untuk menentukan residence time sebagai
dasar jadwal sampling ON->OFF (tunggu 3-5x residence time sebelum
sampel OFF dianggap representatif).

Rumus yang dipakai (identik dengan perhitungan manual sebelumnya):
    A (ft^2)     = (pi/4) * ID(ft)^2
    Q (ft^3/s)   = BFPD * 5.614583 / 86400
    v (ft/s)     = Q / A
    t (detik)    = MD(ft) / v(ft/s)

Jalankan dengan:
    streamlit run kalkulator_kecepatan_alir.py
"""

import json
import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------------------------------------------------
# KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------------------------
st.set_page_config(page_title="Kalkulator Kecepatan Alir & Waktu Tempuh Fluida", layout="wide")

BG = "#0a0c12"
CARD_BG = "#151824"
MUTED = "#94a3b8"
CYAN = "#22d3ee"
GREEN = "#22c55e"
ORANGE = "#f97316"
PURPLE = "#a855f7"
RED = "#ef4444"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    .metric-card {{
        background-color: {CARD_BG}; padding: 16px 20px; border-radius: 12px;
        margin-bottom: 12px; color: white;
    }}
    .border-cyan {{ border-left: 4px solid {CYAN}; }}
    .border-green {{ border-left: 4px solid {GREEN}; }}
    .border-orange {{ border-left: 4px solid {ORANGE}; }}
    .border-purple {{ border-left: 4px solid {PURPLE}; }}
    .metric-label {{ color: {MUTED}; font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .metric-value {{ font-size: 26px; font-weight: 800; color: white; margin-top: 2px; }}
    .metric-sub {{ color: {MUTED}; font-size: 12px; margin-top: 2px; }}
    .section-title {{ color: white; font-size: 17px; font-weight: 700; margin: 6px 0 12px 0; }}
    .step-card {{
        background-color: {CARD_BG}; padding: 14px 18px; border-radius: 10px;
        margin-bottom: 10px; border-left: 3px solid {CYAN};
    }}
    .step-title {{ color: white; font-weight: 700; font-size: 13.5px; margin-bottom: 4px; }}
    .step-detail {{ color: {MUTED}; font-size: 12.5px; }}
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 12px 16px; border-radius: 8px; color: {MUTED}; font-size: 12px; line-height: 1.55;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h2 style='text-align:center; color:white;'>Kalkulator Kecepatan Alir &amp; Waktu Tempuh Fluida</h2>"
    "<p style='text-align:center; color:#94a3b8; margin-top:-8px;'>"
    "Isi angka sumurmu sendiri &mdash; hasil &amp; penjelasannya muncul otomatis</p>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# REFERENSI UKURAN TUBING (ID umum per nominal size) -- bisa dioverride manual
# ----------------------------------------------------------------------
TUBING_PRESETS = {
    "2-3/8\" \u2014 umum EUE 4,7 lb/ft (ID \u2248 1,995 in)": 1.995,
    "2-7/8\" \u2014 umum EUE 6,5 lb/ft (ID \u2248 2,441 in)": 2.441,
    "3-1/2\" \u2014 umum EUE 9,3 lb/ft (ID \u2248 2,992 in)": 2.992,
    "4\" \u2014 umum EUE 11,0 lb/ft (ID \u2248 3,476 in)": 3.476,
    "4-1/2\" \u2014 umum EUE 12,75 lb/ft (ID \u2248 3,958 in)": 3.958,
    "Custom (isi ID manual)": None,
}

BBL_TO_FT3 = 5.614583
SEC_PER_DAY = 86400
FT_TO_M = 0.3048


def hitung(bfpd, md_ft, id_in):
    """Fungsi inti perhitungan. Mengembalikan dict semua nilai antara
    supaya bisa ditampilkan sebagai penjelasan step-by-step."""
    id_ft = id_in / 12.0
    a_ft2 = (math.pi / 4) * id_ft**2

    q_ft3_day = bfpd * BBL_TO_FT3
    q_ft3_s = q_ft3_day / SEC_PER_DAY

    v_ft_s = q_ft3_s / a_ft2 if a_ft2 > 0 else 0.0
    v_ft_min = v_ft_s * 60
    v_m_s = v_ft_s * FT_TO_M

    t_s = md_ft / v_ft_s if v_ft_s > 0 else float("inf")
    t_min = t_s / 60
    t_hr = t_min / 60
    t_day = t_hr / 24

    return dict(
        id_in=id_in, id_ft=id_ft, a_ft2=a_ft2,
        q_ft3_day=q_ft3_day, q_ft3_s=q_ft3_s,
        v_ft_s=v_ft_s, v_ft_min=v_ft_min, v_m_s=v_m_s,
        t_s=t_s, t_min=t_min, t_hr=t_hr, t_day=t_day,
        bfpd=bfpd, md_ft=md_ft,
    )


def fmt_waktu(t_hr):
    if t_hr == float("inf"):
        return "\u221e (kecepatan = 0)"
    if t_hr < 1:
        return f"{t_hr*60:.1f} menit"
    if t_hr < 48:
        return f"{t_hr:.2f} jam"
    return f"{t_hr:.2f} jam ({t_hr/24:.2f} hari)"


# ----------------------------------------------------------------------
# BAGIAN 1 — KALKULATOR SATU SUMUR (INPUT BEBAS)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title'>1. Kalkulator Interaktif</div>", unsafe_allow_html=True)
col_input, col_result = st.columns([1, 1.4])

with col_input:
    st.markdown("<div class='step-title' style='margin-bottom:6px;'>Isi Data Sumur</div>", unsafe_allow_html=True)

    nama_sumur = st.text_input("Nama Sumur (opsional)", value="Sumur Saya")
    bfpd_input = st.number_input("Laju Alir Fluida (BFPD)", min_value=0.0, value=270.0, step=1.0)
    md_input = st.number_input("Kedalaman Sumur / MD (ft)", min_value=0.0, value=8195.0, step=1.0)

    tubing_choice = st.selectbox("Ukuran Tubing", list(TUBING_PRESETS.keys()), index=2)
    if TUBING_PRESETS[tubing_choice] is None:
        id_input = st.number_input("ID Tubing Manual (in)", min_value=0.1, value=2.992, step=0.001, format="%.3f")
    else:
        id_input = TUBING_PRESETS[tubing_choice]
        st.markdown(
            f"<div class='note-box'>ID yang dipakai: <b style='color:white;'>{id_input:.3f} in</b>. "
            "Ini nilai referensi umum -- ganti ke \"Custom\" jika kamu punya data ID aktual dari tally tubing.</div>",
            unsafe_allow_html=True,
        )

res = hitung(bfpd_input, md_input, id_input)

with col_result:
    st.markdown(
        f"""
        <div class='metric-card border-cyan'>
            <div class='metric-label'>Kecepatan Alir Fluida</div>
            <div class='metric-value'>{res['v_ft_s']:.4f} ft/s <span style='font-size:16px; color:{MUTED};'>({res['v_m_s']:.4f} m/s)</span></div>
            <div class='metric-sub'>{res['v_ft_min']:.2f} ft/menit</div>
        </div>
        <div class='metric-card border-purple'>
            <div class='metric-label'>Waktu Tempuh ke Flowline</div>
            <div class='metric-value'>{fmt_waktu(res['t_hr'])}</div>
            <div class='metric-sub'>({res['t_min']:.1f} menit &mdash; ini "residence time" 1&times;)</div>
        </div>
        <div class='metric-card border-orange'>
            <div class='metric-label'>Rekomendasi Tunggu Sampling OFF (3&ndash;5&times; residence time)</div>
            <div class='metric-value' style='font-size:20px;'>{res['t_hr']*3:.1f} &ndash; {res['t_hr']*5:.1f} jam</div>
            <div class='metric-sub'>&asymp; {res['t_hr']*3/24:.2f} &ndash; {res['t_hr']*5/24:.2f} hari</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# PENJELASAN STEP-BY-STEP (dinamis, angka asli dari input pengguna)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:10px;'>Penjelasan Langkah demi Langkah</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class='step-card'>
        <div class='step-title'>Langkah 1 &mdash; Luas Penampang Dalam Tubing (A)</div>
        <div class='step-detail'>ID = {res['id_in']:.3f} in = {res['id_ft']:.5f} ft</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.latex(rf"A = \frac{{\pi}}{{4}} \times ID^2 = \frac{{\pi}}{{4}} \times ({res['id_ft']:.5f})^2 = {res['a_ft2']:.6f}\ ft^2")

st.markdown(
    f"""
    <div class='step-card'>
        <div class='step-title'>Langkah 2 &mdash; Konversi Debit ke ft&sup3;/detik</div>
        <div class='step-detail'>1 barel = 5,614583 ft&sup3; &nbsp;|&nbsp; 1 hari = 86.400 detik</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.latex(rf"Q = \frac{{{res['bfpd']:.1f} \times 5{{,}}614583}}{{86400}} = {res['q_ft3_s']:.6f}\ ft^3/detik")

st.markdown(
    """
    <div class='step-card'>
        <div class='step-title'>Langkah 3 &mdash; Kecepatan Alir</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.latex(rf"v = \frac{{Q}}{{A}} = \frac{{{res['q_ft3_s']:.6f}}}{{{res['a_ft2']:.6f}}} = {res['v_ft_s']:.4f}\ ft/detik = {res['v_m_s']:.4f}\ m/detik")

st.markdown(
    f"""
    <div class='step-card'>
        <div class='step-title'>Langkah 4 &mdash; Waktu Tempuh</div>
        <div class='step-detail'>MD = {res['md_ft']:.0f} ft</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.latex(rf"t = \frac{{MD}}{{v}} = \frac{{{res['md_ft']:.0f}}}{{{res['v_ft_s']:.4f}}} = {res['t_s']:.1f}\ detik = {fmt_waktu(res['t_hr'])}")

st.markdown(
    f"""
    <div class='note-box' style='margin-top:6px;'>
    <b>Artinya untuk {nama_sumur}:</b> tanpa bantuan e-Scale, fluida butuh <b style='color:white;'>{fmt_waktu(res['t_hr'])}</b>
    untuk menempuh jarak dari kedalaman {res['md_ft']:.0f} ft sampai ke flowline. Untuk sampling OFF yang representatif
    (medan sudah benar-benar tidak berpengaruh di titik sampling), disarankan menunggu
    <b style='color:{ORANGE};'>{res['t_hr']*3:.1f}&ndash;{res['t_hr']*5:.1f} jam</b> (3&ndash;5&times; residence time) setelah e-Scale dimatikan.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# BAGIAN 2 — PERBANDINGAN MULTI-SUMUR (TABEL YANG BISA DIEDIT)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:26px;'>2. Perbandingan Multi-Sumur</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='note-box'>Tambah/edit baris di tabel ini untuk membandingkan beberapa sumur sekaligus. "
    "Semua kolom hasil dihitung otomatis dari rumus yang sama di atas.</div>",
    unsafe_allow_html=True,
)

if "well_table" not in st.session_state:
    st.session_state.well_table = pd.DataFrame(
        [
            {"Sumur": "A", "BFPD": 270, "MD (ft)": 8195, "ID Tubing (in)": 2.992},
            {"Sumur": "B", "BFPD": 116, "MD (ft)": 4363, "ID Tubing (in)": 2.992},
            {"Sumur": "C", "BFPD": 134, "MD (ft)": 4750, "ID Tubing (in)": 2.992},
            {"Sumur": "D", "BFPD": 55, "MD (ft)": 4502, "ID Tubing (in)": 2.992},
        ]
    )

edited = st.data_editor(
    st.session_state.well_table,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Sumur": st.column_config.TextColumn("Sumur"),
        "BFPD": st.column_config.NumberColumn("BFPD", min_value=0.0, step=1.0),
        "MD (ft)": st.column_config.NumberColumn("MD (ft)", min_value=0.0, step=1.0),
        "ID Tubing (in)": st.column_config.NumberColumn("ID Tubing (in)", min_value=0.1, step=0.001, format="%.3f"),
    },
    key="well_editor",
)
st.session_state.well_table = edited

# hitung untuk setiap baris
rows_out = []
for _, row in edited.iterrows():
    try:
        r = hitung(float(row["BFPD"]), float(row["MD (ft)"]), float(row["ID Tubing (in)"]))
        rows_out.append({
            "Sumur": row["Sumur"],
            "BFPD": row["BFPD"],
            "MD (ft)": row["MD (ft)"],
            "v (ft/s)": round(r["v_ft_s"], 4),
            "v (m/s)": round(r["v_m_s"], 4),
            "Waktu Tempuh (jam)": round(r["t_hr"], 2),
            "Tunggu OFF 3\u00d7 (jam)": round(r["t_hr"] * 3, 1),
            "Tunggu OFF 5\u00d7 (jam)": round(r["t_hr"] * 5, 1),
        })
    except (ValueError, ZeroDivisionError):
        continue

if rows_out:
    df_result = pd.DataFrame(rows_out)
    st.dataframe(df_result, use_container_width=True, hide_index=True)

    csv = df_result.to_csv(index=False).encode("utf-8")
    st.download_button("\U0001f4e5 Unduh Hasil sebagai CSV", data=csv, file_name="hasil_perhitungan_waktu_tempuh.csv", mime="text/csv")

    # grafik perbandingan
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_result["Sumur"], y=df_result["Waktu Tempuh (jam)"],
        name="Waktu Tempuh (1\u00d7)", marker_color=CYAN,
        text=df_result["Waktu Tempuh (jam)"], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=df_result["Sumur"], y=df_result["Tunggu OFF 5\u00d7 (jam)"] - df_result["Waktu Tempuh (jam)"],
        name="Tambahan hingga 5\u00d7 (rekomendasi tunggu)", marker_color=ORANGE,
        base=df_result["Waktu Tempuh (jam)"],
    ))
    fig.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(t=30, b=10, l=10, r=10), barmode="stack",
        xaxis_title="Sumur", yaxis_title="Jam",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="white")),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Tambahkan minimal satu baris data sumur yang valid untuk melihat perbandingan.")

# ----------------------------------------------------------------------
# BAGIAN 3 — VISUALISASI KECEPATAN RELATIF (HTML/CANVAS)
# ----------------------------------------------------------------------
if rows_out:
    st.markdown("<div class='section-title' style='margin-top:26px;'>3. Visualisasi Kecepatan Relatif Antar Sumur</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='note-box'>Setiap jalur mewakili satu sumur; kecepatan penanda diskalakan proporsional terhadap kecepatan alir sesungguhnya (bukan skala waktu asli) supaya perbedaannya terlihat jelas.</div>",
        unsafe_allow_html=True,
    )

    _LANE_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', sans-serif; }
  canvas { width: 100%; display: block; background: #05060a; border-radius: 12px; }
</style>
</head>
<body>
<canvas id="lanes" width="1000" height="__CANVAS_H__"></canvas>
<script>
const WELLS = __WELLS_JSON__;
const canvas = document.getElementById('lanes');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const marginL = 130, marginR = 40, marginTop = 30;
const laneH = 56;
const maxV = Math.max(...WELLS.map(w => w.v));

const colors = ['#22d3ee', '#a855f7', '#22c55e', '#f97316', '#f43f5e', '#eab308', '#3b82f6', '#ec4899'];

let markers = WELLS.map((w, i) => ({ x: marginL, speed: 1.2 + (w.v / maxV) * 5.5 }));
let frame = 0;

function draw() {
  ctx.clearRect(0, 0, W, H);
  WELLS.forEach((w, i) => {
    const y = marginTop + i * laneH + laneH / 2;
    ctx.strokeStyle = 'rgba(148,163,184,0.25)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(marginL, y); ctx.lineTo(W - marginR, y); ctx.stroke();

    ctx.fillStyle = '#e5e9f0'; ctx.font = 'bold 13px Segoe UI'; ctx.textAlign = 'right';
    ctx.fillText(w.name, marginL - 14, y + 4);
    ctx.fillStyle = '#94a3b8'; ctx.font = '11px Segoe UI'; ctx.textAlign = 'left';
    ctx.fillText(w.v.toFixed(4) + ' ft/s', W - marginR + 8, y + 4);

    const m = markers[i];
    m.x += m.speed;
    if (m.x > W - marginR) m.x = marginL;

    ctx.beginPath();
    ctx.arc(m.x, y, 8, 0, Math.PI * 2);
    ctx.fillStyle = colors[i % colors.length];
    ctx.fill();
    ctx.strokeStyle = 'white'; ctx.lineWidth = 1.5; ctx.stroke();
  });
  frame++;
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);
</script>
</body>
</html>
"""
    wells_for_js = [{"name": str(r["Sumur"]), "v": float(r["v (ft/s)"])} for r in rows_out]
    canvas_h = 30 + 56 * max(1, len(wells_for_js)) + 20
    html = _LANE_HTML_TEMPLATE.replace("__WELLS_JSON__", json.dumps(wells_for_js)).replace("__CANVAS_H__", str(canvas_h))
    components.html(html, height=canvas_h + 20, scrolling=False)

# ----------------------------------------------------------------------
# CATATAN MODEL (footer)
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class='note-box' style='margin-top:20px;'>
    &#9888; <b>Catatan Model:</b> Perhitungan mengasumsikan aliran fluida tunggal homogen mengisi penuh
    penampang tubing (single-phase plug flow) &mdash; bukan model multiphase. Untuk sumur dengan water cut
    dan GLR tinggi, kecepatan aktual masing-masing fasa (minyak, air, gas) bisa berbeda dari kecepatan
    campuran rata-rata karena efek slip antar fasa. ID tubing pada preset bersifat referensi umum
    berdasarkan spesifikasi EUE standar &mdash; gunakan opsi "Custom" dan data tally tubing aktual untuk
    hasil yang presisi.
    </div>
    """,
    unsafe_allow_html=True,
)
