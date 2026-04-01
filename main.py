"""
Geospatial Agricultural Land Value & Productivity Intelligence System
Entry point: streamlit run main.py
"""
import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from src.utils.auth import generate_otp, verify_otp, register_user, get_user, is_registered
from src.gui.farmer_page import show_farmer_page
from src.gui.buyer_page import show_buyer_page
from src.logic.model import train_model

st.set_page_config(
    page_title="AgriLand Value Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* ══════════════════════════════════════════
   ROOT FONT + ANIMATED BACKGROUND
══════════════════════════════════════════ */
.stApp {
  background: linear-gradient(160deg,
    #1a0e00 0%, #3d1f00 20%, #6b3a0a 40%,
    #8b5e1a 60%, #3d2800 80%, #1a0e00 100%);
  background-size: 400% 400%;
  animation: bgShift 16s ease infinite;
  font-family: 'Poppins', sans-serif;
}
@keyframes bgShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ══════════════════════════════════════════
   GLOBAL TEXT — bright cream, always visible
   text-shadow gives a dark halo so letters
   stay readable even over bright photo areas
══════════════════════════════════════════ */
.stApp, .stApp * {
  font-family: 'Poppins', sans-serif !important;
}

/* Base body copy */
p, li, div, span, label {
  color: #f5e6c0 !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.75) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  letter-spacing: 0.015em !important;
}

/* Headings — pure white, heavier weight, stronger shadow */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"],
.stMarkdown h1, .stMarkdown h2,
.stMarkdown h3, .stMarkdown h4 {
  color: #ffffff !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.9),
               0 0 24px rgba(212,160,32,0.25) !important;
}

/* Caption / fine print — slightly dimmer but still readable */
.stCaption, small, caption {
  color: #d4b870 !important;
  font-size: 11px !important;
  font-weight: 400 !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.8) !important;
}

/* ══════════════════════════════════════════
   INPUT FIELDS
══════════════════════════════════════════ */
.stTextInput label,
.stTextInput > label,
[data-testid="stTextInput"] label {
  color: #fde68a !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.03em !important;
  text-shadow: 0 1px 6px rgba(0,0,0,0.9) !important;
}
.stTextInput > div > div > input {
  background: rgba(20,10,0,0.55) !important;
  border: 1.5px solid rgba(212,160,40,0.6) !important;
  border-radius: 10px !important;
  color: #ffffff !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 10px 14px !important;
  text-shadow: none !important;
}
.stTextInput > div > div > input::placeholder {
  color: rgba(253,230,138,0.4) !important;
}
.stTextInput > div > div > input:focus {
  border-color: #f0c040 !important;
  box-shadow: 0 0 0 2px rgba(240,192,64,0.35) !important;
  background: rgba(30,14,0,0.70) !important;
}

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
.stButton > button {
  background: linear-gradient(135deg, #8b5e1a, #d4a020) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: 0.04em !important;
  width: 100% !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 15px rgba(212,160,32,0.40),
              0 1px 3px rgba(0,0,0,0.6) !important;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 22px rgba(212,160,32,0.60) !important;
  color: #fff8e0 !important;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: rgba(20,10,0,0.96) !important;
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(212,160,40,0.3);
}
[data-testid="stSidebar"] * {
  color: #f5e6c0 !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.7) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: #fde68a !important;
  font-weight: 700 !important;
}

/* ══════════════════════════════════════════
   METRICS
══════════════════════════════════════════ */
[data-testid="metric-container"] {
  background: rgba(255,220,120,0.08) !important;
  border: 1px solid rgba(212,160,40,0.30) !important;
  border-radius: 12px !important;
  padding: 14px !important;
  backdrop-filter: blur(8px) !important;
}
[data-testid="metric-container"] label {
  color: #fde68a !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  text-shadow: 0 1px 5px rgba(0,0,0,0.8) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: #ffe066 !important;
  font-weight: 800 !important;
  font-size: 22px !important;
  text-shadow: 0 2px 8px rgba(0,0,0,0.7) !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  color: #86efac !important;
  font-weight: 600 !important;
}

/* ══════════════════════════════════════════
   TABS
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,220,120,0.07) !important;
  border-radius: 10px !important;
  padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  color: #d4b870 !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.7) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg,#8b5e1a,#d4a020) !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
}

/* ══════════════════════════════════════════
   SELECTBOX / DROPDOWNS
══════════════════════════════════════════ */

/* The closed selector box */
.stSelectbox > div > div {
  background: rgba(20,10,0,0.55) !important;
  border: 1.5px solid rgba(212,160,40,0.45) !important;
  border-radius: 10px !important;
  color: #f5e6c0 !important;
  font-weight: 500 !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.7) !important;
}

/* Label above the selectbox */
.stSelectbox label {
  background: transparent !important;
  border: none !important;
  color: #fde68a !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  text-shadow: 0 1px 6px rgba(0,0,0,0.9) !important;
}

/* ── Dropdown popup menu (white list that appears on open) ── */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"] {
  background: #2a1400 !important;
  border: 1px solid rgba(212,160,40,0.4) !important;
  border-radius: 10px !important;
}

