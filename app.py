# app.py
import streamlit as st
import math
from datetime import datetime, timezone
from typing import List

from utils.tle_parser import parse_tle, parse_tle_lines
from utils.anomalies import solve_true_anomaly
from utils.time_utils import parse_epoch, build_time_array
from utils.propagate import propagate_kepler
from plots.earth_3d import build_3d_earth_orbit

st.set_page_config(page_title="Satellite Orbit Visualizer", layout="wide")

# Basic CSS for minimal dark theme
st.markdown("""
    <style>
    body { background-color: #0e1117; color: #e6eef3; }
    .card { background: #161a23; padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.04); margin-bottom: 12px; }
    h1 { font-family: Inter, sans-serif; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("🛰 Satellite Orbit Visualizer")
st.markdown(
    """
    <p style='color:#aaa; font-size:14px; margin-top:-12px;'>
        <span style="font-weight:200;">Created by </span>
        <span style="font-weight:500;">Satyaditya </span><span style="font-weight:999;">Akhandam</span>
        <span style="font-weight:200;"> & </span>
        <span style="font-weight:500;">Jayasheel </span><span style="font-weight:999;">Siram</span>
    </p>
    """,
    unsafe_allow_html=True
)

# Sidebar: Input and options
st.sidebar.header("Input")
input_mode = st.sidebar.selectbox("Input method", ["Paste TLE text", "Upload file (.txt)"])
tle_text = ""
if input_mode == "Paste TLE text":
    tle_text = st.sidebar.text_area("Paste TLE (2 lines). Optional name line above.", height=140)
else:
    uploaded = st.sidebar.file_uploader("Upload TLE .txt", type=["txt"])
    if uploaded:
        tle_text = uploaded.read().decode("utf-8")

st.sidebar.markdown("<br><br><hr>", unsafe_allow_html=True)
debug = st.sidebar.checkbox("Show debug info", False)

# Visualization options
st.sidebar.header("Visualization")
do_visualize = st.sidebar.button("Visualize orbit (Kepler-only)")
numdays = st.sidebar.slider("Propagate days", min_value=0.1, max_value=30.0, value=1.0, step=0.1)
sample_seconds = st.sidebar.number_input("Sample interval (s)", min_value=10, max_value=3600, value=10, step=10)

# If no input, show usage
if not tle_text or tle_text.strip() == "":
    st.info("Paste or upload a TLE to begin. Example sample.tle included.")
    st.stop()

# Accept multiple satellites; parse first if multiple
triples = parse_tle_lines(tle_text)
if len(triples) == 0:
    st.error("No valid TLE found. Ensure lines start with '1 ' and '2 '.")
    st.stop()

# For now, allow user to select which satellite if multiple
if len(triples) > 1:
    names = [t[0] for t in triples]
    chosen = st.sidebar.selectbox("Select satellite", names)
    idx = names.index(chosen)
    name, l1, l2 = triples[idx]
else:
    name, l1, l2 = triples[0]

# Parse the single TLE
data = parse_tle(l1, l2)

# extract values
inc_deg = data["inclination"]
raan_deg = data["raan"]
ecc = data["eccentricity"]
argp_deg = data["argp"]
mean_anom_deg = data["mean_anom"]
mean_motion = data["mean_motion_rev_per_day"]
sma_km = data["sma_km"]

epoch_dt = parse_epoch(data["epoch_year"], data["epoch_day"])
now_dt = datetime.now(timezone.utc)
delta_t_sec = (now_dt - epoch_dt).total_seconds()

# advance mean anomaly and compute true anomaly (like MATLAB)
# mean motion rad/s:
n_rad_s = mean_motion * 2.0 * math.pi / 86400.0
M0_rad = math.radians(mean_anom_deg)
M_now = (M0_rad + n_rad_s * delta_t_sec) % (2.0 * math.pi)
# solve for true anomaly
# using anomalies.newtonm but we can just compute solve_true_anomaly (which uses M degrees)
true_anom_deg_now = solve_true_anomaly(ecc, math.degrees(M_now))

# Display cards (3 columns)
st.markdown(f"<div class='card'><strong style='font-size:18px'>{name}</strong></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='card'><div><strong>Semi-major axis</strong></div><div>{sma_km:.6f} km</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><div><strong>Eccentricity</strong></div><div>{ecc}</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='card'><div><strong>Inclination</strong></div><div>{inc_deg}°</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><div><strong>RAAN (raw)</strong></div><div>{raan_deg}°</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='card'><div><strong>Argument of Periapsis</strong></div><div>{argp_deg}°</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><div><strong>Mean Anomaly (TLE)</strong></div><div>{mean_anom_deg}°</div></div>", unsafe_allow_html=True)

# true anomaly and epoch
st.markdown(f"<div class='card'><div><strong>True Anomaly (now)</strong></div><div>{true_anom_deg_now:.6f}°</div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='card'><div><strong>Epoch (UTC)</strong></div><div>{epoch_dt.isoformat()}</div></div>", unsafe_allow_html=True)

if debug:
    st.subheader("Parsed TLE struct")
    st.json(data)
    st.write("delta_t_sec:", delta_t_sec)
    st.write("M0 (deg):", mean_anom_deg, " M_now (deg):", math.degrees(M_now))

# Visualization: compute positions using Keplerian propagator
if do_visualize:
    st.subheader("3D Keplerian Visualization")
    # build times seconds array from 0 -> numdays*86400 step sample_seconds
    total_seconds = int(numdays * 24 * 3600)
    times_seconds = list(range(0, total_seconds+1, int(sample_seconds)))
    xs, ys, zs = propagate_kepler(sma_km, ecc, inc_deg, raan_deg, argp_deg, mean_anom_deg, mean_motion, times_seconds)
    
    # Use premium Three.js visualization by default
    build_3d_earth_orbit(xs, ys, zs, sat_name=name, premium=True)


