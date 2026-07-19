"""
Simulasi Interaktif — Apakah Sinyal EMSP Benar-Benar Mencapai ESP?
====================================================================
Membandingkan dua teori yang bersaing untuk menjelaskan kenaikan run
life ESP meski EMSP dipasang di permukaan:

  TEORI 1 — "Brine sebagai Waveguide"
    Asumsi vendor/hipotesis: brine salinitas tinggi menghantarkan
    gelombang EM ke bawah nyaris tanpa redaman, sehingga sinyal
    sampai ke ESP dengan kekuatan penuh.

  TEORI 2 — "Realita Fisika (Skin Effect)"
    Dihitung langsung dari rumus skin depth elektromagnetik standar:
        delta = sqrt( 2 / (omega * mu0 * mu_r * sigma) )
    Semua parameter (frekuensi alat, konduktivitas brine, kedalaman
    ESP, material & ketebalan pipa) bisa diubah lewat slider —
    sehingga pengguna bisa mengeksplorasi sendiri kombinasi parameter
    seperti apa yang dibutuhkan agar Teori 1 realistis secara fisika.

Visualisasi memakai pola yang sama dengan simulasi kristalisasi
sebelumnya: HTML5 Canvas + requestAnimationFrame (mulus, tanpa
st.rerun per frame), plus grafik Plotly untuk kurva redaman
kuantitatif.

Jalankan dengan:
    streamlit run simulasi_teori_sinyal_emsp.py
"""

import json
import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------------------------------------------------
# KONFIGURASI HALAMAN & TEMA (konsisten dengan simulasi sebelumnya)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Simulasi: Sinyal EMSP vs ESP", layout="wide")

CYAN = "#00e5ff"
ORANGE = "#ff9100"
BLUE = "#3b82f6"
GREEN = "#10b981"
PURPLE = "#a855f7"
RED = "#ef4444"
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
    .border-purple {{ border-left: 4px solid {PURPLE}; }}
    .border-red {{ border-left: 4px solid {RED}; }}
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }}
    .metric-value-cyan {{ color: {CYAN}; font-weight: 700; }}
    .metric-value-orange {{ color: {ORANGE}; font-weight: 700; }}
    .metric-value-purple {{ color: {PURPLE}; font-weight: 700; }}
    .metric-value-red {{ color: {RED}; font-weight: 700; }}
    .metric-value-white {{ color: white; font-weight: 700; }}
    .metric-label {{ color: {MUTED}; font-size: 13px; }}
    .section-title {{ color: white; font-size: 16px; font-weight: 700; margin: 2px 0 10px 0; }}
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 12px 16px; border-radius: 8px; color: {MUTED}; font-size: 12px; line-height: 1.55;
    }}
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
    "Simulasi interaktif: Teori 1 (\"Brine sebagai Waveguide\") vs Teori 2 (Realita Fisika &mdash; Skin Effect)</p>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# FUNGSI FISIKA — Skin Effect Elektromagnetik
# ----------------------------------------------------------------------
MU0 = 4 * math.pi * 1e-7  # permeabilitas ruang hampa (H/m)

# Nilai tipikal baja karbon (casing/tubing) — pendekatan umum, bisa
# berbeda tergantung grade baja aktual.
SIGMA_STEEL = 6.0e6      # konduktivitas (S/m)
MU_R_STEEL = 300.0        # permeabilitas relatif (feromagnetik, pendekatan)


def skin_depth_m(freq_hz, sigma_s_per_m, mu_r=1.0):
    """Skin depth (meter): jarak di mana amplitudo gelombang EM meluruh
    menjadi 1/e (~37%) dari nilai awal di dalam medium konduktif."""
    omega = 2 * math.pi * max(freq_hz, 1e-9)
    sigma = max(sigma_s_per_m, 1e-15)
    return math.sqrt(2 / (omega * MU0 * mu_r * sigma))


