"""
Simulasi Mekanisme EMSP — Pemisahan Jalur Ion oleh Gaya Lorentz & Hidrasi
==========================================================================
Memvisualisasikan hipotesis mekanisme (salah satu dari beberapa yang
bersaing di literatur, lihat panel "Dasar Literatur" di app): medan
elektromagnetik mengganggu lintasan ion Ca2+ (kation) dan HCO3- (anion)
lewat gaya Lorentz F = q(v x B), serta mengubah selubung hidrasinya,
sehingga saat keduanya bertemu untuk membentuk CaCO3, mereka lebih
cenderung membentuk aragonit (tersuspensi) ketimbang kalsit (menempel).

KEJUJURAN ILMIAH — INI YANG MEMBEDAKAN SIMULASI INI DARI SEKADAR ANIMASI:
  Radius girasi Lorentz r = m*v/(q*B) untuk ion sekecil Ca2+/HCO3- pada
  kekuatan medan & kecepatan alir yang realistis ternyata hanya berorde
  NANOMETER — sekitar 40.000x lebih kecil dari diameter pipa. Artinya
  visual "dua aliran ion terpisah jelas jadi dua jalur berbeda" (seperti
  pada gambar referensi/CGI ilustratif) TIDAK literal secara fisika;
  itu representasi konseptual, bukan lintasan sesungguhnya. Panel
  "Perhitungan Fisika" di app ini menghitung & menampilkan angka aslinya
  secara live, supaya pengguna tahu skala sebenarnya di balik animasi.

  Untuk medan AC/osilasi (spesifikasi asli EMSP, ~100-200 kHz), ion
  bahkan belum sempat menyelesaikan sebagian kecil putaran girasi
  sebelum arah medannya sudah berbalik -- sehingga efek defleksi bersih
  (net) mendekati nol tanpa mekanisme rectifying tambahan. Ini alasan
  simulasi menyediakan mode "Medan Statis (DC)" vs "Medan Osilasi (AC)"
  secara terpisah dan menunjukkan hasil yang BERBEDA di keduanya.

Jalankan dengan:
    streamlit run simulasi_lorentz_pemisahan_ion.py
"""

import json
import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------------------------------------------------
# KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------------------------
st.set_page_config(page_title="Simulasi Mekanisme EMSP: Pemisahan Jalur Ion", layout="wide")

