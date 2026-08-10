import os
import joblib
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Return Risk Analyzer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Light Theme CSS Styling
st.markdown("""
    <style>
    /* App Background & Typography */
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    
    /* Clean Metric Cards with Soft Shadow */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.12);
        border-color: #CBD5E1;
    }
    
    /* Gradient Title Accent */
    .header-title {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.3rem;
        margin-bottom: 0.2rem;
    }

    .header-subtitle {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* Light Mode Risk Badges */
    .badge-high {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        color: #991B1B;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }
    .badge-medium {
        background-color: #FFFBEB;
        border: 1px solid #FCD34D;
        color: #92400E;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }
    .badge-low {
        background-color: #ECFDF5;
        border: 1px solid #6EE7B7;
        color: #065F46;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }

    /* Light Mode Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="header-title">🛒 E-Commerce Product Return Risk Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="header-subtitle">Real-time machine learning decision engine for return probability evaluation, '
    'risk tiering, and automated business triggers.</div>',
    unsafe_allow_html=True
)

st.sidebar.header("⚙️ Order Configuration & Inputs")

# Optional External API URL (default blank)
api_url = st.sidebar.text_input(
    "FastAPI Backend URL (Optional)",
    value="",
    placeholder="e.g. http://localhost:8000",
    help="Leave blank to use embedded ML pipeline engine."
)

# Order Input Controls
st.sidebar.subheader("Order Details")
category = st.sidebar.selectbox(
    "Product Category",
    ["Clothing", "Electronics", "Beauty", "Home", "Books", "Toys", "Sports"],
    index=0
)

shipping_type = st.sidebar.selectbox(
    "Shipping Type",
    ["Standard", "Two-Day", "Express", "Same-Day", "Expedited"],
    index=0
)

price = st.sidebar.number_input(
    "Price ($)",
    min_value=1.0,
    max_value=2000.0,
    value=49.99,
    step=5.0
)

quantity = st.sidebar.number_input(
    "Quantity",
    min_value=1,
    max_value=50,
    value=1,
    step=1
)

discount_applied = st.sidebar.slider(
    "Discount Applied (%)",
    min_value=0,
    max_value=50,
    value=10,
    step=1,
    help="Discount percentage applied at checkout"
) / 100.0

st.sidebar.subheader("Seller & Customer Profile")
seller_rating = st.sidebar.slider(
    "Seller Rating",
    min_value=1.0,
    max_value=5.0,
    value=4.2,
    step=0.1
)

previous_returns = st.sidebar.slider(
    "Previous Returns Count",
    min_value=0,
    max_value=20,
    value=2,
    step=1
)

customer_tenure = st.sidebar.number_input(
    "Customer Tenure (Days)",
    min_value=0,
    max_value=3650,
    value=120,
    step=30
)

is_prime = st.sidebar.checkbox("Is Prime Member", value=True)

# Main Action Area
st.markdown("---")
col_submit, _ = st.columns([2, 5])
with col_submit:
    predict_btn = st.button("🚀 Evaluate Return Risk", type="primary", use_container_width=True)

def run_local_model() -> tuple[float, int, str, list[str], str]:
    """Execute local model pipeline fallback."""
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'pipeline.joblib')
    if not os.path.exists(model_path):
        raise FileNotFoundError("Embedded model artifact `models/pipeline.joblib` not found.")
        
    pipeline = joblib.load(model_path)
    input_df = pd.DataFrame([{
        "product_category": category,
        "price": price,
        "seller_rating": seller_rating,
        "customer_tenure_days": int(customer_tenure),
        "previous_returns_count": int(previous_returns),
        "is_prime_member": 1 if is_prime else 0,
        "quantity": int(quantity),
        "shipping_type": shipping_type,
        "discount_applied": float(discount_applied)
    }])
    
    prob = float(pipeline.predict_proba(input_df)[0, 1])
    score = int(round(prob * 100))
    tier = "High Risk" if prob >= 0.65 else ("Medium Risk" if prob >= 0.35 else "Low Risk")
    
    factors = []
    if previous_returns >= 2:
        factors.append(f"High customer previous return history ({previous_returns} past returns)")
    elif previous_returns == 1:
        factors.append("Moderate return history (1 previous return)")
        
    if category == "Clothing":
        factors.append("Category 'Clothing' has higher baseline size/fit return likelihood")
    elif category == "Electronics":
        factors.append("Category 'Electronics' has higher technical spec return likelihood")
        
    if seller_rating < 3.8:
        factors.append(f"Low seller rating ({seller_rating:.1f}/5.0) correlates with item mismatch")
        
    if discount_applied >= 0.15:
        factors.append(f"Heavy discount applied ({discount_applied*100:.0f}%) increases impulse buy return probability")
        
    if customer_tenure < 60:
        factors.append("New customer account (<60 days tenure)")
        
    if not factors:
        factors.append("Standard order metrics with low risk indicator profile")
        
    if prob >= 0.65:
        rec = "High Risk: Display size-fit warning before checkout & offer instant exchange incentive."
    elif prob >= 0.35:
        rec = "Medium Risk: Highlight clear return policy details & prompt for option confirmation."
    else:
        rec = "Low Risk: Standard checkout approved. Eligible for instant automated refund processing."
        
    return prob, score, tier, factors, rec

if predict_btn:
    payload = {
        "product_category": category,
        "price": price,
        "seller_rating": seller_rating,
        "customer_tenure_days": int(customer_tenure),
        "previous_returns_count": int(previous_returns),
        "is_prime_member": is_prime,
        "quantity": int(quantity),
        "shipping_type": shipping_type,
        "discount_applied": float(discount_applied)
    }

    prob, score, tier, factors, recommendation = None, None, None, None, None

    if api_url.strip():
        try:
            with st.spinner("Connecting to FastAPI backend & evaluating risk..."):
                response = requests.post(f"{api_url.strip()}/predict", json=payload, timeout=5)
            if response.status_code == 200:
                res = response.json()
                prob = res["return_probability"]
                score = res["risk_score"]
                tier = res["risk_tier"]
                factors = res["risk_factors"]
                recommendation = res["recommendation"]
            else:
                st.error(f"Error from API ({response.status_code}): {response.text}")
                st.stop()
        except requests.exceptions.ConnectionError:
            st.warning(f"⚠️ External API at `{api_url}` unreachable. Falling back to embedded ML model.")
            prob, score, tier, factors, recommendation = run_local_model()
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            st.stop()
    else:
        try:
            prob, score, tier, factors, recommendation = run_local_model()
        except Exception as e:
            st.error(f"Inference error: {str(e)}")
            st.stop()

    # Render Results UI
    st.subheader("📊 Risk Assessment Results")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(label="Risk Score", value=f"{score} / 100")

    with m2:
        st.metric(label="Return Probability", value=f"{prob * 100:.1f}%")

    with m3:
        if tier == "High Risk":
            st.markdown(f'<div class="badge-high">🔴 Risk Tier: {tier}</div>', unsafe_allow_html=True)
        elif tier == "Medium Risk":
            st.markdown(f'<div class="badge-medium">🟡 Risk Tier: {tier}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="badge-low">🟢 Risk Tier: {tier}</div>', unsafe_allow_html=True)

    st.write("")
    st.write("**Return Probability Progress Gauge:**")
    st.progress(float(prob))

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🔍 Identified Risk Drivers")
        for factor in factors:
            st.markdown(f"- {factor}")

    with col_right:
        st.subheader("⚡ Automated Business Action Trigger")
        if tier == "High Risk":
            st.error(f"**Recommended Action:**\n\n{recommendation}")
        elif tier == "Medium Risk":
            st.warning(f"**Recommended Action:**\n\n{recommendation}")
        else:
            st.success(f"**Recommended Action:**\n\n{recommendation}")

# Footer
st.markdown("---")
st.caption("Powered by FastAPI & Scikit-Learn RandomForest Pipeline | E-Commerce Return Risk Engine v1.0")
