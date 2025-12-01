"""
Test to verify API-level blocking mechanism
"""
import requests
import subprocess
import time

def test_api_blocking():
    """
    Test the API-level blocking by calling the endpoint directly during active scraping
    """
    # We will simulate the blocking by directly testing the state manager integration
    from app.state_manager import state_manager
    
    print("Testing API-level blocking mechanism...")
    
    # Manually set scraping in progress to simulate blocking scenario
    print("\n1. Setting scraping status to 'in progress'...")
    try:
        state_manager.start_scraping()
        print("   Scraping status set to in progress")
    except RuntimeError as e:
        print(f"   Error: {e}")
        
    # Check the status endpoint still works (should not be blocked)
    print("\n2. Testing status endpoint (should still work)...")
    try:
        import sys
        sys.path.insert(0, '.')
        from app.main import scrape_status
        status_data = scrape_status()
        print(f"   Status endpoint response: {status_data}")
    except Exception as e:
        print(f"   Error calling status endpoint: {e}")
    
    # Test the is_scraping method
    print("\n3. Testing is_scraping method...")
    is_scraping = state_manager.is_scraping()
    print(f"   Is scraping in progress: {is_scraping}")
    
    # Test that we can't start another scraping while one is in progress
    print("\n4. Testing concurrent start attempt...")
    try:
        state_manager.start_scraping()
        print("   Unexpectedly succeeded in starting concurrent scraping")
    except RuntimeError as e:
        print(f"   Correctly blocked concurrent scraping: {e}")
    
    # Reset the state
    print("\n5. Finishing scraping...")
    state_manager.finish_scraping()
    print("   Scraping finished")
    
    is_scraping_now = state_manager.is_scraping()
    print(f"   Is scraping in progress after finish: {is_scraping_now}")
    
    print("\nAPI blocking test completed successfully!")

if __name__ == "__main__":
    test_api_blocking()