/* Individual option rows */
[data-baseweb="menu"] li,
[data-baseweb="option"],
ul[role="listbox"] li,
div[role="option"],
[role="option"] {
  background: #2a1400 !important;
  color: #f5e6c0 !important;
  font-family: 'Poppins', sans-serif !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  text-shadow: none !important;
}

/* Hover state */
[data-baseweb="option"]:hover,
[role="option"]:hover,
[data-baseweb="menu"] li:hover {
  background: rgba(212,160,40,0.20) !important;
  color: #ffe066 !important;
}

/* Selected / highlighted option */
[aria-selected="true"][role="option"],
[data-baseweb="option"][aria-selected="true"] {
  background: rgba(212,160,40,0.28) !important;
  color: #ffe066 !important;
  font-weight: 700 !important;
}

/* Spans inside options */
[data-baseweb="option"] span,
[role="option"] span,
[data-baseweb="menu"] li span {
  color: inherit !important;
  text-shadow: none !important;
}

/* ══════════════════════════════════════════
   RADIO & CHECKBOX
══════════════════════════════════════════ */
.stRadio label, .stCheckbox label {
  color: #f5e6c0 !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  text-shadow: 0 1px 5px rgba(0,0,0,0.8) !important;
}
.stRadio > label:first-child,
.stCheckbox > label:first-child {
  color: #fde68a !important;
  font-weight: 600 !important;
}

/* ══════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════ */
.streamlit-expanderHeader {
  background: rgba(255,220,120,0.08) !important;
  border-radius: 8px !important;
  color: #fde68a !important;
  font-weight: 600 !important;
  border: 1px solid rgba(212,160,40,0.25) !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.7) !important;
}

/* ══════════════════════════════════════════
   ALERTS / INFO / WARNING / ERROR BOXES
══════════════════════════════════════════ */
.stAlert {
  border-radius: 10px !important;
  backdrop-filter: blur(8px) !important;
}
.stAlert p, .stAlert div, .stAlert span {
  font-weight: 500 !important;
  text-shadow: none !important;
}

/* ══════════════════════════════════════════
   DATAFRAMES / TABLES
══════════════════════════════════════════ */
.stDataFrame, .stTable {
  color: #f5e6c0 !important;
}
[data-testid="stDataFrameResizable"] th {
  color: #fde68a !important;
  font-weight: 700 !important;
  font-size: 12px !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  background: rgba(212,160,32,0.18) !important;
}
[data-testid="stDataFrameResizable"] td {
  color: #f5e6c0 !important;
  font-weight: 400 !important;
}

/* ══════════════════════════════════════════
   MISC
══════════════════════════════════════════ */
hr { border-color: rgba(212,160,40,0.25) !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.main .block-container { background: transparent !important; padding-top: 1rem; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,220,120,0.05); }
::-webkit-scrollbar-thumb { background: rgba(212,160,40,0.5); border-radius: 3px; }

/* ── Photo overlay crossfade keyframes ── */
@keyframes photoFade {
  0%   { opacity: 0; }
  8%   { opacity: 1; }
  33%  { opacity: 1; }
  41%  { opacity: 0; }
  100% { opacity: 0; }
}
</style>

<!-- ═══════════════════════════════════════════════════════════════════
     LAYER 1 — LAND PHOTO OVERLAYS (behind the SVG animation)
     6 farmland / agricultural land images crossfade every ~8 s.
     Full-page coverage at very low opacity so UI stays readable.
