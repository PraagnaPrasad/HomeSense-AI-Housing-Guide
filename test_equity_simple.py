#!/usr/bin/env python3
"""
Simple equity tracking demonstration.
Shows the wealth-based comparison without needing full app dependencies.
"""
import numpy as np


def monthly_mortgage_payment(loan, annual_rate, years=30):
    r = annual_rate/12
    n = years*12
    return loan * (r*(1+r)**n) / ((1+r)**n - 1)


def rent_vs_buy_simple(home_price, monthly_rent, down_payment_pct=0.20,
                       mortgage_rate=0.068, years=10, home_growth=0.03,
                       rent_growth=0.03, investment_return=0.07):
    """Simplified rent vs buy with wealth tracking."""

    # Setup
    down_payment = home_price * down_payment_pct
    closing_cost = home_price * 0.03
    loan = home_price - down_payment
    monthly_payment = monthly_mortgage_payment(loan, mortgage_rate)

    # Track wealth year by year
    home_value = home_price
    remaining_loan = loan
    owner_equity = []
    renter_portfolio = down_payment + closing_cost  # What renter didn't spend
    renter_wealth = []

    total_rent_paid = 0
    total_own_paid = down_payment + closing_cost

    for year in range(1, years + 1):
        # Rent costs
        annual_rent = 12 * monthly_rent * ((1 + rent_growth) ** (year - 1))
        total_rent_paid += annual_rent

        # Own costs
        annual_mortgage = monthly_payment * 12
        property_tax = 0.012 * home_value
        maintenance = 0.01 * home_value
        insurance = 1200
        annual_own = annual_mortgage + property_tax + maintenance + insurance
        total_own_paid += annual_own

        # Home value and equity
        home_value *= (1 + home_growth)
        principal_paid = max(annual_mortgage - (remaining_loan * mortgage_rate), 0)
        remaining_loan = max(remaining_loan - principal_paid, 0)
        equity = home_value - remaining_loan
        owner_equity.append(equity)

        # Renter's investment portfolio
        monthly_diff = max((annual_own / 12) - (annual_rent / 12), 0)
        annual_savings = monthly_diff * 12
        renter_portfolio = renter_portfolio * (1 + investment_return) + annual_savings
        renter_wealth.append(renter_portfolio)

    # Final positions
    selling_cost = 0.06 * home_value
    owner_net_worth = equity - selling_cost
    renter_net_worth = renter_portfolio

    return {
        "total_rent_paid": total_rent_paid,
        "total_own_paid": total_own_paid,
        "owner_equity": owner_equity,
        "renter_portfolio": renter_wealth,
        "owner_net_worth": owner_net_worth,
        "renter_net_worth": renter_net_worth,
        "wealth_advantage": owner_net_worth - renter_net_worth,
        "home_value_final": home_value
    }


def main():
    print("🏠 Equity & Wealth Tracking Demonstration")
    print("=" * 80)
    print()

    # Scenario
    home_price = 650000
    monthly_rent = 3000
    years = 10

    print("SCENARIO:")
    print(f"  Home Price: ${home_price:,}")
    print(f"  Monthly Rent: ${monthly_rent:,}")
    print(f"  Down Payment: 20%")
    print(f"  Time Horizon: {years} years")
    print(f"  Home Appreciation: 3%/year")
    print(f"  Investment Return: 7%/year")
    print()

    result = rent_vs_buy_simple(home_price, monthly_rent, years=years)

    print("=" * 80)
    print()
    print("📊 RESULTS")
    print()

    # Cash spent
    print("💸 CASH SPENT")
    print(f"  Renting:  ${result['total_rent_paid']:,.0f}")
    print(f"  Owning:   ${result['total_own_paid']:,.0f}")
    diff = result['total_own_paid'] - result['total_rent_paid']
    print(f"  Owner spent ${abs(diff):,.0f} {'more' if diff > 0 else 'less'}")
    print()

    # Wealth accumulated
    print("💰 WEALTH ACCUMULATED")
    print(f"  Renter's Portfolio:  ${result['renter_net_worth']:,.0f}")
    print(f"  Owner's Home Equity: ${result['owner_net_worth']:,.0f}")
    print(f"  (Home value: ${result['home_value_final']:,.0f})")
    print()

    wealth_adv = result['wealth_advantage']
    if wealth_adv > 0:
        print(f"  ✅ Owner has ${wealth_adv:,.0f} MORE wealth")
    else:
        print(f"  ✅ Renter has ${abs(wealth_adv):,.0f} MORE wealth")
    print()

    # Net position
    rent_net = result['total_rent_paid'] - result['renter_net_worth']
    own_net = result['total_own_paid'] - result['owner_net_worth']

    print("📈 NET POSITION (Cash Spent - Wealth)")
    print(f"  Renting: ${rent_net:,.0f}")
    print(f"  Owning:  ${own_net:,.0f}")
    print()

    if own_net < rent_net:
        print(f"  🎯 BUYING WINS by ${rent_net - own_net:,.0f}")
    else:
        print(f"  🎯 RENTING WINS by ${own_net - rent_net:,.0f}")
    print()

    # Year by year
    print("=" * 80)
    print()
    print("YEAR-BY-YEAR WEALTH ACCUMULATION")
    print()
    print(f"{'Year':<6} {'Owner Equity':<18} {'Renter Portfolio':<18} {'Difference':<18}")
    print("-" * 72)

    for year in range(years):
        owner_eq = result['owner_equity'][year]
        renter_port = result['renter_portfolio'][year]
        diff = owner_eq - renter_port

        print(f"{year+1:<6} ${owner_eq:>13,.0f}     ${renter_port:>13,.0f}     ${diff:>13,.0f}")

    print()
    print("=" * 80)
    print()
    print("KEY INSIGHTS:")
    print("  • Owner builds equity through principal paydown + appreciation")
    print("  • Renter builds wealth by investing down payment + monthly savings")
    print("  • The winner depends on: appreciation rate vs investment returns")
    print("  • Higher investment returns favor renting")
    print("  • Higher home appreciation favors buying")
    print()


if __name__ == "__main__":
    main()