def wall_transmission_factor(thickness_mm, freq_hz):
    """Faktor transmisi (0-1) medan EM menembus dinding pipa baja
    setebal thickness_mm, berdasarkan skin depth di baja pada
    frekuensi freq_hz. Mengembalikan (faktor, skin_depth_baja_mm)."""
    if thickness_mm <= 0:
        return 1.0, None
    delta = skin_depth_m(freq_hz, SIGMA_STEEL, MU_R_STEEL)
    thickness_m = thickness_mm / 1000.0
    exponent = -thickness_m / delta
    factor = 0.0 if exponent < -700 else math.exp(exponent)
    return factor, delta * 1000.0  # delta dikembalikan dalam mm


def signal_fraction_at_depth(depth_m, skin_brine_m, wall_factor=1.0):
    """Fraksi amplitudo sinyal (0-1) yang tersisa di kedalaman depth_m,
    setelah melewati dinding pipa (wall_factor) dan brine (skin_brine_m)."""
    exponent = -depth_m / max(skin_brine_m, 1e-15)
    frac = 0.0 if exponent < -700 else math.exp(exponent)
    return wall_factor * frac


def required_sigma_for_reach(freq_hz, well_depth_m, mu_r=1.0):
    """Konduktivitas brine maksimum (S/m) agar skin depth >= kedalaman
    ESP pada frekuensi freq_hz -- yaitu syarat minimum supaya Teori 1
    ('sinyal sampai ke ESP') mendekati realistis secara fisika."""
    omega = 2 * math.pi * max(freq_hz, 1e-9)
    return 2 / (omega * MU0 * mu_r * max(well_depth_m, 1e-9) ** 2)


def fmt_frac_pct(frac):
    """Format fraksi sinyal jadi persen yang mudah dibaca, termasuk
    notasi ilmiah untuk angka yang sangat kecil."""
    pct = frac * 100
    if pct == 0:
        return "0% (benar-benar nol)"
    if pct >= 0.01:
        return f"{pct:.4f}%"
    return f"{pct:.3e}%"


# ----------------------------------------------------------------------
# LAYOUT: VISUALISASI (kiri) + PARAMETER (kanan)
# ----------------------------------------------------------------------
col_viz, col_param = st.columns([1.65, 1])

# ---------------- PANEL PARAMETER ----------------
with col_param:
    st.markdown("<div class='section-title'>Parameter Simulasi</div>", unsafe_allow_html=True)

    freq_khz = st.slider("Frekuensi Kerja Alat (kHz)", 1, 500, 150, step=1,
                          help="Spesifikasi alat EMSP komersial umumnya di kisaran 100-200 kHz.")
    sigma_brine = st.slider("Konduktivitas Brine (S/m)", 0.05, 10.0, 4.0, step=0.05,
                             help="Air tawar murni ~0.0005-0.05 S/m. Air laut/brine salinitas tinggi ~3-6 S/m.")
    well_depth = st.slider("Kedalaman ESP (m)", 200, 4000, 2000, step=50)

    material = st.radio("Material Pipa/Tubing", ["Non-Metal (PVC/HDPE)", "Metal (Baja/Casing)"], index=1)
    is_metal = material.startswith("Metal")
    wall_thickness = 8.0
    if is_metal:
        wall_thickness = st.slider("Ketebalan Dinding Pipa (mm)", 2.0, 20.0, 8.0, step=0.5)

    threshold_pct = st.slider("Ambang Efektivitas Sinyal (%)", 0.1, 10.0, 1.0, step=0.1,
                               help="Asumsi ilustratif: sinyal minimal yang dianggap masih mampu memengaruhi nukleasi kristal di ESP. Bukan angka tervalidasi — untuk eksplorasi saja.")

    st.markdown("<div class='note-box'>Ubah slider di atas untuk mengeksplorasi sendiri: pada kombinasi parameter seperti apa Teori 1 (\"sinyal sampai ke ESP\") mulai masuk akal secara fisika?</div>", unsafe_allow_html=True)

# --- hitung semua fisika ---
freq_hz = freq_khz * 1000.0
skin_brine = skin_depth_m(freq_hz, sigma_brine)

if is_metal:
    wall_factor, skin_steel_mm = wall_transmission_factor(wall_thickness, freq_hz)
