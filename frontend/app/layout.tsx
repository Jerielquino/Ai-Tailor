export const metadata = {
  title: "AI Tailor",
  description: "Job-aware resume & bullet generator",
};

import "./globals.css";
import React from "react";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container py-10">
          <header className="mb-8">
            <h1 className="text-3xl font-bold">AI Tailor</h1>
            <p className="text-sm opacity-80">Paste a job description and your resume. Get skills match and tailored bullets.</p>
          </header>
          {children}
          <footer className="mt-10 text-xs opacity-70">Built with Next.js & FastAPI • Local only • Optional LLM via Ollama</footer>
        </div>
      </body>
    </html>
  );
}
