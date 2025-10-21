"""
Data sources for FRED API and Zillow data.
Fetches live data from web APIs and URLs (deployment-ready).
"""

import os
import requests
import pandas as pd
from typing import Dict, Optional


def get_fred_rates() -> Dict[str, float]:
    """
    Fetch live mortgage rates and inflation data from FRED API.
    Falls back to default values if API key is not available or request fails.

    Returns:
        dict: {"mortgage_rate_annual": float, "inflation_annual": float}
    """
    api_key = os.environ.get("FRED_API_KEY")

    # Default fallback values
    defaults = {
        "mortgage_rate_annual": 0.068,  # 6.8%
        "inflation_annual": 0.025,      # 2.5%
    }

    if not api_key:
        print("⚠️ FRED_API_KEY not found, using default rates")
        return defaults

    try:
        # Fetch 30-year fixed rate mortgage average (MORTGAGE30US)
        mortgage_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=MORTGAGE30US&api_key={api_key}&file_type=json&sort_order=desc&limit=1"
        mortgage_resp = requests.get(mortgage_url, timeout=5)
        mortgage_resp.raise_for_status()
        mortgage_data = mortgage_resp.json()

        if mortgage_data.get("observations"):
            mortgage_rate = float(mortgage_data["observations"][0]["value"]) / 100.0
        else:
            mortgage_rate = defaults["mortgage_rate_annual"]

        # Fetch CPI inflation (CPIAUCSL - Consumer Price Index)
        # Calculate YoY change
        inflation_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json&sort_order=desc&limit=13"
        inflation_resp = requests.get(inflation_url, timeout=5)
        inflation_resp.raise_for_status()
        inflation_data = inflation_resp.json()

        if len(inflation_data.get("observations", [])) >= 13:
            latest_cpi = float(inflation_data["observations"][0]["value"])
            year_ago_cpi = float(inflation_data["observations"][12]["value"])
            inflation_rate = (latest_cpi - year_ago_cpi) / year_ago_cpi
        else:
            inflation_rate = defaults["inflation_annual"]

        print(f"✅ Fetched FRED rates: Mortgage {mortgage_rate:.4f}, Inflation {inflation_rate:.4f}")

        return {
            "mortgage_rate_annual": mortgage_rate,
            "inflation_annual": inflation_rate,
        }

    except Exception as e:
        print(f"⚠️ Error fetching FRED data: {e}, using defaults")
        return defaults


def load_zillow_data_from_url(region_query: str) -> Dict[str, Optional[float]]:
    """
    Fetch Zillow ZORI (rent) and ZHVI (home price) data directly from Zillow's public URLs
    and compute YoY growth rates for a specific city/region.

    Args:
        region_query: City or metro area name (e.g., "San Francisco", "Austin, TX")

    Returns:
        dict: {
            "rent_growth_annual": float or None,
            "home_price_growth": float or None
        }
    """
    ZORI_URL = "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv"
    ZHVI_URL = "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"

    result = {
        "rent_growth_annual": None,
        "home_price_growth": None,
    }

    try:
        # Fetch ZORI (rent) data
        print("📥 Fetching ZORI (rent) data from Zillow...")
        zori_df = pd.read_csv(ZORI_URL)

        # Search for the region (case-insensitive)
        region_lower = region_query.lower()
        mask = zori_df['RegionName'].str.lower().str.contains(region_lower, na=False)

        if mask.any():
            row = zori_df[mask].iloc[0]
            # Get the last two date columns (most recent data)
            date_cols = [col for col in zori_df.columns if col.startswith('20')]
            if len(date_cols) >= 13:  # Need at least 13 months for YoY
                latest_rent = row[date_cols[-1]]
                year_ago_rent = row[date_cols[-13]]

                if pd.notna(latest_rent) and pd.notna(year_ago_rent) and year_ago_rent > 0:
                    rent_growth = (latest_rent - year_ago_rent) / year_ago_rent
                    result["rent_growth_annual"] = rent_growth
                    print(f"✅ ZORI rent growth for '{row['RegionName']}': {rent_growth*100:.2f}%")
                else:
                    print(f"⚠️ ZORI data incomplete for '{row['RegionName']}'")
        else:
            print(f"⚠️ Region '{region_query}' not found in ZORI data")

    except Exception as e:
        print(f"⚠️ Error fetching ZORI data: {e}")

    try:
        # Fetch ZHVI (home price) data
        print("📥 Fetching ZHVI (home price) data from Zillow...")
        zhvi_df = pd.read_csv(ZHVI_URL)

        # Search for the region
        mask = zhvi_df['RegionName'].str.lower().str.contains(region_lower, na=False)

        if mask.any():
            row = zhvi_df[mask].iloc[0]
            # Get the last date columns
            date_cols = [col for col in zhvi_df.columns if col.startswith('20')]
            if len(date_cols) >= 13:  # Need at least 13 months for YoY
                latest_price = row[date_cols[-1]]
                year_ago_price = row[date_cols[-13]]

                if pd.notna(latest_price) and pd.notna(year_ago_price) and year_ago_price > 0:
                    price_growth = (latest_price - year_ago_price) / year_ago_price
                    result["home_price_growth"] = price_growth
                    print(f"✅ ZHVI home price growth for '{row['RegionName']}': {price_growth*100:.2f}%")
                else:
                    print(f"⚠️ ZHVI data incomplete for '{row['RegionName']}'")
        else:
            print(f"⚠️ Region '{region_query}' not found in ZHVI data")

    except Exception as e:
        print(f"⚠️ Error fetching ZHVI data: {e}")

    return result
