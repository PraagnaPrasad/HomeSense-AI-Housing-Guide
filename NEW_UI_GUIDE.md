# New UI/UX Design Guide 🎨

## Overview

Complete redesign with a clean, modern aesthetic inspired by your reference image. The new design focuses on **simplicity, clarity, and user flow**.

## Design Principles

1. **Soft Gradients** - Purple/pink/orange tones for warmth and approachability
2. **Generous White Space** - Let content breathe
3. **Clear Hierarchy** - Guide users through the experience
4. **Conversational Tone** - Friendly, human copy
5. **Progressive Disclosure** - Show what's needed, hide complexity

## New Page Structure

### 1. Landing Page (`/`)

**Purpose**: Welcome users and present clear paths forward

**Key Elements**:
- Clean hero section with friendly copy
- Playful retro phone illustration (CSS-only, no images needed)
- Two clear CTAs: "Use Calculator" and "Chat with Advisor"
- Minimal navigation: Logo, Sign up, Log in
- Soft gradient background

**Copy**:
```
Not sure if it's time to buy?
Let's check together.

Get personalized rent vs. buy insights in under 2 minutes.
```

**Routes**:
- `/calculator` - Full calculation tool
- `/advisor` - AI chat interface

---

### 2. Calculator Page (`/calculator`)

**Purpose**: Provide comprehensive analysis with clear results

**User Flow**:
1. **Input Form** (simplified by default)
   - 6 essential fields visible
   - Advanced settings collapsed (click to expand)
   - City data integration (coming soon)
   - Live FRED rates (coming soon)

2. **Results Display** (after calculation)
   - Winner card with clear verdict
   - Key metrics grid (3 cards)
   - Wealth comparison (side-by-side)
   - Recommendations with confidence score
   - CTA to chat for questions

**Design Details**:
- White cards with rounded corners (`rounded-3xl`)
- Shadow effects for depth
- Color coding:
  - Green for buying advantage
  - Blue for renting advantage
  - Purple for recommendations
  - Yellow for warnings

---

### 3. Advisor Page (`/advisor`)

**Purpose**: Conversational interface for personalized advice

**Features**:
- Chat interface with message history
- Optional context form (age, income, location, etc.)
- Suggested questions for first-time users
- Real-time responses from Perplexity AI
- Persistent conversation history

**Design Details**:
- Purple gradient header
- White message bubbles for AI
- Dark bubbles for user
- Avatar badges (AI logo, user initials)
- Smooth scrolling to new messages

---

## Color Palette

```css
/* Backgrounds */
bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50

/* Primary Actions */
bg-gray-900 text-white  /* Primary CTA */
bg-white border-gray-200  /* Secondary CTA */

/* Status Colors */
Green (#10b981) - Buying advantage
Blue (#3b82f6) - Renting advantage
Purple (#8b5cf6) - Info/Neutral
Yellow (#f59e0b) - Warnings
Pink (#ec4899) - Accents

/* Text */
text-gray-900 - Headings
text-gray-700 - Body
text-gray-500 - Secondary
```

## Typography

```css
/* Headings */
text-5xl lg:text-6xl font-bold  /* H1 - Hero */
text-4xl font-bold  /* H2 - Page titles */
text-2xl font-bold  /* H3 - Section titles */

/* Body */
text-lg  /* Large body */
text-base  /* Normal body */
text-sm  /* Small text */
text-xs  /* Helper text */
```

## Component Patterns

### Buttons

**Primary CTA**:
```tsx
className="px-8 py-4 bg-gray-900 text-white rounded-full font-semibold text-lg hover:bg-gray-800 transition-all hover:scale-105 shadow-lg"
```

**Secondary CTA**:
```tsx
className="px-8 py-4 bg-white text-gray-900 border-2 border-gray-200 rounded-full font-semibold text-lg hover:border-gray-300 transition-all hover:scale-105 shadow-lg"
```

### Input Fields

```tsx
className="w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 text-gray-900 font-medium focus:outline-none focus:border-purple-400 focus:bg-white transition-all"
```

### Cards

```tsx
className="bg-white rounded-3xl shadow-xl p-8 lg:p-12"
```

### Metric Cards

```tsx
className="bg-white rounded-2xl shadow-lg p-6"
```

## Animations

