"""
Rent vs Buy calculation functions.
This file contains only the core calculation functions needed by the API.
All notebook/demo code has been removed or wrapped in if __name__ == "__main__".
"""
import numpy as np

# sensible defaults (you can tweak later)
DEFAULTS = {
    "mortgage_rate_annual": 0.068,   # 30Y fixed ~6.8%
    "property_tax_rate":    0.012,   # 1.2% of home value per year
    "maintenance_rate":     0.01,    # 1% of home value per year
    "home_price_growth":    0.025,   # 2.5% per year
    "rent_growth":          0.03,    # 3% per year
    "investment_return":    0.04,    # opportunity cost on cash
    "closing_cost_buy":     0.03,    # 3% one-time
    "selling_cost":         0.06,    # 6% at exit
    "insurance_per_year":   1200,    # $/yr
    "years":                10,      # horizon
}

# ---- CELL SEPARATOR ----

def monthly_mortgage_payment(loan, annual_rate, years=30):
    r = annual_rate/12
    n = years*12
    return loan * (r*(1+r)**n) / ((1+r)**n - 1)

def rent_vs_buy(
    home_price, monthly_rent, down_payment_pct,
    mortgage_rate_annual=0.068,
    property_tax_rate=0.012,
    maintenance_rate=0.01,
    home_price_growth=0.025,
    rent_growth=0.03,
    investment_return=0.04,
    closing_cost_buy=0.03,
    selling_cost=0.06,
    insurance_per_year=1200,
    years=10,
    discount_rate=None
):
    # --- Up-front + mortgage setup
    down_payment = home_price * down_payment_pct
    closing_cost = home_price * closing_cost_buy
    loan = home_price - down_payment
    m_payment = monthly_mortgage_payment(loan, mortgage_rate_annual, years=30)

    # --- Time series accumulators
    rent_series_annual = []
    own_series_annual  = []
    equity_series      = []
    price_series       = []

    home_val = home_price
    remaining_loan = loan

    for y in range(1, years+1):
        # Rent that year
        annual_rent = 12 * monthly_rent * ((1 + rent_growth)**(y-1))
        rent_series_annual.append(annual_rent)

        # Owner costs that year
        annual_mortgage = m_payment * 12
        property_tax = property_tax_rate * home_val
        maintenance  = maintenance_rate * home_val
        own_series_annual.append(annual_mortgage + property_tax + maintenance + insurance_per_year)

        # Update home value
        home_val *= (1 + home_price_growth)
        price_series.append(home_val)

        # (Simple principal approximation)
        approx_interest = max(remaining_loan * mortgage_rate_annual, 0)
        approx_principal = max(annual_mortgage - approx_interest, 0)
        remaining_loan = max(remaining_loan - approx_principal, 0)
        equity = home_val - remaining_loan
        equity_series.append(equity)

    # Net sale proceeds at the end of horizon
    net_proceeds = equity_series[-1] - selling_cost * home_val

    # --- Build **equal-length** cashflow arrays (include t=0)
    # Renter: t0 = 0; then annual rents
    rent_cf = [0.0] + rent_series_annual[:]                      # length = years+1

    # Owner: t0 = down + closing; then annual owner costs; subtract sale proceeds in final year
    own_cf  = [down_payment + closing_cost] + own_series_annual[:]  # length = years+1
    own_cf[-1] = own_cf[-1] - net_proceeds                           # apply sale at final year

    # Totals (OLD METHOD - includes equity as cost reduction)
    total_rent_paid = sum(rent_cf)
    total_own_paid  = sum(own_cf)

    # === NEW: WEALTH-BASED COMPARISON ===
    # Calculate total cash spent (without equity credit)
    total_rent_cash_spent = sum(rent_cf)
    total_own_cash_spent = (down_payment + closing_cost) + sum(own_series_annual)

    # Renter's investment portfolio (if they invested down payment + monthly savings)
    renter_savings_series = []
    renter_portfolio = down_payment + closing_cost  # Start with what they didn't spend on down/closing

    for y in range(1, years+1):
        # Monthly difference renter could have saved/invested
        monthly_diff = (own_series_annual[y-1] / 12) - monthly_rent * ((1 + rent_growth)**(y-1))
        annual_savings = max(monthly_diff * 12, 0)  # Only if buying costs more

        # Add savings and compound existing portfolio
        renter_portfolio = renter_portfolio * (1 + investment_return) + annual_savings
        renter_savings_series.append(renter_portfolio)

    # Final wealth positions
    owner_net_worth = net_proceeds  # Equity after selling
    renter_net_worth = renter_portfolio  # Investment portfolio value

    # True cost comparison (cash spent minus wealth accumulated)
    total_rent_true_cost = total_rent_cash_spent - renter_net_worth
    total_own_true_cost = total_own_cash_spent - owner_net_worth

    # Optional NPV
    def npv(cfs, r):
        return sum(cf / ((1+r)**t) for t, cf in enumerate(cfs) if t>0)  # t=0 is same year; discount starts at year 1

    rent_npv = npv(rent_cf, discount_rate) if discount_rate else None
    own_npv  = npv(own_cf,  discount_rate) if discount_rate else None

    # --- Break-even: first year where cumulative own <= cumulative rent
    cum_rent = np.cumsum(rent_cf)   # length years+1
    cum_own  = np.cumsum(own_cf)    # length years+1
    be_idx = np.where(cum_own <= cum_rent)[0]
    break_even_year = int(be_idx[0]) if len(be_idx) > 0 else None  # index corresponds to year number (since t0 included)

    return {
        # Legacy fields (for backwards compatibility)
        "total_rent_paid": float(total_rent_paid),
        "total_own_paid":  float(total_own_paid),

        # New wealth-based comparison
        "total_rent_cash_spent": float(total_rent_cash_spent),
        "total_own_cash_spent": float(total_own_cash_spent),
        "renter_net_worth": float(renter_net_worth),
        "owner_net_worth": float(owner_net_worth),
        "total_rent_true_cost": float(total_rent_true_cost),
        "total_own_true_cost": float(total_own_true_cost),
        "wealth_advantage": float(owner_net_worth - renter_net_worth),  # Positive = owner wins

        # Time series
        "break_even_year": break_even_year if break_even_year != 0 else 1,
        "rent_series":     rent_cf,          # includes t0
        "own_series":      own_cf,           # includes t0
        "equity_series":   equity_series,    # Owner's equity each year
        "renter_savings_series": renter_savings_series,  # Renter's portfolio each year
        "price_series":    price_series,     # Home value each year

        # Financial details
        "net_proceeds":    float(net_proceeds),
        "down_payment":    float(down_payment),
        "closing_cost":    float(closing_cost),

        # NPV (optional)
        "rent_npv":        rent_npv,
        "own_npv":         own_npv,
    }