════════════════════════════════════════════════════════════════════════ -->
<div id="photo-overlay-wrap"
     style="position:fixed;top:0;left:0;width:100%;height:100%;
            pointer-events:none;z-index:0;overflow:hidden;">

  <!-- Photo 1 — Aerial patchwork of agricultural land parcels -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background-image: url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1800&q=80&fit=crop');
    background-size:cover;background-position:center center;
    opacity:0;
    animation: photoFade 48s ease-in-out 0s infinite;
    filter: sepia(50%) saturate(120%) brightness(0.28) hue-rotate(5deg);
  "></div>

  <!-- Photo 2 — Golden wheat field landscape -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background-image: url('https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=1800&q=80&fit=crop');
    background-size:cover;background-position:center center;
    opacity:0;
    animation: photoFade 48s ease-in-out 8s infinite;
    filter: sepia(55%) saturate(130%) brightness(0.26) hue-rotate(3deg);
  "></div>

  <!-- Photo 3 — Ploughed farmland soil texture -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background-image: url('https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1800&q=80&fit=crop');
    background-size:cover;background-position:center center;
    opacity:0;
    animation: photoFade 48s ease-in-out 16s infinite;
    filter: sepia(45%) saturate(140%) brightness(0.26) hue-rotate(8deg);
  "></div>

  <!-- Photo 4 — Green paddy / crop fields -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background-image: url('https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1800&q=80&fit=crop');
    background-size:cover;background-position:center center;
    opacity:0;
    animation: photoFade 48s ease-in-out 24s infinite;
    filter: sepia(40%) saturate(110%) brightness(0.24) hue-rotate(10deg);
  "></div>

  <!-- Photo 5 — Drone aerial farmland / land plots -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background-image: url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1800&q=80&fit=crop');
    background-size:cover;background-position:center center;
    opacity:0;
    animation: photoFade 48s ease-in-out 32s infinite;
    filter: sepia(50%) saturate(125%) brightness(0.25) hue-rotate(6deg);
  "></div>

  <!-- Photo 6 — Harvested grain field at dusk -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background-image: url('https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=1800&q=80&fit=crop');
    background-size:cover;background-position:center center;
    opacity:0;
    animation: photoFade 48s ease-in-out 40s infinite;
    filter: sepia(55%) saturate(115%) brightness(0.24) hue-rotate(4deg);
  "></div>

  <!-- Solid dark overlay — keeps entire page dark enough for readable UI -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background: rgba(12,6,0,0.55);
    pointer-events:none;
  "></div>

  <!-- Radial vignette — softens corners, focuses centre -->
  <div style="
    position:absolute;top:0;left:0;width:100%;height:100%;
    background: radial-gradient(ellipse at center,
      rgba(0,0,0,0)    25%,
      rgba(10,5,0,0.45) 70%,
      rgba(10,5,0,0.75) 100%);
    pointer-events:none;
  "></div>
</div>

<!-- ═══════════════════════════════════════════════════
     LAYER 2 — ANIMATED AGRICULTURAL SCENE (unchanged)
