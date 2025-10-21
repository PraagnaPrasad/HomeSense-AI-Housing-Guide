
# API Service

## Quickstart

### 1. Setup Environment
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys:
# - FRED_API_KEY: Get from https://fred.stlouisfed.org/docs/api/api_key.html
# - PPLX_API_KEY: Get from https://www.perplexity.ai/settings/api
```

### 3. Test Data Sources (Optional)
```bash
python test_data_sources.py
```

### 4. Run the API
```bash
uvicorn app.main:app --reload --port 8080
```
Open http://localhost:8080/docs

## Features

### Data Sources

The API automatically fetches live data from:

1. **FRED (Federal Reserve Economic Data)**
   - 30-year mortgage rates (MORTGAGE30US)
   - CPI inflation rates (CPIAUCSL)
   - Falls back to default values if API key not provided

2. **Zillow Research Data**
   - ZORI (Zillow Observed Rent Index) - rent growth rates
   - ZHVI (Zillow Home Value Index) - home price appreciation
   - Fetches directly from Zillow's public CSV URLs
   - No local files needed - works in deployment

### API Endpoints

- `POST /v1/compute` - Calculate rent vs buy comparison
- `POST /v1/summarize` - Generate summary text
- `POST /v1/monte-carlo` - Run Monte Carlo simulation
- `POST /v1/advise` - Get AI-powered advice (requires Perplexity key)
- `GET /healthz` - Health check

## Deployment

The data sources are designed for cloud deployment:
- FRED data fetched via API (requires key)
- Zillow data fetched from public URLs (no authentication needed)
- All data is fetched on-demand, no local storage required