# ==============================================================================
# All the code below was notebook demonstration code and has been disabled
# to allow this file to be imported as a module without running demo code.
# ==============================================================================

# ---- DEMO CODE REMOVED (was from notebook cells) ----

# ---- CELL SEPARATOR ----

def summarize_rent_vs_buy(inputs, result, params=None):
    """
    Generate a text summary of rent vs buy results.
    """
    years = inputs.get("years", inputs.get("years_horizon", 10))
    be = result.get("break_even_year")
    rent_total = result.get("total_rent_paid", 0.0)
    own_total = result.get("total_own_paid", 0.0)

    # Extract parameters
    if params:
        rate = params.get("mortgage_rate_annual", 0.068)
        rent_g = params.get("rent_growth_annual", params.get("rent_growth", 0.03))
        hp_g = params.get("home_price_growth", 0.025)
        tax = params.get("property_tax_rate", 0.012)
    else:
        rate = inputs.get("mortgage_rate_annual", 0.068)
        rent_g = inputs.get("rent_growth", 0.03)
        hp_g = inputs.get("home_price_growth", 0.025)
        tax = inputs.get("property_tax_rate", 0.012)

    if rent_total < own_total:
        verdict = f"Renting is cheaper by ${own_total - rent_total:,.0f} over {years} years."
    else:
        verdict = f"Buying is cheaper by ${rent_total - own_total:,.0f} over {years} years."

    be_text = f"Break-even year: {be}." if be else "No break-even within the chosen horizon."

    drivers = (
        f"- Mortgage rate: {rate:.2%}\n"
        f"- Rent growth: {rent_g:.2%}\n"
        f"- Home price growth: {hp_g:.2%}\n"
        f"- Property tax: {tax:.2%}"
    )

    return f"""### Decision
{verdict}
{be_text}

### Key drivers
{drivers}

### Notes
Buying generally wins if you stay longer than the break-even point or if rent growth outpaces home appreciation.
Higher mortgage rates or shorter stays make renting more favorable.
"""


