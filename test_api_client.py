import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:5000/api'

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 40)

def test_get_incidents():
    print("Testing GET /incidents...")
    response = requests.get(f'{BASE_URL}/incidents')
    print_response(response)

def test_create_incident():
    print("Testing POST /incidents...")
    # Assuming user_id 1 exists (admin usually)
    payload = {
        "title": "API Test Incident",
        "description": "This incident was created via the Python API client.",
        "user_id": 1,
        "category": "Software",
        "priority": "High"
    }
    response = requests.post(f'{BASE_URL}/incidents', json=payload)
    print_response(response)
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_get_incident(incident_id):
    print(f"Testing GET /incidents/{incident_id}...")
    response = requests.get(f'{BASE_URL}/incidents/{incident_id}')
    print_response(response)

def test_update_incident(incident_id):
    print(f"Testing PUT /incidents/{incident_id}...")
    payload = {
        "status": "In Progress",
        "priority": "Critical",
        "description": "Updated description via API."
    }
    response = requests.put(f'{BASE_URL}/incidents/{incident_id}', json=payload)
    print_response(response)

def main():
    print("Starting API Tests...\n")
    
    # 1. Get all incidents (limit output if too many)
    # test_get_incidents() 
    
    # 2. Create a new incident
    new_id = test_create_incident()
    
    if new_id:
        # 3. Get the created incident
        test_get_incident(new_id)
        
        # 4. Update the incident
        test_update_incident(new_id)
        
        # 5. Verify update
        test_get_incident(new_id)
    else:
        print("Failed to create incident, skipping subsequent tests.")

if __name__ == "__main__":
    try:
        # Check if server is running
        requests.get(BASE_URL.replace('/api', '/'))
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Please ensure the Flask app is running in another terminal:")
        print("  python run.py")
        sys.exit(1)

    main()
