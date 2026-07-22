"""
Simulasi Mekanisme EMSP v2 — Chamber Vertikal (Fountain/Bottle Style)
========================================================================
Versi ini mengganti visualisasi pipa horizontal (v1) dengan chamber
corong vertikal yang meniru gaya gambar referensi: kation Ca2+ & anion
HCO3- tercampur di sumber bawah, menyembur ke atas melalui chamber yang
menyempit, terpisah menjadi dua berkas warna berbeda saat mendekati &
melewati cincin kumparan EMSP di puncak, lalu menyatu kembali membentuk
kristal -- aragonit (mengambang, terbawa keluar) jika medan aktif,
kalsit (jatuh, mengendap) jika tidak.

Seluruh kejujuran ilmiah dari v1 dipertahankan:
  - Radius girasi Lorentz riil (r = m*v/(q*B)) untuk Ca2+/HCO3- dihitung
    live dan dibandingkan dengan skala chamber -- hasilnya berorde
    nanometer, jauh lebih kecil dari pemisahan visual yang digambarkan.
  - Medan statis (DC) vs medan osilasi/AC (spek asli EMSP ~100-200 kHz)
    dibedakan tegas: AC tidak menghasilkan pemisahan berkas yang bersih
    karena arah medan berbalik jauh lebih cepat daripada ion sempat
    bergirasi.
  - Panel mekanisme dari literatur (Lorentz, hidrasi, klaster air,
    antarmuka CO2) ditampilkan sebagai hipotesis yang bersaing, bukan
    fakta yang sudah terbukti.

Jalankan dengan:
    streamlit run simulasi_emsp_chamber_v2.py
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
st.set_page_config(page_title="Simulasi Mekanisme EMSP: Chamber Vertikal", layout="wide")

BG = "#0a0c12"
CARD_BG = "#151824"
MUTED = "#94a3b8"
CYAN = "#22d3ee"
GREEN = "#22c55e"
YELLOW = "#eab308"
ROSE = "#f43f5e"      # kation Ca2+
BLUE = "#3b82f6"      # anion HCO3-
ORANGE = "#f97316"    # kalsit (kerak, mengendap)
PURPLE = "#a855f7"    # aragonit (tersuspensi, terbawa keluar)

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
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13.5px; }}
    .metric-label {{ color: {MUTED}; font-size: 12.5px; }}
    .metric-value-rose {{ color: {ROSE}; font-weight: 700; }}
    .metric-value-blue {{ color: {BLUE}; font-weight: 700; }}
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
    "<h2 style='text-align:center; color:white;'>Simulasi Mekanisme EMSP: Chamber Vertikal</h2>"
    "<p style='text-align:center; color:#94a3b8; margin-top:-8px;'>"
    "Ion tercampur &rarr; terpisah melewati cincin EMSP &rarr; menyatu kembali jadi aragonit (bukan kalsit)</p>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# KONSTANTA & FUNGSI FISIKA (identik dengan v1, untuk konsistensi)
# ----------------------------------------------------------------------
U = 1.66053906660e-27
E = 1.602176634e-19
M_CA = 40.078 * U
Q_CA = 2 * E
M_HCO3 = 61.0168 * U
Q_HCO3 = 1 * E
COIL_LENGTH_M = 0.15
PIPE_DIAM_M = 0.05


def gyroradius(mass_kg, charge_c, v_ms, b_tesla):
    if b_tesla <= 0:
        return float("inf")
    return mass_kg * v_ms / (charge_c * b_tesla)


def ac_half_period(freq_hz):
    return 1 / (2 * max(freq_hz, 1e-9))


def fmt_len(m):
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
col_viz, col_param = st.columns([1.5, 1])

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

    b_field_mT = st.slider("Kekuatan Medan B (mT)", 1, 500, 50, step=1)
    v_flow = st.slider("Kecepatan Alir/Drift Ion (m/s)", 0.05, 2.0, 0.5, step=0.05)
    freq_khz = st.slider("Frekuensi Medan AC (kHz)", 50, 300, 150, step=10, disabled=not field_ac)
    show_hydration = st.checkbox("Tampilkan efek selubung hidrasi", value=True)

    st.markdown(
        "<div class='note-box'>Animasi diskalakan agar terlihat jelas mata &mdash; BUKAN skala fisika asli. Lihat panel Perhitungan Fisika &amp; Catatan Kejujuran di bawah untuk angka sesungguhnya.</div>",
        unsafe_allow_html=True,
    )

b_field_T = b_field_mT / 1000.0
freq_hz = freq_khz * 1000.0
r_ca = gyroradius(M_CA, Q_CA, v_flow, b_field_T)
r_hco3 = gyroradius(M_HCO3, Q_HCO3, v_flow, b_field_T)
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
            <div class='metric-row'><span class='metric-label'>vs. diameter chamber ({PIPE_DIAM_M*100:.0f} cm)</span>
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

BASE_ARAGONITE = 0.15
HYDRATION_BONUS = 0.12
STATIC_LORENTZ_BONUS = 0.55 * min(b_field_mT / 100.0, 1.0) * min(v_flow / 0.5, 1.5)

if field_off:
    frac_aragonite = BASE_ARAGONITE
elif field_ac:
    frac_aragonite = BASE_ARAGONITE + (HYDRATION_BONUS if show_hydration else 0.0)
else:
    frac_aragonite = BASE_ARAGONITE + STATIC_LORENTZ_BONUS + (HYDRATION_BONUS if show_hydration else 0.0)

frac_aragonite = float(np.clip(frac_aragonite, 0.0, 0.95))
frac_calcite = 1 - frac_aragonite

with col_param:
    st.markdown(
        f"""
        <div class='metric-card border-purple'>
            <div class='metric-label'>Hasil Simulasi</div>
            <div class='metric-row'><span>Fraksi Aragonit (tersuspensi, keluar)</span><span class='metric-value-purple'>{frac_aragonite*100:.0f}%</span></div>
            <div class='metric-row'><span>Fraksi Kalsit (mengendap)</span><span class='metric-value-white' style='color:{ORANGE};'>{frac_calcite*100:.0f}%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("\U0001f504 Reset Animasi", use_container_width=True):
        st.session_state.reset_key = st.session_state.get("reset_key", 0) + 1

