#!/usr/bin/env python3
"""
Simple script to test the API server connection.
Run this script to verify that the backend server is working properly.
"""

import sys
import requests
import time
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Test the API server connection')
parser.add_argument('--port', type=int, default=5001, help='Port the server is running on')
args = parser.parse_args()

API_URL = f"http://localhost:{args.port}/api"

def test_ping():
    """Test the API ping endpoint"""
    try:
        response = requests.get(f"{API_URL}/ping")
        if response.status_code == 200:
            data = response.json()
            print("✅ API server is running")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ API server returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API server at {API_URL}")
        print("   Make sure the backend server is running:")
        print("   1. Navigate to the backend directory: cd backend")
        print(f"   2. Start the server: python server.py --port {args.port}")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API server: {e}")
        return False

def test_simple_story_generation():
    """Test a simple story generation request"""
    try:
        print("\nTesting story generation API...")
        
        # Send a test story generation request
        payload = {
            "prompt": "Write a very short test story.",
            "model": "gpt-4o",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-story", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('taskId')
            print(f"✅ Story generation request accepted. Task ID: {task_id}")
            
            # Check status a few times
            print("\nChecking task status...")
            for i in range(3):
                time.sleep(1)
                status_response = requests.get(f"{API_URL}/status/{task_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status: {status_data.get('status')}")
                    print(f"   Elapsed time: {status_data.get('elapsedTime', 0):.1f} seconds")
                else:
                    print(f"❌ Failed to get task status: {status_response.status_code}")
                    break
            
            return True
        else:
            print(f"❌ Story generation API returned error: {response.status_code}")
            if response.text:
                print(f"   Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing story generation: {e}")
        return False

if __name__ == "__main__":
    print("Testing WriteHERE API Server connection...")
    print("-" * 50)
    
    ping_success = test_ping()
    
    # Story generation test disabled as requested
    # if ping_success:
    #     test_simple_story_generation()
    
    print("\nAPI test script completed")