def monte_carlo_prob(inputs, sims=1000, seed=None):
    """
    Run Monte Carlo simulation to estimate probability that buying is cheaper.

    Args:
        inputs: Dict with all parameters (must include home_price, monthly_rent, down_payment_pct)
        sims: Number of simulations
        seed: Random seed for reproducibility

    Returns:
        Dict with buy_cheaper_probability and median_break_even_year
    """
    if seed is not None:
        np.random.seed(seed)

    # Extract required parameters
    price = inputs.get("home_price")
    rent = inputs.get("monthly_rent")
    down = inputs.get("down_payment_pct")
    years = inputs.get("years_horizon", inputs.get("years", 10))

    # Get mean values for distributions
    rate_mu = inputs.get("mortgage_rate_annual", 0.068)
    rent_mu = inputs.get("rent_growth", 0.03)
    home_mu = inputs.get("home_price_growth", 0.025)

    # Standard deviations (can be customized)
    rate_sd = 0.004
    rent_sd = 0.01
    home_sd = 0.008

    wins = 0
    bes = []

    for _ in range(sims):
        # Sample parameters from normal distributions
        r = np.clip(np.random.normal(rate_mu, rate_sd), 0.02, 0.09)
        rg = np.clip(np.random.normal(rent_mu, rent_sd), -0.02, 0.08)
        hg = np.clip(np.random.normal(home_mu, home_sd), -0.02, 0.07)

        # Run simulation
        out = rent_vs_buy(
            price, rent, down,
            mortgage_rate_annual=r,
            rent_growth=rg,
            home_price_growth=hg,
            years=years,
            property_tax_rate=inputs.get("property_tax_rate", 0.012),
            maintenance_rate=inputs.get("maintenance_rate", 0.01),
            insurance_per_year=inputs.get("insurance_per_year", 1200),
            closing_cost_buy=inputs.get("closing_cost_buy", 0.03),
            selling_cost=inputs.get("selling_cost", 0.06)
        )

        if out["total_own_paid"] <= out["total_rent_paid"]:
            wins += 1
        if out["break_even_year"]:
            bes.append(out["break_even_year"])

    return {
        "buy_cheaper_probability": wins / sims,
        "median_break_even_year": float(np.median(bes)) if bes else None
    }


# ==============================================================================
# Perplexity AI Integration Functions (API-compatible, no Streamlit dependencies)
# ==============================================================================

import os
import json
import requests


