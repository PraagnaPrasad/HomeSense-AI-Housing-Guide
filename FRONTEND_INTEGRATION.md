## Frontend Integration Guide 🎨

Complete guide for building a rich UI like the reference design.

## New Endpoint: `/v1/compute-formatted`

### Why Use This?

The standard `/v1/compute` endpoint returns raw calculation data. The new `/v1/compute-formatted` endpoint returns **structured, UI-ready data** that matches the reference design.

### Request

Same as `/v1/compute`:

```typescript
const response = await fetch('/v1/compute-formatted', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    home_price: 400000,
    monthly_rent: 2000,
    down_payment_pct: 0.20,
    mortgage_rate_annual: 0.07,
    property_tax_rate: 0.012,
    maintenance_rate: 0.01,
    years_horizon: 7,
    // ... other fields
  })
});

const data = await response.json();
```

### Response Structure

```typescript
interface FormattedResults {
  summary: {
    winner: "renting" | "buying";
    cost_difference: number;
    break_even_year: number | null;
    time_horizon_years: number;
  };

  key_metrics: {
    break_even: {
      years: number | null;
      label: string;  // "4 years" or "Not reached"
      description?: string;  // "after 7 years"
    };
    total_cost: {
      renting: number;
      buying: number;
      difference: number;
      winner: "renting" | "buying";
      label: string;  // "$17,580"
      description: string;  // "less to buy"
    };
    home_equity: {
      value: number;
      label: string;  // "$214,524"
      percentage: string;  // "53.6%"
    };
    maintenance: {
      rate: number;
      label: string;  // "1.0%"
      annual_cost: number;
    };
  };

  wealth_metrics: {
    renter_portfolio: {
      value: number;
      label: string;
      description: string;
    };
    owner_equity: {
      value: number;
      label: string;
      description: string;
    };
    wealth_advantage: {
      value: number;
      label: string;
      winner: "owner" | "renter";
    };
  };

  cash_flow: {
    rent: {
      total: number;
      monthly_avg: number;
      yearly_avg: number;
    };
    own: {
      down_payment: number;
      closing_costs: number;
      total: number;
      monthly_avg: number;
      yearly_avg: number;
    };
  };

  chart_data: {
    labels: number[];  // [0, 1, 2, ..., 7]
    datasets: [{
      name: "Renting" | "Buying";
      data: number[];  // Cumulative costs
      color: string;  // Hex color
      description: string;
    }];
    crossover_point: number | null;  // Break-even year
  };

  recommendation: {
    summary: string;
    items: [{
      type: "primary" | "info" | "warning" | "suggestion";
      title: string;
      text: string;
      icon: string;  // Icon name
    }];
    confidence: number;  // 0-100
  };

  raw_results: object;  // Full calculation results
}
```

## React Component Examples

### 1. Results Summary Card

```tsx
import { FormattedResults } from './types';

interface ResultsSummaryProps {
  results: FormattedResults;
}

export function ResultsSummary({ results }: ResultsSummaryProps) {
  const { summary, key_metrics } = results;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Results</h2>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Break-Even */}
        <MetricCard
          label="Break-Even"
          value={key_metrics.break_even.label}
          description={key_metrics.break_even.description}
        />

        {/* Total Cost */}
        <MetricCard
          label="Total Cost"
          value={key_metrics.total_cost.label}
          description={key_metrics.total_cost.description}
          highlight={summary.winner === "buying"}
        />

        {/* Home Equity */}
        <MetricCard
          label="Home Equity"
          value={key_metrics.home_equity.label}
          description={key_metrics.home_equity.percentage}
        />

        {/* Maintenance */}
        <MetricCard
          label="Maintenance"
          value={key_metrics.maintenance.label}
          description={`$${key_metrics.maintenance.annual_cost.toLocaleString()}/year`}
        />
      </div>
    </div>
  );
}

function MetricCard({ label, value, description, highlight = false }) {
  return (
    <div className={`p-4 rounded-lg border-2 ${
      highlight ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
    }`}>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
      {description && (
        <div className="text-sm text-gray-500 mt-1">{description}</div>
      )}
    </div>
  );
}
```

