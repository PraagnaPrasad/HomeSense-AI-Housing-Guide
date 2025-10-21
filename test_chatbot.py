#!/usr/bin/env python3
"""
Test script for the financial advisor chatbot.
Simulates a conversation with the /v1/advise endpoint.
"""
import os
import sys
import json

# Add the api directory to path so we can import the function directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/api'))

from app.engine.notebook_full import ask_advisor


def test_chatbot():
    """Run a sample conversation with the financial advisor chatbot."""

    # Check if API key is set
    if not os.environ.get("PPLX_API_KEY"):
        print("❌ PPLX_API_KEY environment variable not set!")
        print("   Set it with: export PPLX_API_KEY='your-key'")
        return

    print("🏠 Financial Advisor Chatbot Test\n")
    print("=" * 60)

    # Conversation 1: General question without calculations
    print("\n💬 Conversation 1: General advice\n")
    print("User: What are the main factors I should consider when deciding to rent or buy?")
    print("\nAdvisor: ", end="")

    response1 = ask_advisor(
        inputs=None,
        question="What are the main factors I should consider when deciding to rent or buy?"
    )
    print(response1)
    print("\n" + "-" * 60)

    # Conversation 2: With calculation data
    print("\n💬 Conversation 2: Specific scenario analysis\n")

    inputs = {
        "home_price": 650000,
        "monthly_rent": 3000,
        "down_payment_pct": 0.20,
        "mortgage_rate_annual": 0.068,
        "property_tax_rate": 0.012,
        "years_horizon": 10
    }

    print(f"User: I'm looking at a ${inputs['home_price']:,} home vs ${inputs['monthly_rent']:,}/month rent.")
    print(f"      I have 20% down and planning to stay {inputs['years_horizon']} years. What do you recommend?")
    print("\nAdvisor: ", end="")

    response2 = ask_advisor(
        inputs=inputs,
        question=f"I'm looking at a ${inputs['home_price']:,} home vs ${inputs['monthly_rent']:,}/month rent. I have 20% down and planning to stay {inputs['years_horizon']} years. What do you recommend?"
    )
    print(response2)
    print("\n" + "-" * 60)

    # Conversation 3: Follow-up with conversation history
    print("\n💬 Conversation 3: Follow-up question with history\n")

    # Update inputs for new scenario
    inputs_5yr = inputs.copy()
    inputs_5yr["years_horizon"] = 5

    conversation_history = [
        {
            "role": "user",
            "content": f"I'm looking at a ${inputs['home_price']:,} home vs ${inputs['monthly_rent']:,}/month rent. I have 20% down and planning to stay {inputs['years_horizon']} years. What do you recommend?"
        },
        {
            "role": "assistant",
            "content": response2
        }
    ]

    print("User: What if I only plan to stay for 5 years instead of 10?")
    print("\nAdvisor: ", end="")

    response3 = ask_advisor(
        inputs=inputs_5yr,
        question="What if I only plan to stay for 5 years instead of 10?",
        conversation_history=conversation_history
    )
    print(response3)
    print("\n" + "-" * 60)

    # Conversation 4: Another follow-up
    print("\n💬 Conversation 4: Exploring scenarios\n")

    conversation_history.extend([
        {
            "role": "user",
            "content": "What if I only plan to stay for 5 years instead of 10?"
        },
        {
            "role": "assistant",
            "content": response3
        }
    ])

    print("User: What about interest rates? If they drop to 5%, how would that change things?")
    print("\nAdvisor: ", end="")

    inputs_low_rate = inputs.copy()
    inputs_low_rate["mortgage_rate_annual"] = 0.05

    response4 = ask_advisor(
        inputs=inputs_low_rate,
        question="What about interest rates? If they drop to 5%, how would that change things?",
        conversation_history=conversation_history
    )
    print(response4)
    print("\n" + "=" * 60)
    print("\n✅ Chatbot test complete!\n")


if __name__ == "__main__":
    try:
        test_chatbot()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
