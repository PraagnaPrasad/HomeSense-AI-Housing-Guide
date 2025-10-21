"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div className="text-2xl font-bold text-gray-900">
            homesense
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 min-h-screen flex items-center">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: Illustration */}
          <div className="flex justify-center lg:justify-end order-2 lg:order-1">
            <div className="relative">
              {/* Retro Phone Illustration */}
              <div className="relative w-80 h-[500px]">
                {/* Phone Body */}
                <div className="absolute inset-0 bg-gradient-to-b from-indigo-300 to-indigo-400 rounded-[3rem] shadow-2xl">
                  {/* Antenna */}
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 w-2 h-8 bg-indigo-400 rounded-t-full"></div>

                  {/* Speaker Holes */}
                  <div className="absolute top-8 left-1/2 -translate-x-1/2 flex gap-2">
                    <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                    <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                    <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                  </div>

                  {/* Screen */}
                  <div className="absolute top-16 left-8 right-8 h-32 bg-gradient-to-br from-green-900 to-green-950 rounded-lg shadow-inner overflow-hidden">
                    <div className="p-3 space-y-1 font-mono text-green-300 text-xs">
                      <div className="animate-pulse">ANALYZING</div>
                      <div className="animate-pulse" style={{ animationDelay: '0.2s' }}>YOUR HOUSING</div>
                      <div className="animate-pulse text-green-400" style={{ animationDelay: '0.4s' }}>MARKET DATA...</div>
                    </div>
                  </div>

                  {/* Directional Pad */}
                  <div className="absolute top-52 left-1/2 -translate-x-1/2">
                    <svg width="70" height="70" viewBox="0 0 70 70" fill="none">
                      {/* Up */}
                      <rect x="26" y="2" width="18" height="22" rx="4" fill="#6366f1" />
                      <path d="M35 10 L30 15 L40 15 Z" fill="#a5b4fc" />

                      {/* Down */}
                      <rect x="26" y="46" width="18" height="22" rx="4" fill="#6366f1" />
                      <path d="M35 60 L30 55 L40 55 Z" fill="#a5b4fc" />

                      {/* Left */}
                      <rect x="2" y="26" width="22" height="18" rx="4" fill="#6366f1" />
                      <path d="M10 35 L15 30 L15 40 Z" fill="#a5b4fc" />

                      {/* Right */}
                      <rect x="46" y="26" width="22" height="18" rx="4" fill="#6366f1" />
                      <path d="M60 35 L55 30 L55 40 Z" fill="#a5b4fc" />

                      {/* Center */}
                      <circle cx="35" cy="35" r="10" fill="#4f46e5" />
                    </svg>
                  </div>

                  {/* Number Pad */}
                  <div className="absolute bottom-8 left-1/2 -translate-x-1/2 grid grid-cols-3 gap-2.5">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, '*', 0, '#'].map((num, i) => (
                      <div
                        key={i}
                        className="w-[46px] h-[38px] bg-indigo-500 rounded-lg shadow-md flex items-center justify-center text-white font-bold text-sm"
                      >
                        {num}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Heart Emoji */}
                <div className="absolute -bottom-4 -left-4 text-6xl animate-bounce" style={{ animationDuration: '2s' }}>
                  💙
                </div>
              </div>
            </div>
          </div>

          {/* Right: Hero Content */}
          <div className="order-1 lg:order-2 text-center lg:text-left">
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              Not sure if it's
              <br />
              time to buy?
              <br />
              <span className="italic">Let's check together.</span>
            </h1>

            <p className="text-xl text-gray-700 mb-10 leading-relaxed">
              Get personalized rent vs. buy
              <br />
              insights in under 2 minutes.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <button
                onClick={() => router.push('/calculator')}
                className="px-8 py-4 bg-gray-900 text-white rounded-full font-semibold text-lg hover:bg-gray-800 transition-all hover:scale-105 shadow-lg"
              >
                Explore the Tradeoffs
              </button>

              <button
                onClick={() => router.push('/advisor')}
                className="px-8 py-4 bg-white text-gray-900 border-2 border-gray-200 rounded-full font-semibold text-lg hover:border-gray-300 transition-all hover:scale-105 shadow-lg"
              >
                Chat with Advisor
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="absolute bottom-0 left-0 right-0 z-10 py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-500">
          © 2025 Homesense · Built by Praagna Prasad
        </div>
      </footer>
    </div>
  );
}
