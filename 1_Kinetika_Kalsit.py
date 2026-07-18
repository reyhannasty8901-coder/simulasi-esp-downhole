"""
Simulasi A — Analisis Komparatif: Pembentukan Kerak & EMSP (v4, animasi mulus)
================================================================================
Versi ini mempertahankan seluruh model kimia dari versi sebelumnya
(LSI, aturan tahapan Ostwald, persamaan Avrami, waktu tinggal di
kumparan), tapi mengganti mesin animasi pipa:

  SEBELUMNYA (v3): posisi partikel dihitung di Python -> digambar
  sebagai satu frame Plotly -> lalu seluruh skrip Streamlit dijalankan
  ulang lewat st.rerun() untuk menghasilkan frame berikutnya. Pola ini
  membuat animasi terlihat patah-patah karena setiap frame = reload
  penuh server + semua widget & chart lain ikut ter-render ulang.

  SEKARANG (v4): panel pipa dirender sebagai satu komponen HTML/JS
  (via streamlit.components.v1.html) yang menggambar di <canvas>
  memakai requestAnimationFrame — pola animasi standar browser yang
  berjalan 60fps di sisi klien, tanpa roundtrip ke server Streamlit
  sama sekali selama animasi berjalan. Streamlit hanya perlu
  menjalankan ulang skrip saat parameter (slider/toggle) berubah,
  bukan setiap frame.

  Proporsi kalsit vs aragonit yang dibentuk di dalam animasi tetap
  ditentukan oleh hasil perhitungan kimia (frac_off, frac_on) dari
  Python, dikirim ke JavaScript sebagai parameter konfigurasi — jadi
  visualnya tetap konsisten dengan angka-angka di dashboard.

Jalankan dengan:
    streamlit run simulasi_kinetika_kristalisasi_v4_smooth.py
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
# FUNGSI PERHITUNGAN KIMIA (tidak berubah dari versi sebelumnya)
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
# ANIMASI PIPA — HTML/CANVAS + requestAnimationFrame (MULUS, TANPA st.rerun)
# ----------------------------------------------------------------------
# Template JS ditulis sebagai string biasa (bukan f-string) supaya kurung
# kurawal JS tidak bentrok dengan sintaks f-string Python. Parameter dari
# Python disisipkan lewat satu token JSON: __CFG_JSON__.
_PIPE_ANIM_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<style>
  :root {
    --bg: #12141c; --panel: #1e212b; --muted: #a0aabf;
    /* Palet sengaja disebar jauh di roda warna supaya ion & kristal
       tidak pernah mirip satu sama lain: biru - kuning - merah - ungu */
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
    <div class="legend-item"><span class="legend-dot" style="background:var(--aragonite);"></span>Aragonite (Tersuspensi, terbentuk setelah EMSP)</div>
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

// Dua pipa: atas = referensi OFF (calcite mode), bawah = kondisi EMSP saat ini.
// Posisi kumparan BERBEDA per pipa:
//  - OFF : kumparan digambar redup di tengah hanya sebagai referensi visual
//          (tidak aktif, tidak memengaruhi apa pun -- sistem ini memang
//          tidak dipasangi EMSP).
//  - ON  : kumparan dipasang DEKAT AWAL pipa (kiri), sehingga hampir
//          seluruh panjang pipa berada di zona "pasca-EMSP" -> ion yang
//          bertabrakan sepanjang sisa pipa langsung membentuk aragonit,
//          dan kerak kalsit praktis tidak sempat menumpuk di dinding.
const pipes = [
  { y: 30,  h: 150, isCoilActive: false, frac: CFG.fracOff, label: 'EMSP: OFF (Calcite Mode)',
    coilX: 350, coilW: 150 },
  { y: 220, h: 150, isCoilActive: CFG.statusOn, frac: CFG.statusOn ? CFG.fracOn : CFG.fracOff,
    label: CFG.statusOn ? 'EMSP: ON (Aragonite Mode)' : 'EMSP: OFF (Calcite Mode)',
    coilX: CFG.statusOn ? 45 : 350, coilW: CFG.statusOn ? 110 : 150 },
];
pipes.forEach(p => { p.coilEndX = p.coilX + p.coilW; });

const flowPx = (0.6 + CFG.flow * 0.9) * CFG.speedMult;   // kecepatan dasar dari Laju Alir (m/s)
const spawnRate = 0.15 + 0.55 * CFG.drivingNorm;          // dari LSI (potensi presipitasi)

// batas tebal kerak maksimum di tiap sisi (top & bottom) sebelum pipa
// dianggap tersumbat penuh di posisi x tersebut
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
  constructor(pipe, x, y, isKalsit) {
    this.isKalsit = isKalsit;
    this.x = x; this.y = y;
    this.size = isKalsit ? 3 : 2;
    this.vx = flowPx * (isKalsit ? 0.55 : 1.05);
    // kalsit hanyut ke dinding terdekat (atas / bawah), aragonit tetap melayang di tengah aliran
    this.side = (y - pipe.y) < pipe.h / 2 ? 'top' : 'bottom';
    this.vy = isKalsit ? (this.side === 'top' ? -1.0 : 1.0) : (Math.random() - 0.5);
    this.stuck = false;
  }
  update(pipe) {
    if (this.stuck) return;
    this.x += this.vx; this.y += this.vy;
    if (this.isKalsit) {
      if (this.size < 10) { this.size += 0.02; this.vy += (this.side === 'top' ? -0.05 : 0.05); }
      const idx = Math.min(W - 1, Math.max(0, Math.floor(this.x)));
      const maxSide = maxScalePerSide(pipe);
      if (this.side === 'top') {
        const wall = pipe.y + this.size + (pipe.state.scaleTop[idx] || 0);
        if (this.y <= wall) {
          this.stuck = true; this.y = wall;
          this._depositTo(pipe, 'scaleTop', maxSide);
        }
      } else {
        const wall = pipe.y + pipe.h - this.size - (pipe.state.scaleBottom[idx] || 0);
        if (this.y >= wall) {
          this.stuck = true; this.y = wall;
          this._depositTo(pipe, 'scaleBottom', maxSide);
        }
      }
    } else {
      // aragonit: tersuspensi, memantul halus di tengah aliran, tidak pernah menempel
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
            // ATURAN POSISI: aragonit HANYA bisa terbentuk dari ion yang
            // sudah melewati zona kumparan EMSP (cx > coilEndX) saat medan
            // aktif. Sebelum/di dalam kumparan, jalur default tetap kalsit
            // (belum "disentuh" medan) -- sesuai mekanisme di catatan model.
            let isKalsit;
            if (pipe.isCoilActive && cx > pipe.coilEndX) {
              isKalsit = Math.random() < pipe.frac; // sisa kalsit yg lolos dari efek EMSP
            } else {
              isKalsit = true;
            }
            st.crystals.push(new Crystal(pipe, cx, cy, isKalsit));
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
  requestAnimationFrame(loop);
} else {
  renderFrame(); // gambar satu frame statis saat animasi dijeda
}
</script>
</body>
</html>
"""


