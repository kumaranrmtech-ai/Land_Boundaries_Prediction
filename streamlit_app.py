"""
Land Boundary Prediction System — Frontend
=============================================
High-Contrast Dashboard with Animated Floating Particles background.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
import streamlit as st
from fpdf import FPDF
import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "Land Boundary AI"
APP_VERSION = "v1.0.0"
API_BASE_URL = "http://127.0.0.1:8000"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
HEALTH_ENDPOINT = f"{API_BASE_URL}/"

REQUEST_TIMEOUT_SECONDS = 10
HEALTH_TIMEOUT_SECONDS = 3

MAX_AREA_SQFT = 10_000_000.0
MIN_AREA_SQFT = 1.0

CSS_FILE_PATH = Path(__file__).parent / "style.css"


# ============================================================
# PAGE CONFIG & STYLING
# ============================================================

st.set_page_config(
    page_title="Land Boundary Prediction System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(css_path: Path) -> None:
    """Load external stylesheet."""
    if css_path.exists():
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_video_base64(video_path: str) -> str:
    """Convert local video file to base64 string once per session."""
    path = Path(video_path)
    if path.exists():
        video_bytes = path.read_bytes()
        return base64.b64encode(video_bytes).decode("utf-8")
    return ""


def render_animated_background() -> None:
    video_b64 = get_video_base64("static/bg_video.mp4")

    if video_b64:
        video_src = f"data:video/mp4;base64,{video_b64}"
    else:
        video_src = "https://assets.mixkit.co/videos/preview/mixkit-abstract-purple-and-blue-lights-31802-large.mp4"

    st.markdown(
        f"""
        <!-- Background Video -->
        <video autoplay muted loop playsinline id="bg-video">
            <source src="{video_src}" type="video/mp4">
        </video>

        <!-- Ultra-Smooth Slow-Mo Controller Script -->
        <script>
            (function() {{
                const bgVid = document.getElementById('bg-video');
                if (bgVid) {{
                    // Set smooth target speed
                    bgVid.playbackRate = 0.15;
                    
                    // Force GPU hardware decoding
                    bgVid.addEventListener('play', () => {{
                        bgVid.style.transform = 'translateZ(0)';
                    }});
                }}
            }})();
        </script>

        <!-- Floating Particles Layer -->
        <ul class="bg-bubbles">
            <li class="bubble"></li>
            <li class="sparkle"></li>
            <li class="diamond"></li>
            <li class="bubble"></li>
            <li class="sparkle"></li>
            <li class="diamond"></li>
            <li class="bubble"></li>
            <li class="sparkle"></li>
            <li class="bubble"></li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
# ============================================================
# SESSION STATE & HANDLERS
# ============================================================

