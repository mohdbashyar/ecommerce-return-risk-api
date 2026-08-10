import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    """FastAPI TestClient fixture executing application lifespan."""
    with TestClient(app) as test_client:
        yield test_client

def test_root_redirect(client):
    """Test root endpoint redirects to Swagger UI documentation."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302, 200)

def test_health_endpoint(client):
    """Test health check endpoint status and model artifact load state."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "version" in data

def test_predict_endpoint_valid_payload(client):
    """Test prediction endpoint with a valid order payload."""
    payload = {
        "product_category": "Clothing",
        "price": 49.99,
        "seller_rating": 4.2,
        "customer_tenure_days": 120,
        "previous_returns_count": 2,
        "is_prime_member": True,
        "quantity": 1,
        "shipping_type": "Standard",
        "discount_applied": 0.10
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert 0.0 <= data["return_probability"] <= 1.0
    assert 0 <= data["risk_score"] <= 100
    assert data["risk_tier"] in ["Low Risk", "Medium Risk", "High Risk"]
    assert isinstance(data["risk_factors"], list)
    assert len(data["risk_factors"]) > 0
    assert isinstance(data["recommendation"], str)
    assert len(data["recommendation"]) > 0

def test_predict_endpoint_invalid_category(client):
    """Test prediction endpoint handles invalid product category with 422 Unprocessable Entity."""
    payload = {
        "product_category": "InvalidCategory",
        "price": 49.99,
        "seller_rating": 4.2,
        "customer_tenure_days": 120,
        "previous_returns_count": 0,
        "is_prime_member": True,
        "quantity": 1,
        "shipping_type": "Standard",
        "discount_applied": 0.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_endpoint_negative_price(client):
    """Test prediction endpoint rejects negative price values with 422 Unprocessable Entity."""
    payload = {
        "product_category": "Electronics",
        "price": -10.0,
        "seller_rating": 4.2,
        "customer_tenure_days": 120,
        "previous_returns_count": 0,
        "is_prime_member": True,
        "quantity": 1,
        "shipping_type": "Standard",
        "discount_applied": 0.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_endpoint_out_of_bounds_rating(client):
    """Test prediction endpoint rejects seller rating > 5.0 with 422 Unprocessable Entity."""
    payload = {
        "product_category": "Electronics",
        "price": 99.99,
        "seller_rating": 6.5,
        "customer_tenure_days": 120,
        "previous_returns_count": 0,
        "is_prime_member": True,
        "quantity": 1,
        "shipping_type": "Standard",
        "discount_applied": 0.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_endpoint_invalid_discount(client):
    """Test prediction endpoint rejects discount > 1.0 with 422 Unprocessable Entity."""
    payload = {
        "product_category": "Beauty",
        "price": 25.00,
        "seller_rating": 4.0,
        "customer_tenure_days": 100,
        "previous_returns_count": 0,
        "is_prime_member": False,
        "quantity": 1,
        "shipping_type": "Standard",
        "discount_applied": 1.5
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
