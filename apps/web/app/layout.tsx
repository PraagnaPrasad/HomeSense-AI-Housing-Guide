import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rent vs Buy Calculator",
  description: "AI-powered housing decisions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
