import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Return Risk Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Load ML Model ───────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_path = os.path.join(base_dir, "models", "pipeline.joblib")
    if os.path.exists(pipeline_path):
        return joblib.load(pipeline_path)
    return None

model_pipeline = load_model()

# ─── Custom CSS (Editorial Stitch Design) ────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=Hanken+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #fbf9f4;
        font-family: 'Hanken Grotesk', sans-serif;
        color: #1b1c19;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f5f3ee;
        border-right: 1px solid rgba(18,18,18,0.08);
    }
    [data-testid="stSidebar"] .stMarkdown h1 {
        font-family: 'Bodoni Moda', serif;
        color: #142275;
        font-size: 1.6rem;
        font-weight: 500;
        letter-spacing: -0.02em;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #454651;
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] label {
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #454651 !important;
    }

    /* Button */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background-color: #142275;
        color: white;
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        border: none;
        border-radius: 2px;
        padding: 0.85rem 1rem;
        margin-top: 1rem;
        transition: background-color 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2e3b8c;
        color: white;
    }

    /* Dividers */
    .editorial-divider {
        border: none;
        border-bottom: 1px solid rgba(18,18,18,0.1);
        margin: 1.5rem 0;
    }

    /* Title Area */
    .page-title {
        font-family: 'Bodoni Moda', serif;
        font-size: 3.2rem;
        font-weight: 600;
        color: #1b1c19;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    .page-subtitle {
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 1.05rem;
        color: #454651;
        line-height: 1.6;
        max-width: 600px;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid rgba(18,18,18,0.1);
        padding: 2rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card-alt {
        background: #f5f3ee;
        border: 1px solid rgba(18,18,18,0.1);
        padding: 2rem;
    }
    .metric-label {
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #454651;
        margin-bottom: 1.2rem;
    }
    .metric-value {
        font-family: 'Bodoni Moda', serif;
        font-size: 3.5rem;
        font-weight: 600;
        line-height: 1;
    }
    .metric-suffix {
        font-family: 'Bodoni Moda', serif;
        font-size: 1.5rem;
        color: rgba(69,70,81,0.5);
        margin-left: 0.25rem;
    }
    .prob-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem;
        font-weight: 500;
        color: #1b1c19;
        letter-spacing: 0.02em;
    }

    /* Risk Badge */
    .risk-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1rem;
    }
    .risk-high {
        color: #ba1a1a;
        border: 1px solid #ba1a1a;
        background: rgba(186,26,26,0.05);
    }
    .risk-medium {
        color: #92640a;
        border: 1px solid #c88a0e;
        background: rgba(200,138,14,0.06);
    }
    .risk-low {
        color: #1a7a2e;
        border: 1px solid #1a7a2e;
        background: rgba(26,122,46,0.05);
    }

    /* Score Colors */
    .score-high { color: #ba1a1a; }
    .score-medium { color: #c88a0e; }
    .score-low { color: #1a7a2e; }

    /* Segmented Bar */
    .seg-bar {
        display: flex;
        gap: 3px;
        height: 6px;
        width: 100%;
        margin-top: 1.5rem;
    }
    .seg-bar div {
        flex: 1;
        border-radius: 1px;
        transition: background-color 0.3s ease;
    }
    .seg-filled-low { background-color: #142275; }
    .seg-filled-med { background-color: #c88a0e; }
    .seg-filled-high { background-color: #ba1a1a; }
    .seg-empty { background-color: rgba(198,197,211,0.3); }
    .seg-labels {
        display: flex;
        justify-content: space-between;
        margin-top: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: rgba(69,70,81,0.6);
    }

    /* Detail Panel */
    .detail-panel {
        background: #ffffff;
        border: 1px solid rgba(18,18,18,0.1);
    }
    .detail-section {
        padding: 2rem;
    }
    .detail-section-alt {
        padding: 2rem;
        background: rgba(240,238,233,0.5);
    }
    .driver-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .driver-icon {
        color: #ba1a1a;
        font-size: 1rem;
        margin-right: 0.75rem;
        margin-top: 0.15rem;
    }
    .driver-text {
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.88rem;
        font-weight: 500;
        color: #1b1c19;
    }

    /* Action Callout */
    .action-box {
        background: rgba(223,224,255,0.3);
        border-left: 2px solid #142275;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .action-text {
        font-family: 'Bodoni Moda', serif;
        font-size: 1.15rem;
        font-weight: 500;
        color: #142275;
        line-height: 1.5;
    }
    .section-label-primary {
        font-family: 'Hanken Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #142275;
        margin-bottom: 1.2rem;
    }

    /* Breadcrumb */
    .breadcrumb {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: rgba(69,70,81,0.6);
        letter-spacing: 0.02em;
        margin-bottom: 2rem;
    }

    /* Hide default Streamlit metric styling */
    [data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar: Input Controls ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# Return Risk Engine")
    st.markdown("### Editorial Control")
    st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

    product_category = st.selectbox("Product Category",
        ["Clothing", "Electronics", "Beauty", "Home", "Books", "Toys", "Sports"])

    shipping_type = st.selectbox("Shipping Type",
        ["Standard", "Two-Day", "Express", "Same-Day", "Expedited"])

    col_a, col_b = st.columns(2)
    with col_a:
        price = st.number_input("Price ($)", min_value=1.0, max_value=5000.0, value=49.99, step=0.01)
    with col_b:
        quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1)

    col_c, col_d = st.columns(2)
    with col_c:
        discount_pct = st.number_input("Discount (%)", min_value=0, max_value=100, value=10)
    with col_d:
        seller_rating = st.number_input("Seller Rating", min_value=1.0, max_value=5.0, value=4.2, step=0.1)

    st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)
    st.markdown("### Customer Profile")

    previous_returns = st.number_input("Previous Returns", min_value=0, max_value=20, value=2)
    customer_tenure = st.number_input("Account Tenure (Days)", min_value=0, max_value=5000, value=120)
    is_prime = st.checkbox("Prime Member", value=True)

    evaluate = st.button("Evaluate Return Risk")

# ─── Prediction Logic ─────────────────────────────────────────────────────────
def predict_risk(cat, ship, pr, qty, disc, rating, prev_ret, tenure, prime):
    """Run ML prediction or fallback heuristic."""
    discount_frac = disc / 100.0
    input_data = pd.DataFrame([{
        "product_category": cat,
        "price": pr,
        "seller_rating": rating,
        "customer_tenure_days": tenure,
        "previous_returns_count": prev_ret,
        "is_prime_member": 1 if prime else 0,
        "quantity": qty,
        "shipping_type": ship,
        "discount_applied": discount_frac,
    }])

    if model_pipeline is not None:
        prob = float(model_pipeline.predict_proba(input_data)[0, 1])
    else:
        # Heuristic fallback
        base = 0.20
        if cat == "Clothing": base += 0.25
        elif cat == "Electronics": base += 0.15
        if prev_ret >= 2: base += 0.30
        elif prev_ret == 1: base += 0.15
        if rating < 3.8: base += 0.15
        if discount_frac >= 0.15: base += 0.10
        if tenure < 60: base += 0.08
        prob = min(0.98, max(0.05, base))

    score = int(round(prob * 100))
    tier = "High Risk" if prob >= 0.65 else ("Medium Risk" if prob >= 0.35 else "Low Risk")

    # Risk factors
    factors = []
    if prev_ret >= 2:
        factors.append(f"High customer return history ({prev_ret} previous returns)")
    elif prev_ret == 1:
        factors.append("Moderate return history (1 previous return)")
    if cat == "Clothing":
        factors.append("Category 'Clothing' has higher size/fit return likelihood")
    elif cat == "Electronics":
        factors.append("Category 'Electronics' has higher spec mismatch return rate")
    if rating < 3.8:
        factors.append(f"Low seller rating ({rating:.1f}/5.0) correlates with item issues")
    if discount_frac >= 0.15:
        factors.append(f"Heavy discount ({disc}%) increases impulse buy return probability")
    if tenure < 60:
        factors.append("New customer account (<60 days tenure)")
    if not factors:
        factors.append("Standard order metrics with low risk profile")

    # Recommendation
    if prob >= 0.65:
        rec = "Display sizing/compatibility warning before checkout and offer instant exchange incentive."
    elif prob >= 0.35:
        rec = "Highlight clear return policy details and prompt for size/option confirmation."
    else:
        rec = "Standard checkout approved. Eligible for instant automated refund processing."

    return prob, score, tier, factors, rec

# ─── Run Prediction ──────────────────────────────────────────────────────────
prob, score, tier, factors, rec = predict_risk(
    product_category, shipping_type, price, quantity,
    discount_pct, seller_rating, previous_returns, customer_tenure, is_prime
)

# ─── Color Logic ──────────────────────────────────────────────────────────────
if tier == "High Risk":
    score_class = "score-high"
    badge_class = "risk-high"
elif tier == "Medium Risk":
    score_class = "score-medium"
    badge_class = "risk-medium"
else:
    score_class = "score-low"
    badge_class = "risk-low"

# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown('<div class="breadcrumb">Engine / Risk Assessment / Active</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="page-title">Return Risk Engine</div>
<div class="page-subtitle">Real-time ML risk scoring and automated business triggers to optimize post-purchase efficiency.</div>
<hr class="editorial-divider">
""", unsafe_allow_html=True)

# ─── Metric Cards Row ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Risk Score</div>
        <div>
            <span class="metric-value {score_class}">{score}</span>
            <span class="metric-suffix">/100</span>
        </div>
        <div class="risk-badge {badge_class}">{tier}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Build segmented bar
    filled = round(prob * 10)
    segments = []
    for i in range(10):
        if i < filled:
            if i >= 6:
                segments.append('<div class="seg-filled-high"></div>')
            elif i >= 3:
                segments.append('<div class="seg-filled-med"></div>')
            else:
                segments.append('<div class="seg-filled-low"></div>')
        else:
            segments.append('<div class="seg-empty"></div>')
    bar_html = "".join(segments)

    st.markdown(f"""
    <div class="metric-card-alt">
        <div class="metric-label">Return Probability</div>
        <div class="prob-value">{prob*100:.1f}%</div>
        <div class="seg-bar">{bar_html}</div>
        <div class="seg-labels"><span>0%</span><span>100%</span></div>
    </div>
    """, unsafe_allow_html=True)

# ─── Detail Panel ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    # Build driver items as plain string (no f-string nesting to avoid escaping)
    driver_items = ""
    for factor in factors:
        driver_items += (
            '<div class="driver-item">'
            '<span class="driver-icon">&#9658;</span>'
            '<span class="driver-text">' + factor + '</span>'
            '</div>'
        )

    drivers_panel = (
        '<div class="detail-panel">'
        '<div class="detail-section">'
        '<div class="metric-label">Primary Risk Drivers</div>'
        + driver_items +
        '</div>'
        '</div>'
    )
    st.markdown(drivers_panel, unsafe_allow_html=True)

with col_right:
    action_panel = (
        '<div class="detail-panel">'
        '<div class="detail-section-alt">'
        '<div class="section-label-primary">Recommended Business Action</div>'
        '<div class="action-box">'
        '<div class="action-text">' + rec + '</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(action_panel, unsafe_allow_html=True)
