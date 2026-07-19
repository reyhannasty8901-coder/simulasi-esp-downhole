"""
Simulasi Komparatif: Teori Transmisi EMSP (Galvanic vs Waveguide)
==================================================================
Versi ini membandingkan dua mekanisme transmisi sinyal elektromagnetik:
1. Galvanic (Konduktor Logam)  : Sinyal merambat melalui tubing/casing baja.
2. Waveguide (Media Air Garam) : Sinyal merambat melalui kolom air formasi.

Perbedaan utama: Efektivitas mode "Waveguide" sangat bergantung pada Water Cut,
sedangkan mode "Galvanic" stabil dan hampir tidak terpengaruh oleh Water Cut.
"""

import json
import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------
# KONFIGURASI HALAMAN & TEMA
# ----------------------------------------------------------------------
st.set_page_config(page_title="Analisis Teori Transmisi EMSP", layout="wide")

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
    .note-box {{
        background-color: {CARD_BG}; border-left: 4px solid {MUTED};
        padding: 12px 16px; border-radius: 8px; color: {MUTED}; font-size: 12px; line-height: 1.55;
    }}
    .progress-label {{ color: white; font-size: 13px; margin-bottom: 2px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2 style='text-align:center; color:white;'>Analisis Komparatif: Transmisi Sinyal EMSP</h2>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# FUNGSI PERHITUNGAN KIMIA (dengan tambahan efisiensi transmisi)
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
    """Waktu kontak air dengan medan elektromagnetik di zona kumparan."""
    residence_time_s = panjang_kumparan_m / max(laju_alir_ms, 0.05)
    return float(np.clip(residence_time_s / referensi_s, 0.2, 1.3))


def hitung_efisiensi_transmisi(mode, water_cut, bonding_baik=True):
    """
    Menghitung seberapa besar sinyal EMSP mencapai downhole (efisiensi 0-1).
    - Galvanic: hampir selalu tinggi, via logam.
    - Waveguide: sangat tergantung pada water cut (air sebagai konduktor).
    """
    if mode == "Galvanic (Konduktor Logam)":
        return 0.95 if bonding_baik else 0.30
    else:  # Waveguide
        # Air garam adalah konduktor, minyak/gas adalah isolator.
        # Efisiensi naik secara eksponensial/sigmoid terhadap water cut.
        # Gunakan pendekatan linear yang konservatif: pada WC 0% efisiensi 5%, WC 100% efisiensi 95%.
        return 0.05 + 0.90 * (water_cut / 100.0)


def fraksi_kalsit(lsi, suhu_c, status_on, dwell_factor=1.0, transmisi_eff=1.0, geser_maks=0.50):
    """
    Estimasi fraksi kalsit dari total CaCO3 yang terbentuk.
    transmisi_eff: seberapa besar efek EMSP sampai ke titik tersebut (0-1).
    """
    driving = max(lsi, 0.0)
    frac_off = 0.55 + 0.06 * driving + 0.0035 * (suhu_c - 20)
    frac_off = float(np.clip(frac_off, 0.50, 0.97))

    if not status_on:
        return frac_off, frac_off

    # Efek EMSP dimodulasi oleh dwell factor dan efisiensi transmisi.
    geser = geser_maks * (0.6 + 0.4 * min(driving / 2.0, 1.0)) * dwell_factor * transmisi_eff
    frac_on = float(np.clip(frac_off - geser, 0.08, 0.95))
    return frac_on, frac_off


def laju_deposit(fraksi_kalsit_val, lsi, k_deposit=1.35):
    """Laju penebalan kerak keras (mm/bulan)."""
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
# ANIMASI PIPA — HTML/CANVAS (DENGAN VISUALISASI MODE TRANSMISI)
# ----------------------------------------------------------------------
_PIPE_ANIM_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  :root {
    --bg: #12141c; --panel: #1e212b; --muted: #a0aabf;
    --ion-ca: #3b82f6;      /* biru   : ion Ca2+ */
    --ion-co3: #facc15;     /* kuning : ion CO3 2- */
    --calcite: #ef4444;     /* merah  : kristal kalsit (menempel, keras) */
    --aragonite: #a855f7;   /* ungu   : kristal aragonit (tersuspensi) */
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', sans-serif; }
  .wrap { display: flex; flex-direction: column; gap: 10px; }
  canvas { width: 100%; display: block; background: #0d0f16; border-radius: 10px; }
  .legend-row { display: flex; gap: 22px; flex-wrap: wrap; align-items: center;
      background-color: var(--panel); padding: 12px 16px; border-radius: 10px; }
  .legend-item { display: flex; align-items: center; gap: 7px; font-size: 12.5px; color: white; white-space: nowrap; }
  .legend-dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
</style>
</head>
<body>
<div class="wrap">
  <canvas id="pipeCanvas" width="900" height="400"></canvas>
  <div class="legend-row">
    <div class="legend-item"><span class="legend-dot" style="background:var(--ion-ca);"></span>Ion Ca&sup2;&#8314;</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--ion-co3);"></span>Ion CO&#8323;&sup2;&#8315;</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--calcite); border-radius:2px;"></span>Calcite (Kerak Melekat)</div>
    <div class="legend-item"><span class="legend-dot" style="background:var(--aragonite);"></span>Aragonite (Tersuspensi)</div>
    <div class="legend-item"><span style="color:#00e5ff;">⚡</span> Sinyal EMSP: <span id="modeLabel">${CFG.transmissionMode}</span></div>
  </div>
</div>

<script>
const CFG = __CFG_JSON__;

const canvas = document.getElementById('pipeCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

const COL_CA = '#3b82f6';
const COL_CO3 = '#facc15';
const COL_CALCITE = '#ef4444';
const COL_CALCITE_STUCK = '#b91c1c';
const COL_ARAGONITE = '#a855f7';
const COL_SIGNAL = '#00e5ff';

const pipes = [
  { y: 30,  h: 150, isCoilActive: false, frac: CFG.fracOff, label: 'EMSP: OFF (Calcite Mode)',
    coilX: 350, coilW: 150 },
  { y: 220, h: 150, isCoilActive: CFG.statusOn, frac: CFG.statusOn ? CFG.fracOn : CFG.fracOff,
    label: CFG.statusOn ? 'EMSP: ON (Aragonite Mode)' : 'EMSP: OFF (Calcite Mode)',
    coilX: CFG.statusOn ? 8 : 350, coilW: CFG.statusOn ? 130 : 150 },
];
pipes.forEach(p => { p.coilEndX = p.coilX + p.coilW; });

const flowPx = (0.6 + CFG.flow * 0.9) * CFG.speedMult;
const spawnRate = 0.15 + 0.55 * CFG.drivingNorm;

function maxScalePerSide(pipe) { return pipe.h / 2 - 4; }

function makeState() {
  return { ions: [], crystals: [], scaleTop: new Array(W).fill(0), scaleBottom: new Array(W).fill(0) };
}
pipes.forEach(p => { p.state = makeState(); });

function boundsAt(pipe, x) {
  const idx = Math.min(W - 1, Math.max(0, Math.floor(x)));
  const top = pipe.y + 6 + (pipe.state.scaleTop[idx] || 0);
  const bottom = pipe.y + pipe.h - 6 - (pipe.state.scaleBottom[idx] || 0);
  return { top, bottom };
}

class Ion {
  constructor(pipe) {
    this.x = Math.random() * 40;
    this.y = pipe.y + 15 + Math.random() * (pipe.h - 30);
    this.type = Math.random() > 0.5 ? 'Ca' : 'CO3';
    this.vx = flowPx * (0.8 + Math.random() * 0.4);
    this.vy = (Math.random() - 0.5) * 1.2;
    this.active = true;
  }
  update(pipe) {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += (Math.random() - 0.5) * 0.6;
    const b = boundsAt(pipe, this.x);
    if (this.y < b.top) { this.y = b.top; this.vy *= -1; }
    if (this.y > b.bottom) { this.y = b.bottom; this.vy *= -1; }
  }
  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, 2.6, 0, Math.PI * 2);
    ctx.fillStyle = this.type === 'Ca' ? COL_CA : COL_CO3;
    ctx.fill();
  }
}

class Crystal {
  constructor(pipe, x, y, isKalsit, canStick) {
    this.isKalsit = isKalsit;
    this.canStick = canStick;
    this.x = x; this.y = y;
    this.size = isKalsit ? 3 : 2;
    this.vx = flowPx * (isKalsit && canStick ? 0.55 : 1.05);
    this.side = (y - pipe.y) < pipe.h / 2 ? 'top' : 'bottom';
    this.vy = (isKalsit && canStick) ? (this.side === 'top' ? -1.0 : 1.0) : (Math.random() - 0.5);
    this.stuck = false;
  }
  update(pipe) {
    if (this.stuck) return;
    this.x += this.vx; this.y += this.vy;
    if (this.isKalsit && this.canStick) {
      if (this.size < 10) { this.size += 0.02; this.vy += (this.side === 'top' ? -0.05 : 0.05); }
      const idx = Math.min(W - 1, Math.max(0, Math.floor(this.x)));
      const maxSide = maxScalePerSide(pipe);
      if (this.side === 'top') {
        const wall = pipe.y + this.size + (pipe.state.scaleTop[idx] || 0);
        if (this.y <= wall) { this.stuck = true; this.y = wall; this._depositTo(pipe, 'scaleTop', maxSide); }
      } else {
        const wall = pipe.y + pipe.h - this.size - (pipe.state.scaleBottom[idx] || 0);
        if (this.y >= wall) { this.stuck = true; this.y = wall; this._depositTo(pipe, 'scaleBottom', maxSide); }
      }
    } else {
      const b = boundsAt(pipe, this.x);
      if (this.y >= b.bottom) { this.y = b.bottom; this.vy = -Math.abs(this.vy || 1); }
      if (this.y <= b.top) { this.y = b.top; this.vy = Math.abs(this.vy || 1); }
    }
  }
  _depositTo(pipe, key, maxSide) {
    const impactX = Math.floor(this.x);
    const arr = pipe.state[key];
    for (let i = Math.max(0, impactX - 10); i < Math.min(W, impactX + 10); i++) {
      arr[i] = Math.min(maxSide, arr[i] + Math.max(0, (10 - Math.abs(impactX - i)) * 0.06));
    }
  }
  draw() {
    ctx.save();
    ctx.translate(this.x, this.y);
    if (this.isKalsit) {
      ctx.fillStyle = this.stuck ? COL_CALCITE_STUCK : COL_CALCITE;
      ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
    } else {
      ctx.fillStyle = COL_ARAGONITE;
      ctx.beginPath();
      ctx.ellipse(0, 0, this.size + 1.5, this.size, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}

function drawSignal(pipe, t) {
    if (!pipe.isCoilActive) return;
    const mode = CFG.transmissionMode;
    const eff = CFG.transmissionEff;

    // Jika efisiensi sangat rendah, sinyal tidak terlihat
    if (eff < 0.1) return;

    ctx.globalAlpha = 0.4 + 0.6 * eff;
    if (mode === 'Galvanic (Konduktor Logam)') {
        // Sinyal merambat di DINDING pipa (atas & bawah)
        ctx.strokeStyle = COL_SIGNAL;
        ctx.lineWidth = 2.5;
        ctx.setLineDash([6, 4]);
        // Dinding atas
        ctx.beginPath();
        ctx.moveTo(0, pipe.y + 4);
        for (let i = 0; i < W; i+=2) {
            const yOffset = Math.sin(i * 0.1 + t * 0.2) * 1.5;
            ctx.lineTo(i, pipe.y + 4 + yOffset);
        }
        ctx.stroke();
        // Dinding bawah
        ctx.beginPath();
        ctx.moveTo(0, pipe.y + pipe.h - 4);
        for (let i = 0; i < W; i+=2) {
            const yOffset = Math.sin(i * 0.1 + t * 0.2 + 1) * 1.5;
            ctx.lineTo(i, pipe.y + pipe.h - 4 + yOffset);
        }
        ctx.stroke();
        ctx.setLineDash([]);
        // Label
        ctx.fillStyle = COL_SIGNAL;
        ctx.font = 'bold 10px Segoe UI';
        ctx.fillText('⚡ Sinyal via Logam (Efisiensi ' + (eff*100).toFixed(0) + '%)', pipe.coilX + 10, pipe.y - 12);
    } else {
        // Waveguide: Sinyal merambat di DALAM FLUIDA (gelombang sinus)
        ctx.strokeStyle = `rgba(0, 229, 255, ${0.2 + 0.5 * eff})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        const amplitude = pipe.h * 0.15 * (0.5 + 0.5 * eff);
        for (let i = 0; i < W; i++) {
            const yWave = pipe.y + pipe.h/2 + Math.sin(i * 0.04 - t * 0.15) * amplitude;
            if (i === 0) ctx.moveTo(i, yWave);
            else ctx.lineTo(i, yWave);
        }
        ctx.stroke();
        ctx.fillStyle = `rgba(0, 229, 255, ${0.1 + 0.5 * eff})`;
        ctx.font = 'bold 10px Segoe UI';
        ctx.fillText('🌊 Sinyal via Air Garam (Efisiensi ' + (eff*100).toFixed(0) + '%)', pipe.coilX + 10, pipe.y - 12);
    }
    ctx.globalAlpha = 1.0;
}

function drawPipeFrame(pipe, t) {
  ctx.strokeStyle = '#3a4150'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(0, pipe.y); ctx.lineTo(W, pipe.y); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, pipe.y + pipe.h); ctx.lineTo(W, pipe.y + pipe.h); ctx.stroke();

  ctx.fillStyle = '#e5e9f0'; ctx.font = 'bold 12.5px Segoe UI';
  ctx.fillText(pipe.label, 6, pipe.y - 8);

  // zona kumparan EMSP
  ctx.fillStyle = pipe.isCoilActive ? 'rgba(168,85,247,0.12)' : 'rgba(255,255,255,0.04)';
  ctx.fillRect(pipe.coilX, pipe.y, pipe.coilW, pipe.h);
  if (pipe.isCoilActive) {
    ctx.strokeStyle = '#a855f7'; ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i <= pipe.coilW; i += 4) {
      const yWave = pipe.y + pipe.h / 2 + Math.sin(i * 0.14 - t * 0.15) * (pipe.h * 0.28);
      if (i === 0) ctx.moveTo(pipe.coilX + i, yWave); else ctx.lineTo(pipe.coilX + i, yWave);
    }
    ctx.stroke();
    ctx.fillStyle = 'rgba(168,85,247,0.85)'; ctx.font = '10px Segoe UI';
    ctx.fillText('medan EMSP', pipe.coilX + 4, pipe.y + pipe.h + 14);
  }

  // Gambarkan indikator sinyal transmisi (baru)
  drawSignal(pipe, t);

  // endapan kerak kalsit dari ATAS
  ctx.fillStyle = '#7f1d1d';
  ctx.beginPath();
  ctx.moveTo(0, pipe.y);
  for (let i = 0; i < W; i++) ctx.lineTo(i, pipe.y + pipe.state.scaleTop[i]);
  ctx.lineTo(W, pipe.y);
  ctx.closePath(); ctx.fill();

  // endapan kerak kalsit dari BAWAH
  ctx.fillStyle = '#7f1d1d';
  ctx.beginPath();
  ctx.moveTo(0, pipe.y + pipe.h);
  for (let i = 0; i < W; i++) ctx.lineTo(i, pipe.y + pipe.h - pipe.state.scaleBottom[i]);
  ctx.lineTo(W, pipe.y + pipe.h);
  ctx.closePath(); ctx.fill();
}

function stepPipe(pipe) {
  const st = pipe.state;
  if (Math.random() < spawnRate && st.ions.length < 90) {
    st.ions.push(new Ion(pipe));
  }
  for (let i = st.ions.length - 1; i >= 0; i--) {
    const a = st.ions[i];
    a.update(pipe); a.draw();
    if (a.x > W) { st.ions.splice(i, 1); continue; }
    if (a.active) {
      for (let j = i - 1; j >= 0; j--) {
        const b = st.ions[j];
        if (b.active && a.type !== b.type) {
          const dist = Math.hypot(a.x - b.x, a.y - b.y);
          if (dist < 11) {
            a.active = false; b.active = false;
            const cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
            let isKalsit, canStick;
            if (pipe.isCoilActive && cx > pipe.coilX) {
              isKalsit = Math.random() < pipe.frac;
              canStick = false;
            } else {
              isKalsit = true;
              canStick = true;
            }
            st.crystals.push(new Crystal(pipe, cx, cy, isKalsit, canStick));
            break;
          }
        }
      }
    }
  }
  st.ions = st.ions.filter(p => p.active);
  for (let i = st.crystals.length - 1; i >= 0; i--) {
    const c = st.crystals[i];
    c.update(pipe); c.draw();
    if (c.x > W && !c.stuck) st.crystals.splice(i, 1);
  }
}

let frameCount = 0;
function renderFrame() {
  ctx.clearRect(0, 0, W, H);
  pipes.forEach(pipe => drawPipeFrame(pipe, frameCount));
  pipes.forEach(pipe => stepPipe(pipe));
  frameCount++;
}

function loop() {
  renderFrame();
  if (CFG.animate) requestAnimationFrame(loop);
}

if (CFG.animate) {
  document.getElementById('modeLabel').innerText = CFG.transmissionMode;
  requestAnimationFrame(loop);
} else {
  renderFrame();
}
</script>
</body>
</html>
"""


def render_animasi_pipa(frac_off, frac_on, laju_alir, driving_norm, status_on, animate, speed_mult,
                        transmission_mode, transmission_eff):
    cfg = dict(
        fracOff=round(frac_off, 4),
        fracOn=round(frac_on, 4),
        flow=round(laju_alir, 3),
        drivingNorm=round(driving_norm, 4),
        statusOn=bool(status_on),
        animate=bool(animate),
        speedMult=round(speed_mult, 3),
        transmissionMode=str(transmission_mode),
        transmissionEff=round(transmission_eff, 3),
    )
    html = _PIPE_ANIM_HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))
    components.html(html, height=440, scrolling=False)


# ----------------------------------------------------------------------
# LAYOUT UTAMA: VISUALISASI (kiri) + PARAMETER (kanan)
# ----------------------------------------------------------------------
col_viz, col_param = st.columns([1.55, 1])

# ---------------- PANEL PARAMETER ----------------
with col_param:
    st.markdown("<div class='section-title'>Parameter Sistem</div>", unsafe_allow_html=True)

    status_on = st.toggle("Status EMSP (ON / OFF)", value=True)
    suhu_c = st.slider("Suhu Air Produksi (°C)", 20, 95, 55)
    pH = st.slider("pH Air Produksi", 6.0, 9.5, 7.8, step=0.1)
    laju_alir = st.slider("Laju Alir (m/s)", 0.2, 5.0, 2.5, step=0.1)

    # ========== PARAMETER TEORI TRANSMISI (BARU) ==========
    st.markdown("---")
    st.markdown("<div class='section-title'>⚡ Teori Transmisi Sinyal</div>", unsafe_allow_html=True)
    
    water_cut = st.slider("Water Cut (%)", 0, 100, 85, help="Kadar air dalam fluida produksi. Semakin tinggi, semakin konduktif.")
    transmission_mode = st.radio(
        "Mekanisme Transmisi",
        ["Galvanic (Konduktor Logam)", "Waveguide (Media Air Garam)"],
        index=0,
        help="Galvanic: Sinyal via dinding pipa baja. Waveguide: Sinyal via kolom air."
    )
    
    bonding_baik = True
    if transmission_mode == "Galvanic (Konduktor Logam)":
        bonding_baik = st.toggle("Kualitas Bonding ke Wellhead", value=True, 
                                 help="Jika ON, kontak listrik sempurna. Jika OFF, sambungan longgar/berkarat.")
    
    # Hitung efisiensi transmisi
    transmisi_eff = hitung_efisiensi_transmisi(transmission_mode, water_cut, bonding_baik)
    # =====================================================

    with st.expander("Parameter lanjutan (kesadahan & alkalinitas)"):
        ca_hardness = st.slider("Kesadahan Kalsium (ppm CaCO3)", 50, 800, 320)
        alkalinity = st.slider("Alkalinitas (ppm CaCO3)", 50, 500, 210)
        tds = st.slider("TDS (ppm)", 500, 5000, 1200)

    # --- hitung semua turunan kimia ---
    lsi, phs = hitung_lsi(pH, suhu_c, ca_hardness, alkalinity, tds)
    dwell = faktor_waktu_tinggal(laju_alir)
    
    # FRAKSI KALSIT SEKARANG DIPENGARUHI OLEH TRANSMISI_EFF
    frac_on, frac_off = fraksi_kalsit(lsi, suhu_c, True, dwell_factor=dwell, transmisi_eff=transmisi_eff)
    frac_kalsit_aktif, _ = fraksi_kalsit(lsi, suhu_c, status_on, dwell_factor=dwell, transmisi_eff=transmisi_eff)

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

    # METRIK EFISIENSI TRANSMISI (BARU)
    st.markdown(
        f"""
        <div class='metric-card' style='border-left: 4px solid {CYAN};'>
            <div class='metric-label'>📡 Efisiensi Transmisi ke Downhole</div>
            <div style='font-size:24px; font-weight:800; color:{CYAN};'>{transmisi_eff*100:.0f}%</div>
            <div class='metric-row' style='margin-top:4px;'>
                <span class='metric-label'>Mode: {transmission_mode}</span>
                <span class='metric-label'>Water Cut: {water_cut}%</span>
            </div>
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

    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0
    if st.button("🔄 Reset Pipa & Grafik", use_container_width=True):
        st.session_state.reset_key += 1

# ---------------- PANEL VISUALISASI PIPA ----------------
with col_viz:
    kontrol_a, kontrol_b = st.columns([1, 1])
    with kontrol_a:
        animasi_aktif = st.toggle("▶️ Animasi Real-Time", value=True, key="animate_flag")
    with kontrol_b:
        kecepatan_anim = st.select_slider(
            "Kecepatan", options=["0.5×", "1×", "2×"], value="1×", key="speed_mult",
        )
    mult = {"0.5×": 0.5, "1×": 1.0, "2×": 2.0}[kecepatan_anim]
    driving_norm = min(max(lsi, 0.0) / 2.0, 1.0)

    render_animasi_pipa(
        frac_off=frac_off,
        frac_on=frac_on,
        laju_alir=laju_alir,
        driving_norm=driving_norm,
        status_on=status_on,
        animate=animasi_aktif,
        speed_mult=mult,
        transmission_mode=transmission_mode,
        transmission_eff=transmisi_eff,
    )

    st.markdown("<div class='progress-label' style='margin-top:6px;'>Perkembangan Kerak (OFF)</div>", unsafe_allow_html=True)
    st.progress(frac_off, text=f"{frac_off*100:.0f}% menuju kerak keras")

    st.markdown("<div class='progress-label' style='margin-top:8px;'>Suspensi Aragonit (ON)</div>", unsafe_allow_html=True)
    st.progress(1 - frac_on, text=f"{(1-frac_on)*100:.0f}% tersuspensi & terbawa aliran")

# ----------------------------------------------------------------------
# ANALISIS LANJUTAN (tidak berubah, tapi tetap relevan)
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
    
    # Penjelasan dengan sentuhan teori transmisi
    st.markdown(
        f"""
        <div class='note-box'>
        <b>Analisis Berdasarkan Teori Transmisi:</b><br>
        Mode <b>'{transmission_mode}'</b> dengan efisiensi <b>{transmisi_eff*100:.0f}%</b>.
        {'Pada mode Galvanic, sinyal kuat dan stabil karena menempel pada konduktor logam.' if transmission_mode == 'Galvanic (Konduktor Logam)' else f'Pada mode Waveguide, efisiensi sangat bergantung pada Water Cut ({water_cut}%). Jika water cut turun drastis, efek EMSP melemah.'}
        <br><br>
        Saat EMSP ON, fraksi kalsit turun dari {frac_off*100:.0f}% menjadi {frac_on*100:.0f}%, digantikan aragonit yang tersuspensi.
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab2:
    t_hari = np.linspace(0, 30, 200)
    driving = max(lsi, 0.0)
    k_off = 0.015 + 0.02 * driving + 0.001 * (suhu_c - 20)
    # konstanta laju ON juga dipengaruhi oleh efisiensi transmisi
    k_on = k_off * (0.35 + 0.65 * (1 - transmisi_eff * 0.8)) * (1.3 - 0.3 * dwell)

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
        Kurva mengikuti persamaan Avrami. Perhatikan bahwa pada mode Waveguide dengan Water Cut rendah,
        kurva ON akan mendekati kurva OFF (tidak efektif).
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
            fo, foff = fraksi_kalsit(lsi_p, suhu_c, True, dwell_factor=dwell, transmisi_eff=transmisi_eff)
            frac_off_ph.append(foff * 100)
            frac_on_ph.append(fo * 100)

        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=pH_range, y=frac_off_ph, mode="lines", name="OFF", line=dict(color=ORANGE, width=3)))
        fig_ph.add_trace(go.Scatter(x=pH_range, y=frac_on_ph, mode="lines", name="ON", line=dict(color=CYAN, width=3)))
        fig_ph.add_vline(x=pH, line_dash="dash", line_color="white", opacity=0.4)
        fig_ph.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400, margin=dict(t=50, b=60, l=10, r=10),
            title=dict(text="Fraksi Kalsit vs pH", x=0.0, xanchor="left", y=0.97, yanchor="top",
                       font=dict(color="white", size=14)),
            xaxis_title="pH", yaxis_title="Fraksi Kalsit (%)",
            legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="white")),
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    with colB:
        suhu_range = np.linspace(20, 95, 40)
        frac_off_t, frac_on_t = [], []
        for t in suhu_range:
            lsi_t, _ = hitung_lsi(pH, t, ca_hardness, alkalinity, tds)
            fo, foff = fraksi_kalsit(lsi_t, t, True, dwell_factor=dwell, transmisi_eff=transmisi_eff)
            frac_off_t.append(foff * 100)
            frac_on_t.append(fo * 100)

        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=suhu_range, y=frac_off_t, mode="lines", name="OFF", line=dict(color=ORANGE, width=3)))
        fig_t.add_trace(go.Scatter(x=suhu_range, y=frac_on_t, mode="lines", name="ON", line=dict(color=CYAN, width=3)))
        fig_t.add_vline(x=suhu_c, line_dash="dash", line_color="white", opacity=0.4)
        fig_t.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400, margin=dict(t=50, b=60, l=10, r=10),
            title=dict(text="Fraksi Kalsit vs Suhu", x=0.0, xanchor="left", y=0.97, yanchor="top",
                       font=dict(color="white", size=14)),
            xaxis_title="Suhu (°C)", yaxis_title="Fraksi Kalsit (%)",
            legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="white")),
        )
        st.plotly_chart(fig_t, use_container_width=True)

    st.markdown(
        """
        <div class='note-box'>
        Garis putus-putus menandai posisi pH/suhu yang sedang dipilih. Jika memilih mode Waveguide,
        coba turunkan Water Cut menjadi < 30% dan amati bagaimana kurva ON merapat ke kurva OFF
        (menandakan sinyal tidak sampai ke dasar sumur).
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
    ⚠️ <b>Kesimpulan Simulasi:</b><br>
    • <b>Teori Galvanic (Logam)</b> adalah mekanisme yang paling masuk akal secara fisika dan paling stabil.
      Sinyal merambat efisien melalui tubing/casing baja, terlepas dari kadar air.<br>
    • <b>Teori Waveguide (Air Garam)</b> hanya efektif jika <b>Water Cut > 80%</b>. Pada sumur dengan water cut
      rendah (banyak minyak), sinyal teredam dan EMSP kehilangan efektivitasnya di downhole.<br>
    • Visualisasi di atas menunjukkan secara langsung bagaimana sinyal merambat (di dinding vs di dalam fluida)
      sesuai dengan mode yang dipilih.
    </div>
    """,
    unsafe_allow_html=True,
)
