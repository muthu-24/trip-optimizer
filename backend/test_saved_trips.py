import json
import urllib.request
import urllib.error
import uuid

BASE_URL = "http://127.0.0.1:8000"

def request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            return status, json.loads(content) if content else None
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            body = json.loads(content)
        except Exception:
            body = content
        return e.code, body

def run_tests():
    print("=== Testing Saved Trips API ===")

    # 1. Register User A and User B
    email_a = f"user_a_{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"user_b_{uuid.uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    code, res_a = request("POST", "/api/auth/register", {"name": "User A", "email": email_a, "password": pwd})
    assert code == 201, f"Register A failed ({code}): {res_a}"
    print("[PASS] User A registered")

    code, res_b = request("POST", "/api/auth/register", {"name": "User B", "email": email_b, "password": pwd})
    assert code == 201, f"Register B failed ({code}): {res_b}"
    print("[PASS] User B registered")

    # 2. Login
    code, login_a = request("POST", "/api/auth/login", {"email": email_a, "password": pwd})
    assert code == 200, f"Login A failed: {login_a}"
    token_a = login_a["access_token"]

    code, login_b = request("POST", "/api/auth/login", {"email": email_b, "password": pwd})
    assert code == 200, f"Login B failed: {login_b}"
    token_b = login_b["access_token"]
    print("[PASS] Both users logged in successfully")

    # 3. Unauthenticated access should be rejected (401 or 403)
    code, _ = request("GET", "/api/saved-trips")
    assert code in (401, 403), f"Expected 401/403 for unauth access, got {code}"
    print("[PASS] Unauthenticated access blocked")

    # 4. User A saves a trip with Day 10 route optimization data
    mock_itinerary_data = {
        "itinerary": [
            {
                "day": 1,
                "activities": [
                    {
                        "id": 1,
                        "name": "Galle Fort Ramparts",
                        "category": "Culture",
                        "estimated_cost": 0.0,
                        "duration": 2.5,
                        "rating": 4.9,
                        "score": 95.0,
                        "latitude": 6.032,
                        "longitude": 80.217,
                        "distance_to_next": 1.5
                    },
                    {
                        "id": 2,
                        "name": "Maritime Museum",
                        "category": "Culture",
                        "estimated_cost": 1500.0,
                        "duration": 1.5,
                        "rating": 4.4,
                        "score": 82.0,
                        "latitude": 6.035,
                        "longitude": 80.220
                    }
                ],
                "total_duration": 4.0,
                "total_cost": 1500.0,
                "total_distance": 1.5
            }
        ],
        "cost_breakdown": {
            "daily_total": 13000.0,
            "trip_activities": 1500.0,
            "estimated_trip_total": 27500.0
        },
        "preferences": {
            "budget": "50000",
            "tripDuration": "2",
            "travelStyle": "Culture",
            "season": "December-April",
            "activities": ["Culture", "History"]
        }
    }

    payload = {
        "destination_name": "Galle",
        "trip_duration": 2,
        "budget": 50000.0,
        "travel_style": "Culture",
        "season": "December-April",
        "total_route_distance": 1.5,
        "itinerary_data": mock_itinerary_data
    }

    code, saved_trip = request("POST", "/api/saved-trips", payload, token=token_a)
    assert code == 201, f"Save trip failed ({code}): {saved_trip}"
    trip_id = saved_trip["id"]
    assert saved_trip["destination_name"] == "Galle"
    assert saved_trip["total_route_distance"] == 1.5
    print(f"[PASS] Trip saved for User A (ID: {trip_id})")

    # 5. User A lists saved trips
    code, list_a = request("GET", "/api/saved-trips", token=token_a)
    assert code == 200
    assert len(list_a) >= 1
    assert any(t["id"] == trip_id for t in list_a)
    print(f"[PASS] User A retrieves saved trips list ({len(list_a)} trips)")

    # 6. User B lists saved trips (must NOT see User A's trips)
    code, list_b = request("GET", "/api/saved-trips", token=token_b)
    assert code == 200
    assert not any(t["id"] == trip_id for t in list_b)
    print("[PASS] User B cannot see User A's saved trips in list")

    # 7. User A views trip details
    code, detail_a = request("GET", f"/api/saved-trips/{trip_id}", token=token_a)
    assert code == 200
    assert detail_a["id"] == trip_id
    assert detail_a["itinerary_data"]["itinerary"][0]["activities"][0]["distance_to_next"] == 1.5
    print("[PASS] User A views full trip details including route distances")

    # 8. User B attempts to view User A's trip (Security check: 403 or 404)
    code, _ = request("GET", f"/api/saved-trips/{trip_id}", token=token_b)
    assert code in (403, 404), f"Expected 403 or 404 for unauthorized view, got {code}"
    print("[PASS] User B blocked from viewing User A's trip (403/404)")

    # 9. User B attempts to delete User A's trip (Security check: 403 or 404)
    code, _ = request("DELETE", f"/api/saved-trips/{trip_id}", token=token_b)
    assert code in (403, 404), f"Expected 403 or 404 for unauthorized delete, got {code}"
    print("[PASS] User B blocked from deleting User A's trip (403/404)")

    # 10. User A deletes trip
    code, _ = request("DELETE", f"/api/saved-trips/{trip_id}", token=token_a)
    assert code == 204, f"Delete failed: {code}"
    print("[PASS] User A successfully deleted trip (204)")

    # 11. Verify trip is deleted
    code, _ = request("GET", f"/api/saved-trips/{trip_id}", token=token_a)
    assert code == 404, f"Expected 404 after deletion, got {code}"
    print("[PASS] Trip no longer exists after deletion (404)")

    print("\nALL 11 BACKEND SAVED TRIPS TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
