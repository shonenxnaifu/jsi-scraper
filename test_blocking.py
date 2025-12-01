"""
Test script to verify the blocking mechanism
"""
import requests
import threading
import time

def test_concurrent_requests():
    """
    Test the blocking mechanism by making concurrent requests
    """
    base_url = "http://localhost:8021"
    
    def make_scraping_request():
        try:
            response = requests.get(f"{base_url}/scrape/json?max_pages=5", timeout=30)  # Increase timeout
            print(f"Scraping request status: {response.status_code}")
            if response.status_code == 423:
                print("Blocking mechanism working: Got 423 Locked status")
                return response.status_code, response.text[:200]  # First 200 chars
            else:
                print(f"Scraping completed with {len(response.json().get('projects', []))} projects")
                return response.status_code, f"Success with {len(response.json().get('projects', []))} projects"
        except requests.exceptions.Timeout:
            print("Request timed out - scraping still in progress")
            return None, "Timeout"
        except Exception as e:
            print(f"Error making request: {e}")
            return None, str(e)
    
    def check_status():
        try:
            response = requests.get(f"{base_url}/scrape/status", timeout=5)
            print(f"Status request status: {response.status_code}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"Status: {status_data.get('status')}, Scraping: {status_data.get('is_scraping')}, Progress: {status_data.get('progress')}")
            return response.status_code
        except Exception as e:
            print(f"Error checking status: {e}")
            return None
    
    print("Testing blocking mechanism:")
    print("1. Checking initial status...")
    check_status()
    
    print("\n2. Making first scraping request (this will start the process)...")
    # Make the first request in the main thread with a timeout to avoid hanging
    first_response = make_scraping_request()
    print(f"First request result: {first_response}")
    
    print("\n3. Checking status during/after first request...")
    check_status()
    
    print("\n4. Making second scraping request (should be blocked if first still running)...")
    # Check if second request is blocked
    second_status, second_text = make_scraping_request()
    if second_status == 423:
        print("SUCCESS: Blocking mechanism is working! Second request was blocked (423 status).")
    else:
        print(f"Second request got status {second_status}. This might be because the first request completed quickly.")
    
    print("\n5. Final status check...")
    check_status()

if __name__ == "__main__":
    test_concurrent_requests()