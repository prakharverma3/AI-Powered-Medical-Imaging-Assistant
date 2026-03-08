"""
🧠 Brain Tumor MRI Analyzer
Input  : Preprocessed .npy file  (256,256,3) float32  ← matches training exactly
         Raw image (.png/.jpg) supported but may give less accurate results
Model  : auto-loaded from same folder (.keras or .h5)
Outputs: Segmentation mask overlay + Classification confidence
"""

import io
import json
import os
import glob
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# ══════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="MRI Tumor Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

IMG_SIZE     = 256
CLASS_NAMES  = ["Glioma", "Meningioma", "Pituitary", "No Tumor"]
CLASS_COLORS = ["#E84545", "#F0A500", "#2EC4B6", "#6BCB77"]
CLASS_DESC   = [
    "Malignant brain tumor arising from glial cells.",
    "Usually benign tumor arising from the meninges.",
    "Tumor of the pituitary gland (usually benign).",
    "No detectable tumor mass found in the scan.",
]

MASK_CMAP = LinearSegmentedColormap.from_list(
    "tumor", [(0, 0, 0, 0), (0.9, 0.1, 0.1, 0.75)], N=256
)

# ══════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; background: #080C10; color: #D0D8E4; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

.hero { padding: 2.5rem 0 1.5rem; border-bottom: 1px solid #1a2030; margin-bottom: 2rem; }
.hero-tag { font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.18em; color: #2EC4B6; text-transform: uppercase; margin-bottom: 0.5rem; }
.hero-title { font-size: 2.6rem; font-weight: 800; color: #F0F4F8; line-height: 1.1; letter-spacing: -0.03em; }
.hero-title span { color: #2EC4B6; }
.hero-sub { font-size: 0.875rem; color: #445; margin-top: 0.5rem; font-weight: 300; }

.model-badge { display: inline-flex; align-items: center; gap: 0.5rem; font-family: 'DM Mono', monospace; font-size: 0.7rem; padding: 0.35rem 0.9rem; border-radius: 20px; margin-top: 0.8rem; letter-spacing: 0.06em; }
.badge-ok  { background: #0d2d1a; border: 1px solid #1e5c33; color: #6BCB77; }
.badge-err { background: #2d0d0d; border: 1px solid #5c1e1e; color: #E84545; }
.badge-dot { width: 7px; height: 7px; border-radius: 50%; }
.badge-dot-ok  { background: #6BCB77; box-shadow: 0 0 6px #6BCB77; animation: pulse 2s infinite; }
.badge-dot-err { background: #E84545; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Warning banner */
.warn-box { background: #1a1400; border: 1px solid #4a3800; border-left: 3px solid #F0A500;
            border-radius: 8px; padding: 0.9rem 1.1rem; margin: 0.8rem 0;
            font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #c8a040; line-height: 1.6; }
.warn-box b { color: #F0A500; }

/* Input type tabs */
.input-tab-row { display: flex; gap: 0.6rem; margin-bottom: 1rem; }
.input-tab { font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.1em;
             padding: 0.4rem 0.9rem; border-radius: 20px; border: 1px solid #1e3040;
             background: #0a1018; color: #445566; text-transform: uppercase; }
.input-tab-active { background: #0d2230; border-color: #2EC4B6; color: #2EC4B6; }

.upload-label { font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em; color: #4a6080; text-transform: uppercase; margin-bottom: 0.4rem; }

.pred-banner { border-radius: 10px; padding: 1.4rem 1.6rem; border-left: 4px solid; margin: 1.2rem 0; display: flex; align-items: center; gap: 1rem; }
.pred-name { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; }
.pred-desc { font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #99aabb; margin-top: 0.15rem; }

.pill-row { display: flex; gap: 0.8rem; flex-wrap: wrap; margin: 1rem 0; }
.pill { background: #0d1420; border: 1px solid #1e2d40; border-radius: 8px; padding: 0.6rem 1rem; flex: 1; min-width: 120px; }
.pill-label { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #445566; text-transform: uppercase; letter-spacing: 0.12em; }
.pill-val { font-size: 1.3rem; font-weight: 700; color: #e8f0fa; margin-top: 0.2rem; }

.prob-row { display: flex; align-items: center; gap: 0.7rem; margin: 0.45rem 0; }
.prob-name { width: 100px; font-size: 0.8rem; color: #99aabb; }
.prob-bar-bg { flex: 1; height: 7px; background: #131c28; border-radius: 4px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 4px; }
.prob-pct { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #667788; width: 42px; text-align: right; }

.sec-head { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.16em; color: #334455; text-transform: uppercase; border-bottom: 1px solid #131c28; padding-bottom: 0.4rem; margin: 1.5rem 0 1rem; }

section[data-testid="stSidebar"] { background: #060A0E; border-right: 1px solid #111820; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #2EC4B6, #1a8fa5) !important; color: #050810 !important; font-weight: 700 !important; font-size: 1rem !important; border: none !important; border-radius: 10px !important; padding: 0.7rem 2rem !important; font-family: 'Sora', sans-serif !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  MODEL LOADING
# ══════════════════════════════════════════════════════
def find_model_file():
    for pattern in [os.path.join(APP_DIR, "*.keras"), os.path.join(APP_DIR, "*.h5")]:
        matches = glob.glob(pattern)
        if matches:
            preferred = [m for m in matches if "model" in os.path.basename(m).lower()]
            return preferred[0] if preferred else matches[0]
    return None


@st.cache_resource(show_spinner=False)
def auto_load_model():
    import tensorflow as tf
    try:
        from model_utils import CUSTOM_OBJECTS
    except ImportError as e:
        return None, None, f"model_utils.py not found: {e}"

    path = find_model_file()
    if path is None:
        return None, None, "No .keras or .h5 model file found in the app folder."

    filename = os.path.basename(path)
    try:
        model = tf.keras.models.load_model(path, custom_objects=CUSTOM_OBJECTS, compile=False)
        return model, filename, None
    except Exception as e:
        return None, filename, str(e)


# ══════════════════════════════════════════════════════
#  PREPROCESSING — matching training pipeline EXACTLY
# ══════════════════════════════════════════════════════
def load_npy(file_bytes: bytes):
    """
    Load a BRISC preprocessed .npy file.
    Training pipeline: np.load(path).astype(np.float32)  — no further normalization.
    Shape must be (256,256,3).
    """
    arr = np.load(io.BytesIO(file_bytes)).astype(np.float32)   # exact match to training

    if arr.ndim == 2:
        # Grayscale .npy — stack to 3 channels
        arr = np.stack([arr, arr, arr], axis=-1)

    if arr.shape != (IMG_SIZE, IMG_SIZE, 3):
        raise ValueError(
            f"Expected shape (256, 256, 3), got {arr.shape}. "
            "Please upload a BRISC preprocessed .npy file."
        )

    return arr[np.newaxis], arr   # (1,256,256,3), (256,256,3)


def load_raw_image(file_bytes: bytes):
    """
    Load a raw MRI image (.png/.jpg).
    ⚠️  Results will differ from training because the model was trained on
    preprocessed .npy arrays, not raw images.  Use only for rough preview.
    """
    pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    pil_img = pil_img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
    arr     = np.array(pil_img, dtype=np.float32) / 255.0   # best approximation
    return arr[np.newaxis], arr


# ══════════════════════════════════════════════════════
#  INFERENCE
# ══════════════════════════════════════════════════════
def run_inference(model, x: np.ndarray):
    import tensorflow as tf
    out = model.predict(x, verbose=0)

    if isinstance(out, dict):
        seg_key = next((k for k in out if "seg" in k.lower()), list(out.keys())[0])
        cls_key = next(
            (k for k in out if "cls" in k.lower() or "class" in k.lower()),
            [k for k in out if k != seg_key][0],
        )
        seg, cls = out[seg_key], out[cls_key]
    elif isinstance(out, (list, tuple)):
        seg, cls = out[0], out[1]
    else:
        raise ValueError("Unexpected model output format.")

    seg_mask  = np.squeeze(seg).astype(np.float32)
    # Model final layer already has softmax — applying it again compresses scores toward ~25% each (double-softmax bug)
    # So we just take the output directly as probabilities
    cls_probs = np.squeeze(cls).astype(np.float32)
    return seg_mask, cls_probs


# ══════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════
def make_viz(original: np.ndarray, mask: np.ndarray, thresh: float) -> plt.Figure:
    disp   = original.copy()
    if disp.max() <= 1.0:
        disp = (disp * 255).astype(np.uint8)
    binary = (mask > thresh).astype(np.float32)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    fig.patch.set_facecolor("#080C10")
    for ax in axes:
        ax.set_facecolor("#080C10")
        ax.axis("off")
        for sp in ax.spines.values():
            sp.set_visible(False)

    def titl(ax, t):
        ax.set_title(t, color="#445566", fontsize=7.5, fontfamily="monospace", pad=10)

    axes[0].imshow(disp)
    titl(axes[0], "INPUT SCAN")

    axes[1].imshow(disp, alpha=0.3)
    axes[1].imshow(mask, cmap="inferno", alpha=0.85, vmin=0, vmax=1)
    titl(axes[1], "PREDICTED MASK")

    axes[2].imshow(disp)
    axes[2].imshow(binary, cmap=MASK_CMAP, alpha=0.7, vmin=0, vmax=1)
    if binary.sum() > 0:
        axes[2].contour(binary, levels=[0.5], colors=["#E84545"], linewidths=[1.5])
    pct = binary.mean() * 100
    axes[2].text(6, IMG_SIZE - 10, f"Coverage: {pct:.2f}%",
        color="#E84545", fontsize=8, fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.3", fc="#080C10", ec="#E84545", alpha=0.85))
    titl(axes[2], "TUMOR OVERLAY")

    fig.tight_layout(pad=1.0)
    return fig


def fig_to_png(fig: plt.Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.read()


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    thresh = st.slider("Mask threshold", 0.1, 0.9, 0.45, 0.05)
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#334455; line-height:1.8;'>
    <b style='color:#2EC4B6'>Recommended input</b><br>
    BRISC preprocessed .npy files<br>
    Shape: (256, 256, 3) float32<br><br>
    <b style='color:#445566'>Architecture</b><br>
    EfficientNetB4 Encoder<br>
    Swin Transformer Bottleneck<br>
    U-Net Decoder + SE Head<br><br>
    <b style='color:#445566'>Classes</b><br>
    Glioma · Meningioma<br>
    Pituitary · No Tumor
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  LOAD MODEL ON STARTUP
# ══════════════════════════════════════════════════════
with st.spinner("🔄 Loading model…"):
    model, model_filename, model_err = auto_load_model()

model_ready = model is not None


# ══════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-tag">Deep Learning · Medical Imaging</div>
    <div class="hero-title">Brain Tumor <span>MRI Analyzer</span></div>
    <div class="hero-sub">EfficientNet + Swin Transformer &nbsp;·&nbsp; Segmentation & Classification &nbsp;·&nbsp; BRISC 2025</div>
""", unsafe_allow_html=True)

if model_ready:
    st.markdown(f"""
    <div class="model-badge badge-ok">
        <div class="badge-dot badge-dot-ok"></div>
        Model ready &nbsp;·&nbsp; {model_filename} &nbsp;·&nbsp; {model.count_params():,} params
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="model-badge badge-err">
        <div class="badge-dot badge-dot-err"></div>
        Model error — see below
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

if not model_ready:
    st.error(
        f"**Could not load the model.**\n\n`{model_err}`\n\n"
        "Make sure `final_model_v3.keras` and `model_utils.py` are in the same folder as `app.py`."
    )
    st.stop()


# ══════════════════════════════════════════════════════
#  UPLOAD  — .npy preferred, image fallback
# ══════════════════════════════════════════════════════
st.markdown('<div class="sec-head">Upload MRI Scan</div>', unsafe_allow_html=True)

tab_npy, tab_img = st.tabs(["✅ .npy file  (recommended)", "⚠️  Raw image (.png / .jpg)"])

uploaded_npy = None
uploaded_img = None

with tab_npy:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#4a8060;
                padding:0.6rem 0.8rem; background:#0a1810; border-radius:6px;
                border:1px solid #1a4030; margin-bottom:0.8rem; line-height:1.7;">
        <b style="color:#6BCB77">Upload the image.
    </div>
    """, unsafe_allow_html=True)
    uploaded_npy = st.file_uploader("Upload .npy file", type=["npy"], label_visibility="collapsed", key="npy_up")

with tab_img:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#4a8060;
                padding:0.6rem 0.8rem; background:#0a1810; border-radius:6px;
                border:1px solid #1a4030; margin-bottom:0.8rem; line-height:1.7;">
        <b style="color:#6BCB77">Upload the image.
    </div>
    """, unsafe_allow_html=True)
    uploaded_img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "tif", "bmp"], label_visibility="collapsed", key="img_up")

# ── Determine what was uploaded
uploaded_file = uploaded_npy or uploaded_img
is_npy        = uploaded_npy is not None

if uploaded_file is None:
    st.markdown("""
    <div style="text-align:center; padding:2.5rem 0; color:#223344;
                font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:0.08em;">
        ↑ &nbsp; UPLOAD A .NPY FILE TO BEGIN ANALYSIS
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════
#  PREPROCESSING
# ══════════════════════════════════════════════════════
file_bytes = uploaded_file.read()

try:
    if is_npy:
        img_input, img_display = load_npy(file_bytes)
    else:
        img_input, img_display = load_raw_image(file_bytes)
        st.markdown("""
        <div class="warn-box">
            <b>⚠️ Raw image mode</b> — Results may not match Kaggle notebook output.<br>
            For accurate predictions, use a <code>.npy</code> file from the BRISC test set.
        </div>
        """, unsafe_allow_html=True)
except ValueError as e:
    st.error(f"**File error:** {e}")
    st.stop()


# ══════════════════════════════════════════════════════
#  INFERENCE
# ══════════════════════════════════════════════════════
with st.spinner("Analyzing MRI…"):
    try:
        seg_mask, cls_probs = run_inference(model, img_input)
    except Exception as e:
        st.error(f"Inference failed: {e}")
        st.stop()

pred_idx   = int(np.argmax(cls_probs))
confidence = float(cls_probs[pred_idx])
binary     = (seg_mask > thresh).astype(np.float32)
coverage   = float(binary.mean()) * 100
c_color    = CLASS_COLORS[pred_idx]
icon       = "⚠️" if pred_idx < 3 else "✅"


# ══════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════
st.markdown('<div class="sec-head">Diagnosis</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="pred-banner" style="border-color:{c_color}; background:{c_color}18;">
    <div style="font-size:2.2rem; line-height:1">{icon}</div>
    <div>
        <div class="pred-name" style="color:{c_color}">{CLASS_NAMES[pred_idx]}</div>
        <div class="pred-desc">{CLASS_DESC[pred_idx]}</div>
    </div>
    <div style="margin-left:auto; text-align:right;">
        <div style="font-family:'DM Mono',monospace; font-size:2rem; font-weight:700; color:{c_color}">{confidence*100:.1f}%</div>
        <div style="font-size:0.7rem; color:#445566; font-family:'DM Mono',monospace;">CONFIDENCE</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="pill-row">
    <div class="pill">
        <div class="pill-label">Tumor Coverage</div>
        <div class="pill-val" style="color:#E84545">{coverage:.2f}%</div>
    </div>
    <div class="pill">
        <div class="pill-label">Positive Pixels</div>
        <div class="pill-val">{int(binary.sum()):,}</div>
    </div>
    <div class="pill">
        <div class="pill-label">Peak Mask Value</div>
        <div class="pill-val">{seg_mask.max():.3f}</div>
    </div>
    <div class="pill">
        <div class="pill-label">Input Format</div>
        <div class="pill-val" style="color:{'#6BCB77' if is_npy else '#F0A500'}">{"NPY ✓" if is_npy else "IMG ⚠"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

viz_col, prob_col = st.columns([3, 1.2])

with viz_col:
    st.markdown('<div class="sec-head">Segmentation Panels</div>', unsafe_allow_html=True)
    fig = make_viz(img_display, seg_mask, thresh)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with prob_col:
    st.markdown('<div class="sec-head">Class Probabilities</div>', unsafe_allow_html=True)
    for i, (name, prob, color) in enumerate(zip(CLASS_NAMES, cls_probs, CLASS_COLORS)):
        bold = "font-weight:700; color:#e8f0fa;" if i == pred_idx else ""
        st.markdown(f"""
        <div class="prob-row">
            <div class="prob-name" style="{bold}">{name}</div>
            <div class="prob-bar-bg">
                <div class="prob-bar-fill" style="width:{int(prob*100)}%; background:{color}"></div>
            </div>
            <div class="prob-pct">{prob*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ranked = sorted(zip(CLASS_NAMES, cls_probs), key=lambda x: -x[1])
    for rank, (name, p) in enumerate(ranked, 1):
        rank_color = "#FFD700" if rank == 1 else "#445566"
        st.markdown(
            f'<div style="font-family:\'DM Mono\',monospace; font-size:0.7rem; '
            f'color:{rank_color}; margin:0.25rem 0">#{rank} {name} — {p*100:.1f}%</div>',
            unsafe_allow_html=True)

# ── Downloads
st.markdown('<div class="sec-head">Export</div>', unsafe_allow_html=True)
dl1, dl2, dl3 = st.columns(3)

with dl1:
    fig_dl = make_viz(img_display, seg_mask, thresh)
    st.download_button("⬇️ Panels (.png)", fig_to_png(fig_dl), "mri_analysis.png", "image/png")
    plt.close(fig_dl)

with dl2:
    mask_buf = io.BytesIO()
    np.save(mask_buf, seg_mask)
    st.download_button("⬇️ Mask (.npy)", mask_buf.getvalue(), "predicted_mask.npy", "application/octet-stream")

with dl3:
    report = {
        "predicted_class":    CLASS_NAMES[pred_idx],
        "confidence":         round(confidence, 4),
        "tumor_coverage_pct": round(coverage, 4),
        "mask_threshold":     thresh,
        "input_format":       "npy" if is_npy else "image",
        "probabilities":      {n: round(float(p), 4) for n, p in zip(CLASS_NAMES, cls_probs)},
    }
    st.download_button("⬇️ Report (.json)", json.dumps(report, indent=2), "diagnosis_report.json", "application/json")

st.markdown("""
<div style="margin-top:4rem; padding-top:1.5rem; border-top:1px solid #111820;
            text-align:center; font-family:'DM Mono',monospace;
            font-size:0.65rem; color:#223344; letter-spacing:0.05em;">
    Research prototype only &nbsp;·&nbsp; Not for clinical use &nbsp;·&nbsp;
    BRISC 2025 &nbsp;·&nbsp; EfficientNetB4 + Swin Transformer
</div>
""", unsafe_allow_html=True)