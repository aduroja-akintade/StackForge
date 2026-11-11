"""Regression tests for authentication, quota handling and API contracts."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import gemini_service, supabase_service

client = TestClient(app)

@pytest.mark.parametrize("path,method,payload", [
    ("/analyse/", "POST", {"jd_text": "A cloud engineer must know Kubernetes and Terraform."}),
    ("/recommend/", "POST", {"jd_text": "A cloud engineer must know Kubernetes and Terraform."}),
    ("/implement/", "POST", {"project_title": "Secure AKS Service"}),
    ("/upgrade/", "POST", {"project_description": "A containerized application with no monitoring or logging."}),
    ("/analyse/history", "GET", None),
])
def test_protected_routes_reject_anonymous_requests(path, method, payload):
    response = client.request(method, path, json=payload)
    assert response.status_code == 401

@pytest.fixture
def authenticated(monkeypatch):
    # Mock external dependencies, never call real Gemini/Supabase services.
    monkeypatch.setattr(supabase_service, "client", object())
    async def verify(token):
        return "11111111-1111-4111-8111-111111111111" if token == "valid" else None
    async def consume(user_id, feature):
        assert user_id == "11111111-1111-4111-8111-111111111111"
        return True
    monkeypatch.setattr(supabase_service, "verify_access_token", verify)
    monkeypatch.setattr(supabase_service, "consume_quota", consume)
    yield {"Authorization": "Bearer valid"}

def test_invalid_token_is_rejected(authenticated):
    response = client.get("/analyse/history", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401

def test_client_cannot_supply_other_user_identity(authenticated):
    response = client.post(
        "/analyse/",
        headers=authenticated,
        json={"jd_text": "A cloud engineer must know Kubernetes and Terraform.",
              "user_id": "22222222-2222-4222-8222-222222222222"},
    )
    assert response.status_code == 422

def test_history_scoped_to_verified_identity(authenticated, monkeypatch):
    async def history(user_id):
        assert user_id == "11111111-1111-4111-8111-111111111111"
        return [{"id": "test", "jd_text": "My analysis"}]
    monkeypatch.setattr(supabase_service, "get_user_history", history)
    response = client.get("/analyse/history", headers=authenticated)
    assert response.status_code == 200
    assert len(response.json()["history"]) == 1
    assert client.get("/analyse/history/22222222-2222-4222-8222-222222222222", headers=authenticated).status_code == 404

def test_quota_limit_returns_429(authenticated, monkeypatch):
    async def exhausted(user_id, feature):
        return False
    monkeypatch.setattr(supabase_service, "consume_quota", exhausted)
    response = client.post(
        "/implement/", headers=authenticated,
        json={"project_title": "Reliable Cloud App"},
    )
    assert response.status_code == 429

def test_analysis_success_persists_under_authenticated_user(authenticated, monkeypatch):
    async def generated(jd_text):
        return {"required_skills": ["Terraform"], "preferred_skills": [],
                "tools_technologies": ["Azure"], "recommended_projects": []}
    async def saved(user_id, jd_text, result_json):
        assert user_id == "11111111-1111-4111-8111-111111111111"
        assert result_json["required_skills"] == ["Terraform"]
    monkeypatch.setattr(gemini_service, "analyse_job_description", generated)
    monkeypatch.setattr(supabase_service, "save_analysis", saved)
    response = client.post(
        "/analyse/", headers=authenticated,
        json={"jd_text": "A cloud engineer must know Kubernetes and Terraform."},
    )
    assert response.status_code == 200
    assert response.json()["analysis"]["required_skills"] == ["Terraform"]

def test_model_provider_error_not_leaked(authenticated, monkeypatch):
    async def failed(jd_text, current_skills):
        return {"error": "provider internal key or detail"}
    monkeypatch.setattr(gemini_service, "recommend_projects", failed)
    response = client.post(
        "/recommend/", headers=authenticated,
        json={"jd_text": "A cloud engineer must know Kubernetes and Terraform."},
    )
    assert response.status_code == 502
    assert "internal" not in response.text

def test_request_size_is_limited():
    response = client.post(
        "/analyse/", headers={"Content-Length": "41000"}, content=b"x",
    )
    assert response.status_code == 413

def test_health_does_not_require_auth():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