def pplx_advisor_message(inputs, result, params, extra_context=""):
    """
    Uses Perplexity to write a concise advisor-style recommendation from your numbers.
    Falls back to summarize_rent_vs_buy on error.

    Args:
        inputs: Dict with user inputs (home_price, monthly_rent, etc.)
        result: Dict with calculation results from rent_vs_buy()
        params: Dict with parameters used in calculation
        extra_context: Additional context or user question

    Returns:
        String with AI-generated recommendation or fallback summary
    """
    pplx_api_key = os.environ.get("PPLX_API_KEY")

    if not pplx_api_key:
        # No API key, fall back to deterministic summary
        return summarize_rent_vs_buy(inputs, result, params)

    try:
        years = inputs.get("years", inputs.get("years_horizon", 10))
        prompt = f"""
You are a pragmatic housing finance advisor. Be concise (<= 8 bullets).
User context: {extra_context}
Inputs: {inputs}
Parameters: {params}
Results: {{
  "total_rent_paid": {round(result.get('total_rent_paid', 0.0), 2)},
  "total_own_paid":  {round(result.get('total_own_paid', 0.0), 2)},
  "break_even_year": {result.get('break_even_year')},
  "net_proceeds":    {round(result.get('net_proceeds', 0.0), 2)}
}}
Write a clear recommendation:
- State which option is cheaper over {years} years and by how much (rounded, USD).
- Include break-even year (or say none).
- Explain 3–4 key drivers (mortgage rate, rent growth, appreciation, taxes).
- Give 2 short what-if tips (e.g., "If you move in 5 years, renting wins.").
Avoid hedging; be direct and user-friendly.
""".strip()

        headers = {
            "Authorization": f"Bearer {pplx_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 700
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return content

    except Exception as e:
        # On error, fall back to deterministic summary
        return summarize_rent_vs_buy(inputs, result, params) + f"\n\n[Perplexity fallback: {e}]"


def pplx_maybe_block():
    """
    Placeholder for budget checking (can be implemented if needed).
    Returns False (not blocked) by default for API usage.
    """
    return False


def pplx_update_spend_from_usage(usage, fallback_prompt_text="", fallback_completion_text=""):
    """
    Placeholder for spend tracking (can be implemented if needed).
    Does nothing by default for API usage.
    """
    pass


def ask_advisor(inputs, question, conversation_history=None, user_context=None):
    """
    Chat with a financial advisor AI about rent vs buy decisions.

    Args:
        inputs: Dict with current calculation inputs (optional, can be None for general questions)
        question: User's question or message
        conversation_history: List of previous messages [{"role": "user"/"assistant", "content": "..."}]
        user_context: Dict with personal context (age, income, relationship_status, kids, education,
                     property_links, location, job_stability, savings, debt, etc.)

    Returns:
        String with AI-generated advice
    """
    pplx_api_key = os.environ.get("PPLX_API_KEY")

    if not pplx_api_key:
        return "Perplexity API key not configured. Please set PPLX_API_KEY environment variable."

    try:
        # Build context from inputs if provided
        context_parts = []

        # Add personal context if provided
        if user_context:
            context_parts.append("=== USER PERSONAL CONTEXT ===")

            # Demographics
            if user_context.get("age"):
                context_parts.append(f"Age: {user_context['age']}")
            if user_context.get("relationship_status"):
                context_parts.append(f"Relationship: {user_context['relationship_status']}")
            if user_context.get("kids"):
                kids_info = user_context['kids']
                if isinstance(kids_info, bool):
                    context_parts.append(f"Has children: {'Yes' if kids_info else 'No'}")
                else:
                    context_parts.append(f"Children: {kids_info}")

            # Financial situation
            if user_context.get("annual_income"):
                context_parts.append(f"Annual income: ${user_context['annual_income']:,.0f}")
            if user_context.get("savings"):
                context_parts.append(f"Savings: ${user_context['savings']:,.0f}")
            if user_context.get("debt"):
                context_parts.append(f"Current debt: ${user_context['debt']:,.0f}")
            if user_context.get("credit_score"):
                context_parts.append(f"Credit score: {user_context['credit_score']}")

            # Career & Education
            if user_context.get("education"):
                context_parts.append(f"Education: {user_context['education']}")
            if user_context.get("job_stability"):
                context_parts.append(f"Job stability: {user_context['job_stability']}")
            if user_context.get("career_stage"):
                context_parts.append(f"Career stage: {user_context['career_stage']}")

            # Location & Lifestyle
            if user_context.get("location"):
                context_parts.append(f"Location: {user_context['location']}")
            if user_context.get("work_situation"):
                context_parts.append(f"Work: {user_context['work_situation']}")
            if user_context.get("lifestyle_priorities"):
                context_parts.append(f"Priorities: {user_context['lifestyle_priorities']}")

            # Property links
            if user_context.get("property_links"):
                links = user_context['property_links']
                if isinstance(links, list):
                    context_parts.append(f"Property links: {', '.join(links)}")
                else:
                    context_parts.append(f"Property link: {links}")

            # Any additional notes
            if user_context.get("additional_info"):
                context_parts.append(f"Additional context: {user_context['additional_info']}")

            context_parts.append("")  # Empty line separator

        if inputs and inputs.get("home_price") and inputs.get("monthly_rent"):
            # Only run calculation if we have the required inputs
            result = rent_vs_buy(
                inputs.get("home_price"),
                inputs.get("monthly_rent"),
                inputs.get("down_payment_pct", 0.20),
                mortgage_rate_annual=inputs.get("mortgage_rate_annual", 0.068),
                property_tax_rate=inputs.get("property_tax_rate", 0.012),
                maintenance_rate=inputs.get("maintenance_rate", 0.01),
                home_price_growth=inputs.get("home_price_growth", 0.025),
                rent_growth=inputs.get("rent_growth", 0.03),
                investment_return=inputs.get("investment_return", 0.04),
                closing_cost_buy=inputs.get("closing_cost_buy", 0.03),
                selling_cost=inputs.get("selling_cost", 0.06),
                insurance_per_year=inputs.get("insurance_per_year", 1200),
                years=inputs.get("years_horizon", inputs.get("years", 10))
            )

            years = inputs.get("years", inputs.get("years_horizon", 10))
            rent_total = result.get("total_rent_paid", 0.0)
            own_total = result.get("total_own_paid", 0.0)
            be_year = result.get("break_even_year")

            context_parts.append("=== FINANCIAL SCENARIO ===")
            context_parts.append(f"Home price: ${inputs.get('home_price', 0):,.0f}")
            context_parts.append(f"Monthly rent: ${inputs.get('monthly_rent', 0):,.0f}")
            context_parts.append(f"Down payment: {inputs.get('down_payment_pct', 0.20):.0%}")
            context_parts.append(f"Mortgage rate: {inputs.get('mortgage_rate_annual', 0.068):.2%}")
            context_parts.append(f"Time horizon: {years} years")

            if inputs.get("city") or inputs.get("location"):
                loc = inputs.get("city") or inputs.get("location")
                context_parts.append(f"Location: {loc}")

            context_parts.append(f"\n=== CALCULATION RESULTS ===")

            # Cash flow comparison
            context_parts.append(f"CASH SPENT:")
            context_parts.append(f"  • Renting: ${result.get('total_rent_cash_spent', 0):,.0f}")
            context_parts.append(f"  • Owning: ${result.get('total_own_cash_spent', 0):,.0f}")

            # Wealth accumulation
            context_parts.append(f"\nWEALTH ACCUMULATED:")
            context_parts.append(f"  • Renter (invested savings): ${result.get('renter_net_worth', 0):,.0f}")
            context_parts.append(f"  • Owner (home equity): ${result.get('owner_net_worth', 0):,.0f}")

            # Net position
            wealth_adv = result.get('wealth_advantage', 0)
            true_rent_cost = result.get('total_rent_true_cost', 0)
            true_own_cost = result.get('total_own_true_cost', 0)

            context_parts.append(f"\nNET POSITION (Cash Spent - Wealth):")
            context_parts.append(f"  • Renting: ${true_rent_cost:,.0f}")
            context_parts.append(f"  • Owning: ${true_own_cost:,.0f}")

            if wealth_adv > 0:
                context_parts.append(f"\n💰 OWNER ADVANTAGE: ${wealth_adv:,.0f} more wealth")
            elif wealth_adv < 0:
                context_parts.append(f"\n💰 RENTER ADVANTAGE: ${abs(wealth_adv):,.0f} more wealth")
            else:
                context_parts.append(f"\n⚖️  Equal wealth outcomes")

            if be_year:
                context_parts.append(f"\nBreak-even year: {be_year}")
            else:
                context_parts.append(f"No break-even within {years} years")

        context_str = "\n".join(context_parts) if context_parts else ""

        # Enhanced system prompt with personal context awareness
        system_prompt = """You are an expert financial advisor specializing in real estate and personalized housing decisions.

GREETING & CASUAL CONVERSATION:
- Respond warmly to greetings (hi, hello, hey, etc.)
- Be friendly and conversational
- If they're just starting, introduce yourself briefly and ask how you can help with their housing decision
- Keep greetings short and natural - don't launch into a speech

WHEN NO NUMBERS ARE PROVIDED:
- Ask helpful questions to understand their situation
- Explore what they're thinking about (buying, renting, unsure)
- Understand their timeline and what's prompting the question
- Don't make assumptions - gather context first

Your role is to provide holistic, life-stage-appropriate advice by:
- Analyzing the user's complete life situation (age, income, family, career, lifestyle)
- Considering their financial capacity (income, savings, debt, credit)
- Factoring in life goals and timeline (career growth, family plans, flexibility needs)
- Evaluating location-specific factors and market conditions
- Reviewing property links when provided (Zillow, StreetEasy, etc.) for market insights
- Explaining trade-offs between financial optimization and life quality

IMPORTANT CONSIDERATIONS BY LIFE STAGE:
- Young professionals (20s-early 30s): Prioritize flexibility, career mobility, debt management
- Established professionals (30s-40s): Balance stability with opportunity cost, consider family needs
- Families with kids: Emphasize school districts, space needs, long-term stability
- Pre-retirement (50s-60s): Consider downsizing, equity building, fixed income planning

PERSONALIZATION FACTORS:
- Job stability: Less stable = favor renting for flexibility
- Family plans: Expecting kids soon? Consider school districts and space
- Income trajectory: High growth potential = can absorb mortgage risk
- Debt levels: High debt = wait and build savings first
- Location: High-cost cities = longer break-even periods
- Lifestyle: Value travel/flexibility? Renting may fit better

RESPONSE STYLE:
- Be conversational, warm, and empathetic
- Reference their specific situation (age, family, career) in advice
- Provide 2-3 concrete, actionable recommendations
- Mention both financial AND lifestyle considerations
- Keep responses focused (2-4 paragraphs)
- Use specific numbers from calculations when available
- Acknowledge uncertainty and give ranges when appropriate
- Never judge their choices or circumstances

When property links are provided, you can search for market insights, neighborhood trends, and property-specific considerations."""

        # Build messages for Perplexity
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # For now, don't include conversation history to avoid message ordering issues
        # TODO: Properly format conversation history to ensure user/assistant alternation

        # Add current context and question
        if context_str.strip():
            # We have context (calculations and/or personal info)
            user_message = f"{context_str}\n\n=== USER QUESTION ===\n{question}"
        else:
            # No context - just the question (e.g., greeting or general question)
            user_message = question

        messages.append({"role": "user", "content": user_message})

        # Call Perplexity API
        headers = {
            "Authorization": f"Bearer {pplx_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar",
            "messages": messages,
            "temperature": 0.7,  # Higher temperature for more conversational responses
            "max_tokens": 800
        }

        print(f"[DEBUG] Sending to Perplexity API:")
        print(f"[DEBUG] Messages count: {len(messages)}")
        print(f"[DEBUG] Payload: {payload}")

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if not response.ok:
            error_detail = response.text
            print(f"[DEBUG] API Error Response: {error_detail}")
            raise Exception(f"Perplexity API error: {response.status_code} - {error_detail}")
        
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return content

    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}")
        return f"Error generating advice: {str(e)}"


def advise_city(city, price, rent, down=0.20, years=10, note=""):
    """
    Run rent vs buy calculation for a specific city and get AI advice.

    Args:
        city: City name
        price: Home price
        rent: Monthly rent
        down: Down payment percentage
        years: Investment horizon
        note: Additional context

    Returns:
        Dict with calculation results
    """
    # Note: Zillow growth integration would go here if implemented
    # For now, use default growth rates

    inputs = {
        "home_price": price,
        "monthly_rent": rent,
        "down_payment_pct": down,
        "years": years,
        "city": city
    }

    result = rent_vs_buy(
        price, rent, down,
        years=years
    )

    # Get AI advice
    advice = pplx_advisor_message(inputs, result, DEFAULTS, extra_context=note or f"City={city}")

    return {
        "advice": advice,
        "result": result
    }


# ==============================================================================
# All code below here was notebook demonstration/example code - disabled
# ==============================================================================

if __name__ == "__main__":
    # Example usage (only runs if this file is executed directly)
    home_price   = 650_000
    print("Example code removed - functions available for import")
