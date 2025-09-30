from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os, re, httpx

app = FastAPI(title="AI Tailor API", version="0.2.0")

# --- CORS: allow your local Next.js app to call this API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Simple tokenizer utils
# -----------------------
COMMON_STOPWORDS = set('''
a an and are as at be but by for if in into is it no not of on or s such t that the their then there these they this to was will with you your i me my we our from which who whom whose where when how why what
about above below between while do does did done doing did n't cant cannot could should would may might must can
'''.split())

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+\-/\.#]*")

def normalize(text: str) -> List[str]:
    tokens = [t.lower() for t in TOKEN_RE.findall(text)]
    return [t for t in tokens if t not in COMMON_STOPWORDS and len(t) > 1]

def top_keywords(tokens: List[str], top_k: int = 50) -> List[str]:
    from collections import Counter
    return [w for w, _ in Counter(tokens).most_common(top_k)]

# -----------------------
# Skill extraction (allow-list)
# -----------------------
# Phrases are matched first on the raw lowercased text; single tokens use the tokenizer.
PHRASE_SKILLS = [
    "machine learning", "data structures", "object-oriented programming", "github actions", "gitlab ci",
    "ci/cd", "rest api", "graph ql", "graphq l", "unit testing", "test driven development",
    "next.js", "react native", "sql server", "windows server"
]

# Single-token skills/tech (lowercase)
KNOWN_SKILLS = {
    "python","java","javascript","typescript","node","react","next","fastapi","flask","django","express",
    "tailwind","html","css","sass",
    "git","github","gitlab",
    "linux","macos","windows",
    "docker","kubernetes","k8s","nginx",
    "aws","gcp","azure","cloud",
    "sql","postgres","mysql","sqlite","mongodb","redis",
    "rest","graphql","oauth","jwt","api",
    "jenkins","pytest","unittest","jest","vitest","playwright","cypress",
    "pandas","numpy","scikit-learn","sklearn","tensorflow","pytorch","ml",
    "uvicorn","gunicorn",
    "terraform","ansible",
    "bash","shell","zsh","powershell",
    "kafka","rabbitmq",
    "langchain","ollama","openai",
}

def extract_skills(text: str) -> List[str]:
    """Return a canonical list of detected skills from text."""
    t = text.lower()

    found = set()

    # phrase match (keeps exact phrases)
    for ph in PHRASE_SKILLS:
        if ph in t:
            found.add(ph)

    # token match for single-word skills
    toks = set(normalize(text))
    for k in KNOWN_SKILLS:
        if " " not in k and k in toks:
            found.add(k)

    # Minor canonicalization
    if "next" in found and "next.js" in t:
        found.discard("next")
        found.add("next.js")

    if "ml" in found:
        found.discard("ml")
        found.add("machine learning")

    return sorted(found)

# -----------------------
# Optional LLM hint (local Ollama)
# -----------------------
class AnalyzeIn(BaseModel):
    job_text: str
    resume_text: str
    use_llm: Optional[bool] = None  # set by UI checkbox; env var is fallback

class AnalyzeOut(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    jd_keywords: List[str]
    resume_keywords: List[str]
    tailored_bullets: List[str]
    notes: Dict[str, Any] = {}

def simple_bullets(matched: List[str], missing: List[str]) -> List[str]:
    bullets = []
    if matched:
        bullets.append(f"Aligned with core requirements including: {', '.join(matched[:8])}.")
    if missing:
        bullets.append(f"Proactively closing gaps in: {', '.join(missing[:6])} (actively learning/implementing).")
    bullets.append("Delivered measurable results by translating requirements into features, tests, and CI workflows.")
    return bullets

async def ollama_hint(jd: str, resume: str, enabled: bool) -> str:
    if not enabled:
        return ""
    try:
        payload = {
            "model": "llama3.1",
            "prompt": f"Write one crisp STAR-style bullet (max 40 words) tailored to this JD.\nJD:\n{jd}\n\nResume:\n{resume}\nBullet:",
            "stream": False
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("http://localhost:11434/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
    except Exception:
        return ""

# -----------------------
# Main endpoint
# -----------------------
@app.post("/analyze", response_model=AnalyzeOut)
async def analyze(inp: AnalyzeIn):
    # Keyword lists (still shown in UI for transparency)
    jd_tokens = normalize(inp.job_text)
    resume_tokens = normalize(inp.resume_text)
    jd_kw = top_keywords(jd_tokens, top_k=60)
    res_kw = top_keywords(resume_tokens, top_k=60)

    # Skill-based match/miss (NEW: only allowed skills/phrases)
    jd_skills = set(extract_skills(inp.job_text))
    res_skills = set(extract_skills(inp.resume_text))
    matched = sorted(jd_skills & res_skills)
    missing = sorted(jd_skills - res_skills)

    bullets = simple_bullets(matched, missing)

    # Optional local LLM bullet
    use_llm = inp.use_llm if inp.use_llm is not None else bool(os.getenv("USE_OLLAMA"))
    hint = await ollama_hint(inp.job_text, inp.resume_text, enabled=use_llm)
    if hint:
        bullets = [hint] + bullets

    # Simple overlap score on *skills* (not raw tokens)
    union = max(1, len(jd_skills | res_skills))
    score = round(len(jd_skills & res_skills) / union, 3)

    return AnalyzeOut(
        matched_skills=matched,
        missing_skills=missing,
        jd_keywords=jd_kw,
        resume_keywords=res_kw,
        tailored_bullets=bullets,
        notes={"skill_match": score}
    )