### 2. Cumulative Cost Chart

Using **Chart.js** or **Recharts**:

```tsx
import { Line } from 'react-chartjs-2';

export function CumulativeCostChart({ chartData }: { chartData: any }) {
  const data = {
    labels: chartData.labels,
    datasets: chartData.datasets.map(ds => ({
      label: ds.name,
      data: ds.data,
      borderColor: ds.color,
      backgroundColor: ds.color + '20',  // Add transparency
      tension: 0.4,
      fill: false
    }))
  };

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Cumulative Costs Over Time'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
          }
        }
      },
      annotation: chartData.crossover_point ? {
        annotations: {
          breakEven: {
            type: 'line',
            xMin: chartData.crossover_point,
            xMax: chartData.crossover_point,
            borderColor: '#10b981',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              content: 'Break-even',
              enabled: true,
              position: 'top'
            }
          }
        }
      } : undefined
    },
    scales: {
      y: {
        ticks: {
          callback: (value) => '$' + (value / 1000).toFixed(0) + 'k'
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-lg p-6 shadow-lg">
      <Line data={data} options={options} />
    </div>
  );
}
```

### 3. Recommendations Panel

```tsx
export function RecommendationsPanel({ recommendation }: { recommendation: any }) {
  const iconMap = {
    home: '🏠',
    'piggy-bank': '🐷',
    calendar: '📅',
    'arrow-up': '⬆️',
    'trending-up': '📈',
    clock: '⏰',
    'alert-circle': '⚠️',
    'bar-chart': '📊'
  };

  const typeStyles = {
    primary: 'bg-blue-50 border-blue-500',
    info: 'bg-cyan-50 border-cyan-500',
    warning: 'bg-yellow-50 border-yellow-500',
    suggestion: 'bg-green-50 border-green-500'
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Recommendation</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Confidence:</span>
          <div className="flex items-center">
            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500"
                style={{ width: `${recommendation.confidence}%` }}
              />
            </div>
            <span className="ml-2 text-sm font-medium">{recommendation.confidence}%</span>
          </div>
        </div>
      </div>

      <p className="text-gray-700 mb-4">{recommendation.summary}</p>

      <div className="space-y-3">
        {recommendation.items.map((item, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-lg border-l-4 ${typeStyles[item.type]}`}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{iconMap[item.icon] || '📌'}</span>
              <div className="flex-1">
                <h4 className="font-semibold mb-1">{item.title}</h4>
                <p className="text-sm text-gray-600">{item.text}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 4. Wealth Comparison

```tsx
export function WealthComparison({ wealthMetrics }: { wealthMetrics: any }) {
  const isOwnerWinner = wealthMetrics.wealth_advantage.winner === 'owner';

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Wealth Accumulation</h3>

      <div className="space-y-4">
        {/* Renter Portfolio */}
        <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
          <div>
            <div className="text-sm text-gray-600">Renter Portfolio</div>
            <div className="text-xl font-bold">{wealthMetrics.renter_portfolio.label}</div>
            <div className="text-sm text-gray-500">{wealthMetrics.renter_portfolio.description}</div>
          </div>
          {!isOwnerWinner && <span className="text-3xl">🏆</span>}
        </div>

        {/* Owner Equity */}
        <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
          <div>
            <div className="text-sm text-gray-600">Owner Equity</div>
            <div className="text-xl font-bold">{wealthMetrics.owner_equity.label}</div>
            <div className="text-sm text-gray-500">{wealthMetrics.owner_equity.description}</div>
          </div>
          {isOwnerWinner && <span className="text-3xl">🏆</span>}
        </div>

        {/* Advantage */}
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">Wealth Advantage</div>
          <div className="text-2xl font-bold text-green-600">
            {wealthMetrics.wealth_advantage.label}
          </div>
          <div className="text-sm text-gray-500">
            {isOwnerWinner ? 'Owner' : 'Renter'} builds more wealth
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 5. Complete Results Page

```tsx
import { useState } from 'react';
import { FormattedResults } from './types';