════════════════════════════════════════════════════════ -->
<div style="position:fixed;top:0;left:0;width:100%;height:100%;
     pointer-events:none;z-index:1;overflow:hidden;">
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 1400 900" preserveAspectRatio="xMidYMid slice"
     style="width:100%;height:100%;opacity:0.40">
  <defs>
    <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#0d0700"/>
      <stop offset="60%"  stop-color="#3d1f00"/>
      <stop offset="100%" stop-color="#6b3a0a"/>
    </linearGradient>
    <linearGradient id="gnd" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#5c3a0a"/>
      <stop offset="100%" stop-color="#2e1c04"/>
    </linearGradient>
    <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ffe066" stop-opacity="0.9"/>
      <stop offset="60%"  stop-color="#f0a500" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#f0a500" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Sky -->
  <rect width="1400" height="900" fill="url(#sky)"/>

  <!-- Horizon warm glow -->
  <ellipse cx="700" cy="620" rx="700" ry="160"
    fill="#c85a00" opacity="0.18">
    <animate attributeName="opacity" values="0.15;0.25;0.15" dur="8s" repeatCount="indefinite"/>
  </ellipse>

  <!-- Sun -->
  <circle cx="1150" cy="130" r="80" fill="url(#sunGlow)" opacity="0.8">
    <animate attributeName="r" values="80;92;80" dur="5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="1150" cy="130" r="44" fill="#ffe066" opacity="0.55">
    <animate attributeName="opacity" values="0.5;0.75;0.5" dur="3.5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="1150" cy="130" r="26" fill="#fff5a0" opacity="0.85"/>

  <!-- Sun rays -->
  <g stroke="#ffe066" stroke-width="1.5" opacity="0.25">
    <line x1="1150" y1="40"  x2="1150" y2="20"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="2s" repeatCount="indefinite"/></line>
    <line x1="1150" y1="220" x2="1150" y2="240"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="2.3s" repeatCount="indefinite"/></line>
    <line x1="1060" y1="130" x2="1040" y2="130"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="1.8s" repeatCount="indefinite"/></line>
    <line x1="1240" y1="130" x2="1260" y2="130"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="2.1s" repeatCount="indefinite"/></line>
    <line x1="1086" y1="66"  x2="1072" y2="52"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="1.9s" repeatCount="indefinite"/></line>
    <line x1="1214" y1="66"  x2="1228" y2="52"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="2.4s" repeatCount="indefinite"/></line>
    <line x1="1086" y1="194" x2="1072" y2="208"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="2.2s" repeatCount="indefinite"/></line>
    <line x1="1214" y1="194" x2="1228" y2="208"><animate attributeName="opacity" values="0.2;0.4;0.2" dur="1.7s" repeatCount="indefinite"/></line>
  </g>

  <!-- Clouds — warm golden tint -->
  <g opacity="0.22">
    <g><animateTransform attributeName="transform" type="translate" from="-260 0" to="1660 0" dur="65s" repeatCount="indefinite"/>
      <ellipse cx="200" cy="90"  rx="100" ry="32" fill="#f5dca0"/>
      <ellipse cx="255" cy="72"  rx="68"  ry="36" fill="#f5dca0"/>
      <ellipse cx="155" cy="80"  rx="55"  ry="28" fill="#f5dca0"/>
    </g>
    <g><animateTransform attributeName="transform" type="translate" from="300 0" to="1900 0" dur="85s" repeatCount="indefinite"/>
      <ellipse cx="620" cy="60"  rx="82"  ry="24" fill="#f0d090"/>
      <ellipse cx="665" cy="46"  rx="58"  ry="30" fill="#f0d090"/>
      <ellipse cx="578" cy="54"  rx="50"  ry="24" fill="#f0d090"/>
    </g>
    <g><animateTransform attributeName="transform" type="translate" from="-700 0" to="1400 0" dur="75s" repeatCount="indefinite"/>
      <ellipse cx="950" cy="108" rx="88"  ry="28" fill="#e8c880"/>
      <ellipse cx="998" cy="90"  rx="60"  ry="32" fill="#e8c880"/>
      <ellipse cx="905" cy="100" rx="52"  ry="26" fill="#e8c880"/>
    </g>
  </g>

  <!-- Ground -->
  <rect x="0" y="620" width="1400" height="280" fill="url(#gnd)"/>

  <!-- Ploughed rows — warm soil tones -->
  <g opacity="0.45">
    <line x1="0"    y1="900" x2="700"  y2="630" stroke="#a06820" stroke-width="3"/>
    <line x1="100"  y1="900" x2="748"  y2="630" stroke="#a06820" stroke-width="2.5"/>
    <line x1="200"  y1="900" x2="796"  y2="630" stroke="#8a5818" stroke-width="2"/>
    <line x1="300"  y1="900" x2="844"  y2="630" stroke="#8a5818" stroke-width="2"/>
    <line x1="400"  y1="900" x2="892"  y2="630" stroke="#784c14" stroke-width="1.8"/>
    <line x1="500"  y1="900" x2="940"  y2="630" stroke="#784c14" stroke-width="1.8"/>
    <line x1="600"  y1="900" x2="988"  y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="700"  y1="900" x2="1036" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="800"  y1="900" x2="1084" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="900"  y1="900" x2="1132" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="1000" y1="900" x2="1180" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="1100" y1="900" x2="1228" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="1200" y1="900" x2="1276" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="1300" y1="900" x2="1324" y2="630" stroke="#664010" stroke-width="1.5"/>
    <line x1="1400" y1="900" x2="1372" y2="630" stroke="#664010" stroke-width="1.5"/>
  </g>

  <!-- Wheat stalks — golden amber colour -->
  <!-- Left foreground cluster -->
  <g>
    <g transform="translate(30,572)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;3 7 70;0 7 70;-2 7 70;0 7 70" dur="3.2s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#c8960a" stroke-width="2.2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#d4a010" transform="rotate(-12,7,0)"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#c89008" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#c89008" transform="rotate(-22,11,21)"/>
    </g>
    <g transform="translate(62,567)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;-2 7 70;0 7 70;3 7 70;0 7 70" dur="2.7s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#c8960a" stroke-width="2.2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#d4a010" transform="rotate(8,7,0)"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#c89008" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#c89008" transform="rotate(-22,11,21)"/>
    </g>
    <g transform="translate(94,576)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;2 7 70;0 7 70;-3 7 70;0 7 70" dur="3.6s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#c8960a" stroke-width="2.2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#d4a010" transform="rotate(-5,7,0)"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#c89008" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#c89008" transform="rotate(-22,11,21)"/>
    </g>
    <g transform="translate(126,570)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;-3 7 70;0 7 70;2 7 70;0 7 70" dur="3.0s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#b88008" stroke-width="2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#c89008" transform="rotate(14,7,0)"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#b87808" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#b87808" transform="rotate(-22,11,21)"/>
    </g>
  </g>

  <!-- Right foreground cluster -->
  <g>
    <g transform="translate(1250,575)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;2 7 70;0 7 70;-3 7 70;0 7 70" dur="3.1s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#c8960a" stroke-width="2.2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#d4a010"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#c89008" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#c89008" transform="rotate(-22,11,21)"/>
    </g>
    <g transform="translate(1282,568)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;-3 7 70;0 7 70;2 7 70;0 7 70" dur="2.9s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#c8960a" stroke-width="2.2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#d4a010"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#c89008" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#c89008" transform="rotate(-22,11,21)"/>
    </g>
    <g transform="translate(1314,578)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;3 7 70;0 7 70;-2 7 70;0 7 70" dur="3.4s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#c8960a" stroke-width="2.2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#d4a010"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#c89008" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#c89008" transform="rotate(-22,11,21)"/>
    </g>
    <g transform="translate(1346,572)">
      <animateTransform attributeName="transform" type="rotate" values="0 7 70;-2 7 70;0 7 70;3 7 70;0 7 70" dur="2.6s" repeatCount="indefinite"/>
      <line x1="7" y1="90" x2="7" y2="0" stroke="#b88008" stroke-width="2"/>
      <ellipse cx="7"  cy="0"  rx="4" ry="11" fill="#c89008"/>
      <ellipse cx="3"  cy="16" rx="3" ry="8"  fill="#b87808" transform="rotate(22,3,16)"/>
      <ellipse cx="11" cy="21" rx="3" ry="8"  fill="#b87808" transform="rotate(-22,11,21)"/>
    </g>
  </g>

  <!-- Trees — warm autumn tones -->
  <g opacity="0.55">
    <rect x="18" y="538" width="11" height="84" fill="#5c3410"/>
    <ellipse cx="24" cy="528" rx="30" ry="36" fill="#7a4c10"/>
    <ellipse cx="24" cy="516" rx="22" ry="27" fill="#9a6418"/>
    <ellipse cx="24" cy="508" rx="15" ry="18" fill="#c8881e"/>

    <rect x="1358" y="542" width="11" height="80" fill="#5c3410"/>
    <ellipse cx="1364" cy="532" rx="28" ry="34" fill="#7a4c10"/>
    <ellipse cx="1364" cy="520" rx="20" ry="25" fill="#9a6418"/>
    <ellipse cx="1364" cy="512" rx="14" ry="17" fill="#c8881e"/>
  </g>

  <!-- Tractor — warmer colour palette -->
  <g>
    <animateTransform attributeName="transform" type="translate"
      from="-180 0" to="1580 0" dur="30s" repeatCount="indefinite"/>
    <g transform="translate(0,648)">
      <!-- Body -->
      <rect x="0"  y="-30" width="72" height="30" rx="4" fill="#a04010"/>
      <!-- Cab -->
      <rect x="36" y="-54" width="36" height="24" rx="3" fill="#c05018"/>
      <!-- Window -->
      <rect x="41" y="-50" width="13" height="14" rx="2" fill="#aed6f1" opacity="0.75"/>
      <!-- Exhaust -->
      <rect x="64" y="-64" width="5" height="16" rx="2" fill="#666"/>
      <!-- Smoke -->
      <circle cx="66" cy="-68" r="4" fill="#ccc" opacity="0.45">
        <animate attributeName="cy" values="-68;-84;-68" dur="1.1s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.45;0;0.45" dur="1.1s" repeatCount="indefinite"/>
        <animate attributeName="r"  values="4;7;4"         dur="1.1s" repeatCount="indefinite"/>
      </circle>
      <!-- Big wheel -->
      <circle cx="18" cy="0" r="21" fill="#2c1a08"/>
      <circle cx="18" cy="0" r="14" fill="#3d2810"/>
      <circle cx="18" cy="0" r="5"  fill="#886644"/>
      <!-- Tyre treads -->
      <line x1="18" y1="-21" x2="18" y2="-14" stroke="#886644" stroke-width="1.5"/>
      <line x1="18" y1="14"  x2="18" y2="21"  stroke="#886644" stroke-width="1.5"/>
      <line x1="-3" y1="0"   x2="3"  y2="0"   stroke="#886644" stroke-width="1.5"/>
      <line x1="33" y1="0"   x2="39" y2="0"   stroke="#886644" stroke-width="1.5"/>
      <!-- Front wheel -->
      <circle cx="62" cy="4" r="14" fill="#2c1a08"/>
      <circle cx="62" cy="4" r="9"  fill="#3d2810"/>
      <circle cx="62" cy="4" r="3"  fill="#886644"/>
      <!-- Plough -->
      <line x1="-22" y1="-6" x2="0" y2="-6" stroke="#aaa" stroke-width="2.5"/>
      <line x1="-22" y1="-6" x2="-24" y2="8" stroke="#aaa" stroke-width="2"/>
      <line x1="-17" y1="-6" x2="-19" y2="8" stroke="#aaa" stroke-width="2"/>
      <line x1="-12" y1="-6" x2="-14" y2="8" stroke="#aaa" stroke-width="2"/>
      <!-- Dust -->
      <ellipse cx="-32" cy="2" rx="16" ry="7" fill="#8b6420" opacity="0.3">
        <animate attributeName="rx" values="16;26;16" dur="0.9s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.3;0.05;0.3" dur="0.9s" repeatCount="indefinite"/>
      </ellipse>
    </g>
  </g>

  <!-- Land boundary plots — golden dashes -->
  <g opacity="0.22" fill="none" stroke="#d4a020" stroke-width="1.5" stroke-dasharray="7,4">
    <rect x="180" y="642" width="160" height="78" rx="2"/>
    <rect x="360" y="637" width="200" height="88" rx="2"/>
    <rect x="580" y="641" width="140" height="82" rx="2"/>
    <rect x="740" y="639" width="180" height="86" rx="2"/>
    <rect x="940" y="643" width="150" height="80" rx="2"/>
    <rect x="1110" y="638" width="165" height="87" rx="2"/>
  </g>

  <!-- Location pins — amber tones -->
  <g>
    <g transform="translate(258,640)" opacity="0.5">
      <circle cx="0" cy="-15" r="9" fill="#e8a020"/>
      <polygon points="-6,-8 6,-8 0,4" fill="#e8a020"/>
      <circle cx="0" cy="-15" r="4" fill="white"/>
      <animate attributeName="opacity" values="0.4;0.75;0.4" dur="2.1s" repeatCount="indefinite"/>
    </g>
    <g transform="translate(460,636)" opacity="0.5">
      <circle cx="0" cy="-15" r="9" fill="#d4601a"/>
      <polygon points="-6,-8 6,-8 0,4" fill="#d4601a"/>
      <circle cx="0" cy="-15" r="4" fill="white"/>
      <animate attributeName="opacity" values="0.4;0.75;0.4" dur="2.7s" repeatCount="indefinite"/>
    </g>
    <g transform="translate(648,640)" opacity="0.5">
      <circle cx="0" cy="-15" r="9" fill="#f0c030"/>
      <polygon points="-6,-8 6,-8 0,4" fill="#f0c030"/>
      <circle cx="0" cy="-15" r="4" fill="white"/>
      <animate attributeName="opacity" values="0.4;0.75;0.4" dur="1.9s" repeatCount="indefinite"/>
    </g>
    <g transform="translate(828,638)" opacity="0.5">
      <circle cx="0" cy="-15" r="9" fill="#e87018"/>
      <polygon points="-6,-8 6,-8 0,4" fill="#e87018"/>
      <circle cx="0" cy="-15" r="4" fill="white"/>
      <animate attributeName="opacity" values="0.4;0.75;0.4" dur="3.1s" repeatCount="indefinite"/>
    </g>
    <g transform="translate(1013,642)" opacity="0.5">
      <circle cx="0" cy="-15" r="9" fill="#c8501a"/>
      <polygon points="-6,-8 6,-8 0,4" fill="#c8501a"/>
      <circle cx="0" cy="-15" r="4" fill="white"/>
      <animate attributeName="opacity" values="0.4;0.75;0.4" dur="2.4s" repeatCount="indefinite"/>
    </g>
  </g>

  <!-- Birds -->
  <g opacity="0.28" stroke="#f5dca0" stroke-width="1.5" fill="none">
    <g>
      <animateTransform attributeName="transform" type="translate"
        from="-100 0" to="1500 -70" dur="24s" repeatCount="indefinite"/>
      <path d="M0,300 Q6,294 12,300"/>
      <path d="M16,298 Q22,292 28,298"/>
      <path d="M32,302 Q38,296 44,302"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="translate"
        from="-300 0" to="1500 -50" dur="32s" repeatCount="indefinite"/>
      <path d="M0,380 Q5,375 10,380"/>
      <path d="M14,377 Q19,372 24,377"/>
    </g>
  </g>

  <!-- Irrigation canal — amber water -->
  <g transform="translate(0,732)" opacity="0.22">
    <rect x="0" y="0" width="1400" height="16" fill="#8b5a0a"/>
    <ellipse cx="250" cy="8" rx="70" ry="5" fill="#d4900a" opacity="0.5">
      <animate attributeName="rx" values="70;100;70" dur="3.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0.1;0.5" dur="3.2s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="750" cy="8" rx="90" ry="5" fill="#d4900a" opacity="0.5">
      <animate attributeName="rx" values="90;120;90" dur="4.1s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0.1;0.5" dur="4.1s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="1150" cy="8" rx="75" ry="5" fill="#d4900a" opacity="0.5">
      <animate attributeName="rx" values="75;105;75" dur="3.7s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0.1;0.5" dur="3.7s" repeatCount="indefinite"/>
    </ellipse>
  </g>