def render_animasi_pipa(frac_off, frac_on, laju_alir, driving_norm, status_on, animate, speed_mult):
    cfg = dict(
        fracOff=round(frac_off, 4),
        fracOn=round(frac_on, 4),
        flow=round(laju_alir, 3),
        drivingNorm=round(driving_norm, 4),
        statusOn=bool(status_on),
        animate=bool(animate),
        speedMult=round(speed_mult, 3),
    )
    html = _PIPE_ANIM_HTML_TEMPLATE.replace("__CFG_JSON__", json.dumps(cfg))
    components.html(html, height=440, scrolling=False)


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

    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0
    if st.button("🔄 Reset Pipa & Grafik", use_container_width=True):
        st.session_state.reset_key += 1

# ---------------- PANEL VISUALISASI PIPA (ANIMASI HTML/CANVAS, MULUS) ----------------
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

    # reset_key dipakai sebagai bagian dari key komponen supaya tombol Reset
    # memaksa Streamlit membuat ulang komponen HTML (state partikel di JS mulai
    # dari nol lagi), tanpa perlu re-render server tiap frame.
    render_animasi_pipa(
        frac_off=frac_off,
        frac_on=frac_on,
        laju_alir=laju_alir,
        driving_norm=driving_norm,
        status_on=status_on,
        animate=animasi_aktif,
        speed_mult=mult,
    )

    st.markdown("<div class='progress-label' style='margin-top:6px;'>Perkembangan Kerak (OFF)</div>", unsafe_allow_html=True)
    st.progress(frac_off, text=f"{frac_off*100:.0f}% menuju kerak keras")

    st.markdown("<div class='progress-label' style='margin-top:8px;'>Suspensi Aragonit (ON)</div>", unsafe_allow_html=True)
    st.progress(1 - frac_on, text=f"{(1-frac_on)*100:.0f}% tersuspensi & terbawa aliran")

# ----------------------------------------------------------------------
# ANALISIS LANJUTAN (tidak berubah dari versi sebelumnya — chart statis,
# tidak butuh animasi real-time, jadi tetap pakai Plotly biasa)
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
            fo, foff = fraksi_kalsit(lsi_t, t, True, dwell_factor=dwell)
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
