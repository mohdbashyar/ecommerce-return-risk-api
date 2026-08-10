import os
from contextlib import asynccontextmanager
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.schemas import ReturnRiskRequest, ReturnRiskResponse, HealthResponse

# Global model pipeline placeholder
model_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model pipeline during app startup."""
    global model_pipeline
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pipeline_path = os.path.join(base_dir, 'models', 'pipeline.joblib')
    
    if os.path.exists(pipeline_path):
        try:
            model_pipeline = joblib.load(pipeline_path)
            print(f"Loaded model pipeline successfully from {pipeline_path}")
        except Exception as e:
            print(f"Error loading model pipeline from {pipeline_path}: {e}")
            model_pipeline = None
    else:
        print(f"Model pipeline not found at {pipeline_path}. API will run in degraded mode until model is trained.")
        
    yield
    model_pipeline = None

app = FastAPI(
    title="E-Commerce Product Return Risk Engine API",
    description="Machine Learning API for real-time order return risk score calculation, risk tiering, and automated business triggers.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend applications (e.g. Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_risk_factors(req: ReturnRiskRequest, prob: float) -> tuple[list[str], str]:
    """Generate interpretable risk drivers and automated business recommendations."""
    factors = []
    
    if req.previous_returns_count >= 2:
        factors.append(f"High customer previous return history ({req.previous_returns_count} past returns)")
    elif req.previous_returns_count == 1:
        factors.append("Moderate return history (1 previous return)")
        
    if req.product_category.value == "Clothing":
        factors.append("Category 'Clothing' has higher baseline size/fit return likelihood")
    elif req.product_category.value == "Electronics":
        factors.append("Category 'Electronics' has higher technical specification return likelihood")
        
    if req.seller_rating < 3.8:
        factors.append(f"Low seller rating ({req.seller_rating:.1f}/5.0) correlates with item mismatch")
        
    if req.discount_applied >= 0.15:
        factors.append(f"Heavy discount applied ({req.discount_applied * 100:.0f}%) increases impulse buy return probability")
        
    if req.customer_tenure_days < 60:
        factors.append("New customer account (<60 days tenure)")
        
    if not factors:
        factors.append("Standard order metrics with low risk indicator profile")
        
    # Recommendation trigger
    if prob >= 0.65:
        rec = "High Risk: Display size-fit/compatibility warning before checkout and offer instant exchange incentive."
    elif prob >= 0.35:
        rec = "Medium Risk: Highlight clear return policy details and prompt for option confirmation."
    else:
        rec = "Low Risk: Standard checkout approved. Eligible for instant automated refund processing."
        
    return factors, rec

@app.get("/", include_in_schema=False)
def root():
    """Redirect root endpoint to Swagger UI documentation."""
    return RedirectResponse(url="/docs")

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System Health"],
    summary="Check API health and model artifact status"
)
def get_health():
    """Return runtime health status and whether the ML model pipeline is loaded."""
    return HealthResponse(
        status="healthy",
        model_loaded=(model_pipeline is not None),
        version="1.0.0"
    )

@app.post(
    "/predict",
    response_model=ReturnRiskResponse,
    tags=["Risk Prediction"],
    summary="Predict product return risk for an e-commerce order payload"
)
def predict_return_risk(request: ReturnRiskRequest):
    """Infers return probability, risk tier, risk factors, and business recommendation for a given order payload."""
    if model_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model pipeline is not loaded. Please train the model using 'python -m src.train' first."
        )
        
    input_data = pd.DataFrame([{
        "product_category": request.product_category.value,
        "price": request.price,
        "seller_rating": request.seller_rating,
        "customer_tenure_days": request.customer_tenure_days,
        "previous_returns_count": request.previous_returns_count,
        "is_prime_member": 1 if request.is_prime_member else 0,
        "quantity": request.quantity,
        "shipping_type": request.shipping_type.value,
        "discount_applied": request.discount_applied
    }])
    
    try:
        prob = float(model_pipeline.predict_proba(input_data)[0, 1])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )
        
    risk_score = int(round(prob * 100))
    
    if prob >= 0.65:
        risk_tier = "High Risk"
    elif prob >= 0.35:
        risk_tier = "Medium Risk"
    else:
        risk_tier = "Low Risk"
        
    factors, rec = analyze_risk_factors(request, prob)
    
    return ReturnRiskResponse(
        return_probability=round(prob, 4),
        risk_score=risk_score,
        risk_tier=risk_tier,
        risk_factors=factors,
        recommendation=rec
    )
