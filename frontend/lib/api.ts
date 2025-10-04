export type AnalyzeResponse = {
  matched_skills: string[];
  missing_skills: string[];
  jd_keywords: string[];
  resume_keywords: string[];
  tailored_bullets: string[];
  notes: { jaccard?: number; skill_match?: number };
};
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";
export async function analyze(job_text: string, resume_text: string, use_llm: boolean): Promise<AnalyzeResponse> {
  const r = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_text, resume_text, use_llm }),
  });
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}
