"""
Direct test of the state manager functionality
"""
import time
import threading
from app.state_manager import state_manager

def test_state_manager():
    print("Testing State Manager functionality...")
    
    # Test initial state
    print("\n1. Initial status:")
    status = state_manager.get_status()
    print(f"   Status: {status}")
    
    # Test starting scraping
    print("\n2. Starting scraping...")
    try:
        state_manager.start_scraping()
        print("   Successfully started scraping")
    except RuntimeError as e:
        print(f"   Error starting: {e}")
    
    # Check status after starting
    print("\n3. Status after starting:")
    status = state_manager.get_status()
    print(f"   Status: {status}")
    
    # Try starting again (should fail)
    print("\n4. Trying to start scraping again (should fail)...")
    try:
        state_manager.start_scraping()
        print("   Unexpectedly succeeded in starting")
    except RuntimeError as e:
        print(f"   Correctly failed to start again: {e}")
    
    # Update progress
    print("\n5. Updating progress...")
    state_manager.update_progress(25.0, 10)
    status = state_manager.get_status()
    print(f"   Status after progress update: {status}")
    
    # Finish scraping
    print("\n6. Finishing scraping...")
    state_manager.finish_scraping("Test completed successfully")
    status = state_manager.get_status()
    print(f"   Status after finishing: {status}")
    
    print("\n7. Trying to start again after finishing...")
    try:
        state_manager.start_scraping()
        print("   Successfully started scraping again after finish")
        state_manager.finish_scraping()
    except RuntimeError as e:
        print(f"   Error: {e}")
    
    print("\nState manager test completed!")

def test_concurrent_access():
    print("\n\nTesting concurrent access simulation...")
    
    def simulate_worker(worker_id):
        print(f"Worker {worker_id}: Checking if scraping in progress...")
        if state_manager.is_scraping():
            print(f"Worker {worker_id}: Scraping in progress, would block request")
            return False
        else:
            print(f"Worker {worker_id}: No scraping in progress, can start scraping")
            try:
                state_manager.start_scraping()
                print(f"Worker {worker_id}: Started scraping successfully")
                # Simulate work with progress updates
                for progress in [25, 50, 75, 100]:
                    time.sleep(0.1)  # Simulate work
                    state_manager.update_progress(progress, progress * 2)
                state_manager.finish_scraping(f"Worker {worker_id} completed")
                print(f"Worker {worker_id}: Finished scraping")
                return True
            except RuntimeError as e:
                print(f"Worker {worker_id}: Failed to start: {e}")
                return False
    
    # Test with two "workers" to simulate concurrent access
    print("Simulating two concurrent requests...")
    
    # First worker starts
    worker1_success = simulate_worker(1)
    
    # Second worker tries immediately after (would be blocked in real scenario)
    worker2_success = simulate_worker(2)
    
    if not worker2_success:
        print("Second worker was correctly blocked!")
    else:
        print("Both workers ran concurrently - this indicates the first completed quickly")

if __name__ == "__main__":
    test_state_manager()
    test_concurrent_access()