else:
    wall_factor, skin_steel_mm = 1.0, None

signal_teori1 = 1.0  # ASUMSI vendor: redaman diabaikan
signal_teori2 = signal_fraction_at_depth(well_depth, skin_brine, wall_factor)

threshold = threshold_pct / 100.0
protected_teori1 = signal_teori1 >= threshold
protected_teori2 = signal_teori2 >= threshold

sigma_required = required_sigma_for_reach(freq_hz, well_depth)

# ---------------- STAT CARDS ----------------
with col_param:
    st.markdown(
        f"""
        <div class='metric-card border-cyan'>
            <div class='metric-row'><span class='metric-label'>Skin Depth di Brine</span>
                <span class='metric-value-cyan'>{skin_brine:.3f} m</span></div>
            {"<div class='metric-row'><span class='metric-label'>Skin Depth di Baja</span><span class='metric-value-orange'>" + f"{skin_steel_mm:.4f} mm</span></div>" if skin_steel_mm else ""}
            {"<div class='metric-row'><span class='metric-label'>Faktor Transmisi Dinding Pipa</span><span class='metric-value-white'>" + f"{wall_factor:.2e}</span></div>" if is_metal else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='metric-card border-red'>
            <div class='metric-label'>Konduktivitas Brine Maksimum agar Teori 1 Realistis</div>
            <div style='font-size:22px; font-weight:800; color:{RED}; margin:4px 0;'>{sigma_required:.3e} S/m</div>
            <div class='metric-label'>Slider kamu saat ini: <b style='color:white;'>{sigma_brine:.2f} S/m</b>
            ({'jauh di atas' if sigma_brine > sigma_required*10 else ('di atas' if sigma_brine > sigma_required else 'di bawah')} batas ini)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# VISUALISASI SUMUR KEMBAR — HTML/CANVAS + requestAnimationFrame
# ----------------------------------------------------------------------
_WELL_ANIM_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  :root {
    --bg: #12141c; --panel: #1e212b; --muted: #a0aabf;
    --cyan: #00e5ff; --purple: #a855f7; --red: #ef4444; --orange: #ff9100;
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', sans-serif; }
  .wrap { display: flex; gap: 18px; justify-content: center; }
  canvas { display: block; background: #0d0f16; border-radius: 10px; }
  .col { display: flex; flex-direction: column; align-items: center; gap: 8px; width: 100%; }
  .well-label { color: white; font-size: 14px; font-weight: 700; text-align: center; }
  .well-sub { color: var(--muted); font-size: 11.5px; text-align: center; margin-top: -4px; }
  .badge { padding: 5px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 700; margin-top: 4px; }
</style>
</head>
<body>
<div class="wrap">
  <div class="col">
    <div class="well-label">TEORI 1 &mdash; Klaim Vendor</div>
    <div class="well-sub">Asumsi: redaman diabaikan</div>
    <canvas id="well1" width="420" height="560"></canvas>
    <div id="badge1" class="badge"></div>
  </div>
  <div class="col">
    <div class="well-label">TEORI 2 &mdash; Realita Fisika</div>
    <div class="well-sub">Dihitung dari rumus skin effect</div>
    <canvas id="well2" width="420" height="560"></canvas>
    <div id="badge2" class="badge"></div>
  </div>
</div>

<script>
const CFG = __CFG_JSON__;
const MU0 = 4 * Math.PI * 1e-7;

function skinDepth(freqHz, sigma, muR) {
  const omega = 2 * Math.PI * Math.max(freqHz, 1e-9);
  return Math.sqrt(2 / (omega * MU0 * muR * Math.max(sigma, 1e-15)));
}
const SKIN_BRINE = skinDepth(CFG.freqHz, CFG.sigma, 1.0);

function intensityAt(depthM, assumption) {
  if (assumption) return 1.0; // Teori 1: asumsi tanpa redaman
  const exponent = -depthM / SKIN_BRINE;
  const frac = exponent < -700 ? 0 : Math.exp(exponent);
  return CFG.wallFactor * frac;
}

const D_MIN = 0.05; // meter, offset dekat permukaan (hindari log(0))
function depthFrac(depthM) {
  const d = Math.max(depthM, D_MIN);
  return Math.log10(d / D_MIN) / Math.log10(Math.max(CFG.wellDepth, D_MIN * 2) / D_MIN);
}

function buildWell(canvasId, assumption) {
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const topPad = 55, botPad = 70;
  const y0 = topPad, y1 = H - botPad;
  const cx = W / 2, tubeW = 70;

  // pra-hitung strip warna sepanjang kedalaman (statis, dihitung sekali)
  const steps = 260;
  const strips = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const depthM = D_MIN * Math.pow(CFG.wellDepth / D_MIN, t);
    const inten = intensityAt(depthM, assumption);
    strips.push({ y: y0 + t * (y1 - y0), inten });
  }
  const finalIntensity = intensityAt(CFG.wellDepth, assumption);
  const protectedWell = finalIntensity >= CFG.threshold;

  let frame = 0;
  const pulses = [];
  const crystals = [];
  let buildup = 0;

  function spawnPulse() {
    pulses.push({ t: 0, speed: 0.006 + Math.random() * 0.004, x: cx + (Math.random() - 0.5) * (tubeW * 0.5) });
  }

  function spawnCrystal() {
    const angle = Math.random() * Math.PI * 2;
    const r0 = 55 + Math.random() * 10;
    crystals.push({
      x: cx + Math.cos(angle) * r0, y: y1 + 18 + Math.sin(angle) * r0 * 0.4,
      angle, settled: false, life: 0, isKalsit: !protectedWell,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    // label kedalaman
    ctx.fillStyle = '#5b6470';
    ctx.font = '10px Segoe UI';
    ctx.textAlign = 'left';
    [0.02, 1, 10, 100].forEach((dM) => {
      if (dM > CFG.wellDepth) return;
      const t = depthFrac(dM);
      const yy = y0 + t * (y1 - y0);
      ctx.fillText((dM < 1 ? dM + ' m' : dM + ' m'), cx + tubeW / 2 + 10, yy + 3);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.beginPath(); ctx.moveTo(cx - tubeW / 2, yy); ctx.lineTo(cx + tubeW / 2, yy); ctx.stroke();
    });
    ctx.fillText(CFG.wellDepth + ' m (ESP)', cx + tubeW / 2 + 10, y1 + 3);

    // dinding sumur (outline)
    ctx.strokeStyle = '#3a4150'; ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx - tubeW / 2, y0); ctx.lineTo(cx - tubeW / 2, y1);
    ctx.moveTo(cx + tubeW / 2, y0); ctx.lineTo(cx + tubeW / 2, y1);
    ctx.stroke();

    // strip intensitas sinyal
    const stripH = (y1 - y0) / steps + 1.2;
    strips.forEach((s) => {
      const alpha = Math.max(0, Math.min(1, s.inten));
      ctx.fillStyle = `rgba(0,229,255,${0.06 + alpha * 0.9})`;
      ctx.fillRect(cx - tubeW / 2 + 2, s.y, tubeW - 4, stripH);
    });

    // ikon EMSP di wellhead (kumparan + gelombang animasi)
    ctx.fillStyle = 'rgba(168,85,247,0.18)';
    ctx.fillRect(cx - tubeW / 2 - 14, y0 - 34, tubeW + 28, 30);
    ctx.strokeStyle = '#a855f7'; ctx.lineWidth = 1.4;
    ctx.beginPath();
    for (let i = 0; i <= tubeW + 20; i += 4) {
      const yy = y0 - 19 + Math.sin(i * 0.22 - frame * 0.18) * 9;
      if (i === 0) ctx.moveTo(cx - tubeW / 2 - 10 + i, yy); else ctx.lineTo(cx - tubeW / 2 - 10 + i, yy);
    }
    ctx.stroke();
    ctx.fillStyle = '#c084fc'; ctx.font = '10px Segoe UI'; ctx.textAlign = 'center';
    ctx.fillText('EMSP', cx, y0 - 40);

    // pulsa sinyal bergerak turun
    pulses.forEach((p) => {
      const depthM = D_MIN * Math.pow(CFG.wellDepth / D_MIN, p.t);
      const inten = intensityAt(depthM, assumption);
      const yy = y0 + p.t * (y1 - y0);
      if (inten > 0.003) {
        ctx.beginPath();
        ctx.arc(p.x, yy, 3.2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${Math.min(1, inten * 1.3)})`;
        ctx.fill();
      }
    });

    // pompa ESP
    ctx.fillStyle = '#2a2f3d';
    ctx.fillRect(cx - 26, y1 + 6, 52, 26);
    ctx.strokeStyle = '#5b6470'; ctx.lineWidth = 1.2;
    ctx.strokeRect(cx - 26, y1 + 6, 52, 26);
    ctx.fillStyle = '#9aa5b3'; ctx.font = '9px Segoe UI'; ctx.textAlign = 'center';
    ctx.fillText('ESP', cx, y1 + 22);

    // kristal di sekitar ESP
    crystals.forEach((c) => {
      ctx.save(); ctx.translate(c.x, c.y);
      if (c.isKalsit) {
        ctx.fillStyle = c.settled ? '#b91c1c' : '#ef4444';
        ctx.fillRect(-4, -4, 8, 8);
      } else {
        ctx.fillStyle = 'rgba(168,85,247,0.85)';
        ctx.beginPath(); ctx.ellipse(0, 0, 5, 3.4, 0, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
    });
  }

  function update() {
    if (Math.random() < 0.55) spawnPulse();
    pulses.forEach((p) => { p.t += p.speed; });
    for (let i = pulses.length - 1; i >= 0; i--) if (pulses[i].t >= 1) pulses.splice(i, 1);

    if (Math.random() < (protectedWell ? 0.5 : 0.35) && crystals.length < (protectedWell ? 26 : 60)) spawnCrystal();
    crystals.forEach((c) => {
      c.life += 1;
      if (c.isKalsit) {
        if (!c.settled) {
          const targetR = 30 + Math.min(buildup, 26);
          c.x = cx + Math.cos(c.angle) * targetR;
          c.y = y1 + 18 + Math.sin(c.angle) * targetR * 0.42;
          if (c.life > 20) c.settled = true;
        }
      } else {
        c.x += Math.sin(c.life * 0.05 + c.angle) * 0.6;
        c.y += Math.cos(c.life * 0.04 + c.angle) * 0.4;
      }
    });
    if (!protectedWell) buildup = Math.min(26, buildup + 0.01);
    for (let i = crystals.length - 1; i >= 0; i--) {
      if (!crystals[i].isKalsit && crystals[i].life > 260) crystals.splice(i, 1);
    }

    frame++;
  }

  function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  const badge = document.getElementById(canvasId === 'well1' ? 'badge1' : 'badge2');
  if (protectedWell) {
    badge.textContent = '\u2713 ESP TERLINDUNGI (aragonit tersuspensi)';
    badge.style.background = 'rgba(16,185,129,0.15)'; badge.style.color = '#34d399';
    badge.style.border = '1px solid #10b981';
  } else {
    badge.textContent = '\u2715 ESP TIDAK TERLINDUNGI (kalsit menumpuk)';
    badge.style.background = 'rgba(239,68,68,0.15)'; badge.style.color = '#f87171';
    badge.style.border = '1px solid #ef4444';
  }
}

buildWell('well1', true);
buildWell('well2', false);
</script>
</body>
</html>
"""


def render_well_comparison(freq_hz, sigma, well_depth_m, wall_factor, threshold):
    cfg = dict(
        freqHz=round(freq_hz, 2),
        sigma=round(sigma, 5),
        wellDepth=round(well_depth_m, 2),
        wallFactor=round(wall_factor, 8),
        threshold=round(threshold, 6),
    )
    html = _WELL_ANIM_HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))
    components.html(html, height=700, scrolling=False)