export function ResultsPage({ inputs }) {
  const [results, setResults] = useState<FormattedResults | null>(null);
  const [loading, setLoading] = useState(false);

  async function calculate() {
    setLoading(true);
    try {
      const response = await fetch('/v1/compute-formatted', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs)
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Calculation error:', error);
    } finally {
      setLoading(false);
    }
  }

  if (!results) {
    return (
      <div className="flex items-center justify-center h-screen">
        <button
          onClick={calculate}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Calculate
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Summary Cards */}
      <ResultsSummary results={results} />

      {/* Chart */}
      <CumulativeCostChart chartData={results.chart_data} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommendations */}
        <RecommendationsPanel recommendation={results.recommendation} />

        {/* Wealth Comparison */}
        <WealthComparison wealthMetrics={results.wealth_metrics} />
      </div>

      {/* Detailed Cash Flow (Optional) */}
      <CashFlowBreakdown cashFlow={results.cash_flow} />
    </div>
  );
}
```

## Styling Tips

### Tailwind Config

Add these colors to match the reference design:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'rent-red': '#ef4444',
        'buy-blue': '#3b82f6',
        'success-green': '#10b981',
        'warning-yellow': '#f59e0b',
      }
    }
  }
}
```

### CSS Classes

```css
/* Metric cards with hover effect */
.metric-card {
  @apply p-4 rounded-lg border-2 border-gray-200 transition-all hover:shadow-md;
}

.metric-card.winner {
  @apply border-blue-500 bg-blue-50;
}

/* Chart container */
.chart-container {
  @apply bg-white rounded-lg p-6 shadow-lg;
  min-height: 400px;
}

/* Recommendation cards */
.recommendation-item {
  @apply p-4 rounded-lg border-l-4 transition-all hover:shadow-sm;
}

.recommendation-item.primary {
  @apply bg-blue-50 border-blue-500;
}

.recommendation-item.info {
  @apply bg-cyan-50 border-cyan-500;
}

.recommendation-item.warning {
  @apply bg-yellow-50 border-yellow-500;
}

.recommendation-item.suggestion {
  @apply bg-green-50 border-green-500;
}
```

## Mobile Responsive

```tsx
// Use responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  {/* Metrics */}
</div>

// Stack on mobile
<div className="flex flex-col lg:flex-row gap-6">
  {/* Panels */}
</div>

// Adjust chart height
<div className="h-64 md:h-96">
  <CumulativeCostChart />
</div>
```

## Testing the Endpoint

```bash
curl -X POST http://localhost:8000/v1/compute-formatted \
  -H "Content-Type: application/json" \
  -d '{
    "home_price": 400000,
    "monthly_rent": 2000,
    "down_payment_pct": 0.20,
    "mortgage_rate_annual": 0.07,
    "years_horizon": 7,
    "property_tax_rate": 0.012,
    "maintenance_rate": 0.01,
    "home_price_growth": 0.03,
    "rent_growth": 0.03,
    "investment_return": 0.04,
    "closing_cost_buy": 0.03,
    "selling_cost": 0.06,
    "insurance_per_year": 1200,
    "discount_rate": 0.04,
    "term_years": 30
  }' | jq
```

## Next Steps

1. **Implement the UI** using the components above
2. **Add animations** for metric transitions
3. **Add interactivity** - hover states, expandable details
4. **Add sharing** - generate shareable result links
5. **Add comparisons** - compare multiple scenarios side-by-side

The formatted endpoint gives you everything you need to build a polished, production-ready UI! 🚀
