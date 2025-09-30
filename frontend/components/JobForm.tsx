'use client';

import React from "react";
import { analyze, type AnalyzeResponse } from "../lib/api";

export default function JobForm() {
  const [jd, setJd] = React.useState("");
  const [resume, setResume] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [useLLM, setUseLLM] = React.useState(false); // <-- NEW toggle
  const [result, setResult] = React.useState<AnalyzeResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      // pass the toggle into the API call
      const data = await analyze(jd, resume, useLLM);
      setResult(data);
    } catch (err: any) {
      setError(err?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold mb-1">Job Description</label>
          <textarea
            className="textarea"
            placeholder="Paste the JD..."
            value={jd}
            onChange={(e)=>setJd(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">Your Resume (text)</label>
          <textarea
            className="textarea"
            placeholder="Paste your resume text..."
            value={resume}
            onChange={(e)=>setResume(e.target.value)}
          />
        </div>

        {/* NEW: Checkbox to turn the local LLM on/off */}
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={useLLM}
            onChange={(e)=>setUseLLM(e.target.checked)}
          />
          Use local LLM (Ollama)
        </label>

        <button className="btn" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {result && (
        <div className="mt-6 grid gap-4">
          <section className="p-4 rounded-xl border">
            <h3 className="font-semibold mb-2">Matched Skills</h3>
            <p className="text-sm">{result.matched_skills.join(", ") || "—"}</p>
          </section>

          <section className="p-4 rounded-xl border">
            <h3 className="font-semibold mb-2">Missing Skills</h3>
            <p className="text-sm">{result.missing_skills.join(", ") || "—"}</p>
          </section>

          <section className="p-4 rounded-xl border">
            <h3 className="font-semibold mb-2">Tailored Bullets</h3>
            <ul className="list-disc pl-6 text-sm space-y-1">
              {result.tailored_bullets.map((b, i) => <li key={i}>{b}</li>)}
            </ul>

            <button
              className="btn mt-3"
              onClick={() => navigator.clipboard.writeText(result.tailored_bullets.join("\n"))}
            >
              Copy bullets
            </button>

            {typeof result.notes?.jaccard === "number" && (
              <p className="text-xs opacity-70 mt-2">
                Match score (rough Jaccard): {result.notes.jaccard}
              </p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
