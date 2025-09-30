from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_minimal():
    r = client.post("/analyze", json={"job_text": "Python FastAPI Postgres CI/CD", "resume_text": "Built FastAPI services with Python and CI"})
    assert r.status_code == 200
    data = r.json()
    assert "matched_skills" in data
    assert isinstance(data["matched_skills"], list)
