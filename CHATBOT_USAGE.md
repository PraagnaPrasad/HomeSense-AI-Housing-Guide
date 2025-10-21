# Financial Advisor Chatbot Usage

Your Perplexity wrapper now behaves like a conversational financial advisor chatbot!

## What Changed

### Before
- Single-shot Q&A only
- No conversation memory
- Focused on calculation analysis only

### After
- **Full chatbot capabilities** with conversation history
- **System prompt** that establishes AI as a financial advisor
- **Conversational tone** - warm, supportive, and professional
- Can answer general questions even without calculation data
- Maintains context across multiple messages

## API Usage

### Endpoint: `POST /v1/advise`

### Request Body

```json
{
  "question": "Should I buy or rent in my situation?",
  "inputs": {
    "home_price": 650000,
    "monthly_rent": 3000,
    "down_payment_pct": 0.20,
    "years_horizon": 10
  },
  "conversation_history": [
    {
      "role": "user",
      "content": "Hi, I'm thinking about buying a home."
    },
    {
      "role": "assistant",
      "content": "Hello! I'd be happy to help you think through your home buying decision..."
    }
  ]
}
```

### Parameters

- **`question`** (required): The user's current message/question
- **`inputs`** (optional): Calculation inputs - can be `null` for general questions
- **`conversation_history`** (optional): Array of previous messages to maintain context

### Response

```json
{
  "answer": "Based on your scenario with a $650,000 home and $3,000/month rent..."
}
```

## Example Conversations

### Example 1: Starting a conversation without calculations

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What factors should I consider when deciding to rent or buy?",
    "inputs": null
  }'
```

### Example 2: With calculation data

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Based on these numbers, what do you recommend?",
    "inputs": {
      "home_price": 650000,
      "monthly_rent": 3000,
      "down_payment_pct": 0.20,
      "mortgage_rate_annual": 0.068,
      "years_horizon": 10
    }
  }'
```

### Example 3: Follow-up question with history

```bash
curl -X POST http://localhost:8000/v1/advise \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What if I only stay for 5 years instead?",
    "inputs": {
      "home_price": 650000,
      "monthly_rent": 3000,
      "years_horizon": 5
    },
    "conversation_history": [
      {
        "role": "user",
        "content": "Based on these numbers, what do you recommend?"
      },
      {
        "role": "assistant",
        "content": "Looking at your 10-year scenario, buying appears to be the better choice..."
      }
    ]
  }'
```

## System Prompt

The chatbot is configured with this personality:

> "You are an expert financial advisor specializing in real estate and housing decisions.
> Your role is to help people make informed rent vs buy decisions by:
> - Analyzing their specific financial situation and goals
> - Explaining complex financial concepts in simple, friendly terms
> - Providing personalized recommendations based on their circumstances
> - Answering follow-up questions and exploring what-if scenarios
> - Being conversational, supportive, and never judgmental
>
> Keep responses concise (2-4 paragraphs max) and actionable. Use a warm, professional tone.
> When you have calculation results, reference specific numbers to support your advice.
> Always consider the user's time horizon, financial flexibility, and lifestyle goals."

## Frontend Integration Tips

1. **Maintain conversation history** in your React/Vue/Angular state
2. **Include previous messages** in each API call for context
3. **Allow users to chat without calculations** for general advice
4. **Update inputs dynamically** as users explore what-if scenarios
5. **Display the conversation** like a typical chat interface

### Example React Hook

```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [inputs, setInputs] = useState(initialInputs);

const sendMessage = async (question: string) => {
  const response = await fetch('/v1/advise', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      inputs,
      conversation_history: messages
    })
  });

  const data = await response.json();

  setMessages([
    ...messages,
    { role: 'user', content: question },
    { role: 'assistant', content: data.answer }
  ]);
};
```

## Environment Setup

Make sure to set your Perplexity API key:

```bash
export PPLX_API_KEY="your-perplexity-api-key"
```

## Testing

You can test the chatbot with the included test script:

```bash
python test_chatbot.py
```

This will run a sample conversation to verify everything works correctly.