def init_session_state() -> None:
    """Initialize session state keys before widgets render."""
    defaults: Dict[str, Any] = {
        "prediction_result": None,
        "prediction_timestamp": None,
        "prediction_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "survey_no_input" not in st.session_state:
        st.session_state["survey_no_input"] = ""
    if "area_sqft_input" not in st.session_state:
        st.session_state["area_sqft_input"] = 1000.0
    if "land_shape_input" not in st.session_state:
        st.session_state["land_shape_input"] = "Other / Unknown"


def handle_reset() -> None:
    """Safely reset session state without Streamlit errors."""
    st.session_state["prediction_result"] = None
    st.session_state["prediction_timestamp"] = None
    st.session_state["prediction_error"] = None

    st.session_state["survey_no_input"] = ""
    st.session_state["area_sqft_input"] = 1000.0
    st.session_state["land_shape_input"] = "Other / Unknown"


# ============================================================
# API HELPERS
# ============================================================

@st.cache_data(ttl=15, show_spinner=False)
def get_api_status() -> Tuple[bool, str]:
    """Check health of FastAPI backend."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=HEALTH_TIMEOUT_SECONDS)
        if response.status_code == 200:
            payload = response.json()
            return True, payload.get("status", "Running")
        return False, f"HTTP {response.status_code}"
    except Exception:
        return False, "Unreachable"


def validate_inputs(survey_no: str, area_sqft: float) -> Tuple[bool, str]:
    """Validate user inputs."""
    survey_no_clean = survey_no.strip()

    if not survey_no_clean:
        return False, "Survey number is required."

    if len(survey_no_clean) > 50:
        return False, "Survey number must be under 50 characters."

    if area_sqft is None or area_sqft < MIN_AREA_SQFT:
        return False, f"Total area must be at least {MIN_AREA_SQFT} sq.ft."

    if area_sqft > MAX_AREA_SQFT:
        return False, f"Total area must not exceed {MAX_AREA_SQFT:,.0f} sq.ft."

    return True, ""


def call_predict_api(
    survey_no: str, area_sqft: float, land_shape: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Call FastAPI backend endpoint."""
    payload = {
        "survey_no": survey_no.strip(),
        "area_sqft": area_sqft,
        "land_shape": land_shape,
    }

    try:
        response = requests.post(PREDICT_ENDPOINT, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json(), None
    except Exception as exc:
        return None, f"Error: {exc}"


# ============================================================
# REPORT BUILDERS
# ============================================================

def build_txt_report(data: Dict[str, Any], timestamp: str) -> str:
    """Build text report."""
    return (
        "LAND BOUNDARY PREDICTION REPORT\n"
        "================================\n\n"
        f"Survey Number     : {data['survey_no']}\n"
        f"Land Shape        : {data.get('land_shape', 'Other / Unknown')}\n"
        f"Total Area        : {data['area_sqft']} Sq.ft\n\n"
        f"North Boundary    : {data['north_ft']} ft\n"
        f"South Boundary    : {data['south_ft']} ft\n"
        f"East Boundary     : {data['east_ft']} ft\n"
        f"West Boundary     : {data['west_ft']} ft\n\n"
        f"Calculated Area   : {data['calculated_area_sqft']} Sq.ft\n\n"
        "Prediction Status : Completed Successfully\n"
        f"Generated On      : {timestamp}\n"
    )


def build_pdf_report(data: Dict[str, Any], timestamp: str) -> bytes:
    """Build PDF report."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_fill_color(139, 47, 201)
    pdf.rect(0, 0, 210, 28, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(12, 8)
    pdf.cell(0, 10, "Land Boundary Prediction Report", ln=1)

    pdf.set_text_color(15, 23, 42)
    pdf.ln(18)

    rows = [
        ("Survey Number", str(data["survey_no"])),
        ("Land Shape", str(data.get("land_shape", "Other / Unknown"))),
        ("Total Area", f"{data['area_sqft']} Sq.ft"),
        ("North Boundary", f"{data['north_ft']} ft"),
        ("South Boundary", f"{data['south_ft']} ft"),
        ("East Boundary", f"{data['east_ft']} ft"),
        ("West Boundary", f"{data['west_ft']} ft"),
        ("Calculated Area", f"{data['calculated_area_sqft']} Sq.ft"),
        ("Prediction Status", "Completed Successfully"),
        ("Generated On", timestamp),
    ]

    for label, value in rows:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(70, 10, label, border="B")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(139, 47, 201)
        pdf.cell(0, 10, value, border="B", ln=1)

    raw_output = pdf.output(dest="S")
    if isinstance(raw_output, str):
        return raw_output.encode("latin-1")
    return bytes(raw_output)


# ============================================================
# UI RENDER FUNCTIONS
# ============================================================

def render_sidebar() -> None:
    """Render sidebar navigation and status."""
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">📐 Land Boundary AI</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.8rem; color:#CBD5E1; margin-bottom:20px;">AI Spatial Intelligence Engine</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-nav-item active">🏠 Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-nav-item">📄 History Logs</div>', unsafe_allow_html=True)

        st.write("---")

        is_online, _ = get_api_status()
        dot_class = "online" if is_online else "offline"
        status_label = "Online" if is_online else "Offline"

        st.markdown(
            f'<div style="display:flex; justify-space-between; font-size:0.85rem; color:#CBD5E1;">'
            f'<span>API Server</span>'
            f'<span><span class="status-dot {dot_class}"></span> {status_label}</span></div>',
            unsafe_allow_html=True,
        )


def render_header() -> None:
    """Render top hero header."""
    with st.container(border=True):
        st.markdown('<div class="hero-badge">⚡ Live Spatial API Connected</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Land Boundary Prediction System</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-subtitle">'
            'A professional prediction dashboard that estimates North, South, East, and West boundary lengths '
            'of a land parcel from its survey number and total area.'
            '</div>',
            unsafe_allow_html=True,
        )


def render_input_section() -> Tuple[bool, bool]:
    """Render input form inside native card."""
    with st.container(border=True):
        st.markdown('<div class="step-eyebrow">STEP 1</div>', unsafe_allow_html=True)
        st.markdown('<div class="step-title">Enter Land Details</div>', unsafe_allow_html=True)

        st.text_input(
            "Survey Number",
            key="survey_no_input",
            placeholder="e.g., 123/4A",
            help="Enter property survey number.",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox(
                "Land Shape",
                ["Square", "Rectangular", "Other / Unknown"],
                key="land_shape_input",
            )
        with col2:
            st.number_input(
                "Total Area (Sq.ft)",
                key="area_sqft_input",
                min_value=0.0,
                step=10.0,
                format="%.2f",
            )

        st.write("")
        btn_col1, btn_col2, _ = st.columns([1.2, 1, 2])
        with btn_col1:
            predict_clicked = st.button("🚀 Predict", type="primary", use_container_width=True)
        with btn_col2:
            reset_clicked = st.button(
                "♻️ Reset",
                type="secondary",
                use_container_width=True,
                on_click=handle_reset,
            )

    return predict_clicked, reset_clicked


def render_metric_tiles(data: Dict[str, Any]) -> None:
    """Render boundary metrics."""
    st.markdown(
        f"""
        <div class="tile-grid">
            <div class="metric-tile">
                <div class="metric-icon">⬆️</div>
                <div class="metric-label">North Boundary</div>
                <div class="metric-value">{data['north_ft']} <span style="font-size:0.9rem;">ft</span></div>
            </div>
            <div class="metric-tile">
                <div class="metric-icon">⬇️</div>
                <div class="metric-label">South Boundary</div>
                <div class="metric-value">{data['south_ft']} <span style="font-size:0.9rem;">ft</span></div>
            </div>
            <div class="metric-tile">
                <div class="metric-icon">➡️</div>
                <div class="metric-label">East Boundary</div>
                <div class="metric-value">{data['east_ft']} <span style="font-size:0.9rem;">ft</span></div>
            </div>
            <div class="metric-tile">
                <div class="metric-icon">⬅️</div>
                <div class="metric-label">West Boundary</div>
                <div class="metric-value">{data['west_ft']} <span style="font-size:0.9rem;">ft</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def compute_plot_dimensions(data: Dict[str, Any]) -> Tuple[int, int]:
    """Calculate dimensions for diagram rendering."""
    width_ft = (float(data["north_ft"]) + float(data["south_ft"])) / 2
    height_ft = (float(data["east_ft"]) + float(data["west_ft"])) / 2

    max_px, min_px = 320.0, 120.0
    if width_ft <= 0 or height_ft <= 0:
        return int(min_px), int(min_px)

    aspect_ratio = width_ft / height_ft
    if aspect_ratio >= 1:
        box_width = max_px
        box_height = max_px / aspect_ratio
    else:
        box_height = max_px
        box_width = max_px * aspect_ratio

    return int(max(min_px, min(max_px, box_width))), int(max(min_px, min(max_px, box_height)))


def render_land_visualization(data: Dict[str, Any]) -> None:
    """Render boundary diagram."""
    with st.container(border=True):
        st.markdown('<div class="step-title" style="text-align:center;">🧭 Boundary Diagram</div>', unsafe_allow_html=True)
        box_width_px, box_height_px = compute_plot_dimensions(data)

        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:0.85rem; font-weight:800; color:#00F2A1; letter-spacing:1px;">NORTH</div>
                <div style="font-size:1.1rem; font-weight:800; color:#FFFFFF;">{data['north_ft']} ft</div>
                <br>
                <table style="width:100%; text-align:center; border-collapse:collapse;">
                    <tr>
                        <td style="width:25%;">
                            <div style="font-size:0.85rem; font-weight:800; color:#00F2A1; letter-spacing:1px;">WEST</div>
                            <div style="font-size:1.1rem; font-weight:800; color:#FFFFFF;">{data['west_ft']} ft</div>
                        </td>
                        <td style="width:50%;">
                            <div style="width:{box_width_px}px; height:{box_height_px}px; margin:0 auto; border:2px dashed #00F2A1; background:rgba(0, 242, 161, 0.08); border-radius:14px; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:800; color:#00F2A1;">
                                <span style="font-size:0.85rem; color:#A855F7;">Area</span>
                                <span style="font-size:1rem; color:#FFFFFF; font-weight:800;">{data['calculated_area_sqft']} Sq.ft</span>
                            </div>
                        </td>
                        <td style="width:25%;">
                            <div style="font-size:0.85rem; font-weight:800; color:#00F2A1; letter-spacing:1px;">EAST</div>
                            <div style="font-size:1.1rem; font-weight:800; color:#FFFFFF;">{data['east_ft']} ft</div>
                        </td>
                    </tr>
                </table>
                <br>
                <div style="font-size:0.85rem; font-weight:800; color:#00F2A1; letter-spacing:1px;">SOUTH</div>
                <div style="font-size:1.1rem; font-weight:800; color:#FFFFFF;">{data['south_ft']} ft</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_report(data: Dict[str, Any], timestamp: str) -> None:
    """Render prediction summary report."""
    with st.container(border=True):
        st.markdown('<div class="step-title">📄 Summary Report</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <table style="width:100%; border-collapse:collapse; color:#FFFFFF;">
                <tr style="border-bottom:1px solid rgba(255,255,255,0.15);"><td style="padding:8px 0; color:#CBD5E1;">Survey Number</td><td style="font-weight:800; text-align:right;">{data['survey_no']}</td></tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.15);"><td style="padding:8px 0; color:#CBD5E1;">Land Shape</td><td style="font-weight:800; text-align:right;">{data.get('land_shape', 'Other / Unknown')}</td></tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.15);"><td style="padding:8px 0; color:#CBD5E1;">Total Area</td><td style="font-weight:800; text-align:right;">{data['area_sqft']} Sq.ft</td></tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.15);"><td style="padding:8px 0; color:#CBD5E1;">Calculated Area</td><td style="font-weight:800; text-align:right;">{data['calculated_area_sqft']} Sq.ft</td></tr>
            </table>
            <div style="margin-top:14px; background:rgba(0,242,161,0.15); border:1px solid #00F2A1; color:#00F2A1; padding:6px 14px; border-radius:20px; display:inline-block; font-size:0.85rem; font-weight:800;">
                ✅ Area Verified Successfully
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        txt_report = build_txt_report(data, timestamp)
        pdf_bytes = build_pdf_report(data, timestamp)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download TXT",
                data=txt_report,
                file_name=f"Report_{data['survey_no']}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "📕 Download PDF",
                data=pdf_bytes,
                file_name=f"Report_{data['survey_no']}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """App entry point."""
    load_css(CSS_FILE_PATH)
    render_animated_background()
    init_session_state()

    render_sidebar()
    render_header()

    predict_clicked, _ = render_input_section()

    if predict_clicked:
        survey_no = st.session_state["survey_no_input"]
        area_sqft = st.session_state["area_sqft_input"]
        land_shape = st.session_state["land_shape_input"]

        is_valid, validation_message = validate_inputs(survey_no, area_sqft)

        if not is_valid:
            st.session_state["prediction_result"] = None
            st.session_state["prediction_error"] = validation_message
        else:
            with st.spinner("Calculating land boundaries..."):
                result, error = call_predict_api(survey_no, area_sqft, land_shape)

            if error:
                st.session_state["prediction_result"] = None
                st.session_state["prediction_error"] = error
            else:
                st.session_state["prediction_result"] = result
                st.session_state["prediction_error"] = None
                st.session_state["prediction_timestamp"] = datetime.now().strftime("%d %b %Y, %I:%M %p")

    if st.session_state["prediction_error"]:
        st.error(st.session_state["prediction_error"])

    result = st.session_state["prediction_result"]
    if result:
        st.success("Prediction generated successfully.")
        render_metric_tiles(result)

        col_left, col_right = st.columns([1.1, 1])
        with col_left:
            render_land_visualization(result)
        with col_right:
            render_report(result, st.session_state["prediction_timestamp"])


if __name__ == "__main__":
    main()