with col_viz:
    render_well_comparison(freq_hz, sigma_brine, well_depth, wall_factor, threshold)

    st.markdown(
        f"""
        <div style='display:flex; gap:14px; margin-top:8px;'>
            <div class='metric-card border-cyan' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP &mdash; Teori 1</div>
                <div style='font-size:24px; font-weight:800; color:{CYAN};'>{fmt_frac_pct(signal_teori1)}</div>
            </div>
            <div class='metric-card border-purple' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP &mdash; Teori 2</div>
                <div style='font-size:24px; font-weight:800; color:{PURPLE};'>{fmt_frac_pct(signal_teori2)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# GRAFIK KUANTITATIF: KEKUATAN SINYAL vs KEDALAMAN
# ----------------------------------------------------------------------
st.markdown("<div class='section-title' style='margin-top:22px;'>Kurva Redaman Sinyal terhadap Kedalaman</div>", unsafe_allow_html=True)

depths = np.logspace(math.log10(0.05), math.log10(well_depth), 400)
teori1_curve = np.ones_like(depths) * 100.0
teori2_curve = np.array([signal_fraction_at_depth(d, skin_brine, wall_factor) * 100 for d in depths])
teori2_curve = np.clip(teori2_curve, 1e-30, None)

fig = go.Figure()
fig.add_trace(go.Scatter(x=depths, y=teori1_curve, mode="lines", name="Teori 1 (asumsi vendor)",
                          line=dict(color=CYAN, width=3, dash="dash")))
fig.add_trace(go.Scatter(x=depths, y=teori2_curve, mode="lines", name="Teori 2 (dihitung, skin effect)",
                          line=dict(color=PURPLE, width=3)))
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
# VERDICT DINAMIS
# ----------------------------------------------------------------------
if protected_teori2:
    verdict_color = GREEN
    verdict_text = (
        f"Dengan parameter saat ini, sinyal Teori 2 di kedalaman ESP masih {fmt_frac_pct(signal_teori2)} "
        f"&mdash; di atas ambang efektivitas ({threshold_pct:.1f}%). Pada kombinasi parameter ini, Teori 1 dan Teori 2 "
        f"sama-sama plausible. Coba naikkan frekuensi atau konduktivitas brine untuk melihat kapan ini berubah."
    )
else:
    verdict_color = RED
    verdict_text = (
        f"Dengan parameter saat ini, sinyal Teori 2 di kedalaman ESP hanya {fmt_frac_pct(signal_teori2)} "
        f"&mdash; jauh di bawah ambang efektivitas ({threshold_pct:.1f}%). Artinya secara fisika, brine JUSTRU MEREDAM "
        f"sinyal dalam radius sangat pendek dari titik pemasangan, bukan menghantarkannya ke ESP. "
        f"Agar Teori 1 realistis, konduktivitas brine harus &le; {sigma_required:.2e} S/m "
        f"&mdash; jutaan kali lebih rendah dari brine salinitas tinggi manapun."
    )

st.markdown(
    f"<div class='verdict-box' style='background-color:{CARD_BG}; border-left:5px solid {verdict_color}; color:{verdict_color};'>{verdict_text}</div>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# CATATAN MODEL (footer)
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class='note-box' style='margin-top:16px;'>
    &#9888; <b>Catatan Model:</b> Simulasi ini menghitung skin depth memakai rumus elektromagnetik standar
    (delta = &radic;(2 / (&omega;&middot;&mu;&#8320;&middot;&mu;<sub>r</sub>&middot;&sigma;))) dengan asumsi gelombang bidang merambat dalam medium
    homogen &mdash; pendekatan ini tidak memodelkan efek galvanis (kontak listrik langsung ke tubing/casing),
    geometri sumur yang kompleks, atau interaksi elektromagnetik dengan formasi di sekitar casing. Nilai
    konduktivitas &amp; permeabilitas baja bersifat tipikal/ilustratif, bukan spesifikasi material aktual.
    "Ambang efektivitas sinyal" adalah asumsi eksplorasi, bukan angka yang tervalidasi secara empiris.
    Gunakan simulasi ini untuk membangun intuisi mengenai skala redaman, bukan sebagai pengganti pengukuran
    lapangan atau uji laboratorium aktual.
    </div>
    """,
    unsafe_allow_html=True,
)
