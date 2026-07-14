# -*- coding: utf-8 -*-
"""
StudyMate AI - Comprehensive End-to-End Test Script.
Tests every API endpoint and reports results.
"""
import requests
import json
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

BASE = "http://127.0.0.1:8000"
RESULTS = []
USER_ID = None

def test(name, method, endpoint, data=None, headers=None, expected_status=200):
    url = f"{BASE}{endpoint}"
    h = headers or {}
    h["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            r = requests.get(url, headers=h, timeout=60)
        elif method == "POST":
            r = requests.post(url, json=data, headers=h, timeout=120)
        elif method == "DELETE":
            r = requests.delete(url, headers=h, timeout=30)
        else:
            RESULTS.append((name, "SKIP", "Unknown method"))
            return None
        
        body = r.json() if r.text else {}
        passed = r.status_code == expected_status
        status = "PASS" if passed else "FAIL"
        detail = f"Status={r.status_code}, Success={body.get('success', 'N/A')}"
        
        if not passed:
            detail += f", Body={json.dumps(body, ensure_ascii=True)[:200]}"
        
        RESULTS.append((name, status, detail))
        return body
        
    except Exception as e:
        RESULTS.append((name, "ERROR", str(e)[:100]))
        return None


print("=" * 60)
print("TESTING STUDYMATE AI -- ALL ENDPOINTS")
print("=" * 60)

# 1. HEALTH CHECK
test("Health Check", "GET", "/health")

# 2. AUTH - REGISTER
result = test("Register User", "POST", "/api/auth/register", {
    "username": "test_e2e_user",
    "email": "test_e2e@example.com",
    "password": "testpass123"
})

if result and result.get("success"):
    USER_ID = result["data"]["id"]
    print(f"  >> Registered user ID: {USER_ID}")
else:
    result = test("Login (fallback)", "POST", "/api/auth/login", {
        "username": "test_e2e_user",
        "password": "testpass123"
    })
    if result and result.get("success"):
        USER_ID = result["data"]["id"]
        print(f"  >> Logged in user ID: {USER_ID}")

# 3. AUTH - LOGIN
test("Login", "POST", "/api/auth/login", {
    "username": "test_e2e_user",
    "password": "testpass123"
})

test("Login Wrong Password", "POST", "/api/auth/login", {
    "username": "test_e2e_user",
    "password": "wrongpass"
}, expected_status=401)

# 4. AUTH - GET ME
if USER_ID:
    test("Get Profile", "GET", "/api/auth/me", headers={"X-User-ID": USER_ID})
    test("Get Profile Unauthorized", "GET", "/api/auth/me", expected_status=401)

# 5. SUBJECTS - CREATE
SUBJECT_ID = None
if USER_ID:
    result = test("Create Subject (Math)", "POST", "/api/subjects/", {
        "name": "Mathematics",
        "description": "High school math course",
        "difficulty_level": "medium"
    }, headers={"X-User-ID": USER_ID})
    
    if result and result.get("success"):
        SUBJECT_ID = result["data"]["id"]
        print(f"  >> Subject ID: {SUBJECT_ID}")
    
    test("Create Subject (Physics)", "POST", "/api/subjects/", {
        "name": "Physics",
        "description": "Mechanics and thermodynamics",
        "difficulty_level": "hard"
    }, headers={"X-User-ID": USER_ID})

# 6. SUBJECTS - LIST
if USER_ID:
    result = test("List Subjects", "GET", "/api/subjects/", headers={"X-User-ID": USER_ID})
    if result and result.get("success"):
        print(f"  >> Found {len(result['data'])} subjects")

# 7. TOPICS - CREATE
TOPIC_ID = None
if SUBJECT_ID and USER_ID:
    result = test("Create Topic (Algebra)", "POST", f"/api/subjects/{SUBJECT_ID}/topics", {
        "name": "Algebra",
        "description": "Quadratic equations and polynomials",
        "priority": 5
    }, headers={"X-User-ID": USER_ID})
    
    if result and result.get("success"):
        TOPIC_ID = result["data"]["id"]
        print(f"  >> Topic ID: {TOPIC_ID}")
    
    test("Create Topic (Calculus)", "POST", f"/api/subjects/{SUBJECT_ID}/topics", {
        "name": "Calculus",
        "description": "Limits, derivatives, integrals",
        "priority": 4
    }, headers={"X-User-ID": USER_ID})
    
    test("Create Topic (Geometry)", "POST", f"/api/subjects/{SUBJECT_ID}/topics", {
        "name": "Geometry",
        "description": "Triangles, circles, coordinate geometry",
        "priority": 3
    }, headers={"X-User-ID": USER_ID})

# 8. PROGRESS - GET
if USER_ID:
    test("Get Progress", "GET", "/api/progress/", headers={"X-User-ID": USER_ID})

# 9. PROGRESS - UPDATE
if USER_ID and TOPIC_ID:
    test("Update Topic Progress", "POST", "/api/progress/update", {
        "topic_id": TOPIC_ID,
        "confidence_score": 0.75
    }, headers={"X-User-ID": USER_ID})

# 10. QUIZ - GENERATE (uses AI agent)
if USER_ID:
    print("\n  >> Testing Quiz Generation (AI call, may take ~30s)...")
    result = test("Generate Quiz", "POST", "/api/quiz/generate", {
        "topic": "Algebra",
        "difficulty": "medium",
        "num_questions": 3
    }, headers={"X-User-ID": USER_ID})
    
    if result and result.get("success"):
        print(f"  >> Quiz response length: {len(result['data'].get('response', ''))}")
        print(f"  >> Tools used: {result['data'].get('tools_used', [])}")

# 11. QUIZ - HISTORY
if USER_ID:
    test("Quiz History", "GET", "/api/quiz/history", headers={"X-User-ID": USER_ID})

# 12. ANALYTICS
if USER_ID:
    test("Get Analytics", "GET", "/api/analytics/", headers={"X-User-ID": USER_ID})
    test("Weekly Summary", "GET", "/api/analytics/weekly", headers={"X-User-ID": USER_ID})

# 13. CHAT - Send message (uses AI agent + MCP tools)
if USER_ID:
    print("\n  >> Testing AI Chat (LLM + MCP tools, may take ~60s)...")
    result = test("Chat - Study Plan", "POST", "/api/chat/message", {
        "message": "Create a study plan for my math exam on 2026-08-15"
    }, headers={"X-User-ID": USER_ID})
    
    if result and result.get("success"):
        print(f"  >> Response length: {len(result['data'].get('response', ''))}")
        print(f"  >> Tools used: {result['data'].get('tools_used', [])}")
        print(f"  >> Agent steps: {len(result['data'].get('agent_steps', []))}")

# 14. CHAT - History
if USER_ID:
    test("Chat History", "GET", f"/api/chat/history/{USER_ID}", headers={"X-User-ID": USER_ID})

# 15. OPENAPI DOCS
test("OpenAPI Docs", "GET", "/docs")

# RESULTS SUMMARY
print("\n" + "=" * 60)
print("TEST RESULTS SUMMARY")
print("=" * 60)

pass_count = sum(1 for _, s, _ in RESULTS if s == "PASS")
fail_count = sum(1 for _, s, _ in RESULTS if s == "FAIL")
error_count = sum(1 for _, s, _ in RESULTS if s == "ERROR")

for name, status, detail in RESULTS:
    icon = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[ERR]"
    print(f"  {icon} {name}: {detail}")

print(f"\n  TOTAL: {len(RESULTS)} tests | {pass_count} passed | {fail_count} failed | {error_count} errors")
print("=" * 60)
