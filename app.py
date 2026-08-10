import streamlit as st
import requests

st.set_page_config(
    page_title="E-Commerce Return Risk Analyzer",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 E-Commerce Product Return Risk Analyzer")
st.markdown(
    "Predict return probability for e-commerce order payloads using real-time machine learning inference, "
    "risk score tiering, and automated business recommendations."
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

# Main action area
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
                    st.error(f"🔴 Tier: **{tier}**")
                elif tier == "Medium Risk":
                    st.warning(f"🟡 Tier: **{tier}**")
                else:
                    st.success(f"🟢 Tier: **{tier}**")

            # Progress Gauge
            st.write("**Return Probability Score:**")
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
