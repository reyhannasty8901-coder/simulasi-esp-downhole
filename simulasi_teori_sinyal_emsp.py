"""
Simulasi Interaktif — Apakah Sinyal EMSP Benar-Benar Mencapai ESP?  (v2)
====================================================================
PERBAIKAN UTAMA dari versi sebelumnya:

Versi lama membandingkan "Teori 1 vs Teori 2" tapi keduanya sebenarnya
menguji MEKANISME YANG SAMA (rambat lewat brine sebagai medium), cuma
beda asumsi redaman. Itu bikin bingung karena di diskusi sebelumnya
"Teori 2" merujuk ke mekanisme yang SAMA SEKALI BERBEDA: konduksi
galvanis lewat logam tubing/casing (bukan rambat lewat fluida).

Versi ini memisahkan dengan jelas TIGA skenario yang mekanismenya
benar-benar berbeda:

  SKENARIO A — "Klaim Vendor (Tanpa Redaman)"
      Asumsi ideal vendor: sinyal sampai ke ESP 100% utuh.
      (Referensi pembanding saja — sengaja tidak realistis.)

  SKENARIO B — "Radiasi Lewat Fluida (Dihitung, Skin Effect)"
      Mekanisme: alat clamp non-invasif di luar pipa -> sinyal harus
      menembus dinding pipa (radial) lalu merambat turun lewat brine
      (aksial). Dihitung pakai rumus skin depth EM standar.

  SKENARIO C — "Konduksi Galvanis Lewat Tubing"
      Mekanisme BERBEDA TOTAL: kalau alat electrically bonded
      (kontak listrik langsung, bukan cuma clamp induktif) ke
      tubing/casing, sinyal merambat AKSIAL di sepanjang logam
      seperti kabel panjang. Redamannya bukan skin-depth radiasi ke
      medium sekitar, tapi rugi resistif per satuan panjang (model
      disederhanakan sebagai dB/km, mirip pendekatan pada EM-MWD /
      casing telemetry). Kalau alat TIDAK di-bonding, skenario ini
      identik dengan Skenario B (harus radiasi lewat fluida juga).

Jalankan dengan:
    streamlit run simulasi_teori_sinyal_emsp_v2.py
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
st.set_page_config(page_title="Simulasi: Sinyal EMSP vs ESP (v2)", layout="wide")

CYAN = "#00e5ff"
ORANGE = "#ff9100"
PURPLE = "#a855f7"
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
    .border-green {{ border-left: 4px solid {GREEN}; }}
    .border-red {{ border-left: 4px solid {RED}; }}
    .metric-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }}
    .metric-value-cyan {{ color: {CYAN}; font-weight: 700; }}
    .metric-value-purple {{ color: {PURPLE}; font-weight: 700; }}
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
    .legend-item {{ display:flex; align-items:center; gap:8px; margin-bottom:6px; color:white; font-size:13px;}}
    .legend-dot {{ width:14px; height:14px; border-radius:50%; display:inline-block; flex-shrink:0; }}
    .legend-sq {{ width:14px; height:14px; display:inline-block; flex-shrink:0; }}
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
    "v2 &mdash; Tiga mekanisme yang benar-benar berbeda, bukan cuma beda asumsi redaman</p>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='warn-box'>
    &#9888; <b>Kenapa versi ini beda dari sebelumnya:</b> Simulasi lama membandingkan dua ASUMSI REDAMAN untuk
    mekanisme yang SAMA (rambat lewat fluida). Simulasi ini memisahkan dengan jelas: Skenario A &amp; B menguji
    mekanisme <i>radiasi lewat fluida</i> (dan terbukti gagal secara fisika di kedalaman berapa pun yang wajar),
    sedangkan Skenario C menguji mekanisme yang <i>sama sekali berbeda</i>: <i>konduksi galvanis lewat logam tubing</i>
    &mdash; inilah kandidat penjelasan yang lebih konsisten dengan kenaikan run life ESP di lapangan.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# FISIKA — Skenario A & B: radiasi lewat fluida (skin effect)
# ----------------------------------------------------------------------
MU0 = 4 * math.pi * 1e-7
SIGMA_STEEL = 6.0e6
MU_R_STEEL = 300.0
D_MIN = 0.05  # meter, offset dekat permukaan untuk hindari log(0)
STEPS = 140


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


def fmt_frac_pct(frac):
    pct = frac * 100
    if pct <= 0:
        return "0% (benar-benar nol)"
    if pct >= 0.01:
        return f"{pct:.4f}%"
    return f"{pct:.3e}%"


def build_curve(intensity_fn, well_depth_m, steps=STEPS):
    """Hasilkan list {t, inten} untuk digambar, plus intensitas final di ESP."""
    curve = []
    for i in range(steps + 1):
        t = i / steps
        d = depth_at_t(t, well_depth_m)
        curve.append({"t": t, "inten": max(0.0, min(1.0, intensity_fn(d)))})
    final_inten = intensity_fn(well_depth_m)
    return curve, max(0.0, min(1.0, final_inten))


# ----------------------------------------------------------------------
# FISIKA — Skenario C: konduksi galvanis lewat tubing
# ----------------------------------------------------------------------
def scenario_c_intensity_fn(depth_m, atten_db_per_km, bonded, fallback_fn):
    """Kalau bonded: redaman linear dB/km sepanjang logam (model
    disederhanakan, mirip pendekatan casing-telemetry). Kalau tidak
    bonded: harus lewat jalur radiasi ke fluida juga (fallback ke
    fungsi Skenario B)."""
    if not bonded:
        return fallback_fn(depth_m)
    depth_km = depth_m / 1000.0
    db_loss = atten_db_per_km * depth_km
    return 10 ** (-db_loss / 20.0)


def required_atten_for_reach(well_depth_m, threshold):
    """dB/km maksimum agar Skenario C (bonded) masih di atas ambang di kedalaman ESP."""
    well_depth_km = max(well_depth_m, 1.0) / 1000.0
    if threshold <= 0:
        return float("inf")
    return -20.0 * math.log10(threshold) / well_depth_km


# ----------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------
col_viz, col_param = st.columns([1.9, 1])

with col_param:
    st.markdown("<div class='section-title'>Parameter Umum</div>", unsafe_allow_html=True)
    freq_khz = st.slider("Frekuensi Kerja Alat (kHz)", 1, 500, 150, step=1,
                          help="Spesifikasi alat EMSP komersial umumnya 100-200 kHz.")
    sigma_brine = st.slider("Konduktivitas Brine (S/m)", 0.05, 10.0, 4.0, step=0.05,
                             help="Air tawar ~0.0005-0.05 S/m. Brine salinitas tinggi ~3-6 S/m.")
    well_depth = st.slider("Kedalaman ESP (m)", 200, 4000, 2000, step=50)

    material = st.radio("Material Pipa/Tubing (untuk Skenario A & B)",
                         ["Non-Metal (PVC/HDPE)", "Metal (Baja/Casing)"], index=1)
    is_metal = material.startswith("Metal")
    wall_thickness = 8.0
    if is_metal:
        wall_thickness = st.slider("Ketebalan Dinding Pipa (mm)", 2.0, 20.0, 8.0, step=0.5)

    threshold_pct = st.slider("Ambang Efektivitas Sinyal (%)", 0.1, 10.0, 1.0, step=0.1,
                               help="Asumsi ilustratif: sinyal minimal yang dianggap masih mampu memengaruhi nukleasi kristal. Bukan angka tervalidasi.")

    st.markdown("<div class='section-title' style='margin-top:18px;'>Skenario C: Konduksi Galvanis</div>", unsafe_allow_html=True)
    bonded = st.toggle("Alat electrically bonded langsung ke tubing/casing?", value=True,
                        help="Kalau OFF, alat cuma clamp induktif dari luar (seperti Skenario B) dan jalur konduksi ini tidak berlaku.")
    atten_db_km = 5.0
    if bonded:
        atten_db_km = st.slider("Redaman Sepanjang Tubing (dB/km)", 0.1, 100.0, 5.0, step=0.1,
                                 help="Ilustratif: rugi resistif per km sepanjang logam. Nilai aktual tergantung grade baja, sambungan (coupling), dan kontinuitas listrik casing/tubing — perlu data lapangan/vendor untuk kalibrasi.")

    st.markdown(
        "<div class='note-box'>Ubah slider untuk eksplorasi: pada kombinasi parameter seperti apa masing-masing skenario mulai realistis secara fisika?</div>",
        unsafe_allow_html=True,
    )

# --- hitung semua fisika ---
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
            {"<div class='metric-row'><span class='metric-label'>Faktor Transmisi Dinding Pipa</span><span class='metric-value-white'>" + f"{wall_factor:.2e}</span></div>" if is_metal else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class='metric-card border-red'>
            <div class='metric-label'>Skenario B: Konduktivitas Brine Maksimum agar Realistis</div>
            <div style='font-size:20px; font-weight:800; color:{RED}; margin:4px 0;'>{sigma_required:.3e} S/m</div>
            <div class='metric-label'>Slidermu: <b style='color:white;'>{sigma_brine:.2f} S/m</b> &mdash; jutaan kali lebih tinggi dari batas ini</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class='metric-card border-green'>
            <div class='metric-label'>Skenario C: Redaman Maksimum agar Realistis</div>
            <div style='font-size:20px; font-weight:800; color:{GREEN}; margin:4px 0;'>{atten_required:.2f} dB/km</div>
            <div class='metric-label'>Slidermu: <b style='color:white;'>{atten_db_km:.1f} dB/km</b> &mdash; {'di bawah' if atten_db_km <= atten_required else 'di atas'} batas ini
            (nilai referensi kabel/pipa bonding di lapangan biasanya jauh di bawah 20 dB/km)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# LEGENDA WARNA
# ----------------------------------------------------------------------
with col_viz:
    st.markdown(
        f"""
        <div style='display:flex; gap:22px; flex-wrap:wrap; margin-bottom:10px; padding:10px 14px; background:{CARD_BG}; border-radius:8px;'>
            <div class='legend-item'><span class='legend-dot' style='background:{CYAN};'></span> Strip biru muda = kekuatan sinyal EM (makin terang = makin kuat)</div>
            <div class='legend-item'><span class='legend-dot' style='background:{PURPLE};'></span> Titik ungu (oval) = kristal <b>aragonit</b> &mdash; lunak, melayang, aman untuk ESP</div>
            <div class='legend-item'><span class='legend-sq' style='background:{RED};'></span> Kotak merah = kristal <b>kalsit</b> &mdash; keras, menumpuk &amp; merusak impeller ESP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# VISUALISASI 3 SUMUR — HTML/CANVAS
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
  .well-label { color: white; font-size: 13.5px; font-weight: 700; text-align: center; }
  .well-sub { color: #a0aabf; font-size: 11px; text-align: center; margin-top: -4px; }
  .badge { padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; margin-top: 4px; text-align:center; }
</style>
</head>
<body>
<div class="wrap" id="wrap"></div>

<script>
const CFG = __CFG_JSON__;
const wrap = document.getElementById('wrap');

CFG.scenarios.forEach((sc, idx) => {
  const colId = 'col' + idx;
  const canvasId = 'well' + idx;
  const badgeId = 'badge' + idx;
  const col = document.createElement('div');
  col.className = 'col';
  col.innerHTML = `
    <div class="well-label">${sc.title}</div>
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
  const cx = W / 2, tubeW = 62;
  const wellDepth = CFG.wellDepth;
  const protectedWell = sc.finalIntensity >= CFG.threshold;

  let frame = 0;
  const pulses = [];
  const crystals = [];
  let buildup = 0;

  function spawnPulse() {
    pulses.push({ t: 0, speed: 0.006 + Math.random() * 0.004, x: cx + (Math.random() - 0.5) * (tubeW * 0.5) });
  }
  function spawnCrystal() {
    const angle = Math.random() * Math.PI * 2;
    const r0 = 50 + Math.random() * 9;
    crystals.push({
      x: cx + Math.cos(angle) * r0, y: y1 + 18 + Math.sin(angle) * r0 * 0.4,
      angle, settled: false, life: 0, isKalsit: !protectedWell,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#5b6470'; ctx.font = '9.5px Segoe UI'; ctx.textAlign = 'left';
    [0.02, 1, 10, 100].forEach((dM) => {
      if (dM > wellDepth) return;
      const t = depthFrac(dM, wellDepth);
      const yy = y0 + t * (y1 - y0);
      ctx.fillText(dM + ' m', cx + tubeW / 2 + 8, yy + 3);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.beginPath(); ctx.moveTo(cx - tubeW / 2, yy); ctx.lineTo(cx + tubeW / 2, yy); ctx.stroke();
    });
    ctx.fillText(wellDepth + ' m (ESP)', cx + tubeW / 2 + 8, y1 + 3);

    ctx.strokeStyle = '#3a4150'; ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx - tubeW / 2, y0); ctx.lineTo(cx - tubeW / 2, y1);
    ctx.moveTo(cx + tubeW / 2, y0); ctx.lineTo(cx + tubeW / 2, y1);
    ctx.stroke();

    const stripH = (y1 - y0) / (sc.curve.length - 1) + 1.2;
    sc.curve.forEach((s) => {
      const yy = y0 + s.t * (y1 - y0);
      const alpha = Math.max(0, Math.min(1, s.inten));
      ctx.fillStyle = `rgba(0,229,255,${0.06 + alpha * 0.9})`;
      ctx.fillRect(cx - tubeW / 2 + 2, yy, tubeW - 4, stripH);
    });

    ctx.fillStyle = 'rgba(168,85,247,0.18)';
    ctx.fillRect(cx - tubeW / 2 - 12, y0 - 34, tubeW + 24, 30);
    ctx.strokeStyle = '#a855f7'; ctx.lineWidth = 1.3;
    ctx.beginPath();
    for (let i = 0; i <= tubeW + 16; i += 4) {
      const yy = y0 - 19 + Math.sin(i * 0.22 - frame * 0.18) * 8;
      if (i === 0) ctx.moveTo(cx - tubeW / 2 - 8 + i, yy); else ctx.lineTo(cx - tubeW / 2 - 8 + i, yy);
    }
    ctx.stroke();
    ctx.fillStyle = '#c084fc'; ctx.font = '9.5px Segoe UI'; ctx.textAlign = 'center';
    ctx.fillText('EMSP', cx, y0 - 40);

    pulses.forEach((p) => {
      const inten = intensityFromCurve(sc.curve, p.t);
      const yy = y0 + p.t * (y1 - y0);
      if (inten > 0.003) {
        ctx.beginPath(); ctx.arc(p.x, yy, 3, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${Math.min(1, inten * 1.3)})`;
        ctx.fill();
      }
    });

    ctx.fillStyle = '#2a2f3d';
    ctx.fillRect(cx - 24, y1 + 6, 48, 26);
    ctx.strokeStyle = '#5b6470'; ctx.lineWidth = 1.2;
    ctx.strokeRect(cx - 24, y1 + 6, 48, 26);
    ctx.fillStyle = '#9aa5b3'; ctx.font = '8.5px Segoe UI'; ctx.textAlign = 'center';
    ctx.fillText('ESP', cx, y1 + 22);

    crystals.forEach((c) => {
      ctx.save(); ctx.translate(c.x, c.y);
      if (c.isKalsit) {
        ctx.fillStyle = c.settled ? '#b91c1c' : '#ef4444';
        ctx.fillRect(-4, -4, 8, 8);
      } else {
        ctx.fillStyle = 'rgba(168,85,247,0.85)';
        ctx.beginPath(); ctx.ellipse(0, 0, 5, 3.2, 0, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
    });
  }

  function update() {
    if (Math.random() < 0.55) spawnPulse();
    pulses.forEach((p) => { p.t += p.speed; });
    for (let i = pulses.length - 1; i >= 0; i--) if (pulses[i].t >= 1) pulses.splice(i, 1);

    if (Math.random() < (protectedWell ? 0.5 : 0.35) && crystals.length < (protectedWell ? 24 : 55)) spawnCrystal();
    crystals.forEach((c) => {
      c.life += 1;
      if (c.isKalsit) {
        if (!c.settled) {
          const targetR = 28 + Math.min(buildup, 24);
          c.x = cx + Math.cos(c.angle) * targetR;
          c.y = y1 + 18 + Math.sin(c.angle) * targetR * 0.42;
          if (c.life > 20) c.settled = true;
        }
      } else {
        c.x += Math.sin(c.life * 0.05 + c.angle) * 0.6;
        c.y += Math.cos(c.life * 0.04 + c.angle) * 0.4;
      }
    });
    if (!protectedWell) buildup = Math.min(24, buildup + 0.01);
    for (let i = crystals.length - 1; i >= 0; i--) {
      if (!crystals[i].isKalsit && crystals[i].life > 260) crystals.splice(i, 1);
    }
    frame++;
  }

  function loop() { update(); draw(); requestAnimationFrame(loop); }
  requestAnimationFrame(loop);

  const badge = document.getElementById(badgeId);
  if (protectedWell) {
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


def render_well_comparison(scenarios, well_depth_m, threshold_frac):
    cfg = dict(
        wellDepth=round(well_depth_m, 2),
        threshold=round(threshold_frac, 6),
        scenarios=scenarios,
    )
    html = _WELL_ANIM_HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))
    components.html(html, height=650, scrolling=False)