### Fade In (for results)

Add to `tailwind.config.ts`:
```typescript
animation: {
  'fade-in': 'fadeIn 0.5s ease-in-out',
}
keyframes: {
  fadeIn: {
    '0%': { opacity: '0', transform: 'translateY(10px)' },
    '100%': { opacity: '1', transform: 'translateY(0)' },
  }
}
```

### Hover Scale

```tsx
className="transition-all hover:scale-105"
```

### Loading Spinner

```tsx
<div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
```

## Responsive Design

All pages are fully responsive:

**Breakpoints**:
- `sm:` - 640px
- `md:` - 768px
- `lg:` - 1024px

**Mobile**:
- Single column layouts
- Stacked CTAs
- Simplified navigation

**Desktop**:
- Multi-column grids
- Side-by-side comparisons
- Expanded navigation

## User Flow

```
Landing Page (/)
    ├─> Use Calculator ─> Calculator Page (/calculator)
    │                          ├─> Fill inputs
    │                          ├─> Calculate
    │                          ├─> See results
    │                          └─> Chat with Advisor ─> Advisor Page
    │
    └─> Chat with Advisor ─> Advisor Page (/advisor)
                                 ├─> Ask questions
                                 ├─> Get personalized advice
                                 └─> Try Calculator ─> Calculator Page
```

## API Integration

### Calculator Page

Uses `/v1/compute-formatted` endpoint:
```typescript
const res = await fetch("http://localhost:8080/v1/compute-formatted", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(inputs),
});
const data = await res.json();
// data contains: summary, key_metrics, wealth_metrics, cash_flow, chart_data, recommendation
```

### Advisor Page

Uses `/v1/advise` endpoint:
```typescript
const res = await fetch("http://localhost:8080/v1/advise", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: userMessage,
    conversation_history: messages,
    user_context: context,  // Optional
  }),
});
const data = await res.json();
// data.answer contains AI response
```

## What Changed from Old UI

### Before:
- ❌ Split-screen calculator + chat on same page
- ❌ Black background with neon gradients
- ❌ All inputs visible at once (overwhelming)
- ❌ Results mixed with chat
- ❌ Unclear user journey
- ❌ No landing page

### After:
- ✅ Separate, focused pages for each task
- ✅ Soft, approachable gradients
- ✅ Progressive disclosure (essential → advanced)
- ✅ Clean results presentation
- ✅ Clear user flow (landing → calculate OR chat)
- ✅ Professional landing page

## Quick Start

1. **Start the backend** (if not already running):
   ```bash
   cd apps/api
   uvicorn app.main:app --reload --port 8080
   ```

2. **Start the frontend**:
   ```bash
   cd apps/web
   npm run dev
   ```

3. **Open browser**:
   - Landing: http://localhost:3000
   - Calculator: http://localhost:3000/calculator
   - Advisor: http://localhost:3000/advisor

## Next Steps (Optional Enhancements)

1. **City Data Integration**
   - Add city selector to calculator
   - Auto-populate growth rates from Zillow

2. **FRED Rates**
   - "Load Current Rates" button
   - Auto-fill mortgage rate and inflation

3. **Chart Visualization**
   - Add cumulative cost chart using Chart.js or Recharts
   - Show break-even point visually

4. **Saved Calculations**
   - Allow users to save scenarios
   - Compare multiple scenarios side-by-side

5. **Authentication**
   - Connect Sign up / Log in buttons
   - Save user preferences and history

6. **Mobile App**
   - PWA support
   - Native app using React Native

## File Structure

```
apps/web/app/
├── page.tsx              # Landing page (NEW)
├── calculator/
│   └── page.tsx         # Calculator page (NEW)
├── advisor/
│   └── page.tsx         # Advisor chat page (NEW)
├── layout.tsx           # Root layout (existing)
└── globals.css          # Global styles (existing)
```

## Summary

This redesign delivers on your vision:
- ✅ Clean, modern aesthetic matching reference image
- ✅ Soft gradients (purple/pink/orange)
- ✅ Clear user flow (landing → calculator OR advisor)
- ✅ Conversational, friendly copy
- ✅ Fully responsive
- ✅ Production-ready code

The UI is now **simple, beautiful, and effective** - focused on helping users make informed housing decisions without overwhelming them.
