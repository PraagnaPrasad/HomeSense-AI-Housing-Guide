# 🏠 Rent vs Buy Calculator - Quick Start Guide

## ✅ Current Status

- **API**: ✅ Running on http://localhost:8080
- **Frontend Config**: ✅ Already configured in `.env.local`
- **Integration**: Ready to connect!

## 🚀 How to Connect Frontend to API

### Your Setup is Already Done!

Your `.env.local` file already has:
```bash
NEXT_PUBLIC_API_BASE=http://localhost:8080
```

And your `page.tsx` is already using it:
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";
```

### Start the Frontend:

```bash
# Terminal 1: API is already running on port 8080 ✅

# Terminal 2: Start the frontend
cd apps/web
npm install    # If you haven't already
npm run dev
```

Then open: **http://localhost:3000**

## 🔗 How the Connection Works

### 1. Frontend calls API directly:

```typescript
// In your page.tsx
async function compute(inputs: any, base: string) {
  const r = await fetch(`${base}/v1/compute`, {  // Calls localhost:8080
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inputs),
  });
  return r.json();
}
```

### 2. API Endpoints Available:

| Frontend Calls | API Endpoint | What It Does |
|---------------|--------------|--------------|
| `fetch('/v1/compute')` | `POST /v1/compute` | Calculate rent vs buy |
| `fetch('/v1/summarize')` | `POST /v1/summarize` | Get text summary |
| `fetch('/v1/monte-carlo')` | `POST /v1/monte-carlo` | Run simulations |
| `fetch('/v1/advise')` | `POST /v1/advise` | AI-powered advice |

## 📝 Example API Call from Frontend

```typescript
// Already in your page.tsx!
async function onCompute() {
  setLoading(true);
  try {
    const resp = await fetch(`${API_BASE}/v1/compute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inputs),
    });
    const data = await resp.json();
    setData(data);
  } catch (e) {
    alert(e.message);
  } finally {
    setLoading(false);
  }
}
```

## 🎯 Testing the Connection

### Option 1: Use the Test Script
```bash
cd apps/api
./test_api.sh
```

### Option 2: Manual Test
```bash
# Test from browser console (when on localhost:3000):
fetch('http://localhost:8080/healthz')
  .then(r => r.json())
  .then(console.log)
```

## 🔧 Troubleshooting

### CORS Issues?
FastAPI allows all origins by default in development. If you get CORS errors:

```python
# In apps/api/app/main.py (already done if needed):
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Port Already in Use?
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

### API Not Responding?
```bash
# Check if API is running
curl http://localhost:8080/healthz

# Should return: {"ok":true,"version":"2.0.0"}
```

## 📦 Full Workflow

```bash
# Terminal 1: Start API (already running!)
cd apps/api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8080

# Terminal 2: Start Frontend
cd apps/web
npm install
npm run dev
```

## 🎉 You're All Set!

Your setup is complete:
- ✅ API running on port 8080
- ✅ Frontend configured to connect
- ✅ Environment variables set
- ✅ CORS enabled by default

Just run `npm run dev` in the `apps/web` directory and you're ready to go!

## 🔑 API Keys (Already Configured)

Your `.env` files have:
- **FRED_API_KEY**: For live mortgage rates
- **PPLX_API_KEY**: For AI recommendations

Update `apps/web/.env.local` if you want the frontend to use Perplexity directly:
```bash
PPLX_API_KEY=your_perplexity_api_key_here
```
