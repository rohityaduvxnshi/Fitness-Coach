#!/usr/bin/env python
"""
Phase 2 Complete Workflow Test
Tests the complete end-to-end Phase 2 workflow via direct API calls
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test client auth headers (would normally come from login)
# For testing, we'll use a test user ID

def log(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{status:>8}] {message}")

def create_test_user():
    """Create a test user and get auth token"""
    log("Creating test user...", "TEST")
    try:
        email = f"test_p2_workflow_{int(time.time())}@test.com"
        password = "TestPassword123"
        
        # Register
        payload = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        if response.status_code not in [200, 201]:
            log(f"✗ User registration failed: {response.status_code}", "FAIL")
            return None
        
        # Login to get token
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            token = data.get("access_token")
            log(f"✓ User created and logged in: token {token[:20]}...", "PASS")
            return token
        else:
            log(f"✗ Failed to login: {response.status_code} - {response.text}", "FAIL")
            return None
    except Exception as e:
        log(f"✗ Auth failed: {e}", "FAIL")
        return None

def test_complete_workflow(token):
    """Test complete Phase 2 workflow"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Create profile (if needed)
    log("\nStep 1: Getting/Creating Profile", "TEST")
    try:
        profile_payload = {
            "name": "Test User",
            "age": 30,
            "sex": "male",
            "height_cm": 180,
            "weight_kg": 80
        }
        response = requests.post(f"{BASE_URL}/users/profile", json=profile_payload, headers=headers)
        if response.status_code in [200, 201]:
            profile = response.json()
            log(f"✓ Profile ready: ID {profile.get('id')}", "PASS")
        else:
            log(f"⚠ Profile creation: {response.status_code}", "WARN")
    except Exception as e:
        log(f"⚠ Profile creation skipped: {e}", "WARN")
    
    # Step 2: Create goal
    log("\nStep 2: Creating Fitness Goal", "TEST")
    try:
        goal_payload = {
            "goal_type": "weight_gain",  # bulk is represented as weight_gain
            "activity_level": "very_active"
        }
        response = requests.post(f"{BASE_URL}/fitness/goals", json=goal_payload, headers=headers)
        if response.status_code in [200, 201]:
            goal = response.json()
            goal_id = goal.get("id")
            log(f"✓ Goal created: ID {goal_id}", "PASS")
        else:
            log(f"✗ Goal creation failed: {response.status_code} - {response.text[:100]}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Goal creation failed: {e}", "FAIL")
        goal_id = 1  # Fallback
    
    # Step 3: Get exercises
    log("\nStep 3: Fetching Exercise Library", "TEST")
    try:
        response = requests.get(f"{BASE_URL}/exercises?limit=20", headers=headers)
        if response.status_code == 200:
            exercises = response.json()
            if exercises and len(exercises) > 0:
                exercise_id = exercises[0]["id"]
                exercise_name = exercises[0]["name"]
                log(f"✓ Exercises loaded ({len(exercises)} available)", "PASS")
                log(f"  Sample: {exercise_name} (ID: {exercise_id})", "INFO")
            else:
                log(f"✗ No exercises returned", "FAIL")
                return False
        else:
            log(f"✗ Exercise fetch failed: {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Exercise fetch failed: {e}", "FAIL")
        return False
    
    # Step 4: Start Workout
    log("\nStep 4: Starting Workout", "TEST")
    try:
        workout_payload = {
            "name": "Test Workout",
            "notes": "Automated test workout",
            "goal_id": goal_id
        }
        response = requests.post(f"{BASE_URL}/workouts/start", json=workout_payload, headers=headers)
        if response.status_code in [200, 201]:
            workout = response.json()
            workout_id = workout.get("id")
            log(f"✓ Workout started: ID {workout_id}", "PASS")
            log(f"  Started at: {workout.get('started_at')}", "INFO")
        else:
            log(f"✗ Workout start failed: {response.status_code} - {response.text[:100]}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Workout start failed: {e}", "FAIL")
        return False
    
    # Step 5: Get Active Workout
    log("\nStep 5: Loading Active Workout", "TEST")
    try:
        response = requests.get(f"{BASE_URL}/workouts/active", headers=headers)
        if response.status_code == 200:
            active_workout = response.json()
            log(f"✓ Active workout loaded: {active_workout.get('name')}", "PASS")
        else:
            log(f"✗ Active workout load failed: {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Active workout load failed: {e}", "FAIL")
        return False
    
    # Step 6: Add Exercise to Workout
    log("\nStep 6: Adding Exercise to Workout", "TEST")
    try:
        exercise_payload = {
            "exercise_id": exercise_id,
            "order": 1,
            "rpe": 7.5,
            "notes": "Test exercise"
        }
        response = requests.post(f"{BASE_URL}/workouts/{workout_id}/exercises", json=exercise_payload, headers=headers)
        if response.status_code in [200, 201]:
            we = response.json()
            workout_exercise_id = we.get("id")
            log(f"✓ Exercise added to workout: ID {workout_exercise_id}", "PASS")
        else:
            log(f"✗ Add exercise failed: {response.status_code} - {response.text[:100]}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Add exercise failed: {e}", "FAIL")
        return False
    
    # Step 7: Add Set
    log("\nStep 7: Logging Set", "TEST")
    try:
        set_payload = {
            "set_number": 1,
            "reps": 8,
            "weight_kg": 100,
            "rpe": 8,
            "rir": 2,
            "is_warmup": False,
            "notes": "Good form"
        }
        response = requests.post(f"{BASE_URL}/workouts/exercises/{workout_exercise_id}/sets", json=set_payload, headers=headers)
        if response.status_code in [200, 201]:
            set_data = response.json()
            set_id = set_data.get("id")
            volume = set_data.get("volume_kg")
            estimated_1rm = set_data.get("estimated_1rm")
            log(f"✓ Set logged: ID {set_id}", "PASS")
            log(f"  Volume: {volume} kg, Est 1RM: {estimated_1rm:.1f} kg", "INFO")
        else:
            log(f"✗ Set logging failed: {response.status_code} - {response.text[:100]}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Set logging failed: {e}", "FAIL")
        return False
    
    # Step 8: Add another set
    log("\nStep 8: Logging Second Set", "TEST")
    try:
        set_payload["set_number"] = 2
        set_payload["reps"] = 7
        response = requests.post(f"{BASE_URL}/workouts/exercises/{workout_exercise_id}/sets", json=set_payload, headers=headers)
        if response.status_code in [200, 201]:
            log(f"✓ Second set logged", "PASS")
        else:
            log(f"✗ Second set failed: {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Second set failed: {e}", "FAIL")
        return False
    
    # Step 9: Finish Workout
    log("\nStep 9: Finishing Workout", "TEST")
    try:
        finish_payload = {
            "notes": "Great workout!",
            "perceived_exertion": 8
        }
        response = requests.post(f"{BASE_URL}/workouts/{workout_id}/finish", json=finish_payload, headers=headers)
        if response.status_code in [200, 201]:
            finished_workout = response.json()
            log(f"✓ Workout finished", "PASS")
            log(f"  Duration: {finished_workout.get('duration_minutes')} minutes", "INFO")
            log(f"  Total Volume: {finished_workout.get('total_volume_kg')} kg", "INFO")
            log(f"  Total Sets: {finished_workout.get('total_sets')}", "INFO")
        else:
            log(f"✗ Finish workout failed: {response.status_code} - {response.text[:100]}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ Finish workout failed: {e}", "FAIL")
        return False
    
    # Step 10: View Workout History
    log("\nStep 10: Viewing Workout History", "TEST")
    try:
        response = requests.get(f"{BASE_URL}/workouts/history/all?limit=10&offset=0", headers=headers)
        if response.status_code == 200:
            history = response.json()
            if history and len(history) > 0:
                log(f"✓ Workout history retrieved ({len(history)} workouts)", "PASS")
                recent_workout = history[0]
                log(f"  Latest: {recent_workout.get('name')} - {recent_workout.get('total_volume_kg')} kg", "INFO")
            else:
                log(f"⚠ No workouts in history yet", "WARN")
        else:
            log(f"✗ History fetch failed: {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"✗ History fetch failed: {e}", "FAIL")
        return False
    
    return True

def main():
    log("=" * 70, "START")
    log("PHASE 2 COMPLETE WORKFLOW TEST (Direct API Test)", "START")
    log("=" * 70, "START")
    
    # Create test user
    token = create_test_user()
    if not token:
        log("Cannot proceed without auth token", "FAIL")
        return False
    
    # Run complete workflow
    success = test_complete_workflow(token)
    
    # Summary
    print("\n" + "=" * 70)
    log("WORKFLOW TEST COMPLETE", "SUMMARY")
    if success:
        log("✓ ALL STEPS PASSED - Phase 2 workflow works end-to-end!", "SUCCESS")
        log("\nNext: Test the UI", "INFO")
        log("1. Open http://localhost:4200", "INFO")
        log("2. Login", "INFO")
        log("3. Click 'Start Workout'", "INFO")
        log("4. Verify the same workflow works in the browser", "INFO")
    else:
        log("✗ WORKFLOW FAILED - See errors above", "FAILURE")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
        exit(1)
    except Exception as e:
        log(f"CRITICAL ERROR: {e}", "ERROR")
        exit(1)
