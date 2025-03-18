#!/usr/bin/env python3
"""
Simple script to test the API server connection.
Run this script to verify that the backend server is working properly.
"""

import sys
import requests
import time

API_URL = "http://localhost:5001/api"

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
        print("❌ Could not connect to API server at http://localhost:5001")
        print("   Make sure the backend server is running:")
        print("   1. Navigate to the backend directory: cd backend")
        print("   2. Start the server: python server.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API server: {e}")
        return False

def test_simple_story_generation():
    """Test a simple story generation request"""
    try:
        print("\nTesting story generation API...")
        
        # Test English story generation
        print("\nTesting English story generation...")
        payload = {
            "prompt": "Write a very short test story.",
            "model": "gpt-4o",
            "outputLanguage": "english",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-story", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('taskId')
            print(f"✅ English story generation request accepted. Task ID: {task_id}")
            
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
        else:
            print(f"❌ English story generation API returned error: {response.status_code}")
            if response.text:
                print(f"   Error details: {response.text}")
            return False
            
        # Test Chinese story generation
        print("\nTesting Chinese story generation...")
        payload = {
            "prompt": "Write a very short test story about a cat.",
            "model": "gpt-4o",
            "outputLanguage": "chinese",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-story", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('taskId')
            print(f"✅ Chinese story generation request accepted. Task ID: {task_id}")
            
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
        else:
            print(f"❌ Chinese story generation API returned error: {response.status_code}")
            if response.text:
                print(f"   Error details: {response.text}")
            return False
            
        # Test invalid language
        print("\nTesting invalid language...")
        payload = {
            "prompt": "Write a very short test story.",
            "model": "gpt-4o",
            "outputLanguage": "french",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-story", json=payload)
        
        if response.status_code == 400:
            print("✅ Invalid language correctly rejected")
        else:
            print(f"❌ Invalid language not properly handled: {response.status_code}")
            if response.text:
                print(f"   Response details: {response.text}")
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ Error testing story generation: {e}")
        return False

def test_simple_report_generation():
    """Test a simple report generation request"""
    try:
        print("\nTesting report generation API...")
        
        # Test English report generation
        print("\nTesting English report generation...")
        payload = {
            "prompt": "Write a very short test report.",
            "model": "gpt-4o",
            "outputLanguage": "english",
            "enableSearch": True,
            "searchEngine": "google",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key",
                "serpapi": "test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-report", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('taskId')
            print(f"✅ English report generation request accepted. Task ID: {task_id}")
            
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
        else:
            print(f"❌ English report generation API returned error: {response.status_code}")
            if response.text:
                print(f"   Error details: {response.text}")
            return False
            
        # Test Chinese report generation
        print("\nTesting Chinese report generation...")
        payload = {
            "prompt": "Write a very short test report about renewable energy.",
            "model": "gpt-4o",
            "outputLanguage": "chinese",
            "enableSearch": True,
            "searchEngine": "google",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key",
                "serpapi": "test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-report", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('taskId')
            print(f"✅ Chinese report generation request accepted. Task ID: {task_id}")
            
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
        else:
            print(f"❌ Chinese report generation API returned error: {response.status_code}")
            if response.text:
                print(f"   Error details: {response.text}")
            return False
            
        # Test invalid language
        print("\nTesting invalid language...")
        payload = {
            "prompt": "Write a very short test report.",
            "model": "gpt-4o",
            "outputLanguage": "french",
            "enableSearch": True,
            "searchEngine": "google",
            "apiKeys": {
                "openai": "sk-test-key",
                "claude": "sk-ant-test-key",
                "serpapi": "test-key"
            }
        }
        
        response = requests.post(f"{API_URL}/generate-report", json=payload)
        
        if response.status_code == 400:
            print("✅ Invalid language correctly rejected")
        else:
            print(f"❌ Invalid language not properly handled: {response.status_code}")
            if response.text:
                print(f"   Response details: {response.text}")
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ Error testing report generation: {e}")
        return False

if __name__ == "__main__":
    print("Testing WriteHERE API Server connection...")
    print("-" * 50)
    
    ping_success = test_ping()
    
    if ping_success:
        test_simple_story_generation()
        test_simple_report_generation()
    
    print("\nAPI test script completed")