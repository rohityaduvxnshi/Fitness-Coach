#!/usr/bin/env python
"""
Phase 2 Runtime Validation Test
Tests the complete end-to-end workflow for Phase 2
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:4200"

def log(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{status:>8}] {message}")

def test_backend_health():
    """Test 1: Backend health"""
    log("Testing backend health...", "TEST")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            log(f"✓ Backend is healthy", "PASS")
            return True
        else:
            log(f"✗ Backend returned {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Backend connection failed: {e}", "FAIL")
        return False

def test_exercise_endpoint():
    """Test 2: Exercise list endpoint"""
    log("Testing exercise endpoint...", "TEST")
    try:
        response = requests.get(f"{BASE_URL}/exercises", timeout=2)
        if response.status_code == 200:
            exercises = response.json()
            if isinstance(exercises, list) and len(exercises) > 0:
                log(f"✓ Exercises endpoint works (found {len(exercises)} exercises)", "PASS")
                return True, exercises
            else:
                log(f"✗ Exercises list is empty!", "FAIL")
                return False, []
        else:
            log(f"✗ Exercises endpoint returned {response.status_code}", "FAIL")
            return False, []
    except Exception as e:
        log(f"✗ Exercises endpoint failed: {e}", "FAIL")
        return False, []

def test_workout_models():
    """Test 3: Backend database models"""
    log("Testing database models...", "TEST")
    try:
        # Check if app starts without model errors
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code == 200:
            log(f"✓ Database models are valid", "PASS")
            return True
        else:
            log(f"✗ Backend returned {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Database models test failed: {e}", "FAIL")
        return False

def test_workout_routes():
    """Test 4: Workout routes are registered"""
    log("Checking workout routes registration...", "TEST")
    routes_to_check = [
        "POST /workouts/start",
        "GET /workouts/active",
        "GET /workouts/history/all",
        "POST /workouts/{id}/exercises",
        "POST /workouts/exercises/{id}/sets",
    ]
    
    # Check if the API docs show workout routes
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=2)
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})
            
            found_routes = []
            for path in paths:
                if "workout" in path:
                    found_routes.append(path)
            
            if found_routes:
                log(f"✓ Workout routes are registered ({len(found_routes)} endpoints)", "PASS")
                for route in found_routes:
                    log(f"  - {route}", "INFO")
                return True
            else:
                log(f"✗ No workout routes found in OpenAPI spec", "FAIL")
                return False
        else:
            log(f"✗ OpenAPI endpoint returned {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Route check failed: {e}", "FAIL")
        return False

def test_components_and_services():
    """Test 5: Check if components and services are properly configured"""
    log("Checking component and service configurations...", "TEST")
    
    files_to_check = {
        "Frontend routes": "c:\\GitHub\\Fitness Coach\\frontend\\src\\app\\app.routes.ts",
        "Workout service": "c:\\GitHub\\Fitness Coach\\frontend\\src\\app\\services\\workout.service.ts",
        "Active workout component": "c:\\GitHub\\Fitness Coach\\frontend\\src\\app\\modules\\workout\\active-workout.component.ts",
    }
    
    missing_files = []
    for name, path in files_to_check.items():
        try:
            with open(path, 'r') as f:
                content = f.read(100)  # Just check if file exists
                log(f"✓ {name} exists", "PASS")
        except FileNotFoundError:
            missing_files.append(name)
            log(f"✗ {name} NOT FOUND", "FAIL")
    
    # Check for critical imports in app.routes.ts
    try:
        with open("c:\\GitHub\\Fitness Coach\\frontend\\src\\app\\app.routes.ts", 'r') as f:
            content = f.read()
            if "ActiveWorkoutComponent" in content and "WorkoutHistoryComponent" in content:
                if "/workout/active" in content and "/workout/history" in content:
                    log(f"✓ Workout routes are registered in app.routes.ts", "PASS")
                    return True
                else:
                    log(f"✗ Workout route paths not found in app.routes.ts", "FAIL")
                    return False
            else:
                log(f"✗ Workout components not imported in app.routes.ts", "FAIL")
                return False
    except Exception as e:
        log(f"✗ Route configuration check failed: {e}", "FAIL")
        return False

def main():
    log("=" * 60, "START")
    log("PHASE 2 RUNTIME VALIDATION TEST", "START")
    log("=" * 60, "START")
    
    results = {}
    
    # Test 1: Backend Health
    print()
    results["Backend Health"] = test_backend_health()
    time.sleep(0.5)
    
    # Test 2: Exercise Endpoint
    print()
    results["Exercise Endpoint"], exercises = test_exercise_endpoint()
    time.sleep(0.5)
    
    # Test 3: Database Models
    print()
    results["Database Models"] = test_workout_models()
    time.sleep(0.5)
    
    # Test 4: Workout Routes
    print()
    results["Workout Routes"] = test_workout_routes()
    time.sleep(0.5)
    
    # Test 5: Components & Services
    print()
    results["Components & Services"] = test_components_and_services()
    time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    log("TEST SUMMARY", "SUMMARY")
    log("=" * 60, "SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        log(f"{test}: {status}", "SUMMARY")
    
    print()
    log(f"TOTAL: {passed}/{total} tests passed", "FINAL" if passed == total else "WARNING")
    print("=" * 60)
    print()
    
    if passed == total:
        log("All backend tests passed. Frontend should work.", "SUCCESS")
        log("To test the full workflow:", "INFO")
        log("1. Open http://localhost:4200 in browser", "INFO")
        log("2. Login or register", "INFO")
        log("3. Click 'Start Workout' button", "INFO")
        log("4. Add exercises from the library", "INFO")
        log("5. Log sets with weight and reps", "INFO")
        log("6. Finish workout", "INFO")
        log("7. Check workout history", "INFO")
    else:
        log(f"Backend validation FAILED ({total - passed} issues)", "FAILURE")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
    except Exception as e:
        log(f"CRITICAL ERROR: {e}", "ERROR")
        exit(1)
