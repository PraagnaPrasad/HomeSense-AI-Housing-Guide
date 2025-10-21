"""
Enhanced results formatter for rent vs buy calculator.
Provides structured output for frontend display similar to the reference design.
"""
import numpy as np


def format_results_for_display(inputs, result):
    """
    Format calculation results for rich frontend display.

    Args:
        inputs: Dict with user inputs (home_price, monthly_rent, etc.)
        result: Dict with calculation results from rent_vs_buy()

    Returns:
        Dict with formatted results for UI display
    """
    years = inputs.get("years_horizon", inputs.get("years", 10))
    home_price = inputs.get("home_price", 0)
    monthly_rent = inputs.get("monthly_rent", 0)
    down_pct = inputs.get("down_payment_pct", 0.20)

    # Extract key metrics
    break_even = result.get("break_even_year")
    equity_final = result.get("owner_net_worth", 0)

    # Calculate total cost difference (who wins?)
    rent_true_cost = result.get("total_rent_true_cost", 0)
    own_true_cost = result.get("total_own_true_cost", 0)
    cost_difference = own_true_cost - rent_true_cost

    # Who's the winner?
    winner = "renting" if cost_difference > 0 else "buying"

    # Generate recommendation
    recommendation = generate_recommendation(
        winner=winner,
        cost_difference=abs(cost_difference),
        break_even=break_even,
        years=years,
        inputs=inputs,
        result=result
    )

    # Build cumulative cost series for chart
    cumulative_data = build_cumulative_series(result, years)

    # Key metrics for display
    key_metrics = {
        "break_even": {
            "years": break_even if break_even else None,
            "label": f"{break_even} years" if break_even else "Not reached",
            "description": f"after {years} years" if not break_even else None
        },
        "total_cost": {
            "renting": float(rent_true_cost),
            "buying": float(own_true_cost),
            "difference": float(abs(cost_difference)),
            "winner": winner,
            "label": f"${abs(cost_difference):,.0f}",
            "description": f"{'less' if winner == 'buying' else 'more'} to buy"
        },
        "home_equity": {
            "value": float(equity_final),
            "label": f"${equity_final:,.0f}",
            "percentage": f"{(equity_final / home_price * 100):.1f}%" if home_price > 0 else "0%"
        },
        "maintenance": {
            "rate": inputs.get("maintenance_rate", 0.01),
            "label": f"{inputs.get('maintenance_rate', 0.01):.1%}",
            "annual_cost": float(home_price * inputs.get("maintenance_rate", 0.01))
        }
    }

    # Wealth comparison
    wealth_metrics = {
        "renter_portfolio": {
            "value": float(result.get("renter_net_worth", 0)),
            "label": f"${result.get('renter_net_worth', 0):,.0f}",
            "description": "Investment portfolio"
        },
        "owner_equity": {
            "value": float(result.get("owner_net_worth", 0)),
            "label": f"${result.get('owner_net_worth', 0):,.0f}",
            "description": "Home equity"
        },
        "wealth_advantage": {
            "value": float(result.get("wealth_advantage", 0)),
            "label": f"${abs(result.get('wealth_advantage', 0)):,.0f}",
            "winner": "owner" if result.get("wealth_advantage", 0) > 0 else "renter"
        }
    }

    # Cash flow breakdown
    cash_flow = {
        "rent": {
            "total": float(result.get("total_rent_cash_spent", 0)),
            "monthly_avg": float(result.get("total_rent_cash_spent", 0) / (years * 12)),
            "yearly_avg": float(result.get("total_rent_cash_spent", 0) / years)
        },
        "own": {
            "down_payment": float(result.get("down_payment", 0)),
            "closing_costs": float(result.get("closing_cost", 0)),
            "total": float(result.get("total_own_cash_spent", 0)),
            "monthly_avg": float((result.get("total_own_cash_spent", 0) - result.get("down_payment", 0) - result.get("closing_cost", 0)) / (years * 12)),
            "yearly_avg": float(result.get("total_own_cash_spent", 0) / years)
        }
    }

    return {
        "summary": {
            "winner": winner,
            "cost_difference": float(abs(cost_difference)),
            "break_even_year": break_even,
            "time_horizon_years": years
        },
        "key_metrics": key_metrics,
        "wealth_metrics": wealth_metrics,
        "cash_flow": cash_flow,
        "chart_data": cumulative_data,
        "recommendation": recommendation,
        "raw_results": result  # Include full results for advanced users
    }