# ----------------------------------------------------------------------
# VISUALISASI CHAMBER VERTIKAL — HTML/CANVAS + requestAnimationFrame
# ----------------------------------------------------------------------
_CHAMBER_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  :root { --panel: #151824; --muted: #94a3b8; }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', sans-serif; }
  .wrap { display: flex; flex-direction: column; gap: 10px; align-items: center; }
  canvas { display: block; background: #05060a; border-radius: 12px; max-width: 100%; }
  .legend-row { display: flex; gap: 18px; flex-wrap: wrap; align-items: center; justify-content: center;
      background-color: var(--panel); padding: 12px 16px; border-radius: 10px; width: 100%; }
  .legend-item { display: flex; align-items: center; gap: 7px; font-size: 12px; color: white; white-space: nowrap; }
  .legend-dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
  .badge { padding: 6px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; }
</style>
</head>
<body>
<div class="wrap">
  <canvas id="chamber" width="760" height="620"></canvas>
  <div id="badge" class="badge"></div>
  <div class="legend-row">
    <div class="legend-item"><span class="legend-dot" style="background:#f43f5e;"></span>Kation Ca&sup2;&#8314;</div>
    <div class="legend-item"><span class="legend-dot" style="background:#3b82f6;"></span>Anion HCO&#8323;&#8315;</div>
    <div class="legend-item"><span class="legend-dot" style="background:#22c55e; border-radius:2px;"></span>Cincin Kumparan EMSP</div>
    <div class="legend-item"><span class="legend-dot" style="background:#f97316; border-radius:2px;"></span>Kalsit (mengendap)</div>
    <div class="legend-item"><span class="legend-dot" style="background:#a855f7;"></span>Aragonit (tersuspensi, keluar)</div>
  </div>
</div>

<script>
const CFG = __CFG_JSON__;
const canvas = document.getElementById('chamber');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const cx = W / 2;

// --- Geometri chamber (corong menyempit ke atas, seperti botol) ---
const yBottom = H - 60;   // dasar chamber (sumber ion)
const yRing = 95;         // ketinggian cincin EMSP (puncak)
const yTop = 30;          // batas atas kanvas (keluar chamber)
const halfWBottom = 260;
const halfWRing = 62;

function funnelHalfWidth(y) {
  const t = Math.min(1, Math.max(0, (yBottom - y) / (yBottom - yRing)));
  return halfWBottom + (halfWRing - halfWBottom) * t;
}

// Zona ketinggian (arah gerak: ke ATAS, y mengecil)
const ySeparateStart = yBottom - (yBottom - yRing) * 0.22;  // mulai berpisah
const ySeparateFull  = yBottom - (yBottom - yRing) * 0.62;  // berpisah penuh (dekat coil marker)
const yRecombineEnd  = yRing + (yBottom - yRing) * 0.06;    // selesai menyatu tepat sebelum cincin

const ROSE = '#f43f5e', BLUE = '#3b82f6', ORANGE = '#f97316', ORANGE_STUCK = '#c2410c', PURPLE = '#a855f7';

const riseSpeed = 0.55 + CFG.vFlow * 1.6;

let ions = [];
let crystals = [];
let frame = 0;

function spawnIon() {
  const isCation = Math.random() > 0.5;
  const hw = funnelHalfWidth(yBottom);
  ions.push({
    x: cx + (Math.random() - 0.5) * hw * 0.5,
    y: yBottom - Math.random() * 10,
    isCation,
    phase: Math.random() * Math.PI * 2,
    active: true,
  });
}

function laneTargetX(y, isCation) {
  const hw = funnelHalfWidth(y);
  const offset = hw * 0.42;
  return isCation ? (cx - offset) : (cx + offset);
}

function updateIon(ion) {
  ion.y -= riseSpeed;

  const fieldActive = CFG.fieldStatic || CFG.fieldAc;
  let targetX = cx;

  if (fieldActive && ion.y <= ySeparateStart && ion.y > yRecombineEnd) {
    if (CFG.fieldStatic) {
      // medan statis: lane terpisah bersih (representasi konseptual dari
      // hipotesis Lorentz -- lihat catatan kejujuran fisika di panel Streamlit)
      targetX = laneTargetX(ion.y, ion.isCation);
      ion.x += (targetX - ion.x) * 0.05;
    } else if (CFG.fieldAc) {
      // medan AC: getaran cepat simetris di sekitar posisi tengah,
      // TIDAK ada pemisahan lane bersih (rata-rata net ~ 0)
      ion.phase += 0.85;
      const jitterAmp = funnelHalfWidth(ion.y) * 0.10;
      ion.x = cx + Math.sin(ion.phase) * jitterAmp * (ion.isCation ? 1 : -1) * 0.15
                 + Math.sin(ion.phase * 1.7) * jitterAmp * 0.4;
    }
  } else if (fieldActive && ion.y <= yRecombineEnd) {
    // zona rekombinasi tepat sebelum cincin: lane ditarik kembali ke tengah
    ion.x += (cx - ion.x) * 0.08;
  } else {
    // sebelum berpisah (masih bergabung) / medan OFF: goyangan kecil acak di dekat tengah
    ion.x += (Math.random() - 0.5) * 1.6;
    const hw = funnelHalfWidth(ion.y) * 0.5;
    if (ion.x < cx - hw) ion.x = cx - hw;
    if (ion.x > cx + hw) ion.x = cx + hw;
  }

  // batasi ion tetap di dalam dinding corong
  const hwNow = funnelHalfWidth(ion.y);
  if (ion.x < cx - hwNow + 6) ion.x = cx - hwNow + 6;
  if (ion.x > cx + hwNow - 6) ion.x = cx + hwNow - 6;
}

function tryReact() {
  for (let i = ions.length - 1; i >= 0; i--) {
    const a = ions[i];
    if (!a.active || a.y < yTop) { a.active = false; continue; }
    for (let j = i - 1; j >= 0; j--) {
      const b = ions[j];
      if (!b.active || a.isCation === b.isCation) continue;
      const dist = Math.hypot(a.x - b.x, a.y - b.y);
      if (dist < 10) {
        a.active = false; b.active = false;
        const px = (a.x + b.x) / 2, py = (a.y + b.y) / 2;
        const isKalsit = Math.random() >= CFG.fracAragonite;
        crystals.push({
          x: px, y: py, isKalsit,
          size: isKalsit ? 3 : 2,
          vy: isKalsit ? 0.55 : -riseSpeed * 0.9,
          vx: (Math.random() - 0.5) * (isKalsit ? 0.4 : 0.8),
          stuck: false,
        });
        break;
      }
    }
  }
  ions = ions.filter(p => p.active);
}

function updateCrystal(c) {
  if (c.stuck) return;
  c.x += c.vx; c.y += c.vy;
  if (c.isKalsit) {
    if (c.size < 9) c.size += 0.015;
    // kalsit jatuh & menempel ke dinding corong terdekat saat menyentuhnya
    const hw = funnelHalfWidth(c.y);
    if (c.x <= cx - hw + c.size) { c.x = cx - hw + c.size; c.stuck = true; }
    if (c.x >= cx + hw - c.size) { c.x = cx + hw - c.size; c.stuck = true; }
    if (c.y >= yBottom - 4) { c.y = yBottom - 4; c.stuck = true; }
  } else {
    // aragonit melayang naik & keluar dari chamber
    if (c.y < yTop - 20) c.dead = true;
  }
}

function drawChamber() {
  ctx.clearRect(0, 0, W, H);

  // dinding corong (kiri & kanan), sedikit wireframe tambahan
  ctx.strokeStyle = 'rgba(148,163,184,0.35)'; ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(cx - halfWBottom, yBottom); ctx.lineTo(cx - halfWRing, yRing);
  ctx.moveTo(cx + halfWBottom, yBottom); ctx.lineTo(cx + halfWRing, yRing);
  ctx.stroke();
  // garis dasar
  ctx.beginPath(); ctx.moveTo(cx - halfWBottom, yBottom); ctx.lineTo(cx + halfWBottom, yBottom); ctx.stroke();

  // greebling tipis (dekorasi struktural ringan, meniru referensi)
  ctx.strokeStyle = 'rgba(148,163,184,0.10)'; ctx.lineWidth = 1;
  for (let k = 1; k <= 4; k++) {
    const t = k / 5;
    const yy = yBottom - (yBottom - yRing) * t;
    const hw = funnelHalfWidth(yy);
    ctx.beginPath();
    ctx.moveTo(cx - hw - 14, yy + 6); ctx.lineTo(cx - hw, yy);
    ctx.moveTo(cx + hw + 14, yy + 6); ctx.lineTo(cx + hw, yy);
    ctx.stroke();
  }

  // dua berkas cahaya vertikal (beam), mengikuti perspektif corong
  const beamColor = 'rgba(103,232,249,0.07)';
  ctx.fillStyle = beamColor;
  const steps = 40;
  for (let s = 0; s < steps; s++) {
    const y0 = yBottom - (yBottom - yRing) * (s / steps);
    const y1 = yBottom - (yBottom - yRing) * ((s + 1) / steps);
    const lx0 = laneTargetX(y0, true), lx1 = laneTargetX(y1, true);
    const rx0 = laneTargetX(y0, false), rx1 = laneTargetX(y1, false);
    const bw0 = funnelHalfWidth(y0) * 0.22, bw1 = funnelHalfWidth(y1) * 0.22;
    ctx.beginPath();
    ctx.moveTo(lx0 - bw0, y0); ctx.lineTo(lx0 + bw0, y0); ctx.lineTo(lx1 + bw1, y1); ctx.lineTo(lx1 - bw1, y1);
    ctx.closePath(); ctx.fill();
    ctx.beginPath();
    ctx.moveTo(rx0 - bw0, y0); ctx.lineTo(rx0 + bw0, y0); ctx.lineTo(rx1 + bw1, y1); ctx.lineTo(rx1 - bw1, y1);
    ctx.closePath(); ctx.fill();
  }

  // sumber ion (glow merah muda) di dasar chamber
  const grad = ctx.createRadialGradient(cx, yBottom - 10, 4, cx, yBottom - 10, 90);
  grad.addColorStop(0, 'rgba(244,63,94,0.55)');
  grad.addColorStop(1, 'rgba(244,63,94,0)');
  ctx.fillStyle = grad;
  ctx.beginPath(); ctx.ellipse(cx, yBottom - 10, 90, 26, 0, 0, Math.PI * 2); ctx.fill();

  // dua marker kumparan kecil (kiri & kanan), di ketinggian zona pemisahan
  const markerY = ySeparateFull;
  const markerHw = funnelHalfWidth(markerY);
  const fieldActive = CFG.fieldStatic || CFG.fieldAc;
  [cx - markerHw - 26, cx + markerHw + 26].forEach((mx) => {
    ctx.save();
    ctx.strokeStyle = fieldActive ? '#eab308' : '#4b5563'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.ellipse(mx - 10, markerY, 7, 10, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(mx + 10, markerY, 7, 10, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(mx - 10, markerY); ctx.lineTo(mx + 10, markerY); ctx.stroke();
    ctx.restore();
  });

  // cincin kumparan EMSP di puncak (hijau, wireframe silinder)
  ctx.save();
  const ringGlow = fieldActive ? 'rgba(34,197,94,0.9)' : 'rgba(75,85,99,0.6)';
  ctx.strokeStyle = ringGlow; ctx.lineWidth = 2.4;
  ctx.beginPath(); ctx.ellipse(cx, yRing, halfWRing, 16, 0, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath(); ctx.ellipse(cx, yRing - 22, halfWRing, 16, 0, 0, Math.PI * 2); ctx.stroke();
  // garis vertikal silinder
  for (let a = -1; a <= 1; a++) {
    const xx = cx + a * halfWRing * 0.95;
    ctx.beginPath(); ctx.moveTo(xx, yRing - 22); ctx.lineTo(xx, yRing); ctx.stroke();
  }
  if (fieldActive) {
    const waveAmp = CFG.fieldAc ? 6 : 3;
    const waveSpeed = CFG.fieldAc ? 0.6 : 0.15;
    ctx.strokeStyle = 'rgba(234,179,8,0.8)'; ctx.lineWidth = 1.3;
    ctx.beginPath();
    for (let i = -halfWRing; i <= halfWRing; i += 4) {
      const yy = (yRing - 11) + Math.sin(i * 0.25 - frame * waveSpeed) * waveAmp;
      if (i === -halfWRing) ctx.moveTo(cx + i, yy); else ctx.lineTo(cx + i, yy);
    }
    ctx.stroke();
  }
  ctx.restore();

  // selubung hidrasi opsional
  if (CFG.showHydration && fieldActive) {
    ions.forEach((ion) => {
      if (ion.y < ySeparateStart + 40 && ion.y > yRecombineEnd - 40) {
        ctx.beginPath();
        ctx.arc(ion.x, ion.y, 7 + Math.sin(frame * 0.2 + ion.phase) * 2, 0, Math.PI * 2);
        ctx.strokeStyle = ion.isCation ? 'rgba(244,63,94,0.25)' : 'rgba(59,130,246,0.25)';
        ctx.lineWidth = 1.4;
        ctx.stroke();
      }
    });
  }

  // ion
  ions.forEach((ion) => {
    ctx.beginPath();
    ctx.arc(ion.x, ion.y, 3, 0, Math.PI * 2);
    ctx.fillStyle = ion.isCation ? ROSE : BLUE;
    ctx.globalAlpha = 0.9;
    ctx.fill();
    ctx.globalAlpha = 1;
  });

  // kristal
  crystals.forEach((c) => {
    ctx.save(); ctx.translate(c.x, c.y);
    if (c.isKalsit) {
      ctx.fillStyle = c.stuck ? ORANGE_STUCK : ORANGE;
      ctx.fillRect(-c.size / 2, -c.size / 2, c.size, c.size);
    } else {
      ctx.fillStyle = PURPLE;
      ctx.globalAlpha = Math.max(0, Math.min(1, (c.y - (yTop - 20)) / 40));
      ctx.beginPath(); ctx.ellipse(0, 0, c.size + 1.3, c.size, 0, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 1;
    }
    ctx.restore();
  });
}

function loop() {
  if (Math.random() < 0.55 && ions.length < 150) spawnIon();
  ions.forEach(updateIon);
  tryReact();
  crystals.forEach(updateCrystal);
  crystals = crystals.filter(c => !c.dead && c.y < yBottom + 20);
  if (crystals.length > 500) crystals = crystals.slice(crystals.length - 500);

  drawChamber();
  frame++;
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

const badge = document.getElementById('badge');
if (CFG.fieldStatic) {
  badge.textContent = '\u2713 Medan Statis: berkas kation/anion terpisah lalu menyatu jadi aragonit (representasi konseptual)';
  badge.style.background = 'rgba(34,197,94,0.15)'; badge.style.color = '#4ade80'; badge.style.border = '1px solid #22c55e';
} else if (CFG.fieldAc) {
  badge.textContent = '\u26a0 Medan AC (spek asli EMSP): ion bergetar di tempat, TIDAK ada pemisahan berkas bersih';
  badge.style.background = 'rgba(234,179,8,0.15)'; badge.style.color = '#fbbf24'; badge.style.border = '1px solid #eab308';
} else {
  badge.textContent = '\u2715 Medan OFF: ion bercampur bebas menuju cincin, kalsit dominan mengendap';
  badge.style.background = 'rgba(239,68,68,0.15)'; badge.style.color = '#f87171'; badge.style.border = '1px solid #ef4444';
}
</script>
</body>
</html>
"""


def render_chamber(field_static_flag, field_ac_flag, v_flow_val, frac_arag, show_hyd):
    cfg = dict(
        fieldStatic=bool(field_static_flag),
        fieldAc=bool(field_ac_flag),
        vFlow=round(v_flow_val, 3),
        fracAragonite=round(frac_arag, 4),
        showHydration=bool(show_hyd),
    )
    html = _CHAMBER_HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))
    components.html(html, height=740, scrolling=False)


with col_viz:
    render_chamber(field_static, field_ac, v_flow, frac_aragonite, show_hydration)

# ----------------------------------------------------------------------
# GRAFIK: DEFLEKSI STATIS vs AC (MATEMATIS, TANPA EKSAGERASI)
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:20px;'>Perbandingan Matematis: Defleksi Statis vs AC (Skala Riil)</div>", unsafe_allow_html=True)

t_ns = np.linspace(0, 20, 500)
t_s = t_ns * 1e-9
a_lorentz_ca = (Q_CA * v_flow * b_field_T) / M_CA
static_defl_nm = np.clip(0.5 * a_lorentz_ca * t_s**2 * 1e9, 0, r_ca * 1e9 * 4)
omega_ac = 2 * math.pi * freq_hz
ac_defl_nm = (r_ca * 1e9) * np.sin(omega_ac * t_s)

fig = go.Figure()
fig.add_trace(go.Scatter(x=t_ns, y=static_defl_nm, mode="lines", name="Medan Statis (DC)", line=dict(color=GREEN, width=3)))
fig.add_trace(go.Scatter(x=t_ns, y=ac_defl_nm, mode="lines", name=f"Medan AC ({freq_khz} kHz)", line=dict(color=YELLOW, width=3)))
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
    Grafik ini <b>tidak diperbesar/eksagerasi</b> seperti animasi chamber di atas &mdash; sumbu-y dalam nanometer
    sesungguhnya. Medan statis (hijau) memberi defleksi yang terus terakumulasi searah. Medan AC (kuning) membuat
    posisi ion berosilasi maju-mundur {freq_khz} ribu kali per detik &mdash; rata-rata perpindahan bersihnya
    mendekati nol.
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
        st.markdown(f"<div class='mech-card'><div class='mech-title'>{title}</div><div class='mech-body'>{body}</div></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class='note-box' style='margin-top:14px;'>
    Setelah lebih dari satu abad diteliti, tinjauan literatur secara eksplisit menyatakan mekanisme magnetic/
    electromagnetic water treatment <b>"masih belum sepenuhnya dipahami"</b>, dan beberapa mekanisme di atas
    diduga <b>bekerja bersamaan</b>, bukan saling eksklusif. Simulasi ini memvisualisasikan Gaya Lorentz &amp;
    hidrasi sebagai salah satu hipotesis &mdash; bukan fakta yang sudah terbukti secara konklusif.
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
    <b>Animasi chamber di atas TIDAK berskala fisika asli.</b> Radius girasi Lorentz riil untuk Ca&sup2;&#8314;
    pada parameter yang kamu pilih hanya <b>{fmt_len(r_ca)}</b> &mdash; sekitar <b>{ratio_pipe_ca:.1e}&times;</b>
    lebih kecil dari skala chamber. "Dua berkas ion yang terlihat terpisah jelas" seperti pada gambar
    ilustratif/CGI referensi <b>bukan representasi lintasan sesungguhnya</b>, melainkan penggambaran konseptual
    dari sebuah hipotesis &mdash; efek nyata (jika ada) terjadi di skala nanometer, di sekitar proses nukleasi
    molekuler, bukan pemisahan aliran makroskopik yang kasat mata.<br><br>
    Untuk medan AC sesuai spesifikasi asli EMSP ({freq_khz} kHz), ion bahkan belum sempat menyelesaikan
    sebagian kecil putaran girasi sebelum arah medan sudah berbalik &mdash; sehingga mekanisme "pemisahan
    jalur oleh Lorentz" secara khusus lebih relevan untuk perangkat <b>magnet statis (DC)</b>, bukan untuk
    kumparan AC berfrekuensi radio seperti EMSP. Mekanisme hidrasi ion, di sisi lain, tidak memerlukan defleksi
    bersih searah, sehingga secara prinsip tetap mungkin berlaku pada kedua jenis medan &mdash; meski derajat
    efektivitasnya di lapangan tetap memerlukan pembuktian empiris.
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
    &#9888; <b>Catatan Model:</b> Fraksi aragonit yang mewarnai kristal pada animasi adalah parameter ilustratif
    yang dikalibrasi manual (base 15%, bonus hidrasi +12%, bonus Lorentz-statis hingga +55%) &mdash; BUKAN hasil
    pengukuran laboratorium. Geometri chamber, posisi berkas, kecepatan pemisahan visual, dan ukuran partikel
    diperbesar drastis dari skala fisika aslinya demi keterbacaan; nilai kuantitatif yang benar-benar dihitung
    dari rumus fisika ditampilkan terpisah di panel angka &amp; grafik Plotly di atas. Gunakan simulasi ini untuk
    membangun intuisi konseptual mengenai hipotesis mekanisme, bukan sebagai bukti bahwa mekanisme ini sudah
    terverifikasi atau efektif di kondisi lapangan sesungguhnya.
    </div>
    """,
    unsafe_allow_html=True,
)
