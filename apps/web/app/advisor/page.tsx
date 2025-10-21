"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";

const toNumber = (v: string): number | undefined => {
  const s = (v || "").replace(/[,\s]/g, "");
  if (s === "") return undefined;
  const n = Number(s);
  return Number.isFinite(n) ? n : undefined;
};

type Message = {
  role: "user" | "assistant";
  content: string;
};

type UserContext = {
  age?: number;
  annual_income?: number;
  relationship_status?: string;
  kids?: string;
  location?: string;
  savings?: number;
  property_links?: string;
  additional_info?: string;
};

export default function AdvisorPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm your personal housing advisor. I can help you decide whether renting or buying makes sense for your situation. Tell me a bit about yourself - where are you located, what's your budget, and what are your goals?"
    }
  ]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const [context, setContext] = useState<UserContext>({});

  const [ageInput, setAgeInput] = useState("");
  const [incomeInput, setIncomeInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [relationshipInput, setRelationshipInput] = useState("");
  const [savingsInput, setSavingsInput] = useState("");
  const [kidsInput, setKidsInput] = useState("");
  const [additionalInput, setAdditionalInput] = useState("");

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!draft.trim()) return;

    const userMessage = draft.trim();
    const history = [...messages, { role: "user" as const, content: userMessage }];

    // Build context snapshot at send time (prevents stale/NaN values)
    const ctx: UserContext = {
      age: toNumber(ageInput),
      annual_income: toNumber(incomeInput),
      location: locationInput || undefined,
      relationship_status: relationshipInput || undefined,
      savings: toNumber(savingsInput),
      kids: kidsInput || undefined,
      additional_info: additionalInput || undefined,
    };

    setMessages(history);
    setDraft("");
    setLoading(true);

    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/v1/advise` : "http://localhost:8080/v1/advise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userMessage,
          conversation_history: history.map(m => ({ role: m.role, content: m.content })),
          user_context: Object.values(ctx).some(v => v !== undefined && v !== null && !(typeof v === 'number' && Number.isNaN(v))) ? ctx : undefined,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to get response");
      }

      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.answer }]);
    } catch (err: any) {
      const errorMsg = err.message === "Failed to fetch"
        ? "Backend API is not running! Please start it with: cd apps/api && uvicorn app.main:app --reload --port 8080"
        : `Error: ${err.message}`;
      setMessages(prev => [...prev, { role: "assistant", content: errorMsg }]);
    } finally {
      setLoading(false);
    }
  }

  const suggestedQuestions = [
    "Should I rent or buy in my city?",
    "What's the break-even point for buying?",
    "How much do I need for a down payment?",
    "Is now a good time to buy with current rates?",
    "What if I only stay 5 years?",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            homesense
          </Link>
          <Link
            href="/calculator"
            className="px-6 py-2 bg-white border-2 border-gray-200 text-gray-900 rounded-full font-medium hover:border-gray-300 transition-all"
          >
            Start with Calculator
          </Link>
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6 py-8">
        <div className="flex-1 flex flex-col bg-white rounded-3xl shadow-xl overflow-hidden">
          {/* Chat Header */}
          <div className="px-8 py-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold mb-1">Housing Advisor</h1>
                <p className="text-purple-100">
                  Get personalized advice for your situation
                </p>
              </div>
              <button
                onClick={() => setShowContext(!showContext)}
                className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium hover:bg-white/30 transition-all"
              >
                {showContext ? "Hide" : "Add"} Context
              </button>
            </div>
          </div>

          {/* Context Form (Collapsible) */}
          {showContext && (
            <div className="px-8 py-6 bg-purple-50 border-b border-purple-100 relative z-10">
              <h3 className="font-semibold text-gray-900 mb-4">
                Tell us about yourself (optional)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="Age"
                  value={ageInput}
                  onChange={(e) => {
                    const v = e.target.value;
                    console.log('Age changed to:', v);
                    setAgeInput(v);
                  }}
                  onClick={() => console.log('Age input clicked')}
                  onFocus={() => console.log('Age input focused')}
                  className="px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 relative z-20"
                  autoComplete="off"
                  style={{ 
                    pointerEvents: 'auto', 
                    userSelect: 'text',
                    color: '#000000',
                    backgroundColor: '#ffffff',
                    opacity: 1,
                    fontSize: '16px'
                  }}
                />
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="Annual Income"
                  value={incomeInput}
                  onChange={(e) => setIncomeInput(e.target.value)}
                  className="px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 relative z-20"
                  autoComplete="off"
                  style={{ 
                    pointerEvents: 'auto', 
                    userSelect: 'text',
                    color: '#000000',
                    backgroundColor: '#ffffff',
                    opacity: 1,
                    fontSize: '16px'
                  }}
                />
                <input
                  type="text"
                  placeholder="Location (e.g., San Francisco)"
                  value={locationInput}
                  onChange={(e) => setLocationInput(e.target.value)}
                  className="px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 relative z-20"
                  autoComplete="off"
                  style={{ 
                    pointerEvents: 'auto', 
                    userSelect: 'text',
                    color: '#000000',
                    backgroundColor: '#ffffff',
                    opacity: 1,
                    fontSize: '16px'
                  }}
                />
                <input
                  type="text"
                  placeholder="Relationship status"
                  value={relationshipInput}
                  onChange={(e) => setRelationshipInput(e.target.value)}
                  className="px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 relative z-20"
                  autoComplete="off"
                  style={{ pointerEvents: 'auto', userSelect: 'text' }}
                />
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="Savings"
                  value={savingsInput}
                  onChange={(e) => setSavingsInput(e.target.value)}
                  className="px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 relative z-20"
                  autoComplete="off"
                  style={{ 
                    pointerEvents: 'auto', 
                    userSelect: 'text',
                    color: '#000000',
                    backgroundColor: '#ffffff',
                    opacity: 1,
                    fontSize: '16px'
                  }}
                />
                <input
                  type="text"
                  placeholder="Kids (e.g., 2 kids, ages 5 and 7)"
                  value={kidsInput}
                  onChange={(e) => setKidsInput(e.target.value)}
                  className="px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 relative z-20"
                  autoComplete="off"
                  style={{ 
                    pointerEvents: 'auto', 
                    userSelect: 'text',
                    color: '#000000',
                    backgroundColor: '#ffffff',
                    opacity: 1,
                    fontSize: '16px'
                  }}
                />
              </div>
              <textarea
                placeholder="Property links or additional info..."
                value={additionalInput}
                onChange={(e) => setAdditionalInput(e.target.value)}
                className="mt-4 w-full px-4 py-2 bg-white border-2 border-purple-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none relative z-20"
                rows={2}
                autoComplete="off"
                style={{ 
                  pointerEvents: 'auto', 
                  userSelect: 'text',
                  color: '#000000',
                  backgroundColor: '#ffffff',
                  opacity: 1,
                  fontSize: '16px'
                }}
              />
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold mr-3 flex-shrink-0">
                    AI
                  </div>
                )}
                <div
                  className={`max-w-[75%] px-5 py-4 rounded-2xl ${
                    msg.role === "user"
                      ? "bg-gray-900 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold mr-3">
                  AI
                </div>
                <div className="bg-gray-100 px-5 py-4 rounded-2xl">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Suggested Questions */}
          {messages.length === 1 && (
            <div className="px-8 pb-4">
              <div className="text-sm text-gray-600 mb-3">Suggested questions:</div>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setDraft(q)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="px-8 py-6 bg-gray-50 border-t border-gray-200">
            <div className="relative">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask about rent vs buy..."
                className="w-full bg-white border-2 border-gray-200 rounded-2xl pl-5 pr-14 py-4 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-purple-400 transition-all resize-none"
                rows={3}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !draft.trim()}
                className="absolute right-3 bottom-4 bg-purple-500 text-white p-3 rounded-xl hover:bg-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="mt-8 text-center">
          <p className="text-gray-600 mb-4">
            Want to see the numbers?
          </p>
          <Link
            href="/calculator"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 border-2 border-gray-200 rounded-full font-semibold hover:border-gray-300 transition-all shadow-lg"
          >
            Try the Calculator
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