def build_cumulative_series(result, years):
    """
    Build cumulative cost series for charting.
    Returns data in format ready for frontend charts.
    """
    rent_series = result.get("rent_series", [])
    own_series = result.get("own_series", [])

    # Cumulative sums
    cumulative_rent = np.cumsum(rent_series).tolist()
    cumulative_own = np.cumsum(own_series).tolist()

    # Build year labels
    year_labels = list(range(len(cumulative_rent)))

    return {
        "labels": year_labels,
        "datasets": [
            {
                "name": "Renting",
                "data": [float(x) for x in cumulative_rent],
                "color": "#ef4444",  # Red
                "description": "Total rent paid over time"
            },
            {
                "name": "Buying",
                "data": [float(x) for x in cumulative_own],
                "color": "#3b82f6",  # Blue
                "description": "Total ownership costs (including equity credit)"
            }
        ],
        "crossover_point": result.get("break_even_year")
    }


def generate_recommendation(winner, cost_difference, break_even, years, inputs, result):
    """
    Generate a smart recommendation based on the results.
    """
    home_price = inputs.get("home_price", 0)
    monthly_rent = inputs.get("monthly_rent", 0)
    down_pct = inputs.get("down_payment_pct", 0.20)
    mortgage_rate = inputs.get("mortgage_rate_annual", 0.068)

    # Build recommendation text
    recommendations = []

    # Primary recommendation
    if winner == "buying":
        recommendations.append({
            "type": "primary",
            "title": "Buying is better in the long run",
            "text": f"Over {years} years, buying saves ${cost_difference:,.0f} compared to renting.",
            "icon": "home"
        })

        # Add break-even context
        if break_even and break_even <= years:
            recommendations.append({
                "type": "info",
                "title": f"Break-even at year {break_even}",
                "text": f"You'll start saving money after {break_even} years. Plan to stay at least this long.",
                "icon": "calendar"
            })

        # Suggest optimizations
        if down_pct < 0.20:
            recommendations.append({
                "type": "suggestion",
                "title": "Consider a higher down payment",
                "text": f"Increasing from {down_pct:.0%} to 20% would eliminate PMI and reduce your monthly payment.",
                "icon": "arrow-up"
            })
    else:
        recommendations.append({
            "type": "primary",
            "title": "Renting is more cost-effective",
            "text": f"Renting saves ${cost_difference:,.0f} over {years} years, giving you more financial flexibility.",
            "icon": "piggy-bank"
        })

        # Explain why
        wealth_adv = result.get("wealth_advantage", 0)
        if wealth_adv < 0:  # Renter has more wealth
            recommendations.append({
                "type": "info",
                "title": "Better wealth building",
                "text": f"By investing your down payment, you'd have ${abs(wealth_adv):,.0f} more wealth than owning.",
                "icon": "trending-up"
            })

        # Timeline consideration
        if not break_even or break_even > years:
            recommendations.append({
                "type": "warning",
                "title": "Short time horizon",
                "text": f"You won't break even within {years} years. Buying makes more sense if you stay longer.",
                "icon": "clock"
            })

    # Market-specific advice
    if mortgage_rate > 0.065:
        recommendations.append({
            "type": "warning",
            "title": "High mortgage rate",
            "text": f"At {mortgage_rate:.1%}, consider waiting for rates to drop or looking for adjustable rate options.",
            "icon": "alert-circle"
        })

    # Opportunity cost consideration
    investment_return = inputs.get("investment_return", 0.04)
    home_growth = inputs.get("home_price_growth", 0.025)
    if investment_return > home_growth + 0.02:  # 2% buffer
        recommendations.append({
            "type": "info",
            "title": "Strong investment alternative",
            "text": f"Stock market returns ({investment_return:.1%}) significantly exceed home appreciation ({home_growth:.1%}).",
            "icon": "bar-chart"
        })

    return {
        "summary": recommendations[0]["text"] if recommendations else "Results are close. Consider your personal circumstances.",
        "items": recommendations,
        "confidence": calculate_confidence(cost_difference, years, break_even)
    }


def calculate_confidence(cost_difference, years, break_even):
    """
    Calculate confidence level in the recommendation (0-100).
    Higher when the difference is large and break-even is clear.
    """
    # Base confidence on cost difference as % of typical spending
    typical_annual_cost = 36000  # ~$3k/month rent
    diff_pct = abs(cost_difference) / (typical_annual_cost * years)

    # Scale to 0-100
    confidence = min(diff_pct * 100, 95)  # Cap at 95%

    # Reduce if no break-even (indicates close race)
    if not break_even:
        confidence *= 0.7

    # Reduce if break-even is late
    if break_even and break_even > years * 0.8:
        confidence *= 0.8

    return int(confidence)


# Preset display configurations
DISPLAY_CONFIGS = {
    "minimal": {
        "show_metrics": ["break_even", "total_cost"],
        "show_chart": False,
        "show_wealth": False
    },
    "standard": {
        "show_metrics": ["break_even", "total_cost", "home_equity"],
        "show_chart": True,
        "show_wealth": False
    },
    "detailed": {
        "show_metrics": ["break_even", "total_cost", "home_equity", "maintenance"],
        "show_chart": True,
        "show_wealth": True
    }
}
