from enum import Enum
from typing import List
from pydantic import BaseModel, Field, ConfigDict

class ProductCategory(str, Enum):
    CLOTHING = "Clothing"
    ELECTRONICS = "Electronics"
    BEAUTY = "Beauty"
    HOME = "Home"
    BOOKS = "Books"
    TOYS = "Toys"
    SPORTS = "Sports"

class ShippingType(str, Enum):
    STANDARD = "Standard"
    TWO_DAY = "Two-Day"
    EXPRESS = "Express"
    SAME_DAY = "Same-Day"
    EXPEDITED = "Expedited"

class ReturnRiskRequest(BaseModel):
    product_category: ProductCategory = Field(..., description="Product category")
    price: float = Field(..., gt=0.0, description="Price in USD (> 0)")
    seller_rating: float = Field(..., ge=1.0, le=5.0, description="Seller rating between 1.0 and 5.0")
    customer_tenure_days: int = Field(..., ge=0, description="Customer tenure in days")
    previous_returns_count: int = Field(..., ge=0, description="Number of previous returns")
    is_prime_member: bool = Field(False, description="Is the customer a Prime member?")
    quantity: int = Field(1, ge=1, description="Quantity ordered")
    shipping_type: ShippingType = Field(..., description="Selected shipping method")
    discount_applied: float = Field(0.0, ge=0.0, le=1.0, description="Discount percentage applied (0.0 to 1.0)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
        }
    )

class ReturnRiskResponse(BaseModel):
    return_probability: float = Field(..., description="Model return probability (0.0 to 1.0)")
    risk_score: int = Field(..., description="Calibrated risk score (0 to 100)")
    risk_tier: str = Field(..., description="Risk tier: Low Risk, Medium Risk, or High Risk")
    risk_factors: List[str] = Field(..., description="Key risk drivers identified for this order")
    recommendation: str = Field(..., description="Automated business action recommendation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "return_probability": 0.725,
                "risk_score": 73,
                "risk_tier": "High Risk",
                "risk_factors": [
                    "High customer previous returns history (2 returns)",
                    "Category 'Clothing' has higher baseline size fit return rates",
                    "Discount applied (10%) increases impulse purchase return likelihood"
                ],
                "recommendation": "Display size-fit sizing guide prompt before checkout and offer exchange incentive."
            }
        }
    )

class HealthResponse(BaseModel):
    status: str = Field("healthy", description="API status")
    model_loaded: bool = Field(..., description="Indicates if model pipeline is loaded")
    version: str = Field("1.0.0", description="API Version")
