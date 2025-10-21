# Personalized Financial Advice - Enhanced Chatbot 🎯

Your financial advisor chatbot now provides **deeply personalized advice** based on a user's complete life situation!

## What's New

### Personal Context Fields

The chatbot now accepts detailed user information to provide life-stage-appropriate advice:

#### Demographics
- **age** - Life stage considerations
- **relationship_status** - "single", "married", "partnered", etc.
- **kids** - Boolean or descriptive (e.g., "2 kids (ages 5, 7)")

#### Financial Situation
- **annual_income** - Current income level
- **savings** - Available cash/liquid assets
- **debt** - Outstanding debt (student loans, car, etc.)
- **credit_score** - Creditworthiness

#### Career & Education
- **education** - Educational background
- **job_stability** - "stable", "startup", "freelance", "contract"
- **career_stage** - "early career", "mid-career", "senior", "executive"

#### Location & Lifestyle
- **location** - City/region for market-specific insights
- **work_situation** - "remote", "hybrid", "in-office"
- **lifestyle_priorities** - What matters most to them

#### Property Information
- **property_links** - Zillow, StreetEasy, or other listing URLs (string or array)
- **additional_info** - Any other relevant context

## Enhanced System Prompt

The AI now considers:

### Life Stage Guidance
- **Young Professionals (20s-early 30s)**: Flexibility, career mobility, debt management
- **Established Professionals (30s-40s)**: Stability vs opportunity cost, family needs
- **Families with Kids**: School districts, space, long-term stability
- **Pre-retirement (50s-60s)**: Downsizing, equity, fixed income planning

### Personalization Factors
- **Job Stability**: Unstable = favor renting for flexibility
- **Family Plans**: Kids soon? Consider schools and space
- **Income Trajectory**: High growth = can absorb mortgage risk
- **Debt Levels**: High debt = build savings first
- **Location**: High-cost cities = longer break-even
- **Lifestyle**: Value travel? Renting fits better

### Property Link Analysis
When you provide Zillow or StreetEasy links, the AI can:
- Search for market insights and trends
- Consider neighborhood characteristics
- Evaluate property-specific factors

## API Usage

### Updated Request Format

```json
{
  "question": "Should I buy this place?",
  "inputs": {
    "home_price": 650000,
    "monthly_rent": 3000,
    "years_horizon": 10
  },
  "user_context": {
    "age": 28,
    "annual_income": 150000,
    "relationship_status": "single",
    "kids": false,
    "education": "Bachelor's in Computer Science",
    "job_stability": "startup",
    "career_stage": "early career",
    "savings": 80000,
    "debt": 25000,
    "location": "San Francisco, CA",
    "work_situation": "hybrid",
    "lifestyle_priorities": "career growth and flexibility",
    "property_links": "https://www.zillow.com/homedetails/123-Main-St/",
    "additional_info": "Might relocate in 2-3 years"
  }
}
```

## Example Scenarios

### Example 1: Young Tech Professional

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I buy my first home?",
    "inputs": {
      "home_price": 900000,
      "monthly_rent": 3500,
      "years_horizon": 7
    },
    "user_context": {
      "age": 28,
      "annual_income": 150000,
      "job_stability": "startup",
      "savings": 80000,
      "debt": 25000,
      "location": "San Francisco",
      "additional_info": "Might relocate in 2-3 years"
    }
  }'
```

**Expected Advice Focus:**
- Emphasize flexibility given startup job and potential relocation
- Consider student debt impact
- Discuss San Francisco market dynamics
- Break-even timeline relative to potential move
- Career trajectory and income growth potential

### Example 2: Family with Young Kids

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "We need more space for our kids. Should we buy?",
    "inputs": {
      "home_price": 550000,
      "monthly_rent": 2800,
      "years_horizon": 15
    },
    "user_context": {
      "age": 36,
      "relationship_status": "married",
      "kids": "2 kids (ages 3 and 5)",
      "annual_income": 180000,
      "savings": 150000,
      "job_stability": "stable",
      "location": "Austin, TX",
      "work_situation": "both remote",
      "lifestyle_priorities": "good schools, outdoor space, stability",
      "property_links": [
        "https://www.zillow.com/homedetails/456-Oak-Ave/",
        "https://www.zillow.com/homedetails/789-Elm-St/"
      ]
    }
  }'
```

**Expected Advice Focus:**
- School district quality and long-term plans
- Space needs as kids grow
- Stability vs flexibility trade-off
- Remote work flexibility benefits
- Strong financial position (high savings, dual income)
- Austin market trends

### Example 3: Pre-Retirement Downsizing

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should we downsize now or rent and invest our home equity?",
    "inputs": {
      "home_price": 475000,
      "monthly_rent": 2400,
      "down_payment_pct": 0.40,
      "years_horizon": 10
    },
    "user_context": {
      "age": 58,
      "annual_income": 140000,
      "relationship_status": "married",
      "kids": "adult children (independent)",
      "savings": 450000,
      "debt": 0,
      "credit_score": 820,
      "job_stability": "stable, retiring at 65",
      "lifestyle_priorities": "downsizing, low maintenance, retirement planning",
      "additional_info": "Currently own larger home"
    }
  }'
