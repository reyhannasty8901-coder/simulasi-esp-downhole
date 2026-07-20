"""
Simulasi Interaktif — Apakah Sinyal EMSP Benar-Benar Mencapai ESP?  (v3)
====================================================================
PERUBAHAN DARI v2:
  - Animasi sekarang BERBEDA SECARA VISUAL sesuai mekanisme masing-masing
    skenario (bukan cuma beda warna strip):
      * Skenario A & B -> mode "wave": gelombang zigzag UNGU di TENGAH
        fluida (satu keluarga warna karena mekanisme fisiknya sama:
        rambatan lewat brine). A: amplitudo relatif konstan dari atas
        ke ESP. B: amplitudo & opasitas mengecil mengikuti kurva
        redaman yang SAMA seperti dihitung di v2 (skin effect) sampai
        nyaris hilang sebelum ESP.
      * Skenario C -> mode "wall": TIDAK ADA gelombang di tengah.
        Diganti dua garis putus-putus BIRU yang menempel di dinding
        tubing/casing (menggambarkan konduksi logam), dengan glow di
        dinding & panah kecil sesekali ke arah fluida.
  - Ion (Ca2+, Ba2+, Sr2+, HCO3-, SO4 2-) divisualisasikan sebagai
    partikel kecil berwarna yang bergetar sesuai kekuatan medan lokal:
      * Mode "wave": ion di SELURUH penampang fluida bergetar mengikuti
        intensitas di kedalaman itu (A: bergetar merata; B: kuat di
        atas, meluruh ke bawah).
      * Mode "wall": HANYA ion dekat dinding yang bergetar; ion di
        tengah tetap tenang mengikuti aliran, berapa pun kedalamannya.
  - Kartu "hipotesis" ditambahkan di bawah animasi untuk tiap skenario,
    meniru gaya infografis referensi, tapi tetap konsisten dengan angka
    fisika yang sudah dihitung (tidak asal optimis).

Jalankan dengan:
    streamlit run simulasi_teori_sinyal_emsp_v3.py
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
st.set_page_config(page_title="Simulasi: Sinyal EMSP vs ESP (v3)", layout="wide")

CYAN = "#00e5ff"
BLUE = "#3b82f6"
ORANGE = "#ff9100"
PURPLE = "#a855f7"
VIOLET = "#c084fc"  # ungu muda -> dipakai skenario B (satu keluarga warna dg A)
GREEN = "#10b981"
RED = "#ef4444"
GRAY = "#5b6470"
BG = "#12141c"
CARD_BG = "#1e212b"
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
    .border-purple {{ border-left: 4px solid {PURPLE}; }}
    .border-violet {{ border-left: 4px solid {VIOLET}; }}
    .border-blue {{ border-left: 4px solid {BLUE}; }}
    .border-green {{ border-left: 4px solid {GREEN}; }}
    .border-red {{ border-left: 4px solid {RED}; }}
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }}
    .metric-value-cyan {{ color: {CYAN}; font-weight: 700; }}
    .metric-value-purple {{ color: {PURPLE}; font-weight: 700; }}
    .metric-value-violet {{ color: {VIOLET}; font-weight: 700; }}
    .metric-value-blue {{ color: {BLUE}; font-weight: 700; }}
    .metric-value-green {{ color: {GREEN}; font-weight: 700; }}
    .metric-value-white {{ color: white; font-weight: 700; }}
    .metric-label {{ color: {MUTED}; font-size: 13px; }}
    .section-title {{ color: white; font-size: 16px; font-weight: 700; margin: 2px 0 10px 0; }}
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 12px 16px; border-radius: 8px; color: {MUTED}; font-size: 12px; line-height: 1.55;
    }}
    .warn-box {{
        background-color: rgba(255,145,0,0.08); border-left: 4px solid {ORANGE};
        padding: 12px 16px; border-radius: 8px; color: {ORANGE}; font-size: 12.5px; line-height: 1.55;
        margin-bottom: 14px;
    }}
    .legend-item {{ display:flex; align-items:center; gap:7px; margin-bottom:5px; color:white; font-size:12.5px;}}
    .legend-dot {{ width:12px; height:12px; border-radius:50%; display:inline-block; flex-shrink:0; }}
    .legend-sq {{ width:12px; height:12px; display:inline-block; flex-shrink:0; }}
    .hip-card {{
        background-color: {CARD_BG}; border-radius: 10px; padding: 14px 16px;
        color: white; font-size: 12.5px; line-height: 1.6; height: 100%;
    }}
    .hip-title {{ font-size: 13.5px; font-weight: 800; margin-bottom: 8px; }}
    .hip-tag {{ display:inline-block; padding:2px 9px; border-radius:12px; font-size:11px; font-weight:700; margin-bottom:8px; }}
    .verdict-box {{
        padding: 16px 20px; border-radius: 10px; font-size: 15px; line-height: 1.5; font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h2 style='text-align:center; color:white;'>Apakah Sinyal EMSP Benar-Benar Mencapai ESP?</h2>"
    "<p style='text-align:center; color:#a0aabf; margin-top:-8px;'>"
    "v3 &mdash; Animasi khas per mekanisme (gelombang di tengah vs konduksi di dinding) + visualisasi ion</p>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# FISIKA (identik dengan v2 — lihat catatan model di bagian bawah)
# ----------------------------------------------------------------------
MU0 = 4 * math.pi * 1e-7
SIGMA_STEEL = 6.0e6
MU_R_STEEL = 300.0
D_MIN = 0.05
STEPS = 160


def skin_depth_m(freq_hz, sigma_s_per_m, mu_r=1.0):
    omega = 2 * math.pi * max(freq_hz, 1e-9)
    sigma = max(sigma_s_per_m, 1e-15)
    return math.sqrt(2 / (omega * MU0 * mu_r * sigma))


def wall_transmission_factor(thickness_mm, freq_hz):
    if thickness_mm <= 0:
        return 1.0, None
    delta = skin_depth_m(freq_hz, SIGMA_STEEL, MU_R_STEEL)
    thickness_m = thickness_mm / 1000.0
    exponent = -thickness_m / delta
    factor = 0.0 if exponent < -700 else math.exp(exponent)
    return factor, delta * 1000.0


def depth_at_t(t, well_depth_m):
    return D_MIN * (well_depth_m / D_MIN) ** t


def required_sigma_for_reach(freq_hz, well_depth_m, mu_r=1.0):
    omega = 2 * math.pi * max(freq_hz, 1e-9)
    return 2 / (omega * MU0 * mu_r * max(well_depth_m, 1e-9) ** 2)


def required_atten_for_reach(well_depth_m, threshold):
    well_depth_km = max(well_depth_m, 1.0) / 1000.0
    if threshold <= 0:
        return float("inf")
    return -20.0 * math.log10(threshold) / well_depth_km


def fmt_frac_pct(frac):
    pct = frac * 100
    if pct <= 0:
        return "0% (benar-benar nol)"
    if pct >= 0.01:
        return f"{pct:.4f}%"
    return f"{pct:.3e}%"


def build_curve(intensity_fn, well_depth_m, steps=STEPS):
    curve = []
    for i in range(steps + 1):
        t = i / steps
        d = depth_at_t(t, well_depth_m)
        curve.append({"t": t, "inten": max(0.0, min(1.0, intensity_fn(d)))})
    final_inten = intensity_fn(well_depth_m)
    return curve, max(0.0, min(1.0, final_inten))


def scenario_c_intensity_fn(depth_m, atten_db_per_km, bonded, fallback_fn):
    if not bonded:
        return fallback_fn(depth_m)
    depth_km = depth_m / 1000.0
    db_loss = atten_db_per_km * depth_km
    return 10 ** (-db_loss / 20.0)


# ----------------------------------------------------------------------
# LAYOUT — PARAMETER
# ----------------------------------------------------------------------
col_viz, col_param = st.columns([1.9, 1])

with col_param:
    st.markdown("<div class='section-title'>Parameter Umum</div>", unsafe_allow_html=True)
    freq_khz = st.slider("Frekuensi Kerja Alat (kHz)", 1, 500, 150, step=1)
    sigma_brine = st.slider("Konduktivitas Brine (S/m)", 0.05, 10.0, 4.0, step=0.05)
    well_depth = st.slider("Kedalaman ESP (m)", 200, 4000, 2000, step=50)

    material = st.radio("Material Pipa/Tubing (Skenario A & B)",
                         ["Non-Metal (PVC/HDPE)", "Metal (Baja/Casing)"], index=0)
    is_metal = material.startswith("Metal")
    wall_thickness = 8.0
    if is_metal:
        wall_thickness = st.slider("Ketebalan Dinding Pipa (mm)", 2.0, 20.0, 8.0, step=0.5)

    threshold_pct = st.slider("Ambang Efektivitas Sinyal (%)", 0.1, 10.0, 1.0, step=0.1)

    st.markdown("<div class='section-title' style='margin-top:18px;'>Skenario C: Konduksi Galvanis</div>", unsafe_allow_html=True)
    bonded = st.toggle("Alat electrically bonded ke tubing/casing?", value=True)
    atten_db_km = 5.0
    if bonded:
        atten_db_km = st.slider("Redaman Sepanjang Tubing (dB/km)", 0.1, 100.0, 5.0, step=0.1)

    st.markdown(
        "<div class='note-box'>Ubah slider untuk eksplorasi: pada kombinasi parameter seperti apa masing-masing skenario mulai realistis?</div>",
        unsafe_allow_html=True,
    )

freq_hz = freq_khz * 1000.0
skin_brine = skin_depth_m(freq_hz, sigma_brine)
if is_metal:
    wall_factor, skin_steel_mm = wall_transmission_factor(wall_thickness, freq_hz)
else:
    wall_factor, skin_steel_mm = 1.0, None
threshold = threshold_pct / 100.0


def fn_A(d):
    return 1.0


def fn_B(d):
    exponent = -d / max(skin_brine, 1e-15)
    frac = 0.0 if exponent < -700 else math.exp(exponent)
    return wall_factor * frac


def fn_C(d):
    return scenario_c_intensity_fn(d, atten_db_km, bonded, fn_B)


curve_A, final_A = build_curve(fn_A, well_depth)
curve_B, final_B = build_curve(fn_B, well_depth)
curve_C, final_C = build_curve(fn_C, well_depth)

protected_A = final_A >= threshold
protected_B = final_B >= threshold
protected_C = final_C >= threshold

sigma_required = required_sigma_for_reach(freq_hz, well_depth)
atten_required = required_atten_for_reach(well_depth, threshold)

# ---------------- STAT CARDS ----------------
with col_param:
    st.markdown(
        f"""
        <div class='metric-card border-cyan'>
            <div class='metric-row'><span class='metric-label'>Skin Depth di Brine</span>
                <span class='metric-value-cyan'>{skin_brine:.3f} m</span></div>
            {"<div class='metric-row'><span class='metric-label'>Skin Depth di Baja</span><span class='metric-value-white'>" + f"{skin_steel_mm:.4f} mm</span></div>" if skin_steel_mm else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class='metric-card border-red'>
            <div class='metric-label'>B: Konduktivitas Brine Maks agar Realistis</div>
            <div style='font-size:19px; font-weight:800; color:{RED};'>{sigma_required:.3e} S/m</div>
            <div class='metric-label'>Slidermu: <b style='color:white;'>{sigma_brine:.2f} S/m</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class='metric-card border-blue'>
            <div class='metric-label'>C: Redaman Maks agar Realistis</div>
            <div style='font-size:19px; font-weight:800; color:{BLUE};'>{atten_required:.2f} dB/km</div>
            <div class='metric-label'>Slidermu: <b style='color:white;'>{atten_db_km:.1f} dB/km</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# LEGENDA
# ----------------------------------------------------------------------
ION_COLORS = {
    "Ca2+": "#f97316", "Ba2+": "#14b8a6", "Sr2+": "#eab308",
    "HCO3-": "#38bdf8", "SO4 2-": "#f472b6",
}
with col_viz:
    ion_legend_html = "".join(
        f"<div class='legend-item'><span class='legend-dot' style='background:{c};'></span>{name}</div>"
        for name, c in ION_COLORS.items()
    )
    st.markdown(
        f"""
        <div style='display:flex; gap:20px; flex-wrap:wrap; margin-bottom:10px; padding:10px 14px; background:{CARD_BG}; border-radius:8px;'>
            <div class='legend-item'><span class='legend-dot' style='background:{PURPLE};'></span>Gelombang EM lewat brine (A &amp; B)</div>
            <div class='legend-item'><span class='legend-dot' style='background:{BLUE};'></span>Konduksi lewat logam tubing/casing (C)</div>
            {ion_legend_html}
            <div class='legend-item'><span class='legend-dot' style='background:{PURPLE};'></span>Aragonit (lunak, melayang, aman)</div>
            <div class='legend-item'><span class='legend-sq' style='background:{RED};'></span>Kalsit (keras, menumpuk)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# VISUALISASI — HTML/CANVAS
# ----------------------------------------------------------------------
_WELL_ANIM_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', sans-serif; }
  .wrap { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
  canvas { display: block; background: #0d0f16; border-radius: 10px; }
  .col { display: flex; flex-direction: column; align-items: center; gap: 8px; width: 100%; max-width: 330px; }
  .well-label { font-size: 13.5px; font-weight: 800; text-align: center; }
  .well-sub { color: #a0aabf; font-size: 10.8px; text-align: center; margin-top: -4px; }
  .badge { padding: 5px 12px; border-radius: 20px; font-size: 11.5px; font-weight: 700; margin-top: 4px; text-align:center; }
</style>
</head>
<body>
<div class="wrap" id="wrap"></div>
<script>
const CFG = __CFG_JSON__;
const ION_COLORS = __ION_COLORS_JSON__;
const ION_KEYS = Object.keys(ION_COLORS);
const wrap = document.getElementById('wrap');

CFG.scenarios.forEach((sc, idx) => {
  const canvasId = 'well' + idx, badgeId = 'badge' + idx;
  const col = document.createElement('div');
  col.className = 'col';
  col.innerHTML = `
    <div class="well-label" style="color:${sc.color};">${sc.title}</div>
    <div class="well-sub">${sc.subtitle}</div>
    <canvas id="${canvasId}" width="320" height="520"></canvas>
    <div id="${badgeId}" class="badge"></div>
  `;
  wrap.appendChild(col);
  buildWell(canvasId, badgeId, sc);
});

const D_MIN = 0.05;
function depthFrac(depthM, wellDepth) {
  const d = Math.max(depthM, D_MIN);
  return Math.log10(d / D_MIN) / Math.log10(Math.max(wellDepth, D_MIN * 2) / D_MIN);
}
function intensityFromCurve(curve, t) {
  const idx = Math.min(curve.length - 1, Math.max(0, Math.round(t * (curve.length - 1))));
  return curve[idx].inten;
}

function buildWell(canvasId, badgeId, sc) {
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const topPad = 55, botPad = 70;
  const y0 = topPad, y1 = H - botPad;
  const cx = W / 2, tubeW = 66;
  const wellDepth = CFG.wellDepth;
  const isWave = sc.mode === 'wave';
  const protectedWell = sc.finalIntensity >= CFG.threshold;

  // --- generate ion & crystal populations sekali di awal ---
  const ions = [];
  const N_IONS = 46;
  for (let i = 0; i < N_IONS; i++) {
    const t = Math.random();
    const nearWall = !isWave && Math.random() < 0.55;
    let x;
    if (nearWall) {
      x = Math.random() < 0.5 ? (cx - tubeW / 2 + 6 + Math.random() * 7) : (cx + tubeW / 2 - 6 - Math.random() * 7);
    } else {
      x = cx + (Math.random() - 0.5) * (tubeW - 16);
    }
    ions.push({
      species: ION_KEYS[Math.floor(Math.random() * ION_KEYS.length)],
      t, baseX: x, baseY: y0 + t * (y1 - y0),
      phase: Math.random() * Math.PI * 2, nearWall,
      driftPhase: Math.random() * Math.PI * 2,
    });
  }

  let frame = 0;
  const pulses = [];
  const crystals = [];
  const arrows = [];
  let buildup = 0;

  function spawnPulse() {
    if (isWave) {
      pulses.push({ t: 0, speed: 0.005 + Math.random() * 0.003 });
    }
  }
  function spawnCrystal() {
    const angle = Math.random() * Math.PI * 2;
    const r0 = 50 + Math.random() * 9;
    crystals.push({
      x: cx + Math.cos(angle) * r0, y: y1 + 18 + Math.sin(angle) * r0 * 0.4,
      angle, settled: false, life: 0,
      kind: protectedWell ? 'safe' : (sc.id === 'B' ? 'neutral' : 'kalsit'),
    });
  }
  function spawnArrow() {
    if (!isWave) {
      const t = Math.random();
      const inten = intensityFromCurve(sc.curve, t);
      if (inten > 0.05) {
        const y = y0 + t * (y1 - y0);
        const fromLeft = Math.random() < 0.5;
        arrows.push({ y, fromLeft, life: 0, inten });
      }
    }
  }

  function drawTicks() {
    ctx.fillStyle = '#5b6470'; ctx.font = '9.5px Segoe UI'; ctx.textAlign = 'left';
    [0.02, 1, 10, 100].forEach((dM) => {
      if (dM > wellDepth) return;
      const t = depthFrac(dM, wellDepth);
      const yy = y0 + t * (y1 - y0);
      ctx.fillText(dM + ' m', cx + tubeW / 2 + 8, yy + 3);
      ctx.strokeStyle = 'rgba(255,255,255,0.05)';
      ctx.beginPath(); ctx.moveTo(cx - tubeW / 2, yy); ctx.lineTo(cx + tubeW / 2, yy); ctx.stroke();
    });
    ctx.fillText(wellDepth + ' m (ESP)', cx + tubeW / 2 + 8, y1 + 3);
  }

  function drawTubeOutline(glowAlpha) {
    if (glowAlpha > 0.02) {
      ctx.save();
      ctx.shadowColor = sc.color; ctx.shadowBlur = 10 * glowAlpha;
      ctx.strokeStyle = sc.color; ctx.lineWidth = 2.2;
      ctx.globalAlpha = Math.min(1, 0.35 + glowAlpha * 0.65);
      ctx.beginPath();
      ctx.moveTo(cx - tubeW / 2, y0); ctx.lineTo(cx - tubeW / 2, y1);
      ctx.moveTo(cx + tubeW / 2, y0); ctx.lineTo(cx + tubeW / 2, y1);
      ctx.stroke();
      ctx.restore();
    }
    ctx.strokeStyle = '#3a4150'; ctx.lineWidth = 2; ctx.globalAlpha = 1;
    ctx.beginPath();
    ctx.moveTo(cx - tubeW / 2, y0); ctx.lineTo(cx - tubeW / 2, y1);
    ctx.moveTo(cx + tubeW / 2, y0); ctx.lineTo(cx + tubeW / 2, y1);
    ctx.stroke();
  }

  function drawWaveCenter() {
    // gelombang zigzag ungu di tengah, dengan glow supaya lebih hidup (mirip referensi)
    ctx.save();
    ctx.shadowColor = sc.color;
    ctx.shadowBlur = 9;
    ctx.lineWidth = 3.4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    let started = false;
    for (let y = y0; y <= y1; y += 3) {
      const t = (y - y0) / (y1 - y0);
      const inten = intensityFromCurve(sc.curve, t);
      if (inten < 0.006) { started = false; continue; }
      const amp = (tubeW * 0.30) * Math.pow(inten, 0.35);
      const x = cx + Math.sin(y * 0.09 - frame * 0.10) * amp;
      if (!started) { ctx.moveTo(x, y); started = true; } else { ctx.lineTo(x, y); }
    }
    ctx.strokeStyle = sc.color;
    ctx.globalAlpha = 0.95;
    ctx.stroke();
    ctx.restore();
    ctx.globalAlpha = 1;

    // gelembung putih kecil mengiringi gelombang turun (mirip trail bubbles referensi)
    pulses.forEach((p) => {
      const inten = intensityFromCurve(sc.curve, p.t);
      if (inten > 0.01) {
        const y = y0 + p.t * (y1 - y0);
        const amp = (tubeW * 0.30) * Math.pow(inten, 0.35);
        const x = cx + Math.sin(y * 0.09 - frame * 0.10) * amp + (Math.sin(p.t * 40 + frame * 0.05) * 4);
        ctx.beginPath(); ctx.arc(x, y, 1.7, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${Math.min(0.85, inten * 0.9 + 0.08)})`;
        ctx.fill();
      }
    });
  }

  function drawWallConduction() {
    const wallAmp = 6.5;
    const baseL = cx - tubeW / 2 + 9;
    const baseR = cx + tubeW / 2 - 9;

    ctx.save();
    ctx.shadowColor = sc.color;
    ctx.shadowBlur = 7;
    ctx.lineWidth = 2.6;
    ctx.lineCap = 'round';
    ctx.setLineDash([7, 6]);
    ctx.lineDashOffset = -frame * 0.7;

    [baseL, baseR].forEach((baseX) => {
      ctx.beginPath();
      let started = false;
      for (let y = y0; y <= y1; y += 3) {
        const t = (y - y0) / (y1 - y0);
        const inten = intensityFromCurve(sc.curve, t);
        if (inten < 0.006) { started = false; continue; }
        const amp = wallAmp * Math.pow(inten, 0.3);
        const x = baseX + Math.sin(y * 0.14 - frame * 0.16) * amp;
        if (!started) { ctx.moveTo(x, y); started = true; } else { ctx.lineTo(x, y); }
      }
      ctx.strokeStyle = sc.color;
      ctx.globalAlpha = 0.9;
      ctx.stroke();
    });
    ctx.restore();
    ctx.setLineDash([]); ctx.globalAlpha = 1;

    // panah kecil dari dinding ke fluida
    arrows.forEach((a) => {
      const alpha = Math.max(0, 1 - a.life / 40) * a.inten;
      if (alpha <= 0.02) return;
      const xStart = a.fromLeft ? cx - tubeW / 2 + 6 : cx + tubeW / 2 - 6;
      const xEnd = a.fromLeft ? xStart + 14 : xStart - 14;
      ctx.strokeStyle = `rgba(59,130,246,${alpha})`;
      ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.moveTo(xStart, a.y); ctx.lineTo(xEnd, a.y); ctx.stroke();
      ctx.beginPath();
      const dir = a.fromLeft ? 1 : -1;
      ctx.moveTo(xEnd, a.y);
      ctx.lineTo(xEnd - dir * 4, a.y - 3);
      ctx.lineTo(xEnd - dir * 4, a.y + 3);
      ctx.closePath();
      ctx.fillStyle = `rgba(59,130,246,${alpha})`;
      ctx.fill();
    });
  }

  function drawIons() {
    ions.forEach((ion) => {
      const inten = intensityFromCurve(sc.curve, ion.t);
      let excitement;
      if (isWave) {
        excitement = inten;
      } else {
        const distFromWall = Math.min(Math.abs(ion.baseX - (cx - tubeW / 2)), Math.abs(ion.baseX - (cx + tubeW / 2)));
        const proximity = Math.max(0, 1 - distFromWall / 16);
        excitement = inten * proximity;
      }
      const drift = Math.sin(frame * 0.01 + ion.driftPhase) * 2;
      const jitterAmp = 0.6 + excitement * 6.5;
      const jx = ion.baseX + Math.sin(frame * (0.12 + excitement * 0.35) + ion.phase) * jitterAmp;
      const jy = ion.baseY + drift + Math.cos(frame * (0.10 + excitement * 0.3) + ion.phase) * (jitterAmp * 0.5);
      ctx.beginPath();
      ctx.arc(jx, jy, excitement > 0.15 ? 2.6 : 2.0, 0, Math.PI * 2);
      ctx.fillStyle = ION_COLORS[ion.species];
      ctx.globalAlpha = 0.55 + excitement * 0.45;
      ctx.fill();
      ctx.globalAlpha = 1;
    });
  }

  function drawESP() {
    ctx.fillStyle = '#2a2f3d';
    ctx.fillRect(cx - 24, y1 + 6, 48, 26);
    ctx.strokeStyle = '#5b6470'; ctx.lineWidth = 1.2;
    ctx.strokeRect(cx - 24, y1 + 6, 48, 26);
    ctx.fillStyle = '#9aa5b3'; ctx.font = '8.5px Segoe UI'; ctx.textAlign = 'center';
    ctx.fillText('ESP', cx, y1 + 22);
  }

  function drawCrystals() {
    crystals.forEach((c) => {
      ctx.save(); ctx.translate(c.x, c.y);
      if (c.kind === 'safe') {
        ctx.fillStyle = 'rgba(168,85,247,0.85)';
        ctx.beginPath(); ctx.ellipse(0, 0, 5, 3.2, 0, 0, Math.PI * 2); ctx.fill();
      } else if (c.kind === 'neutral') {
        ctx.fillStyle = c.settled ? 'rgba(148,163,184,0.55)' : 'rgba(203,213,225,0.7)';
        ctx.beginPath(); ctx.arc(0, 0, 3.4, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.fillStyle = c.settled ? '#b91c1c' : '#ef4444';
        ctx.fillRect(-4, -4, 8, 8);
      }
      ctx.restore();
    });
  }

  function drawEmspDevice() {
    ctx.fillStyle = `${sc.color}30`;
    ctx.fillRect(cx - tubeW / 2 - 12, y0 - 34, tubeW + 24, 30);
    if (isWave) {
      ctx.strokeStyle = sc.color; ctx.lineWidth = 1.3;
      ctx.beginPath();
      for (let i = 0; i <= tubeW + 16; i += 4) {
        const yy = y0 - 19 + Math.sin(i * 0.22 - frame * 0.18) * 8;
        if (i === 0) ctx.moveTo(cx - tubeW / 2 - 8 + i, yy); else ctx.lineTo(cx - tubeW / 2 - 8 + i, yy);
      }
      ctx.stroke();
    } else {
      ctx.strokeStyle = sc.color; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(cx - tubeW / 2 - 6, y0 - 19); ctx.lineTo(cx - 4, y0 - 19); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx + 4, y0 - 19); ctx.lineTo(cx + tubeW / 2 + 6, y0 - 19); ctx.stroke();
      ctx.beginPath(); ctx.arc(cx, y0 - 19, 4, 0, Math.PI * 2); ctx.strokeStyle = sc.color; ctx.stroke();
    }
    ctx.fillStyle = sc.color; ctx.font = '9.5px Segoe UI'; ctx.textAlign = 'center';
    ctx.fillText('EMSP', cx, y0 - 40);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    drawTicks();
    const glowAlpha = isWave ? 0 : intensityFromCurve(sc.curve, 0.05);
    drawTubeOutline(glowAlpha);
    drawEmspDevice();
    if (isWave) drawWaveCenter(); else drawWallConduction();
    drawIons();
    drawESP();
    drawCrystals();
  }

  function update() {
    if (isWave && frame % 9 === 0) spawnPulse();
    pulses.forEach((p) => { p.t += p.speed; });
    for (let i = pulses.length - 1; i >= 0; i--) if (pulses[i].t >= 1) pulses.splice(i, 1);

    if (!isWave && Math.random() < 0.12) spawnArrow();
    arrows.forEach((a) => { a.life += 1; });
    for (let i = arrows.length - 1; i >= 0; i--) if (arrows[i].life > 40) arrows.splice(i, 1);

    const maxCrystals = protectedWell ? 24 : 55;
    if (Math.random() < (protectedWell ? 0.5 : 0.35) && crystals.length < maxCrystals) spawnCrystal();
    crystals.forEach((c) => {
      c.life += 1;
      if (c.kind !== 'safe') {
        if (!c.settled) {
          const targetR = 28 + Math.min(buildup, 24);
          c.x = cx + Math.cos(c.angle) * targetR;
          c.y = y1 + 18 + Math.sin(c.angle) * targetR * 0.42;
          if (c.life > (c.kind === 'neutral' ? 45 : 20)) c.settled = true;
        }
      } else {
        c.x += Math.sin(c.life * 0.05 + c.angle) * 0.6;
        c.y += Math.cos(c.life * 0.04 + c.angle) * 0.4;
      }
    });
    if (!protectedWell) buildup = Math.min(24, buildup + 0.01);
    for (let i = crystals.length - 1; i >= 0; i--) {
      if (crystals[i].kind === 'safe' && crystals[i].life > 260) crystals.splice(i, 1);
    }
    frame++;
  }

  function loop() { update(); draw(); requestAnimationFrame(loop); }
  requestAnimationFrame(loop);

  const badge = document.getElementById(badgeId);
  if (sc.id === 'B') {
    badge.textContent = protectedWell ? '\u2713 Efek langsung terdeteksi' : '? Efek langsung diperkirakan sangat kecil';
    badge.style.background = protectedWell ? 'rgba(16,185,129,0.15)' : 'rgba(255,145,0,0.12)';
    badge.style.color = protectedWell ? '#34d399' : '#ffb454';
    badge.style.border = protectedWell ? '1px solid #10b981' : '1px solid #ff9100';
  } else if (sc.id === 'C') {
    badge.textContent = protectedWell
      ? '\u2713 Terlindungi (JIKA bonded)'
      : '\u2715 Tidak terlindungi';
    badge.style.background = protectedWell ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)';
    badge.style.color = protectedWell ? '#34d399' : '#f87171';
    badge.style.border = protectedWell ? '1px solid #10b981' : '1px solid #ef4444';
  } else if (protectedWell) {
    badge.textContent = '\u2713 ESP TERLINDUNGI';
    badge.style.background = 'rgba(16,185,129,0.15)'; badge.style.color = '#34d399';
    badge.style.border = '1px solid #10b981';
  } else {
    badge.textContent = '\u2715 ESP TIDAK TERLINDUNGI';
    badge.style.background = 'rgba(239,68,68,0.15)'; badge.style.color = '#f87171';
    badge.style.border = '1px solid #ef4444';
  }
}
</script>
</body>
</html>
"""


def render_well_comparison(scenarios, well_depth_m, threshold_frac, ion_colors):
    cfg = dict(wellDepth=round(well_depth_m, 2), threshold=round(threshold_frac, 6), scenarios=scenarios)
    html = (
        _WELL_ANIM_HTML_TEMPLATE
        .replace("__CFG_JSON__", json.dumps(cfg))
        .replace("__ION_COLORS_JSON__", json.dumps(ion_colors))
    )
    components.html(html, height=650, scrolling=False)


# Pemetaan warna per skenario (disamakan dengan legenda di atas):
#   A & B -> keluarga UNGU (mekanisme sama: gelombang lewat brine)
#   C     -> BIRU (mekanisme berbeda: konduksi lewat logam tubing/casing)
scenarios_payload = [
    {"id": "A", "title": "SKENARIO A", "subtitle": "Hipotesis vendor (belum terverifikasi)",
     "mode": "wave", "color": PURPLE, "curve": curve_A, "finalIntensity": final_A},
    {"id": "B", "title": "SKENARIO B", "subtitle": "Teori elektromagnetika (atenuasi oleh brine)",
     "mode": "wave", "color": VIOLET, "curve": curve_B, "finalIntensity": final_B},
    {"id": "C", "title": "SKENARIO C", "subtitle": f"Konduksi logam {'(bonded)' if bonded else '(TIDAK bonded)'}",
     "mode": "wall", "color": BLUE, "curve": curve_C, "finalIntensity": final_C},
]

with col_viz:
    render_well_comparison(scenarios_payload, well_depth, threshold, ION_COLORS)

    st.markdown(
        f"""
        <div style='display:flex; gap:12px; margin-top:8px;'>
            <div class='metric-card border-purple' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP — A</div>
                <div style='font-size:18px; font-weight:800; color:{PURPLE};'>{fmt_frac_pct(final_A)}</div>
            </div>
            <div class='metric-card border-violet' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP — B</div>
                <div style='font-size:18px; font-weight:800; color:{VIOLET};'>{fmt_frac_pct(final_B)}</div>
            </div>
            <div class='metric-card border-blue' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP — C</div>
                <div style='font-size:18px; font-weight:800; color:{BLUE};'>{fmt_frac_pct(final_C)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# KARTU HIPOTESIS (gaya infografis, tetap jujur ke angka)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:20px;'>Ringkasan Tiap Hipotesis</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class='hip-card' style='border-top:4px solid {PURPLE};'>
            <span class='hip-tag' style='background:rgba(168,85,247,0.15); color:{PURPLE};'>Belum terverifikasi</span>
            <div class='hip-title' style='color:{PURPLE};'>A — Hipotesis Vendor (Propagasi lewat Brine)</div>
            &bull; Gelombang ungu berada di <b>tengah fluida</b> (bukan di dinding tubing) &mdash; energi diasumsikan merambat lewat brine.<br>
            &bull; Amplitudo gelombang <b>tetap relatif konstan</b> dari permukaan hingga ESP, tidak mengecil seperti Skenario B.<br>
            &bull; Gelombang bergerak kontinu dari atas ke bawah sampai mencapai ESP.<br>
            &bull; Ion (Ca&sup2;&#8314;, Ba&sup2;&#8314;, Sr&sup2;&#8314;, HCO&#8323;&#8315;, SO&#8324;&sup2;&#8315;) di sepanjang jalur gelombang bergetar/berubah arah &mdash; ilustrasi medan memengaruhi proses nukleasi.<br>
            &bull; Di dekat ESP, kristal scale digambarkan berubah jadi partikel halus (aragonit) yang tetap melayang, sehingga tidak menempel di impeller.<br>
            &bull; <b>Cek angka:</b> perlu konduktivitas brine &le; {sigma_required:.2e} S/m agar realistis &mdash; jutaan kali lebih rendah dari brine manapun. Klaim ini <b>tidak konsisten</b> dengan fisika skin effect.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class='hip-card' style='border-top:4px solid {VIOLET};'>
            <span class='hip-tag' style='background:rgba(192,132,252,0.15); color:{VIOLET};'>Sesuai teori EM standar</span>
            <div class='hip-title' style='color:{VIOLET};'>B — Atenuasi oleh Brine</div>
            &bull; Gelombang ungu juga di <b>tengah fluida</b> &mdash; mekanisme sama seperti A, tapi energi diserap (attenuation) oleh brine yang bersifat konduktif.<br>
            &bull; Tepat di bawah EMSP amplitudo masih besar, lalu makin <b>tipis, transparan, dan akhirnya menghilang</b> sebelum mencapai ESP.<br>
            &bull; Ion hanya bergetar di <b>bagian atas tubing</b> (masih dalam jangkauan medan); makin dalam, gerakan ion makin berkurang lalu kembali normal mengikuti aliran.<br>
            &bull; Di sekitar ESP <b>tidak ditampilkan interaksi langsung</b> antara gelombang dan partikel scale, karena medan diperkirakan sudah melemah signifikan &mdash; partikel scale tetap tampak normal (bukan bukti pasti ESP tidak terlindungi, hanya efek langsung diperkirakan sangat kecil).<br>
            &bull; <b>Cek angka:</b> sinyal di ESP saat ini {fmt_frac_pct(final_B)}. Ini penjelasan yang paling konsisten dengan hukum fisika standar, tapi <b>gagal menjelaskan sendiri</b> kenaikan run life yang drastis.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class='hip-card' style='border-top:4px solid {BLUE};'>
            <span class='hip-tag' style='background:rgba(59,130,246,0.15); color:{BLUE};'>Bergantung desain alat</span>
            <div class='hip-title' style='color:{BLUE};'>C — Konduksi Logam (Electrical Bonding)</div>
            &bull; <b>Tidak ada gelombang</b> di tengah fluida &mdash; pada hipotesis ini energi tidak diasumsikan merambat lewat brine.<br>
            &bull; Sebagai gantinya, dua garis biru putus-putus menempel di dinding kiri &amp; kanan tubing/casing, bergerak kontinu dari permukaan menuju ESP &mdash; menggambarkan jalur konduksi lewat logam. Dinding tubing sedikit <b>glow</b> mengikuti pergerakan garis.<br>
            &bull; Sesekali muncul panah kecil dari dinding menuju fluida: medan di sekitar logam dapat berinteraksi dengan ion yang berada <b>dekat dinding</b>.<br>
            &bull; Ion dekat dinding sedikit bergetar/berubah arah; ion di <b>tengah fluida tetap tenang</b> mengikuti aliran &mdash; efek terlokalisasi di dinding, bukan memenuhi seluruh penampang seperti Skenario A.<br>
            &bull; Garis biru tetap mencapai ESP, sehingga ion/kristal di sekitar impeller masih bisa divisualisasikan berubah orientasi &mdash; namun ini sepenuhnya <b>hipotesis yang bergantung</b> pada apakah alat electrically bonded ke tubing/casing (kontak listrik langsung), bukan cuma clamp non-invasif.<br>
            &bull; <b>Syarat mutlak & status saat ini:</b> {'BONDED (diasumsikan)' if bonded else 'TIDAK bonded → mekanisme ini runtuh jadi sama dengan B'}. Redaman perlu &le; {atten_required:.2f} dB/km agar realistis; slidermu {atten_db_km:.1f} dB/km.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# GRAFIK KUANTITATIF
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:22px;'>Kurva Redaman Sinyal terhadap Kedalaman</div>", unsafe_allow_html=True)

depths = np.logspace(math.log10(D_MIN), math.log10(well_depth), 400)
curve_A_full = np.array([fn_A(d) * 100 for d in depths])
curve_B_full = np.clip(np.array([fn_B(d) * 100 for d in depths]), 1e-30, None)
curve_C_full = np.clip(np.array([fn_C(d) * 100 for d in depths]), 1e-30, None)

fig = go.Figure()
fig.add_trace(go.Scatter(x=depths, y=curve_A_full, mode="lines", name="A: Klaim vendor",
                          line=dict(color=PURPLE, width=2.5, dash="dash")))
fig.add_trace(go.Scatter(x=depths, y=curve_B_full, mode="lines", name="B: Atenuasi brine",
                          line=dict(color=VIOLET, width=3)))
fig.add_trace(go.Scatter(x=depths, y=curve_C_full, mode="lines", name="C: Konduksi logam",
                          line=dict(color=BLUE, width=3)))
fig.add_hline(y=threshold_pct, line_dash="dot", line_color=ORANGE,
              annotation_text=f"Ambang efektivitas ({threshold_pct:.1f}%)", annotation_font_color=ORANGE)
fig.add_vline(x=well_depth, line_dash="dot", line_color=MUTED,
              annotation_text="Kedalaman ESP", annotation_font_color=MUTED)
fig.update_layout(
    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    height=430, margin=dict(t=30, b=10, l=10, r=10),
    xaxis=dict(title="Kedalaman (m)", type="log"),
    yaxis=dict(title="Kekuatan Sinyal (% dari awal)", type="log"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="white")),
)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# VERDICT
# ----------------------------------------------------------------------
if bonded and protected_C:
    verdict_color = GREEN
    verdict_text = (
        f"Dengan parameter saat ini, <b>Skenario C (bonded)</b> menghasilkan sinyal {fmt_frac_pct(final_C)} di "
        f"kedalaman ESP &mdash; di atas ambang. Ini kandidat penjelasan paling konsisten untuk kenaikan run life. "
        f"<b>Tapi validitasnya bergantung total pada satu fakta yang harus dicek langsung ke vendor/spesifikasi "
        f"alat:</b> apakah device benar-benar electrically bonded ke tubing/casing, bukan cuma clamp non-invasif."
    )
elif not bonded:
    verdict_color = RED
    verdict_text = (
        f"Alat diasumsikan TIDAK bonded. Dalam kondisi ini Skenario C otomatis identik dengan Skenario B: sinyal "
        f"cuma {fmt_frac_pct(final_B)} di ESP. Kalau EMSP-mu memang jenis clamp non-invasif, ketiga jalur sinyal "
        f"yang dimodelkan di sini TIDAK ada yang sampai ke ESP. Kenaikan run life kemungkinan besar berasal dari "
        f"efek tidak langsung (kerak berkurang di permukaan/flowline, backpressure turun) atau confounder lapangan."
    )
else:
    verdict_color = RED
    verdict_text = (
        f"Redaman Skenario C ({atten_db_km:.1f} dB/km) masih terlalu besar untuk kedalaman {well_depth} m. "
        f"Turunkan di bawah {atten_required:.2f} dB/km untuk melihat kapan jalur ini realistis."
    )

st.markdown(
    f"<div class='verdict-box' style='background-color:{CARD_BG}; border-left:5px solid {verdict_color}; color:{verdict_color};'>{verdict_text}</div>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# CATATAN MODEL
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class='note-box' style='margin-top:16px;'>
    &#9888; <b>Catatan Model:</b><br>
    &bull; Fisika A &amp; B: gelombang EM meradiasi lewat dinding pipa lalu merambat lewat brine, dihitung pakai
    rumus skin depth standar. Visualisasi "gelombang di tengah" &amp; getaran ion memakai nilai intensitas
    yang SAMA dengan kurva kuantitatif di bawah &mdash; jadi animasi dan angka selalu konsisten satu sama lain.<br>
    &bull; Fisika C: mekanisme konduksi aksial lewat logam, disederhanakan sebagai redaman linear (dB/km) &mdash;
    pendekatan ILUSTRATIF untuk membangun intuisi, bukan angka final. Nilai dB/km aktual tergantung grade baja,
    kontinuitas sambungan, isolasi packer, dan frekuensi kerja alat.<br>
    &bull; "Ambang efektivitas sinyal" &amp; posisi/jenis ion adalah penyederhanaan untuk keperluan ilustrasi,
    bukan simulasi elektrokimia yang presisi.<br>
    &bull; Gunakan simulasi ini untuk membangun intuisi &amp; membedakan mekanisme secara jujur ke publik/tim,
    bukan sebagai pengganti pengukuran lapangan atau uji laboratorium aktual.
    </div>
    """,
    unsafe_allow_html=True,
)
