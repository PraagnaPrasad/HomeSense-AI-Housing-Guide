#!/usr/bin/env python3
"""
Test script demonstrating the new wealth-based comparison.
Shows how equity building is now properly accounted for.
"""
import sys
import os

# Add the api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/api'))

from app.engine.notebook_full import rent_vs_buy


def format_currency(value):
    """Format number as currency."""
    return f"${value:,.0f}"


def test_equity_tracking():
    """Test the equity tracking and wealth comparison."""

    print("🏠 Equity & Wealth Tracking Test")
    print("=" * 80)
    print()

    # Test scenario: Typical home purchase
    inputs = {
        "home_price": 650000,
        "monthly_rent": 3000,
        "down_payment_pct": 0.20,
        "mortgage_rate_annual": 0.068,
        "property_tax_rate": 0.012,
        "maintenance_rate": 0.01,
        "home_price_growth": 0.03,  # 3% appreciation
        "rent_growth": 0.03,
        "investment_return": 0.07,  # 7% stock market return
        "years": 10
    }

    print("SCENARIO:")
    print(f"  Home Price: {format_currency(inputs['home_price'])}")
    print(f"  Monthly Rent: {format_currency(inputs['monthly_rent'])}")
    print(f"  Down Payment: {inputs['down_payment_pct']:.0%}")
    print(f"  Time Horizon: {inputs['years']} years")
    print(f"  Home Appreciation: {inputs['home_price_growth']:.1%}/year")
    print(f"  Investment Return: {inputs['investment_return']:.1%}/year")
    print()
    print("-" * 80)

    # Run calculation
    result = rent_vs_buy(**inputs)

    print()
    print("📊 RESULTS")
    print("=" * 80)
    print()

    # Section 1: Cash Flow
    print("1️⃣  CASH SPENT (Out-of-Pocket Costs)")
    print("-" * 80)
    print(f"Renting:  {format_currency(result['total_rent_cash_spent'])}")
    print(f"Owning:   {format_currency(result['total_own_cash_spent'])}")
    diff_cash = result['total_own_cash_spent'] - result['total_rent_cash_spent']
    print(f"Difference: {format_currency(abs(diff_cash))} {'more' if diff_cash > 0 else 'less'} for owning")
    print()

    # Section 2: Wealth Accumulation
    print("2️⃣  WEALTH ACCUMULATED")
    print("-" * 80)
    print(f"Renter's Portfolio:  {format_currency(result['renter_net_worth'])}")
    print(f"  (invested {format_currency(result['down_payment'])} down payment")
    print(f"   + monthly savings at {inputs['investment_return']:.1%} return)")
    print()
    print(f"Owner's Home Equity: {format_currency(result['owner_net_worth'])}")
    print(f"  (home value grew from {format_currency(inputs['home_price'])}")
    print(f"   to {format_currency(result['price_series'][-1])}")
    print(f"   minus {format_currency(result['price_series'][-1] - result['owner_net_worth'])} remaining loan + selling costs)")
    print()
    wealth_diff = result['wealth_advantage']
    print(f"Wealth Advantage: {format_currency(abs(wealth_diff))} {'Owner' if wealth_diff > 0 else 'Renter'}")
    print()

    # Section 3: Net Position
    print("3️⃣  NET POSITION (Cash Spent - Wealth Accumulated)")
    print("-" * 80)
    print(f"Renting: {format_currency(result['total_rent_true_cost'])}")
    print(f"  ({format_currency(result['total_rent_cash_spent'])} spent - {format_currency(result['renter_net_worth'])} in portfolio)")
    print()
    print(f"Owning:  {format_currency(result['total_own_true_cost'])}")
    print(f"  ({format_currency(result['total_own_cash_spent'])} spent - {format_currency(result['owner_net_worth'])} in equity)")
    print()

    true_diff = result['total_own_true_cost'] - result['total_rent_true_cost']
    if true_diff < 0:
        print(f"✅ BUYING WINS: {format_currency(abs(true_diff))} better net position")
    elif true_diff > 0:
        print(f"✅ RENTING WINS: {format_currency(abs(true_diff))} better net position")
    else:
        print("⚖️  TIE: Equal net positions")
    print()

    # Section 4: Year-by-year breakdown
    print("4️⃣  YEAR-BY-YEAR WEALTH ACCUMULATION")
    print("-" * 80)
    print(f"{'Year':<6} {'Owner Equity':<18} {'Renter Portfolio':<18} {'Owner Advantage':<18}")
    print("-" * 80)

    for year in range(1, inputs['years'] + 1):
        owner_equity = result['equity_series'][year - 1]
        renter_portfolio = result['renter_savings_series'][year - 1]
        advantage = owner_equity - renter_portfolio

        print(f"{year:<6} {format_currency(owner_equity):<18} {format_currency(renter_portfolio):<18} {format_currency(advantage):<18}")

    print()
    print("=" * 80)

    # Legacy comparison (for reference)
    print()
    print("📝 LEGACY COMPARISON (Old Method)")
    print("-" * 80)
    print("The old method credited equity as a cost reduction in the final year:")
    print(f"  Total 'Rent Paid': {format_currency(result['total_rent_paid'])}")
    print(f"  Total 'Own Paid':  {format_currency(result['total_own_paid'])}")
    print(f"    (This subtracts the {format_currency(result['net_proceeds'])} net proceeds from costs)")
    print()
    print("⚠️  This method is misleading because it doesn't account for:")
    print("   • Opportunity cost of down payment")
    print("   • Renter's ability to invest monthly savings")
    print("   • True wealth accumulation comparison")
    print()
    print("✅ Use the NEW wealth-based comparison above for accurate analysis!")
    print()


if __name__ == "__main__":
    try:
        test_equity_tracking()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
