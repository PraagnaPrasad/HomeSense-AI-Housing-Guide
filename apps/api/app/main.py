from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# Import settings first to ensure environment variables are set
from settings import settings

from app.engine.core import rent_vs_buy, summarize_rent_vs_buy, monte_carlo_prob
from app.services.perplexity import ask_advisor, advise_city
from app.engine.results_formatter import format_results_for_display

app = FastAPI(title="Rent vs Buy API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Inputs(BaseModel):
    home_price: float = Field(..., gt=0)
    monthly_rent: float = Field(..., gt=0)
    down_payment_pct: float = Field(0.20, ge=0, lt=1)
    mortgage_rate_annual: float = Field(0.065, ge=0, lt=1)
    term_years: int = Field(30, gt=0, le=40)
    property_tax_rate: float = Field(0.012, ge=0, lt=1)
    maintenance_rate: float = Field(0.01, ge=0, lt=1)
    insurance_per_year: float = Field(1500, ge=0)
    home_price_growth: float = Field(0.03, ge=-1, lt=1)
    rent_growth: float = Field(0.03, ge=-1, lt=1)
    investment_return: float = Field(0.05, ge=-1, lt=1)
    closing_cost_buy: float = Field(0.03, ge=0, lt=1)
    selling_cost: float = Field(0.06, ge=0, lt=1)
    years_horizon: int = Field(10, gt=0, le=50)
    discount_rate: float = Field(0.04, ge=0, lt=1)

class ComputeResponse(BaseModel):
    inputs: Dict[str, Any]
    results: Dict[str, Any]

@app.post("/v1/compute", response_model=ComputeResponse)
def compute(req: Inputs):
    try:
        # Prepare parameters for rent_vs_buy (note: term_years is not used by the function)
        params = req.dict()
        params.pop('term_years', None)  # Remove term_years as it's not used
        params['years'] = params.pop('years_horizon')  # Rename years_horizon to years

        results = rent_vs_buy(**params)
        return {"inputs": req.dict(), "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1/compute-formatted")
def compute_formatted(req: Inputs):
    """
    Enhanced compute endpoint with formatted results for rich UI display.
    Returns structured data matching the reference design.
    """
    try:
        # Prepare parameters
        params = req.dict()
        inputs_dict = req.dict()
        params.pop('term_years', None)
        params['years'] = params.pop('years_horizon')

        # Run calculation
        results = rent_vs_buy(**params)

        # Format for display
        formatted = format_results_for_display(inputs_dict, results)

        return formatted
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class CityDataRequest(BaseModel):
    city: str = Field(..., description="City or metro area name (e.g., 'San Francisco', 'Austin, TX')")

@app.post("/v1/city-data")
def get_city_data(req: CityDataRequest):
    """
    Fetch live Zillow growth rates for a specific city/metro area.
    Returns rent_growth_annual and home_price_growth based on real market data.
    """
    try:
        from rvb.data_sources import load_zillow_data_from_url

        data = load_zillow_data_from_url(req.city)

        if data["rent_growth_annual"] is None and data["home_price_growth"] is None:
            return {
                "city": req.city,
                "found": False,
                "message": f"No data found for '{req.city}'. Try a different city or metro area name.",
                "rent_growth_annual": None,
                "home_price_growth": None
            }

        return {
            "city": req.city,
            "found": True,
            "rent_growth_annual": data["rent_growth_annual"],
            "home_price_growth": data["home_price_growth"],
            "message": f"Found data for {req.city}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching city data: {str(e)}")

@app.get("/v1/fred-rates")
def get_live_rates():
    """
    Fetch live mortgage rates and inflation from FRED.
    """
    try:
        from rvb.data_sources import get_fred_rates

        rates = get_fred_rates()
        return {
            "mortgage_rate_annual": rates["mortgage_rate_annual"],
            "inflation_annual": rates["inflation_annual"],
            "source": "FRED API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching FRED data: {str(e)}")

class SummarizeRequest(BaseModel):
    inputs: Dict[str, Any]
    results: Dict[str, Any]

@app.post("/v1/summarize")
def summarize(req: SummarizeRequest):
    try:
        return {"text": summarize_rent_vs_buy(req.inputs, req.results)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class MonteCarloRequest(BaseModel):
    inputs: Dict[str, Any]
    sims: int = Field(1000, gt=0, le=20000)
    seed: Optional[int] = None

@app.post("/v1/monte-carlo")
def mc(req: MonteCarloRequest):
    try:
        return monte_carlo_prob(req.inputs, req.sims, req.seed)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str

class UserContext(BaseModel):
    """Personal context about the user for personalized advice."""
    age: Optional[int] = None
    annual_income: Optional[float] = None
    relationship_status: Optional[str] = None  # e.g., "single", "married", "partnered"
    kids: Optional[Any] = None  # Can be bool or string like "2 kids (ages 5, 7)"
    education: Optional[str] = None
    job_stability: Optional[str] = None  # e.g., "stable", "startup", "freelance"
    career_stage: Optional[str] = None  # e.g., "early career", "mid-career", "senior"
    savings: Optional[float] = None
    debt: Optional[float] = None
    credit_score: Optional[int] = None
    location: Optional[str] = None
    work_situation: Optional[str] = None  # e.g., "remote", "hybrid", "in-office"
    lifestyle_priorities: Optional[str] = None  # e.g., "flexibility", "stability", "travel"
    property_links: Optional[Any] = None  # Can be string or list of strings (Zillow, StreetEasy URLs)
    additional_info: Optional[str] = None

class AdvisorRequest(BaseModel):
    inputs: Optional[Dict[str, Any]] = None
    question: str
    conversation_history: Optional[List[Message]] = None
    user_context: Optional[UserContext] = None

@app.post("/v1/advise")
def advise(req: AdvisorRequest):
    try:
        # Convert Pydantic models to dicts for the function
        history = [msg.dict() for msg in req.conversation_history] if req.conversation_history else None
        context = req.user_context.dict(exclude_none=True) if req.user_context else None

        # This calls your Perplexity advisor wrapper (key should be set in env on the web app side)
        return {"answer": ask_advisor(req.inputs, req.question, history, context)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/healthz")
def health():
    return {"ok": True, "version": app.version}
