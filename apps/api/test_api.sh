#!/bin/bash
# Test script for Rent vs Buy API

API_URL="http://localhost:8080"

echo "🏠 Rent vs Buy API Test Suite"
echo "=============================="
echo ""

# Test 1: Health Check
echo "1️⃣ Testing Health Endpoint..."
curl -s $API_URL/healthz | python3 -m json.tool
echo ""
echo ""

# Test 2: Compute Endpoint
echo "2️⃣ Testing Compute Endpoint..."
curl -s -X POST $API_URL/v1/compute \
  -H "Content-Type: application/json" \
  -d '{
    "home_price": 650000,
    "monthly_rent": 2800,
    "down_payment_pct": 0.20,
    "years_horizon": 10
  }' | python3 -m json.tool | head -60
echo ""
echo ""

# Test 3: Monte Carlo Simulation
echo "3️⃣ Testing Monte Carlo Simulation..."
curl -s -X POST $API_URL/v1/monte-carlo \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "home_price": 650000,
      "monthly_rent": 2800,
      "down_payment_pct": 0.20,
      "years_horizon": 10
    },
    "sims": 1000,
    "seed": 42
  }' | python3 -m json.tool
echo ""
echo ""

# Test 4: Summarize
echo "4️⃣ Testing Summarize Endpoint..."
curl -s -X POST $API_URL/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "home_price": 650000,
      "monthly_rent": 2800,
      "years_horizon": 10
    },
    "results": {
      "total_rent_paid": 385186,
      "total_own_paid": 345588,
      "break_even_year": 10
    }
  }' | python3 -m json.tool
echo ""
echo ""

# Test 5: AI Advisor
echo "5️⃣ Testing AI Advisor Endpoint..."
curl -s -X POST $API_URL/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "home_price": 650000,
      "monthly_rent": 2800,
      "down_payment_pct": 0.20,
      "years_horizon": 10
    },
    "question": "Should I buy or rent?"
  }' | python3 -m json.tool
echo ""
echo ""

echo "✅ All tests completed!"
