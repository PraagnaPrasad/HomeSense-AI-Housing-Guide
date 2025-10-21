#!/usr/bin/env python3
"""
Test script for the enhanced personalized financial advisor chatbot.
Demonstrates how personal context makes advice more relevant.
"""
import os
import sys
import json

# Add the api directory to path so we can import the function directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/api'))

from app.engine.notebook_full import ask_advisor


def test_personalized_chatbot():
    """Run sample conversations with different personal contexts."""

    # Check if API key is set
    if not os.environ.get("PPLX_API_KEY"):
        print("❌ PPLX_API_KEY environment variable not set!")
        print("   Set it with: export PPLX_API_KEY='your-key'")
        return

    print("🏠 Personalized Financial Advisor Chatbot Test\n")
    print("=" * 80)

    # =========================================================================
    # Scenario 1: Young professional, early career
    # =========================================================================
    print("\n📋 SCENARIO 1: Young Professional in Tech\n")
    print("-" * 80)

    user_context_1 = {
        "age": 28,
        "annual_income": 150000,
        "relationship_status": "single",
        "kids": False,
        "education": "Bachelor's in Computer Science",
        "job_stability": "startup",
        "career_stage": "early career",
        "savings": 80000,
        "debt": 25000,  # student loans
        "location": "San Francisco, CA",
        "work_situation": "hybrid (3 days office)",
        "lifestyle_priorities": "career growth and flexibility",
        "property_links": "https://www.zillow.com/homedetails/123-Main-St-San-Francisco-CA-94103/example",
        "additional_info": "Might relocate for better opportunities in 2-3 years"
    }

    inputs_1 = {
        "home_price": 900000,
        "monthly_rent": 3500,
        "down_payment_pct": 0.20,
        "mortgage_rate_annual": 0.068,
        "years_horizon": 7
    }

    print("User Profile:")
    print(f"  • 28yo single tech professional")
    print(f"  • Income: $150k, Savings: $80k, Debt: $25k")
    print(f"  • Works at startup, considering relocation in 2-3 years")
    print(f"  • Location: San Francisco")
    print(f"\nProperty Details:")
    print(f"  • Home: $900k vs Rent: $3,500/mo")
    print(f"  • 20% down, 7-year horizon")

    question_1 = "I'm looking at buying my first home. Given my situation, should I buy now or keep renting?"

    print(f"\nUser: {question_1}")
    print("\nAdvisor: ", end="")

    response_1 = ask_advisor(
        inputs=inputs_1,
        question=question_1,
        user_context=user_context_1
    )
    print(response_1)
    print("\n" + "=" * 80)

    # =========================================================================
    # Scenario 2: Married couple with young kids
    # =========================================================================
    print("\n📋 SCENARIO 2: Married Couple with Young Kids\n")
    print("-" * 80)

    user_context_2 = {
        "age": 36,
        "annual_income": 180000,  # combined household income
        "relationship_status": "married",
        "kids": "2 kids (ages 3 and 5)",
        "education": "Both have Master's degrees",
        "job_stability": "stable",
        "career_stage": "mid-career",
        "savings": 150000,
        "debt": 15000,  # car loan
        "credit_score": 780,
        "location": "Austin, TX",
        "work_situation": "both remote",
        "lifestyle_priorities": "good schools, outdoor space, long-term stability",
        "property_links": [
            "https://www.zillow.com/homedetails/456-Oak-Ave-Austin-TX-78704/example",
            "https://www.zillow.com/homedetails/789-Elm-St-Austin-TX-78704/example"
        ],
        "additional_info": "Planning to stay in Austin long-term, need space for growing family"
    }

    inputs_2 = {
        "home_price": 550000,
        "monthly_rent": 2800,
        "down_payment_pct": 0.25,
        "mortgage_rate_annual": 0.065,
        "years_horizon": 15,
        "location": "Austin, TX"
    }

    print("User Profile:")
    print(f"  • 36yo married couple with 2 young kids (3yo, 5yo)")
    print(f"  • Household income: $180k, Savings: $150k")
    print(f"  • Both remote workers, stable jobs")
    print(f"  • High credit score (780)")
    print(f"  • Looking at 2 properties in Austin")
    print(f"\nProperty Details:")
    print(f"  • Home: $550k vs Rent: $2,800/mo")
    print(f"  • 25% down, 15-year horizon")

    question_2 = "We're tired of renting and want space for our kids. We're looking at these two properties - should we buy now? What should we prioritize?"

    print(f"\nUser: {question_2}")
    print("\nAdvisor: ", end="")

    response_2 = ask_advisor(
        inputs=inputs_2,
        question=question_2,
        user_context=user_context_2
    )
    print(response_2)
    print("\n" + "=" * 80)

    # =========================================================================
    # Scenario 3: Pre-retirement professional
    # =========================================================================
    print("\n📋 SCENARIO 3: Pre-Retirement Professional\n")
    print("-" * 80)

    user_context_3 = {
        "age": 58,
        "annual_income": 140000,
        "relationship_status": "married",
        "kids": "adult children (independent)",
        "education": "MBA",
        "job_stability": "stable, planning retirement at 65",
        "career_stage": "senior executive",
        "savings": 450000,
        "debt": 0,
        "credit_score": 820,
        "location": "Denver, CO",
        "work_situation": "in-office",
        "lifestyle_priorities": "downsizing, low maintenance, retirement planning",
        "property_links": "https://www.zillow.com/homedetails/321-Mountain-View-Denver-CO-80202/example",
        "additional_info": "Currently own larger home, considering downsizing before retirement"
    }

    inputs_3 = {
        "home_price": 475000,
        "monthly_rent": 2400,
        "down_payment_pct": 0.40,  # larger down payment available
        "mortgage_rate_annual": 0.062,
        "years_horizon": 10,
        "location": "Denver, CO"
    }

    print("User Profile:")
    print(f"  • 58yo married couple, kids independent")
    print(f"  • Income: $140k, Savings: $450k, No debt")
    print(f"  • Planning retirement at 65")
    print(f"  • Currently own larger home")
    print(f"\nProperty Details:")
    print(f"  • Smaller home: $475k vs Rent: $2,400/mo")
    print(f"  • 40% down possible, 10-year horizon")

    question_3 = "We're thinking of downsizing from our current home. Should we buy a smaller place or rent and use the equity for retirement?"

    print(f"\nUser: {question_3}")
    print("\nAdvisor: ", end="")

    response_3 = ask_advisor(
        inputs=inputs_3,
        question=question_3,
        user_context=user_context_3
    )
    print(response_3)
    print("\n" + "=" * 80)

    # =========================================================================
    # Scenario 4: Recent grad with property link
    # =========================================================================
    print("\n📋 SCENARIO 4: Recent Graduate\n")
    print("-" * 80)

    user_context_4 = {
        "age": 24,
        "annual_income": 75000,
        "relationship_status": "single",
        "kids": False,
        "education": "Bachelor's degree (graduated 2 years ago)",
        "job_stability": "stable but early in career",
        "career_stage": "entry-level",
        "savings": 35000,
        "debt": 45000,  # student loans
        "credit_score": 680,
        "location": "Brooklyn, NY",
        "work_situation": "in-office",
        "lifestyle_priorities": "social life, city living, career development",
        "property_links": "https://streeteasy.com/building/123-bedford-ave-brooklyn/1a",
        "additional_info": "First time looking at real estate, parents suggesting I buy"
    }

    inputs_4 = {
        "home_price": 650000,
        "monthly_rent": 2600,
        "down_payment_pct": 0.05,  # FHA loan
        "mortgage_rate_annual": 0.07,
        "years_horizon": 5,
        "location": "Brooklyn, NY"
    }

    print("User Profile:")
    print(f"  • 24yo recent grad, 2 years in workforce")
    print(f"  • Income: $75k, Savings: $35k, Student loans: $45k")
    print(f"  • Credit score: 680")
    print(f"  • Parents encouraging them to buy")
    print(f"  • Looking at StreetEasy listing")
    print(f"\nProperty Details:")
    print(f"  • Brooklyn condo: $650k vs Rent: $2,600/mo")
    print(f"  • 5% down (FHA), 5-year horizon")

    question_4 = "My parents keep saying I'm 'throwing money away' on rent and I should buy this place. I found this condo on StreetEasy. Is this a good idea for me?"

    print(f"\nUser: {question_4}")
    print("\nAdvisor: ", end="")

    response_4 = ask_advisor(
        inputs=inputs_4,
        question=question_4,
        user_context=user_context_4
    )
    print(response_4)
    print("\n" + "=" * 80)

    print("\n✅ All personalized chatbot tests complete!\n")
    print("Notice how the advice changes based on:")
    print("  • Life stage (young pro vs family vs pre-retirement)")
    print("  • Financial situation (income, savings, debt)")
    print("  • Career stability and trajectory")
    print("  • Family circumstances")
    print("  • Lifestyle priorities")
    print("  • Time horizon and goals")
    print()


if __name__ == "__main__":
    try:
        test_personalized_chatbot()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
