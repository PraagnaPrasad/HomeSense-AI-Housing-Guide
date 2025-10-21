#!/usr/bin/env python3
"""
Test script to verify FRED and Zillow data source integration.
Run this to ensure your data sources are working correctly.
"""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fred_integration():
    """Test FRED API integration."""
    print("\n" + "="*60)
    print("Testing FRED API Integration")
    print("="*60)

    from rvb.data_sources import get_fred_rates

    try:
        rates = get_fred_rates()
        print(f"\n✅ FRED integration successful!")
        print(f"   Mortgage Rate: {rates['mortgage_rate_annual']:.4f} ({rates['mortgage_rate_annual']*100:.2f}%)")
        print(f"   Inflation Rate: {rates['inflation_annual']:.4f} ({rates['inflation_annual']*100:.2f}%)")
        return True
    except Exception as e:
        print(f"\n❌ FRED integration failed: {e}")
        return False


def test_zillow_integration():
    """Test Zillow data fetching."""
    print("\n" + "="*60)
    print("Testing Zillow Data Integration")
    print("="*60)

    from rvb.data_sources import load_zillow_data_from_url

    test_cities = ["New York", "Austin", "San Francisco"]

    for city in test_cities:
        print(f"\n📍 Testing: {city}")
        try:
            data = load_zillow_data_from_url(city)

            if data['rent_growth_annual'] is not None:
                print(f"   ✅ Rent growth: {data['rent_growth_annual']:.4f} ({data['rent_growth_annual']*100:.2f}%)")
            else:
                print(f"   ⚠️ Rent growth: Not found")

            if data['home_price_growth'] is not None:
                print(f"   ✅ Home price growth: {data['home_price_growth']:.4f} ({data['home_price_growth']*100:.2f}%)")
            else:
                print(f"   ⚠️ Home price growth: Not found")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    return True


def test_combined_scenario():
    """Test a complete rent vs buy scenario with live data."""
    print("\n" + "="*60)
    print("Testing Complete Scenario (New York Example)")
    print("="*60)

    from rvb.data_sources import get_fred_rates, load_zillow_data_from_url

    try:
        # Get FRED rates
        fred_rates = get_fred_rates()

        # Get Zillow data for New York
        zillow_data = load_zillow_data_from_url("New York")

        # Combine parameters
        params = {
            "mortgage_rate_annual": fred_rates['mortgage_rate_annual'],
            "rent_growth_annual": zillow_data.get('rent_growth_annual', 0.03),
            "home_price_growth": zillow_data.get('home_price_growth', 0.025),
            "inflation_annual": fred_rates['inflation_annual'],
        }

        print("\n✅ Combined scenario parameters:")
        for key, value in params.items():
            print(f"   {key}: {value:.4f} ({value*100:.2f}%)")

        return True

    except Exception as e:
        print(f"\n❌ Combined scenario failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🏠"*30)
    print("Rent vs Buy - Data Sources Test Suite")
    print("🏠"*30)

    # Check for .env file
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("\n⚠️ Warning: .env file not found")
        print("   Copy .env.example to .env and add your API keys")
        print("   FRED will fall back to default values if no key is set")

    # Run tests
    results = []
    results.append(("FRED API", test_fred_integration()))
    results.append(("Zillow Data", test_zillow_integration()))
    results.append(("Combined Scenario", test_combined_scenario()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests passed! Your data sources are configured correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please check the output above for details.")
        sys.exit(1)