</svg>
</div>
""", unsafe_allow_html=True)

# ── Session state ───────────────────────────────────────────────────────────────
for key, default in [
    ("logged_in", False), ("phone", ""), ("otp_sent", False),
    ("otp_verified", False), ("dev_otp", ""), ("all_points_df", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

@st.cache_resource(show_spinner="Loading AI model…")
def load_model():
    return train_model(force_retrain=False)
load_model()


# ══════════════════════════════════════════════════════════════════════════════
# LOGGED IN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in:
    user = get_user(st.session_state.phone)
    role = user.get("role", "")

    st.markdown(f"""
    <div style='background:rgba(26,10,0,0.72);backdrop-filter:blur(12px);
         border:1px solid rgba(212,160,40,0.3);border-radius:12px;
         padding:12px 20px;margin-bottom:16px;
         display:flex;align-items:center;gap:12px;position:relative;z-index:2'>
      <span style='font-size:28px'>🌾</span>
      <div>
        <span style='color:white;font-weight:700;font-size:16px'>
          AgriLand Value Intelligence
        </span>
        <span style='color:rgba(255,255,255,0.35);font-size:13px'> &nbsp;|&nbsp; </span>
        <span style='color:#d4a020;font-size:13px'>
          {'🌾 Farmer' if role=='Farmer' else '🏡 Buyer'} — {user.get('name','')}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, lc = st.columns([8, 1])
    with lc:
        if st.button("🚪 Logout"):
            for k in ["logged_in","phone","otp_sent","otp_verified","dev_otp","all_points_df"]:
                st.session_state[k] = (
                    False if k in ["logged_in","otp_sent","otp_verified"]
                    else "" if k in ["phone","dev_otp"] else None)
            st.rerun()

    if role == "Farmer":
        show_farmer_page()
    elif role == "Buyer":
        show_buyer_page()
    else:
        st.error("Unknown role. Please logout and login again.")


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div style='text-align:center;padding:38px 20px 22px;position:relative;z-index:2'>
      <div style='display:inline-block;background:rgba(212,160,32,0.15);
           border:2px solid rgba(212,160,32,0.45);border-radius:50%;
           width:82px;height:82px;line-height:82px;font-size:44px;
           box-shadow:0 0 28px rgba(212,160,32,0.35)'>🌾</div>
      <h1 style='color:white;font-size:30px;font-weight:700;
           margin:14px 0 6px;text-shadow:0 2px 14px rgba(0,0,0,0.6)'>
        AgriLand Value Intelligence
      </h1>
      <p style='color:rgba(255,240,180,0.5);font-size:14px;margin:0'>
        Ludhiana District &nbsp;·&nbsp; AI-Powered Agricultural Land Valuation
      </p>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])
    with center:
        card = ("background:rgba(20,10,0,0.68);backdrop-filter:blur(20px);"
                "border:1px solid rgba(212,160,40,0.22);border-radius:20px;"
                "padding:32px 28px;box-shadow:0 8px 40px rgba(0,0,0,0.45);"
                "position:relative;z-index:2;margin-top:4px")

        # Step 1 ───────────────────────────────────────────────────────────────
        if not st.session_state.otp_sent:
            st.markdown(f"""
            <div style='{card}'>
              <div style='text-align:center;margin-bottom:22px'>
                <div style='font-size:38px'>📱</div>
                <h3 style='color:white;margin:8px 0 4px;font-size:19px'>Login / Register</h3>
                <p style='color:rgba(255,240,180,0.45);font-size:13px;margin:0'>
                  Enter your mobile number to get started
                </p>
              </div>
            </div>""", unsafe_allow_html=True)
            phone = st.text_input("Mobile Number", placeholder="e.g. 9876543210", max_chars=10)
            st.caption("10-digit number without country code")
            if st.button("📲 Send OTP"):
                phone = phone.strip()
                if len(phone) != 10 or not phone.isdigit():
                    st.error("Please enter a valid 10-digit mobile number")
                else:
                    otp = generate_otp(phone)
                    st.session_state.phone    = phone
                    st.session_state.otp_sent = True
                    st.session_state.dev_otp  = otp
                    st.rerun()

        # Step 2 ───────────────────────────────────────────────────────────────
        elif st.session_state.otp_sent and not st.session_state.otp_verified:
            st.markdown(f"""
            <div style='{card}'>
              <div style='text-align:center;margin-bottom:22px'>
                <div style='font-size:38px'>🔐</div>
                <h3 style='color:white;margin:8px 0 4px;font-size:19px'>Enter OTP</h3>
                <p style='color:rgba(255,240,180,0.45);font-size:13px;margin:0'>
                  Sent to <b style='color:#d4a020'>+91 {st.session_state.phone}</b>
                </p>
              </div>
            </div>""", unsafe_allow_html=True)
            st.info(f"🧪 **Demo OTP:** `{st.session_state.dev_otp}` *(SMS in production)*")
            otp_input = st.text_input("6-digit OTP", max_chars=6, placeholder="e.g. 482910")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Verify OTP"):
                    if verify_otp(st.session_state.phone, otp_input):
                        st.session_state.otp_verified = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid or expired OTP.")
            with c2:
                if st.button("🔄 Resend OTP"):
                    otp = generate_otp(st.session_state.phone)
                    st.session_state.dev_otp = otp
                    st.success("New OTP sent!")
                    st.rerun()
            if st.button("← Change Number"):
                st.session_state.otp_sent = False
                st.session_state.phone    = ""
                st.rerun()

        # Step 3 ───────────────────────────────────────────────────────────────
        elif st.session_state.otp_verified:
            phone = st.session_state.phone
            if is_registered(phone):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.markdown(f"""
                <div style='{card}'>
                  <div style='text-align:center;margin-bottom:22px'>
                    <div style='font-size:38px'>👤</div>
                    <h3 style='color:white;margin:8px 0 4px;font-size:19px'>
                      Complete Your Profile
                    </h3>
                    <p style='color:rgba(255,240,180,0.45);font-size:13px;margin:0'>
                      One last step
                    </p>
                  </div>
                </div>""", unsafe_allow_html=True)

                name = st.text_input("Your Full Name", placeholder="e.g. Gurpreet Singh")
                st.markdown("<p style='color:rgba(255,240,180,0.7);font-size:14px;"
                            "margin:14px 0 8px'>I am a…</p>", unsafe_allow_html=True)

                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown("""
                    <div style='background:rgba(212,160,32,0.1);
                         border:1px solid rgba(212,160,32,0.4);
                         border-radius:14px;padding:16px;text-align:center;margin-bottom:8px'>
                      <svg width="58" height="58" viewBox="0 0 58 58">
                        <rect width="58" height="58" rx="29" fill="rgba(212,160,32,0.18)"/>
                        <line x1="29" y1="50" x2="29" y2="10" stroke="#d4a020" stroke-width="2.5"/>
                        <ellipse cx="29" cy="10" rx="5" ry="11" fill="#d4a020" transform="rotate(-10,29,10)"/>
                        <ellipse cx="23" cy="22" rx="3.5" ry="8" fill="#c89010" transform="rotate(24,23,22)"/>
                        <ellipse cx="35" cy="26" rx="3.5" ry="8" fill="#c89010" transform="rotate(-24,35,26)"/>
                        <line x1="16" y1="50" x2="42" y2="50" stroke="#a06820" stroke-width="2.5"/>
                      </svg>
                      <div style='color:white;font-weight:600;margin-top:10px;font-size:14px'>
                        Farmer
                      </div>
                      <div style='color:rgba(255,240,180,0.45);font-size:11px;margin-top:3px'>
                        Value my land
                      </div>
                    </div>""", unsafe_allow_html=True)
                    farmer_btn = st.button("Select — Farmer", use_container_width=True, key="fb")

                with rc2:
                    st.markdown("""
                    <div style='background:rgba(200,80,20,0.1);
                         border:1px solid rgba(200,80,20,0.4);
                         border-radius:14px;padding:16px;text-align:center;margin-bottom:8px'>
                      <svg width="58" height="58" viewBox="0 0 58 58">
                        <rect width="58" height="58" rx="29" fill="rgba(200,80,20,0.18)"/>
                        <rect x="14" y="32" width="26" height="18" rx="2" fill="#c05018"/>
                        <polygon points="12,32 29,16 46,32" fill="#e06828"/>
                        <rect x="24" y="40" width="9" height="10" rx="1" fill="#8b3410"/>
                        <circle cx="42" cy="20" r="7" fill="#e87820"/>
                        <polygon points="38,25 46,25 42,33" fill="#e87820"/>
                        <circle cx="42" cy="20" r="3" fill="white"/>
                      </svg>
                      <div style='color:white;font-weight:600;margin-top:10px;font-size:14px'>
                        Buyer
                      </div>
                      <div style='color:rgba(255,240,180,0.45);font-size:11px;margin-top:3px'>
                        Explore land prices
                      </div>
                    </div>""", unsafe_allow_html=True)
                    buyer_btn = st.button("Select — Buyer", use_container_width=True, key="bb")

                role = "Farmer" if farmer_btn else ("Buyer" if buyer_btn else None)
                if role:
                    if not name.strip():
                        st.error("Please enter your name first")
                    else:
                        register_user(phone, name.strip(), role)
                        st.session_state.logged_in = True
                        st.rerun()

    st.markdown("""
    <div style='text-align:center;padding:28px 0 12px;position:relative;z-index:2'>
      <p style='color:rgba(255,240,180,0.18);font-size:11px;margin:0'>
        AgriLand Value Intelligence &nbsp;·&nbsp; Ludhiana District, Punjab
        &nbsp;·&nbsp; Random Forest ML · SoilGrids · MODIS Irrigation
      </p>
    </div>""", unsafe_allow_html=True)
