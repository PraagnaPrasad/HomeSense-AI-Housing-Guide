"use client";

import React, { useState } from "react";
import Link from "next/link";

type Inputs = {
  home_price: number;
  monthly_rent: number;
  down_payment_pct: number;
  mortgage_rate_annual: number;
  years_horizon: number;
  property_tax_rate: number;
  maintenance_rate: number;
  insurance_per_year: number;
  home_price_growth: number;
  rent_growth: number;
  investment_return: number;
  closing_cost_buy: number;
  selling_cost: number;
  discount_rate: number;
  term_years: number;
};

const DEFAULTS: Inputs = {
  home_price: 650000,
  monthly_rent: 3000,
  down_payment_pct: 0.20,
  mortgage_rate_annual: 0.068,
  years_horizon: 10,
  property_tax_rate: 0.012,
  maintenance_rate: 0.01,
  insurance_per_year: 1500,
  home_price_growth: 0.025,
  rent_growth: 0.03,
  investment_return: 0.07,
  closing_cost_buy: 0.03,
  selling_cost: 0.06,
  discount_rate: 0.04,
  term_years: 30,
};

export default function CalculatorPage() {
  const [inputs, setInputs] = useState<Inputs>(DEFAULTS);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [cityLoading, setCityLoading] = useState(false);
  const [selectedCity, setSelectedCity] = useState<string>("");
  const [loadingRates, setLoadingRates] = useState(false);
  const [view, setView] = useState<"input" | "results">("input");

  async function handleCitySelect(city: string) {
    if (!city) return;

    setSelectedCity(city);
    setCityLoading(true);

    try {
      const res = await fetch("http://localhost:8080/v1/city-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city }),
      });

      if (!res.ok) throw new Error("Failed to fetch city data");

      const data = await res.json();

      if (data.found) {
        // Auto-fill growth rates from Zillow (round to 2 decimal places when displayed as %)
        setInputs(prev => ({
          ...prev,
          home_price_growth: data.home_price_growth ? Number(data.home_price_growth.toFixed(4)) : prev.home_price_growth,
          rent_growth: data.rent_growth_annual ? Number(data.rent_growth_annual.toFixed(4)) : prev.rent_growth,
        }));

        // Show success toast
        showToast(`✓ Loaded ${city} market data`, "success");
      } else {
        showToast(`No data found for ${city}`, "warning");
      }
    } catch (err) {
      console.error("City data error:", err);
      showToast("Could not fetch city data", "error");
    } finally {
      setCityLoading(false);
    }
  }

  async function handleLoadLiveRates() {
    setLoadingRates(true);

    try {
      const res = await fetch("http://localhost:8080/v1/fred-rates");
      if (!res.ok) throw new Error("Failed to fetch rates");

      const data = await res.json();

      // Auto-fill current mortgage rate and inflation (round to 2 decimal places when displayed as %)
      setInputs(prev => ({
        ...prev,
        mortgage_rate_annual: data.mortgage_rate_annual ? Number(data.mortgage_rate_annual.toFixed(4)) : prev.mortgage_rate_annual,
        discount_rate: data.inflation_annual ? Number(data.inflation_annual.toFixed(4)) : prev.discount_rate,
      }));

      showToast(`✓ Loaded current rates: ${(data.mortgage_rate_annual * 100).toFixed(2)}%`, "success");
    } catch (err) {
      console.error("FRED rates error:", err);
      showToast("Could not fetch current rates", "error");
    } finally {
      setLoadingRates(false);
    }
  }

  function showToast(message: string, type: "success" | "warning" | "error") {
    // Simple toast implementation - you can enhance this
    alert(message);
  }

  async function handleCalculate() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8080/v1/compute-formatted", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to calculate");
      }

      const data = await res.json();
      setResults(data);
      setView("results");
    } catch (err: any) {
      if (err.message === "Failed to fetch") {
        alert("Backend API is not running!\n\nPlease start it with:\ncd apps/api\nuvicorn app.main:app --reload --port 8080");
      } else {
        alert("Error: " + err.message);
      }
    } finally {
      setLoading(false);
    }
  }

  // Results View
  if (view === "results" && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-gray-900">
              homesense
            </Link>
            <button
              onClick={() => setView("input")}
              className="px-6 py-2 bg-white border-2 border-gray-200 text-gray-900 rounded-full font-medium hover:border-gray-300 transition-all"
            >
              ← Back to Calculator
            </button>
          </div>
        </header>

        <div className="max-w-5xl mx-auto px-6 py-12">
          <div className="space-y-6 animate-fade-in">
            {/* Winner Card */}
            <div className="bg-white rounded-3xl shadow-xl p-8 lg:p-12 text-center">
              <div className="mb-6">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  After {results.summary.time_horizon_years} years
                </div>
              </div>

              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6 leading-tight">
                {results.summary.winner === "buying" ? (
                  <>
                    Buying saves you
                    <br />
                    <span className="text-green-600">
                      ${results.summary.cost_difference.toLocaleString()}
                    </span>
                  </>
                ) : (
                  <>
                    Renting saves you
                    <br />
                    <span className="text-blue-600">
                      ${results.summary.cost_difference.toLocaleString()}
                    </span>
                  </>
                )}
              </h2>

              <p className="text-lg text-gray-600">
                {results.recommendation.summary}
              </p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                label="Break-Even Point"
                value={results.key_metrics.break_even.label}
                description={results.key_metrics.break_even.description || "When buying becomes cheaper"}
                icon="📅"
              />

              <MetricCard
                label="Total Wealth (Renting)"
                value={results.wealth_metrics.renter_portfolio.label}
                description="Investment portfolio value"
                icon="📊"
              />

              <MetricCard
                label="Total Wealth (Buying)"
                value={results.wealth_metrics.owner_equity.label}
                description="Home equity after selling"
                icon="🏠"
              />
            </div>

            {/* Wealth Comparison */}
            <div className="bg-white rounded-3xl shadow-xl p-8 lg:p-12">
              <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
                Wealth Comparison
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* Renting */}
                <div className={`p-6 rounded-2xl border-2 ${
                  results.wealth_metrics.wealth_advantage.winner === "renter"
                    ? "border-blue-400 bg-blue-50"
                    : "border-gray-200 bg-gray-50"
                }`}>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-900">Renting</h4>
                    {results.wealth_metrics.wealth_advantage.winner === "renter" && (
                      <span className="text-2xl">🏆</span>
                    )}
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm text-gray-600">Investment Portfolio</div>
                      <div className="text-3xl font-bold text-gray-900">
                        {results.wealth_metrics.renter_portfolio.label}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Down payment invested + monthly savings compounded
                    </div>
                  </div>
                </div>

                {/* Buying */}
                <div className={`p-6 rounded-2xl border-2 ${
                  results.wealth_metrics.wealth_advantage.winner === "owner"
                    ? "border-green-400 bg-green-50"
                    : "border-gray-200 bg-gray-50"
                }`}>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-900">Buying</h4>
                    {results.wealth_metrics.wealth_advantage.winner === "owner" && (
                      <span className="text-2xl">🏆</span>
                    )}
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm text-gray-600">Home Equity</div>
                      <div className="text-3xl font-bold text-gray-900">
                        {results.wealth_metrics.owner_equity.label}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Principal paydown + appreciation - selling costs
                    </div>
                  </div>
                </div>
              </div>

              {/* Cash Flow Summary */}
              <div className="pt-6 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                  <div>
                    <div className="text-gray-600 mb-2">Total Cash Spent (Renting)</div>
                    <div className="text-2xl font-bold text-gray-900">
                      ${results.cash_flow.rent.total.toLocaleString()}
                    </div>
                    <div className="text-gray-500 mt-1">
                      ~${Math.round(results.cash_flow.rent.monthly_avg).toLocaleString()}/month avg
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600 mb-2">Total Cash Spent (Buying)</div>
                    <div className="text-2xl font-bold text-gray-900">
                      ${results.cash_flow.own.total.toLocaleString()}
                    </div>
                    <div className="text-gray-500 mt-1">
                      ~${Math.round(results.cash_flow.own.monthly_avg).toLocaleString()}/month avg
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-3xl shadow-xl p-8 lg:p-12">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                Recommendations
              </h3>

              <div className="space-y-4">
                {results.recommendation.items.map((item: any, i: number) => (
                  <div
                    key={i}
                    className={`p-6 rounded-2xl border-l-4 ${
                      item.type === "primary"
                        ? "border-blue-500 bg-blue-50"
                        : item.type === "warning"
                        ? "border-yellow-500 bg-yellow-50"
                        : item.type === "suggestion"
                        ? "border-green-500 bg-green-50"
                        : "border-purple-500 bg-purple-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="text-2xl flex-shrink-0">
                        {item.icon === "home" && "🏠"}
                        {item.icon === "piggy-bank" && "🐷"}
                        {item.icon === "calendar" && "📅"}
                        {item.icon === "trending-up" && "📈"}
                        {item.icon === "arrow-up" && "⬆️"}
                        {item.icon === "clock" && "⏰"}
                        {item.icon === "alert-circle" && "⚠️"}
                        {item.icon === "bar-chart" && "📊"}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-1">
                          {item.title}
                        </h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {item.text}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 text-center">
                <div className="text-sm text-gray-600 mb-2">Confidence Level</div>
                <div className="flex items-center justify-center gap-3">
                  <div className="flex-1 max-w-md h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 transition-all duration-1000"
                      style={{ width: `${results.recommendation.confidence}%` }}
                    />
                  </div>
                  <span className="text-lg font-bold text-gray-900">
                    {results.recommendation.confidence}%
                  </span>
                </div>
              </div>
            </div>

            {/* CTA to Chat */}
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl shadow-xl p-8 lg:p-12 text-center text-white">
              <h3 className="text-3xl font-bold mb-4">
                Still have questions?
              </h3>
              <p className="text-lg mb-8 opacity-90">
                Chat with our AI advisor for personalized guidance based on your unique situation.
              </p>
              <Link
                href="/advisor"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-purple-600 rounded-full font-semibold text-lg hover:bg-gray-100 transition-all shadow-lg"
              >
                Chat with Advisor
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Input View
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            homesense
          </Link>
          <Link
            href="/advisor"
            className="px-6 py-2 bg-white border-2 border-gray-200 text-gray-900 rounded-full font-medium hover:border-gray-300 transition-all"
          >
            Chat with Advisor
          </Link>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Rent vs. Buy Calculator
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Answer a few quick questions to see which option builds more wealth for your situation.
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-3xl shadow-xl p-8 lg:p-12 mb-8">
          <div className="space-y-8">
            {/* Quick Fill Options */}
            <div className="pb-8 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Quick Fill
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* City Selector */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    📍 Select City (Auto-fill growth rates)
                  </label>
                  <select
                    value={selectedCity}
                    onChange={(e) => handleCitySelect(e.target.value)}
                    disabled={cityLoading}
                    className="w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 text-gray-900 font-medium focus:outline-none focus:border-purple-400 focus:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <option value="">Choose a city...</option>
                    <option value="San Francisco, CA">San Francisco, CA</option>
                    <option value="New York, NY">New York, NY</option>
                    <option value="Los Angeles, CA">Los Angeles, CA</option>
                    <option value="Austin, TX">Austin, TX</option>
                    <option value="Seattle, WA">Seattle, WA</option>
                    <option value="Chicago, IL">Chicago, IL</option>
                    <option value="Boston, MA">Boston, MA</option>
                    <option value="Denver, CO">Denver, CO</option>
                    <option value="Miami, FL">Miami, FL</option>
                    <option value="Portland, OR">Portland, OR</option>
                  </select>
                  {cityLoading && (
                    <div className="mt-2 text-sm text-purple-600 flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-purple-600/30 border-t-purple-600 rounded-full animate-spin" />
                      Loading city data...
                    </div>
                  )}
                </div>

                {/* Load Current Rates Button */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    📊 Current Market Rates
                  </label>
                  <button
                    onClick={handleLoadLiveRates}
                    disabled={loadingRates}
                    className="w-full bg-purple-500 text-white py-3 px-4 rounded-xl font-medium hover:bg-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loadingRates ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Load Current Rates
                      </>
                    )}
                  </button>
                  <p className="mt-2 text-xs text-gray-500">
                    Auto-fills mortgage rate & inflation from FRED
                  </p>
                </div>
              </div>
            </div>

            {/* Essential Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <InputField
                label="Home Price"
                value={inputs.home_price}
                onChange={(v) => setInputs({ ...inputs, home_price: v })}
                prefix="$"
                helper="The purchase price of the home"
              />

              <InputField
                label="Monthly Rent"
                value={inputs.monthly_rent}
                onChange={(v) => setInputs({ ...inputs, monthly_rent: v })}
                prefix="$"
                helper="For a comparable property"
              />

              <InputField
                label="Down Payment"
                value={inputs.down_payment_pct * 100}
                onChange={(v) => setInputs({ ...inputs, down_payment_pct: v / 100 })}
                suffix="%"
                helper="Typically 20% to avoid PMI"
              />

              <InputField
                label="Mortgage Rate"
                value={inputs.mortgage_rate_annual * 100}
                onChange={(v) => setInputs({ ...inputs, mortgage_rate_annual: v / 100 })}
                suffix="%"
                helper="Annual interest rate"
              />

              <InputField
                label="Time Horizon"
                value={inputs.years_horizon}
                onChange={(v) => setInputs({ ...inputs, years_horizon: v })}
                suffix="years"
                helper="How long you plan to stay"
              />

              <InputField
                label="Investment Return"
                value={inputs.investment_return * 100}
                onChange={(v) => setInputs({ ...inputs, investment_return: v / 100 })}
                suffix="%"
                helper="Expected return on alternative investments"
              />
            </div>

            {/* Advanced Settings (Collapsible) */}
            <details className="group">
              <summary className="cursor-pointer text-gray-600 hover:text-gray-900 font-medium flex items-center gap-2">
                <svg className="w-5 h-5 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                Advanced Settings
              </summary>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-8 pl-7">
                <InputField
                  label="Property Tax Rate"
                  value={inputs.property_tax_rate * 100}
                  onChange={(v) => setInputs({ ...inputs, property_tax_rate: v / 100 })}
                  suffix="%"
                  helper="Annual property tax as % of home value"
                />

                <InputField
                  label="Maintenance Rate"
                  value={inputs.maintenance_rate * 100}
                  onChange={(v) => setInputs({ ...inputs, maintenance_rate: v / 100 })}
                  suffix="%"
                  helper="Annual maintenance as % of home value"
                />

                <InputField
                  label="Home Insurance"
                  value={inputs.insurance_per_year}
                  onChange={(v) => setInputs({ ...inputs, insurance_per_year: v })}
                  prefix="$"
                  helper="Annual insurance premium"
                />

                <InputField
                  label="Home Appreciation"
                  value={inputs.home_price_growth * 100}
                  onChange={(v) => setInputs({ ...inputs, home_price_growth: v / 100 })}
                  suffix="%"
                  helper={selectedCity ? `Auto-filled from ${selectedCity} Zillow data` : "Expected annual home value growth"}
                />

                <InputField
                  label="Rent Growth"
                  value={inputs.rent_growth * 100}
                  onChange={(v) => setInputs({ ...inputs, rent_growth: v / 100 })}
                  suffix="%"
                  helper={selectedCity ? `Auto-filled from ${selectedCity} Zillow data` : "Expected annual rent increase"}
                />

                <InputField
                  label="Closing Costs"
                  value={inputs.closing_cost_buy * 100}
                  onChange={(v) => setInputs({ ...inputs, closing_cost_buy: v / 100 })}
                  suffix="%"
                  helper="Costs when buying (% of price)"
                />

                <InputField
                  label="Selling Costs"
                  value={inputs.selling_cost * 100}
                  onChange={(v) => setInputs({ ...inputs, selling_cost: v / 100 })}
                  suffix="%"
                  helper="Costs when selling (% of price)"
                />

                <InputField
                  label="Inflation Rate"
                  value={inputs.discount_rate * 100}
                  onChange={(v) => setInputs({ ...inputs, discount_rate: v / 100 })}
                  suffix="%"
                  helper="Expected annual inflation (discount rate)"
                />
              </div>
            </details>
          </div>

          {/* Calculate Button */}
          <button
            onClick={handleCalculate}
            disabled={loading}
            className="mt-10 w-full bg-gray-900 text-white py-5 px-8 rounded-2xl font-semibold text-lg hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                Calculate
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

function InputField({
  label,
  value,
  onChange,
  prefix,
  suffix,
  helper,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  prefix?: string;
  suffix?: string;
  helper?: string;
}) {
  // Round display value to 2 decimal places for percentages
  const displayValue = suffix === "%" ? Number(value.toFixed(2)) : value;

  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-gray-900">
        {label}
      </label>
      {helper && (
        <p className="text-xs text-gray-500">{helper}</p>
      )}
      <div className="relative">
        {prefix && (
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
            {prefix}
          </span>
        )}
        <input
          type="number"
          value={displayValue}
          onChange={(e) => onChange(Number(e.target.value))}
          step={suffix === "%" ? "0.01" : "1"}
          className={`w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 text-gray-900 font-medium focus:outline-none focus:border-purple-400 focus:bg-white transition-all ${
            prefix ? "pl-10" : ""
          } ${suffix ? "pr-16" : ""}`}
        />
        {suffix && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
            {suffix}
          </span>
        )}
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  description,
  icon,
}: {
  label: string;
  value: string;
  description?: string;
  icon: string;
}) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="text-3xl mb-3">{icon}</div>
      <div className="text-sm text-gray-600 mb-2">{label}</div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      {description && (
        <div className="text-xs text-gray-500">{description}</div>
      )}
    </div>
  );
}