scenarios_payload = [
    {
        "title": "SKENARIO A",
        "subtitle": "Klaim vendor (tanpa redaman)",
        "curve": curve_A,
        "finalIntensity": final_A,
    },
    {
        "title": "SKENARIO B",
        "subtitle": "Radiasi lewat fluida (skin effect)",
        "curve": curve_B,
        "finalIntensity": final_B,
    },
    {
        "title": "SKENARIO C",
        "subtitle": f"Konduksi galvanis {'(bonded)' if bonded else '(TIDAK bonded → = Skenario B)'}",
        "curve": curve_C,
        "finalIntensity": final_C,
    },
]

with col_viz:
    render_well_comparison(scenarios_payload, well_depth, threshold)

    st.markdown(
        f"""
        <div style='display:flex; gap:12px; margin-top:8px;'>
            <div class='metric-card border-cyan' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP — A</div>
                <div style='font-size:19px; font-weight:800; color:{CYAN};'>{fmt_frac_pct(final_A)}</div>
            </div>
            <div class='metric-card border-purple' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP — B</div>
                <div style='font-size:19px; font-weight:800; color:{PURPLE};'>{fmt_frac_pct(final_B)}</div>
            </div>
            <div class='metric-card border-green' style='flex:1; text-align:center;'>
                <div class='metric-label'>Sinyal di ESP — C</div>
                <div style='font-size:19px; font-weight:800; color:{GREEN};'>{fmt_frac_pct(final_C)}</div>
            </div>
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
                          line=dict(color=CYAN, width=2.5, dash="dash")))
fig.add_trace(go.Scatter(x=depths, y=curve_B_full, mode="lines", name="B: Radiasi lewat fluida",
                          line=dict(color=PURPLE, width=3)))
fig.add_trace(go.Scatter(x=depths, y=curve_C_full, mode="lines", name="C: Konduksi galvanis",
                          line=dict(color=GREEN, width=3)))
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
if protected_C and bonded:
    verdict_color = GREEN
    verdict_text = (
        f"Dengan parameter saat ini, <b>Skenario C (konduksi galvanis, bonded)</b> menghasilkan sinyal "
        f"{fmt_frac_pct(final_C)} di kedalaman ESP &mdash; di atas ambang. Ini konsisten dengan mekanisme yang "
        f"lebih masuk akal secara fisika untuk menjelaskan kenaikan run life. <b>Tapi ini baru valid kalau alat "
        f"memang terbukti electrically bonded ke tubing/casing</b> &mdash; cek spesifikasi teknis vendor, jangan "
        f"cuma asumsi dari gambar clamp di luar pipa."
    )
elif not bonded and not protected_B:
    verdict_color = RED
    verdict_text = (
        f"Alat diasumsikan TIDAK bonded (cuma clamp induktif). Dalam kondisi ini, Skenario C otomatis sama "
        f"dengan Skenario B: sinyal cuma {fmt_frac_pct(final_B)} di kedalaman ESP &mdash; jauh di bawah ambang. "
        f"Kalau EMSP-mu memang jenis clamp non-invasif, maka secara fisika sinyal TIDAK mungkin sampai ke ESP "
        f"lewat cara apapun yang dimodelkan di sini. Kenaikan run life kemungkinan besar berasal dari efek "
        f"tidak langsung (kerak berkurang di permukaan/flowline) atau confounder lain, bukan sinyal yang "
        f"'sampai' ke pompa."
    )
else:
    verdict_color = RED
    verdict_text = (
        f"Redaman Skenario C ({atten_db_km:.1f} dB/km) masih terlalu besar untuk kedalaman {well_depth} m. "
        f"Turunkan redaman di bawah {atten_required:.2f} dB/km (atau perkecil kedalaman) untuk melihat kapan "
        f"jalur konduksi galvanis ini mulai realistis."
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
    &bull; Skenario A &amp; B memodelkan gelombang EM meradiasi lewat dinding pipa lalu merambat lewat brine
    (medium dielektrik/konduktif homogen), pakai rumus skin depth standar
    (&delta; = &radic;(2/(&omega;&middot;&mu;&#8320;&middot;&mu;<sub>r</sub>&middot;&sigma;))). Ini tidak memodelkan geometri sumur riil atau
    interaksi dengan formasi di sekitar casing.<br>
    &bull; Skenario C memodelkan mekanisme yang BEDA: konduksi aksial lewat logam sebagai konduktor bonded,
    disederhanakan sebagai redaman linear (dB/km). Ini pendekatan ILUSTRATIF untuk membangun intuisi &mdash;
    nilai dB/km aktual tergantung grade baja, kontinuitas sambungan (coupling/centralizer), isolasi packer,
    dan frekuensi kerja alat. Untuk angka yang bisa dipertanggungjawabkan, perlu data pengukuran lapangan
    atau spesifikasi teknis dari vendor/riset EM-telemetry (mis. literatur EM-MWD/casing telemetry).<br>
    &bull; "Ambang efektivitas sinyal" adalah asumsi eksplorasi, bukan angka tervalidasi.<br>
    &bull; Gunakan simulasi ini untuk membangun intuisi soal skala redaman &amp; membedakan mekanisme,
    bukan sebagai pengganti pengukuran lapangan atau uji laboratorium aktual.
    </div>
    """,
    unsafe_allow_html=True,
)
