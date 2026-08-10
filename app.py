import streamlit as st
import requests

st.set_page_config(
    page_title="E-Commerce Return Risk Analyzer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Theme CSS Styling
st.markdown("""
    <style>
    /* Dark Theme Background & Fonts */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Sleek Dark Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(108, 92, 231, 0.25);
    }
    
    /* Header Gradient Accent */
    .header-title {
        background: linear-gradient(90deg, #A855F7 0%, #6366F1 50%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 0.2rem;
    }

    /* Subtitle text */
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* Custom Risk Badges */
    .badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid #EF4444;
        color: #FCA5A5;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }
    .badge-medium {
        background-color: rgba(245, 158, 11, 0.15);
        border: 1px solid #F59E0B;
        color: #FDE68A;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }
    .badge-low {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        color: #6EE7B7;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155;
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

# API URL Configuration
api_url = st.sidebar.text_input("FastAPI Backend URL", value="http://localhost:8000")

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

    try:
        with st.spinner("Connecting to FastAPI backend & evaluating risk..."):
            response = requests.post(f"{api_url}/predict", json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            prob = result["return_probability"]
            score = result["risk_score"]
            tier = result["risk_tier"]
            factors = result["risk_factors"]
            recommendation = result["recommendation"]

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

        else:
            st.error(f"Error from API ({response.status_code}): {response.text}")

    except requests.exceptions.ConnectionError:
        st.error(
            f"❌ Unable to connect to backend at `{api_url}`. "
            "Please ensure the FastAPI server is running with `uvicorn src.main:app --reload`."
        )
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.caption("Powered by FastAPI & Scikit-Learn RandomForest Pipeline | E-Commerce Return Risk Engine v1.0")
