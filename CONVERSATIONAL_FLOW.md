# Conversational Flow Guide

Your chatbot now handles natural conversation flow, from simple greetings to complex financial analysis!

## Fixed Issues

### ❌ Before
```json
{
  "question": "hi",
  "inputs": {}
}
```
**Result**: Error or weird response trying to calculate with missing data

### ✅ After
```json
{
  "question": "hi",
  "inputs": null  // or empty object
}
```
**Result**: "Hi! I'm a financial advisor specializing in rent vs buy decisions. How can I help you today?"

## How It Works

### Smart Context Detection

The chatbot now intelligently detects what information is available:

1. **No inputs, no context** → Greeting/general conversation mode
2. **Personal context only** → Can discuss situation, ask clarifying questions
3. **Partial inputs** → Can discuss what's provided, ask for missing pieces
4. **Complete inputs** → Full analysis with calculations

### Calculation Requirements

Calculations only run when BOTH are provided:
- `home_price` (required)
- `monthly_rent` (required)

If either is missing, the chatbot converses without numbers.

## Example Flows

### Flow 1: Starting from Scratch

```javascript
// Message 1: Greeting
{
  question: "hi",
  inputs: null
}
→ Response: "Hello! I'm a financial advisor specializing in housing decisions.
             Are you thinking about buying a home, or exploring your options?"

// Message 2: Context setting
{
  question: "I'm thinking about buying in San Francisco",
  inputs: null,
  user_context: { location: "San Francisco, CA" },
  conversation_history: [...]
}
→ Response: "San Francisco is a unique market! Tell me about your situation -
             what's your timeline, and have you found any properties you're
             considering?"

// Message 3: Adding numbers
{
  question: "I'm looking at a $900k home, currently paying $3500/month rent",
  inputs: {
    home_price: 900000,
    monthly_rent: 3500
  },
  conversation_history: [...]
}
→ Response: "Let me analyze these numbers for you... [calculation + advice]"
```

### Flow 2: Starting with Numbers

```javascript
// Message 1: Direct question with data
{
  question: "Should I buy? Home is $650k, rent is $3000",
  inputs: {
    home_price: 650000,
    monthly_rent: 3000,
    years_horizon: 10
  }
}
→ Response: "Based on your numbers, over 10 years... [full analysis]

             To give you more personalized advice, can you tell me about
             your situation? Age, family status, job stability?"

// Message 2: Adding personal context
{
  question: "I'm 28, single, working at a startup",
  inputs: { home_price: 650000, monthly_rent: 3000 },
  user_context: {
    age: 28,
    relationship_status: "single",
    job_stability: "startup"
  },
  conversation_history: [...]
}
→ Response: "Given your startup role, I'd actually recommend... [personalized]"
```

### Flow 3: Empty/Partial Inputs (Common Frontend Bug)

```javascript
// Frontend accidentally sends empty object
{
  question: "Should I buy or rent?",
  inputs: {}  // Empty - no home_price or monthly_rent
}
→ Response: "I'd be happy to help you decide! Can you share some details about
             the properties you're comparing? What's the home price and your
             current rent?"

// Partial data
{
  question: "Rent is $3000, should I buy?",
  inputs: { monthly_rent: 3000 }  // Missing home_price
}
→ Response: "At $3000/month rent, that's $36k per year. To compare properly,
             what's the purchase price of the home you're considering?"
```

## API Behavior

### Request Variations

All of these work correctly:

```javascript
// 1. Null inputs (greeting/general)
{ question: "hi", inputs: null }

// 2. Empty inputs object
{ question: "hello", inputs: {} }

// 3. Partial inputs
{ question: "rent is $3k", inputs: { monthly_rent: 3000 } }

// 4. Complete inputs
{
  question: "Should I buy?",
  inputs: { home_price: 650000, monthly_rent: 3000 }
}

// 5. With personal context, no numbers
{
  question: "I'm 30, thinking of buying",
  inputs: null,
  user_context: { age: 30 }
}
```

### Response Patterns

**Greeting Response** (no data):
- Short and friendly
- Asks how they can help
- 1-2 sentences

**Exploratory Response** (partial data):
- Works with what's provided
- Asks clarifying questions
- Offers general guidance
- 2-3 paragraphs