BG = "#0a0c12"
CARD_BG = "#151824"
CARD_BG2 = "#1b1f2e"
MUTED = "#94a3b8"
CYAN = "#22d3ee"
GREEN = "#22c55e"
YELLOW = "#eab308"
ROSE = "#f43f5e"      # kation Ca2+
BLUE = "#3b82f6"      # anion HCO3-
ORANGE = "#f97316"    # kalsit (kerak, menempel)
PURPLE = "#a855f7"    # aragonit (tersuspensi)
RED = "#ef4444"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    .metric-card {{
        background-color: {CARD_BG}; padding: 14px 18px; border-radius: 10px;
        margin-bottom: 12px; color: white;
    }}
    .border-rose {{ border-left: 4px solid {ROSE}; }}
    .border-blue {{ border-left: 4px solid {BLUE}; }}
    .border-green {{ border-left: 4px solid {GREEN}; }}
    .border-purple {{ border-left: 4px solid {PURPLE}; }}
    .border-orange {{ border-left: 4px solid {ORANGE}; }}
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13.5px; }}
    .metric-label {{ color: {MUTED}; font-size: 12.5px; }}
    .metric-value-rose {{ color: {ROSE}; font-weight: 700; }}
    .metric-value-blue {{ color: {BLUE}; font-weight: 700; }}
    .metric-value-green {{ color: {GREEN}; font-weight: 700; }}
    .metric-value-purple {{ color: {PURPLE}; font-weight: 700; }}
    .metric-value-white {{ color: white; font-weight: 700; }}
    .section-title {{ color: white; font-size: 16px; font-weight: 700; margin: 4px 0 10px 0; }}
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 12px 16px; border-radius: 8px; color: {MUTED}; font-size: 12px; line-height: 1.55;
    }}
    .mech-card {{
        background-color: {CARD_BG}; padding: 14px 16px; border-radius: 10px; height: 100%;
        border-top: 3px solid {CYAN};
    }}
    .mech-title {{ color: white; font-weight: 700; font-size: 13.5px; margin-bottom: 6px; }}
    .mech-body {{ color: {MUTED}; font-size: 12px; line-height: 1.5; }}
    .honesty-box {{
        background-color: #2a1620; border-left: 5px solid {ROSE};
        padding: 16px 20px; border-radius: 10px; color: #fecdd3; font-size: 13.5px; line-height: 1.6;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h2 style='text-align:center; color:white;'>Simulasi Mekanisme EMSP: Pemisahan Jalur Ion oleh Gaya Lorentz &amp; Hidrasi</h2>"
    "<p style='text-align:center; color:#94a3b8; margin-top:-8px;'>"
    "Kation Ca&sup2;&#8314; &amp; anion HCO&#8323;&#8315; &mdash; dengan panel fisika kuantitatif jujur di sampingnya</p>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# KONSTANTA & FUNGSI FISIKA
# ----------------------------------------------------------------------
U = 1.66053906660e-27   # kg per amu
E = 1.602176634e-19     # C

M_CA = 40.078 * U        # massa Ca2+
Q_CA = 2 * E              # muatan Ca2+
M_HCO3 = 61.0168 * U      # massa HCO3-
Q_HCO3 = 1 * E             # muatan HCO3-

COIL_LENGTH_M = 0.15      # m, panjang kumparan (konsisten dgn simulasi pipa sebelumnya)
PIPE_DIAM_M = 0.05        # m, diameter tubing tipikal


def gyroradius(mass_kg, charge_c, v_ms, b_tesla):
    """Radius girasi Lorentz: r = m*v / (q*B)."""
    if b_tesla <= 0:
        return float("inf")
    return mass_kg * v_ms / (charge_c * b_tesla)


def transit_time(v_ms, length_m):
    return length_m / max(v_ms, 1e-9)


def ac_half_period(freq_hz):
    return 1 / (2 * max(freq_hz, 1e-9))


def fmt_len(m):
    """Format panjang dalam satuan paling terbaca (nm/um/mm/m)."""
    if m == float("inf"):
        return "\u221e"
    a = abs(m)
    if a < 1e-6:
        return f"{m*1e9:.2f} nm"
    if a < 1e-3:
        return f"{m*1e6:.2f} \u03bcm"
    if a < 1:
        return f"{m*1e3:.2f} mm"
    return f"{m:.3f} m"


# ----------------------------------------------------------------------
# LAYOUT: VISUALISASI (kiri) + PARAMETER (kanan)
# ----------------------------------------------------------------------
col_viz, col_param = st.columns([1.6, 1])

with col_param:
    st.markdown("<div class='section-title'>Parameter Medan</div>", unsafe_allow_html=True)

    mode = st.radio(
        "Mode Medan Elektromagnetik",
        ["OFF (tanpa medan)", "ON \u2014 Medan Statis (magnet DC)", "ON \u2014 Medan Osilasi (AC, sesuai spek EMSP)"],
        index=2,
        help="EMSP komersial memakai medan AC berosilasi ~100-200 kHz, BUKAN magnet permanen statis. Bandingkan ketiga mode untuk melihat bedanya.",
    )
    field_off = mode.startswith("OFF")
    field_static = mode.startswith("ON \u2014 Medan Statis")
    field_ac = mode.startswith("ON \u2014 Medan Osilasi")

    b_field_mT = st.slider("Kekuatan Medan B (mT)", 1, 500, 50, step=1,
                            help="50-100 mT tergolong kuat untuk kumparan clamp-on non-superkonduktor.")
    v_flow = st.slider("Kecepatan Alir/Drift Ion (m/s)", 0.05, 2.0, 0.5, step=0.05)
    freq_khz = st.slider("Frekuensi Medan AC (kHz)", 50, 300, 150, step=10,
                          disabled=not field_ac)
    show_hydration = st.checkbox("Tampilkan efek selubung hidrasi", value=True,
                                  help="Mekanisme independen dari pemisahan Lorentz: medan dapat mengubah lapisan air di sekitar ion, memengaruhi nukleasi meski tanpa defleksi bersih.")

    st.markdown(
        "<div class='note-box'>Animasi di kiri diskalakan agar terlihat jelas mata &mdash; BUKAN skala fisika asli. Radius girasi ion sesungguhnya jauh lebih kecil dari pipa (lihat panel Perhitungan Fisika di bawah).</div>",
        unsafe_allow_html=True,
    )

# --- Hitung fisika ---
b_field_T = b_field_mT / 1000.0
freq_hz = freq_khz * 1000.0

r_ca = gyroradius(M_CA, Q_CA, v_flow, b_field_T)
r_hco3 = gyroradius(M_HCO3, Q_HCO3, v_flow, b_field_T)

t_transit = transit_time(v_flow, COIL_LENGTH_M)
t_half_ac = ac_half_period(freq_hz)
dist_per_halfcycle = v_flow * t_half_ac
n_gyrations_per_halfcycle = dist_per_halfcycle / max(r_ca, 1e-30)

ratio_pipe_ca = r_ca / PIPE_DIAM_M

with col_param:
    st.markdown("<div class='section-title' style='margin-top:6px;'>Perhitungan Fisika (Live)</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='metric-card border-rose'>
            <div class='metric-label'>Radius Girasi Lorentz r = m&middot;v / (q&middot;B)</div>
            <div class='metric-row'><span>Ca&sup2;&#8314;</span><span class='metric-value-rose'>{fmt_len(r_ca)}</span></div>
            <div class='metric-row'><span>HCO&#8323;&#8315;</span><span class='metric-value-blue'>{fmt_len(r_hco3)}</span></div>
            <div class='metric-row'><span class='metric-label'>vs. diameter pipa ({PIPE_DIAM_M*100:.0f} cm)</span>
                <span class='metric-value-white'>{ratio_pipe_ca:.2e}&times;</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if field_ac:
        st.markdown(
            f"""
            <div class='metric-card border-blue'>
                <div class='metric-label'>Medan AC @{freq_khz} kHz</div>
                <div class='metric-row'><span>Setengah periode</span><span class='metric-value-white'>{t_half_ac*1e6:.2f} \u03bcs</span></div>
                <div class='metric-row'><span>Jarak tempuh ion / setengah-siklus</span><span class='metric-value-white'>{fmt_len(dist_per_halfcycle)}</span></div>
                <div class='metric-row'><span>Fraksi girasi tercapai sebelum medan berbalik</span>
                    <span class='metric-value-white'>{min(n_gyrations_per_halfcycle,1)*100:.1f}%</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------------------
# TENTUKAN FRAKSI ARAGONIT BERDASARKAN MODE (mengkodekan kejujuran fisika)
# ----------------------------------------------------------------------
# OFF        : baseline rendah (aragonit selalu punya sedikit peluang alami)
# AC (nyata) : girasi ion terlalu kecil & terlalu cepat berbalik utk defleksi
#              bersih -> TIDAK ada bonus dari pemisahan lintasan. Hanya
#              mekanisme hidrasi (independen arah) yang mungkin memberi
#              sedikit bonus jika diaktifkan.
# Statis DC  : mekanisme literatur yang lebih umum dibahas utk efek Lorentz;
#              diberi bonus lebih besar (namun TETAP diberi catatan bahwa
#              skala defleksi riil tidak sebesar animasi).
BASE_ARAGONITE = 0.15
HYDRATION_BONUS = 0.12
STATIC_LORENTZ_BONUS = 0.55 * min(b_field_mT / 100.0, 1.0) * min(v_flow / 0.5, 1.5)

if field_off:
    frac_aragonite = BASE_ARAGONITE
elif field_ac:
    frac_aragonite = BASE_ARAGONITE + (HYDRATION_BONUS if show_hydration else 0.0)
else:  # static
    frac_aragonite = BASE_ARAGONITE + STATIC_LORENTZ_BONUS + (HYDRATION_BONUS if show_hydration else 0.0)

frac_aragonite = float(np.clip(frac_aragonite, 0.0, 0.95))
frac_calcite = 1 - frac_aragonite

with col_param:
    st.markdown(
        f"""
        <div class='metric-card border-purple'>
            <div class='metric-label'>Hasil Simulasi (berdasar mode &amp; parameter di atas)</div>
            <div class='metric-row'><span>Fraksi Aragonit (tersuspensi)</span><span class='metric-value-purple'>{frac_aragonite*100:.0f}%</span></div>
            <div class='metric-row'><span>Fraksi Kalsit (menempel)</span><span class='metric-value-white' style='color:{ORANGE};'>{frac_calcite*100:.0f}%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("\U0001f504 Reset Animasi", use_container_width=True):
        st.session_state.reset_key = st.session_state.get("reset_key", 0) + 1

# ----------------------------------------------------------------------
# VISUALISASI PIPA — HTML/CANVAS + requestAnimationFrame
# ----------------------------------------------------------------------
_PIPE_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  :root {
    --bg: #0a0c12; --panel: #151824; --muted: #94a3b8;
    --rose: #f43f5e; --blue: #3b82f6; --green: #22c55e; --yellow: #eab308;
    --orange: #f97316; --purple: #a855f7;
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', sans-serif; }
  .wrap { display: flex; flex-direction: column; gap: 10px; }
  canvas { width: 100%; display: block; background: #06070c; border-radius: 12px; }
  .legend-row { display: flex; gap: 20px; flex-wrap: wrap; align-items: center;
      background-color: var(--panel); padding: 12px 16px; border-radius: 10px; }
  .legend-item { display: flex; align-items: center; gap: 7px; font-size: 12px; color: white; white-space: nowrap; }
  .legend-dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
  .badge-row { display: flex; justify-content: center; margin-top: 6px; }
  .badge { padding: 6px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; }
</style>
</head>
<body>
<div class="wrap">
  <canvas id="pipe" width="1000" height="440"></canvas>
  <div class="legend-row">
    <div class="legend-item"><span class="legend-dot" style="background:var(--rose);"></span>Kation Ca&sup2;&#8314;</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--blue);"></span>Anion HCO&#8323;&#8315;</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--green); border-radius:2px;"></span>Zona Kumparan EMSP</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--orange); border-radius:2px;"></span>Kalsit (menempel)</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--purple);"></span>Aragonit (tersuspensi)</div>
  </div>
  <div class="badge-row"><div id="badge" class="badge"></div></div>
</div>

<script>
const CFG = __CFG_JSON__;

const canvas = document.getElementById('pipe');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const yTop = 50, yBot = H - 70;
const midY = (yTop + yBot) / 2;
const coilX0 = W * 0.42, coilX1 = W * 0.58;
const recombX0 = coilX1, recombX1 = coilX1 + 140;

const ROSE = '#f43f5e', BLUE = '#3b82f6', ORANGE = '#f97316', ORANGE_STUCK = '#c2410c', PURPLE = '#a855f7';

const flowPx = 0.9 + CFG.vFlow * 2.2;

// -------------------- Partikel ion --------------------
let ions = [];
let crystals = [];
let scaleTop = new Array(W).fill(0);
let scaleBot = new Array(W).fill(0);
let frame = 0;

function spawnIon() {
  const isCation = Math.random() > 0.5;
  ions.push({
    x: Math.random() * 30,
    y: midY + (Math.random() - 0.5) * (yBot - yTop - 30),
    isCation,
    phase: Math.random() * Math.PI * 2,
    active: true,
  });
}

function laneTargetY(isCation) {
  // Jalur "lane" saat medan statis ON: kation naik ke atas, anion turun ke bawah
  const spread = (yBot - yTop) * 0.32;
  return isCation ? (midY - spread) : (midY + spread);
}

function updateIon(ion) {
  ion.x += flowPx;

  const inCoil = ion.x >= coilX0 && ion.x <= coilX1;
  const inRecomb = ion.x > coilX1 && ion.x <= recombX1;
  const beforeCoil = ion.x < coilX0;

  if (CFG.fieldStatic && (inCoil || (ion.x > coilX0 && ion.x <= recombX0))) {
    // defleksi mulus menuju lane masing-masing (representasi VISUAL yang
    // disederhanakan & diperbesar dari gaya Lorentz -- lihat catatan
    // kejujuran fisika: radius asli jauh lebih kecil dari ini)
    const target = laneTargetY(ion.isCation);
    ion.y += (target - ion.y) * 0.06;
  } else if (CFG.fieldAc && inCoil) {
    // jitter cepat simetris -> rata-rata net perpindahan mendekati nol
    ion.phase += 0.9;
    ion.y += Math.sin(ion.phase) * 2.2 * (ion.isCation ? 1 : -1) * 0.0 + Math.sin(ion.phase) * 2.4;
  } else if (inRecomb && CFG.fieldStatic) {
    // zona rekombinasi terkendali: lane ditarik pelan-pelan kembali ke
    // tengah agar bertemu secara lebih teratur (representasi hipotesis
    // "geometri pertemuan berbeda -> polimorf berbeda")
    ion.y += (midY - ion.y) * 0.01;
  } else {
    // gerak brownian biasa (tanpa medan / sebelum kumparan / AC di luar kumparan)
    ion.y += (Math.random() - 0.5) * 1.3;
  }

  const margin = 8;
  if (ion.y < yTop + margin) ion.y = yTop + margin;
  if (ion.y > yBot - margin) ion.y = yBot - margin;
}

function tryReact() {
  for (let i = ions.length - 1; i >= 0; i--) {
    const a = ions[i];
    if (!a.active) continue;
    for (let j = i - 1; j >= 0; j--) {
      const b = ions[j];
      if (!b.active || a.isCation === b.isCation) continue;
      const dist = Math.hypot(a.x - b.x, a.y - b.y);
      if (dist < 9) {
        a.active = false; b.active = false;
        const cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
        const isKalsit = Math.random() >= CFG.fracAragonite;
        crystals.push(makeCrystal(cx, cy, isKalsit));
        break;
      }
    }
  }
  ions = ions.filter(p => p.active);
}

function makeCrystal(x, y, isKalsit) {
  const side = (y - yTop) < (yBot - yTop) / 2 ? 'top' : 'bottom';
  return {
    x, y, isKalsit, side,
    size: isKalsit ? 3 : 2,
    vx: flowPx * (isKalsit ? 0.5 : 1.0),
    vy: isKalsit ? (side === 'top' ? -0.9 : 0.9) : (Math.random() - 0.5),
    stuck: false,
  };
}

function updateCrystal(c) {
  if (c.stuck) return;
  c.x += c.vx; c.y += c.vy;
  if (c.isKalsit) {
    if (c.size < 10) { c.size += 0.02; c.vy += (c.side === 'top' ? -0.04 : 0.04); }
    const idx = Math.min(W - 1, Math.max(0, Math.floor(c.x)));
    if (c.side === 'top') {
      const wall = yTop + c.size + (scaleTop[idx] || 0);
      if (c.y <= wall) {
        c.stuck = true; c.y = wall;
        for (let k = Math.max(0, idx - 9); k < Math.min(W, idx + 9); k++) {
          scaleTop[k] = Math.min(60, scaleTop[k] + Math.max(0, (9 - Math.abs(idx - k)) * 0.06));
        }
      }
    } else {
      const wall = yBot - c.size - (scaleBot[idx] || 0);
      if (c.y >= wall) {
        c.stuck = true; c.y = wall;
        for (let k = Math.max(0, idx - 9); k < Math.min(W, idx + 9); k++) {
          scaleBot[k] = Math.min(60, scaleBot[k] + Math.max(0, (9 - Math.abs(idx - k)) * 0.06));
        }
      }
    }
  } else {
    if (c.y > yBot - 6) { c.y = yBot - 6; c.vy = -Math.abs(c.vy || 1); }
    if (c.y < yTop + 6) { c.y = yTop + 6; c.vy = Math.abs(c.vy || 1); }
  }
}

function drawPipe() {
  ctx.clearRect(0, 0, W, H);

  // dinding pipa
  ctx.strokeStyle = '#2c3348'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(0, yTop); ctx.lineTo(W, yTop); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, yBot); ctx.lineTo(W, yBot); ctx.stroke();

  // endapan kerak kalsit
  ctx.fillStyle = '#7c2d12';
  ctx.beginPath(); ctx.moveTo(0, yTop);
  for (let i = 0; i < W; i++) ctx.lineTo(i, yTop + scaleTop[i]);
  ctx.lineTo(W, yTop); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#7c2d12';
  ctx.beginPath(); ctx.moveTo(0, yBot);
  for (let i = 0; i < W; i++) ctx.lineTo(i, yBot - scaleBot[i]);
  ctx.lineTo(W, yBot); ctx.closePath(); ctx.fill();

  // label zona
  ctx.fillStyle = '#94a3b8'; ctx.font = '11px Segoe UI'; ctx.textAlign = 'center';
  ctx.fillText('Sebelum kumparan (bercampur)', coilX0 * 0.5, yTop - 14);
  ctx.fillText('Kumparan EMSP', (coilX0 + coilX1) / 2, yTop - 14);
  ctx.fillText(CFG.fieldStatic ? 'Zona rekombinasi terkendali' : 'Setelah kumparan', (recombX1 + W) / 2, yTop - 14);

  // zona kumparan
  const coilActive = CFG.fieldStatic || CFG.fieldAc;
  ctx.fillStyle = coilActive ? 'rgba(34,197,94,0.10)' : 'rgba(255,255,255,0.03)';
  ctx.fillRect(coilX0, yTop, coilX1 - coilX0, yBot - yTop);

  if (coilActive) {
    // cincin kumparan (hijau & kuning, meniru gambar referensi)
    const cx1 = coilX0 + (coilX1 - coilX0) * 0.15;
    const cx2 = coilX0 + (coilX1 - coilX0) * 0.85;
    [cx1, cx2].forEach((cx) => {
      ctx.save();
      ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.ellipse(cx, midY, 14, (yBot - yTop) / 2 - 6, 0, 0, Math.PI * 2); ctx.stroke();
      ctx.strokeStyle = 'rgba(234,179,8,0.7)'; ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.ellipse(cx, midY, 9, (yBot - yTop) / 2 - 14, 0, 0, Math.PI * 2); ctx.stroke();
      ctx.restore();
    });
    // gelombang medan
    ctx.strokeStyle = CFG.fieldAc ? 'rgba(234,179,8,0.55)' : 'rgba(34,197,94,0.5)';
    ctx.lineWidth = 1.3;
    ctx.beginPath();
    for (let i = 0; i <= (coilX1 - coilX0); i += 4) {
      const speedMul = CFG.fieldAc ? 0.55 : 0.15;
      const yy = midY + Math.sin(i * 0.14 - frame * speedMul) * ((yBot - yTop) * 0.34);
      if (i === 0) ctx.moveTo(coilX0 + i, yy); else ctx.lineTo(coilX0 + i, yy);
    }
    ctx.stroke();
  }

  // selubung hidrasi (opsional): halo lembut di sekitar ion dekat kumparan
  if (CFG.showHydration && coilActive) {
    ions.forEach((ion) => {
      if (ion.x > coilX0 - 40 && ion.x < coilX1 + 40) {
        ctx.beginPath();
        ctx.arc(ion.x, ion.y, 8 + Math.sin(frame * 0.2 + ion.phase) * 2, 0, Math.PI * 2);
        ctx.strokeStyle = ion.isCation ? 'rgba(244,63,94,0.25)' : 'rgba(59,130,246,0.25)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    });
  }

  // ion
  ions.forEach((ion) => {
    ctx.beginPath();
    ctx.arc(ion.x, ion.y, 3.2, 0, Math.PI * 2);
    ctx.fillStyle = ion.isCation ? ROSE : BLUE;
    ctx.fill();
  });

  // kristal
  crystals.forEach((c) => {
    ctx.save(); ctx.translate(c.x, c.y);
    if (c.isKalsit) {
      ctx.fillStyle = c.stuck ? ORANGE_STUCK : ORANGE;
      ctx.fillRect(-c.size / 2, -c.size / 2, c.size, c.size);
    } else {
      ctx.fillStyle = PURPLE;
      ctx.beginPath(); ctx.ellipse(0, 0, c.size + 1.5, c.size, 0, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  });
}

function loop() {
  if (Math.random() < 0.5 && ions.length < 140) spawnIon();
  ions.forEach(updateIon);
  tryReact();
  crystals.forEach(updateCrystal);
  if (crystals.length > 700) crystals = crystals.slice(crystals.length - 700);

  drawPipe();
  frame++;
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

const badge = document.getElementById('badge');
if (CFG.fieldStatic) {
  badge.textContent = '\u2713 Medan Statis: lane kation/anion terpisah (representasi konseptual)';
  badge.style.background = 'rgba(34,197,94,0.15)'; badge.style.color = '#4ade80'; badge.style.border = '1px solid #22c55e';
} else if (CFG.fieldAc) {
  badge.textContent = '\u26a0 Medan AC (spek asli EMSP): ion bergetar di tempat, TIDAK ada pemisahan lane bersih';
  badge.style.background = 'rgba(234,179,8,0.15)'; badge.style.color = '#fbbf24'; badge.style.border = '1px solid #eab308';
} else {
  badge.textContent = '\u2715 Medan OFF: ion bercampur bebas, kalsit dominan';
  badge.style.background = 'rgba(239,68,68,0.15)'; badge.style.color = '#f87171'; badge.style.border = '1px solid #ef4444';
}
</script>
</body>
</html>
"""


def render_pipe(field_static_flag, field_ac_flag, v_flow_val, frac_arag, show_hyd):
    cfg = dict(
        fieldStatic=bool(field_static_flag),
        fieldAc=bool(field_ac_flag),
        vFlow=round(v_flow_val, 3),
        fracAragonite=round(frac_arag, 4),
        showHydration=bool(show_hyd),
    )
    html = _PIPE_HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))
    components.html(html, height=560, scrolling=False)


with col_viz:
    render_pipe(field_static, field_ac, v_flow, frac_aragonite, show_hydration)

# ----------------------------------------------------------------------
# GRAFIK: DEFLEKSI STATIS vs AC (MATEMATIS, TANPA EKSAGERASI)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:20px;'>Perbandingan Matematis: Defleksi Statis vs AC (Skala Riil)</div>", unsafe_allow_html=True)

t_ns = np.linspace(0, 20, 500)  # nanodetik
t_s = t_ns * 1e-9

# defleksi static: akumulasi linier dari gaya konstan (perkiraan sederhana, arah tetap)
a_lorentz_ca = (Q_CA * v_flow * b_field_T) / M_CA  # percepatan sentripetal ~ perkiraan magnitude gaya/massa
static_defl_nm = 0.5 * a_lorentz_ca * t_s**2 * 1e9
static_defl_nm = np.clip(static_defl_nm, 0, r_ca * 1e9 * 4)

# defleksi AC: posisi berosilasi sinusoidal, amplitudo terbatas oleh setengah-periode
omega_ac = 2 * math.pi * freq_hz
ac_defl_nm = (r_ca * 1e9) * np.sin(omega_ac * t_s)

fig = go.Figure()
fig.add_trace(go.Scatter(x=t_ns, y=static_defl_nm, mode="lines", name="Medan Statis (DC)",
                          line=dict(color=GREEN, width=3)))
fig.add_trace(go.Scatter(x=t_ns, y=ac_defl_nm, mode="lines", name=f"Medan AC ({freq_khz} kHz)",
                          line=dict(color=YELLOW, width=3)))
fig.add_hline(y=0, line_color=MUTED, line_width=1)
fig.update_layout(
    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    height=380, margin=dict(t=30, b=10, l=10, r=10),
    xaxis_title="Waktu (nanodetik)", yaxis_title="Defleksi lateral Ca\u00b2\u207a (nm)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="white")),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    f"""
    <div class='note-box'>
    Grafik ini <b>tidak diperbesar/eksagerasi</b> seperti animasi pipa di atas &mdash; sumbu-y dalam nanometer sesungguhnya.
    Medan statis (hijau) memberi defleksi yang terus terakumulasi searah selama ion berada dalam medan. Medan AC (kuning)
    membuat posisi ion berosilasi maju-mundur mengikuti perubahan arah medan {freq_khz} kali per detik &times; 1000 &mdash;
    rata-rata perpindahan bersihnya mendekati nol dalam periode yang lebih panjang.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# DASAR LITERATUR: MEKANISME YANG BERSAING
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:22px;'>Dasar Literatur: Mekanisme yang Bersaing (Belum Ada Konsensus)</div>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
mechanisms = [
    ("Gaya Lorentz", "Medan magnet memberi gaya pada ion bermuatan yang bergerak, berpotensi mengubah lintasan/orientasinya sebelum bertemu ion lawan muatan."),
    ("Perubahan Selubung Hidrasi", "Medan dapat mengubah lapisan molekul air di sekitar Ca\u00b2\u207a dan HCO\u2083\u207b, memengaruhi kemudahan mereka membentuk struktur kristal stabil."),
    ("Transformasi Klaster Air", "Ikatan hidrogen antar-klaster air melemah, sedangkan ikatan dalam-klaster menguat akibat polarisasi ion oleh gaya Lorentz."),
    ("Efek Antarmuka CO\u2082/Air", "Sebagian studi mengaitkan efek medan dengan gangguan pada antarmuka gas CO\u2082 dan air, bukan langsung pada ion terlarut."),
]
for col, (title, body) in zip([c1, c2, c3, c4], mechanisms):
    with col:
        st.markdown(
            f"<div class='mech-card'><div class='mech-title'>{title}</div><div class='mech-body'>{body}</div></div>",
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class='note-box' style='margin-top:14px;'>
    Setelah lebih dari satu abad diteliti, tinjauan literatur (mis. review di ScienceDirect &amp; ACS Publications)
    secara eksplisit menyatakan mekanisme magnetic/electromagnetic water treatment <b>"masih belum sepenuhnya
    dipahami"</b>, dan beberapa mekanisme di atas diduga <b>bekerja bersamaan</b>, bukan saling eksklusif.
    Simulasi ini memvisualisasikan mekanisme Gaya Lorentz &amp; hidrasi sebagai salah satu hipotesis &mdash;
    bukan fakta yang sudah terbukti secara konklusif.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# KOTAK KEJUJURAN UTAMA
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:20px;'>Catatan Kejujuran Ilmiah</div>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class='honesty-box'>
    <b>Animasi pipa di atas TIDAK berskala fisika asli.</b> Radius girasi Lorentz riil untuk Ca&sup2;&#8314;
    pada kekuatan medan &amp; kecepatan alir yang kamu pilih hanya <b>{fmt_len(r_ca)}</b> &mdash; sekitar
    <b>{ratio_pipe_ca:.1e}&times;</b> lebih kecil dari diameter pipa. "Pemisahan dua aliran ion yang terlihat jelas"
    seperti pada gambar ilustratif/CGI referensi <b>bukan representasi lintasan sesungguhnya</b>, melainkan
    penggambaran konseptual dari sebuah hipotesis &mdash; efek nyata (jika ada) terjadi di skala nanometer,
    di sekitar proses nukleasi molekuler, bukan pemisahan aliran makroskopik yang kasat mata.<br><br>
    Untuk medan AC sesuai spesifikasi asli EMSP ({freq_khz} kHz), ion bahkan belum sempat menyelesaikan
    sebagian kecil putaran girasi sebelum arah medan sudah berbalik &mdash; sehingga mekanisme "pemisahan
    jalur oleh Lorentz" secara khusus lebih relevan untuk perangkat <b>magnet statis (DC)</b> yang lebih umum
    dibahas di literatur, bukan untuk kumparan AC berfrekuensi radio seperti EMSP. Mekanisme hidrasi ion,
    di sisi lain, tidak memerlukan defleksi bersih searah, sehingga secara prinsip tetap mungkin berlaku
    pada kedua jenis medan &mdash; meski derajat efektivitasnya di lapangan tetap memerlukan pembuktian empiris.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# CATATAN MODEL (footer)
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class='note-box' style='margin-top:16px;'>
    &#9888; <b>Catatan Model:</b> Fraksi aragonit yang dipakai untuk mewarnai kristal pada animasi adalah
    parameter ilustratif yang dikalibrasi manual (base 15%, bonus hidrasi +12%, bonus Lorentz-statis hingga
    +55% tergantung kekuatan medan &amp; kecepatan alir) &mdash; BUKAN hasil pengukuran laboratorium. Posisi
    lane, kecepatan defleksi visual, dan ukuran partikel pada animasi diperbesar drastis dari skala fisika
    aslinya demi keterbacaan; nilai kuantitatif yang benar-benar dihitung dari rumus fisika (radius girasi,
    periode AC, dan grafik defleksi nanometer) ditampilkan terpisah di panel angka &amp; grafik Plotly di atas.
    Gunakan simulasi ini untuk membangun intuisi konseptual mengenai hipotesis mekanisme, bukan sebagai bukti
    bahwa mekanisme ini sudah terverifikasi atau efektif di kondisi lapangan sesungguhnya.
    </div>
    """,
    unsafe_allow_html=True,
)