```

**Expected Advice Focus:**
- Retirement timeline (7 years out)
- Tax implications of selling current home
- Maintenance burden considerations
- Fixed income planning
- Estate planning considerations
- Flexibility in retirement

### Example 4: Recent Grad with Parental Pressure

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "My parents say I should buy. Is this a good idea?",
    "inputs": {
      "home_price": 650000,
      "monthly_rent": 2600,
      "down_payment_pct": 0.05,
      "years_horizon": 5
    },
    "user_context": {
      "age": 24,
      "annual_income": 75000,
      "savings": 35000,
      "debt": 45000,
      "credit_score": 680,
      "career_stage": "entry-level",
      "location": "Brooklyn, NY",
      "lifestyle_priorities": "social life, career development",
      "property_links": "https://streeteasy.com/building/123-bedford/1a",
      "additional_info": "First time looking at real estate"
    }
  }'
```

**Expected Advice Focus:**
- High debt-to-income ratio concerns
- Limited savings vs down payment + closing costs
- Career flexibility at early stage
- NYC market dynamics and costs
- FHA loan implications
- Opportunity cost vs building equity
- Respectfully address parental pressure

## Frontend Integration

### Collecting User Context

Here's a React example for collecting this information:

```typescript
interface UserContext {
  age?: number;
  annual_income?: number;
  relationship_status?: string;
  kids?: boolean | string;
  education?: string;
  job_stability?: string;
  career_stage?: string;
  savings?: number;
  debt?: number;
  credit_score?: number;
  location?: string;
  work_situation?: string;
  lifestyle_priorities?: string;
  property_links?: string | string[];
  additional_info?: string;
}

// Multi-step onboarding form
function UserContextForm({ onSubmit }) {
  const [context, setContext] = useState<UserContext>({});

  return (
    <form onSubmit={() => onSubmit(context)}>
      <h2>Tell us about yourself</h2>

      <section>
        <h3>Basic Info</h3>
        <input
          type="number"
          placeholder="Age"
          onChange={(e) => setContext({...context, age: parseInt(e.target.value)})}
        />
        <select onChange={(e) => setContext({...context, relationship_status: e.target.value})}>
          <option>Single</option>
          <option>Married</option>
          <option>Partnered</option>
        </select>
        <input
          placeholder="Kids? (e.g., '2 kids, ages 5 and 7')"
          onChange={(e) => setContext({...context, kids: e.target.value})}
        />
      </section>

      <section>
        <h3>Financial Situation</h3>
        <input
          type="number"
          placeholder="Annual Income"
          onChange={(e) => setContext({...context, annual_income: parseFloat(e.target.value)})}
        />
        <input
          type="number"
          placeholder="Savings"
          onChange={(e) => setContext({...context, savings: parseFloat(e.target.value)})}
        />
        <input
          type="number"
          placeholder="Total Debt"
          onChange={(e) => setContext({...context, debt: parseFloat(e.target.value)})}
        />
      </section>

      <section>
        <h3>Property Info (Optional)</h3>
        <input
          placeholder="Zillow/StreetEasy link"
          onChange={(e) => setContext({...context, property_links: e.target.value})}
        />
        <input
          placeholder="Location (e.g., 'Austin, TX')"
          onChange={(e) => setContext({...context, location: e.target.value})}
        />
      </section>

      <button type="submit">Get Personalized Advice</button>
    </form>
  );
}
```

### Sending Request with Context

```typescript
async function getAdvice(
  question: string,
  inputs: any,
  userContext: UserContext,
  conversationHistory: Message[]
) {
  const response = await fetch('/v1/advise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      inputs,
      user_context: userContext,
      conversation_history: conversationHistory
    })
  });

  return await response.json();
}
```

## Testing

Run the personalized test script to see how advice changes based on different profiles:

```bash
export PPLX_API_KEY="your-key"
python test_chatbot_personalized.py
```

This will simulate 4 different scenarios:
1. Young tech professional considering first home
2. Married couple with young kids needing space
3. Pre-retirement couple looking to downsize
4. Recent grad facing parental pressure to buy

## Best Practices

### Progressive Disclosure
Don't overwhelm users - collect context progressively:
1. Start with basic question
2. If they engage, ask for key details (age, income, family)
3. If they're serious, collect full financial picture
4. Always make fields optional

### Privacy & Security
- Never store sensitive financial info without consent
- Use HTTPS in production
- Consider encrypting context data in transit
- Allow users to clear their context
- Be transparent about how data is used

### UX Tips
- Pre-fill context from previous sessions (with permission)
- Offer quick personas: "I'm a young professional", "I have kids", etc.
- Allow editing context mid-conversation
- Show which context fields influence advice
- Let users paste property URLs directly in chat

## Benefits of Personalization

### For Users
- More relevant, actionable advice
- Life-stage-appropriate recommendations
- Feels like talking to a real advisor
- Addresses their specific concerns
- Considers trade-offs beyond just numbers

### For Your Product
- Higher engagement and trust
- Better conversion rates
- Fewer generic responses
- Stands out from calculator-only tools
- Enables premium features

---

**Pro Tip**: The AI is particularly good at balancing financial optimization with quality of life considerations when it has rich personal context!