**Analytical Response** (full data):
- Runs calculations
- Provides specific numbers
- Gives concrete recommendation
- 3-4 paragraphs

## Frontend Implementation Tips

### Progressive Disclosure Pattern

```typescript
interface ChatState {
  messages: Message[];
  userContext: Partial<UserContext>;
  inputs: Partial<CalculatorInputs>;
}

function ChatInterface() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    userContext: {},
    inputs: {}
  });

  async function sendMessage(question: string) {
    // Only send inputs if we have the minimum required
    const hasMinimumInputs =
      state.inputs.home_price &&
      state.inputs.monthly_rent;

    const response = await fetch('/v1/advise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        inputs: hasMinimumInputs ? state.inputs : null,
        user_context: Object.keys(state.userContext).length > 0
          ? state.userContext
          : null,
        conversation_history: state.messages
      })
    });

    // Update state...
  }

  return (
    <div>
      <ChatMessages messages={state.messages} />

      {/* Optional: Show what context we have */}
      <ContextIndicator
        hasInputs={!!(state.inputs.home_price && state.inputs.monthly_rent)}
        hasContext={Object.keys(state.userContext).length > 0}
      />

      <ChatInput onSend={sendMessage} />

      {/* Side panel for calculator or context form */}
      <CalculatorPanel
        inputs={state.inputs}
        onChange={(inputs) => setState({...state, inputs})}
      />
    </div>
  );
}
```

### Handling User Input

```typescript
// Parse natural language for numbers
function extractNumbers(message: string) {
  const patterns = {
    homePrice: /(?:home|house|property).*?(\$?[\d,]+k?)/i,
    rent: /rent.*?(\$?[\d,]+)/i
  };

  const matches = {
    home_price: parsePrice(message.match(patterns.homePrice)?.[1]),
    monthly_rent: parsePrice(message.match(patterns.rent)?.[1])
  };

  return matches;
}

// Example: "Home is $650k, rent is $3000"
// Returns: { home_price: 650000, monthly_rent: 3000 }
```

### Context Indicators

Show users what information you have:

```tsx
function ContextIndicator({ hasInputs, hasContext }) {
  return (
    <div className="context-chips">
      {hasInputs && <Chip>📊 Numbers provided</Chip>}
      {hasContext && <Chip>👤 Personal info added</Chip>}
      {!hasInputs && !hasContext && (
        <Chip variant="outline">💬 General conversation</Chip>
      )}
    </div>
  );
}
```

## Testing

Run the greeting test suite:

```bash
export PPLX_API_KEY="your-key"
python test_greetings.py
```

This tests:
- ✓ Simple greetings ("hi", "hello")
- ✓ General questions without numbers
- ✓ Empty inputs object
- ✓ Partial inputs (missing required fields)
- ✓ Conversation flow with history
- ✓ Personal context without calculations

## Common Pitfalls

### ❌ Don't Do This

```javascript
// Don't send inputs if you don't have the data
{
  question: "hi",
  inputs: {
    home_price: 0,      // Bad: fake data
    monthly_rent: 0     // Bad: fake data
  }
}

// Don't always send empty object
{
  question: "hi",
  inputs: {}  // Use null instead
}
```

### ✅ Do This

```javascript
// Send null when no data
{
  question: "hi",
  inputs: null
}

// Only send inputs when you have real data
{
  question: "Should I buy?",
  inputs: userHasEnteredNumbers ? calculatorState : null
}

// Build up context progressively
{
  question: "I'm 28 and thinking about buying",
  inputs: null,  // No numbers yet
  user_context: { age: 28 }  // But we have personal context
}
```

## Best Practices

1. **Start with greetings** - Let users warm up naturally
2. **Collect context progressively** - Don't ask for everything at once
3. **Parse natural language** - Extract numbers from conversational messages
4. **Show what you know** - Display chips/badges for available context
5. **Allow editing** - Let users correct extracted information
6. **Null vs empty** - Use `null` for missing data, not empty objects
7. **Validate before sending** - Check for required fields

---

**Remember**: A good conversation builds trust. Start friendly, ask questions, and only dive into numbers when appropriate! 💬
