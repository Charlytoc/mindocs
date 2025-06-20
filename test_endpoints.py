#!/usr/bin/env python3
"""
Test script for the new endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8006"


def test_update_demand():
    """Test updating a demand"""
    case_id = "test-case-id"  # You'll need to use a real case ID
    html_content = "<h1>Test Demand</h1><p>This is a test demand content.</p>"

    data = {"html_content": html_content}

    try:
        response = requests.put(f"{BASE_URL}/api/case/{case_id}/demand", data=data)
        print(f"Update Demand Response: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing update demand: {e}")


def test_update_agreement():
    """Test updating an agreement"""
    case_id = "test-case-id"  # You'll need to use a real case ID
    html_content = "<h1>Test Agreement</h1><p>This is a test agreement content.</p>"

    data = {"html_content": html_content}

    try:
        response = requests.put(f"{BASE_URL}/api/case/{case_id}/agreement", data=data)
        print(f"Update Agreement Response: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing update agreement: {e}")


def test_request_ai_changes():
    """Test requesting AI changes"""
    case_id = "test-case-id"  # You'll need to use a real case ID
    document_type = "demand"
    user_feedback = (
        "Please make the tone more formal and add more details about the facts."
    )

    data = {"document_type": document_type, "user_feedback": user_feedback}

    try:
        response = requests.post(
            f"{BASE_URL}/api/case/{case_id}/request-ai-changes", data=data
        )
        print(f"Request AI Changes Response: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing request AI changes: {e}")


if __name__ == "__main__":
    print("Testing new endpoints...")
    print("=" * 50)

    test_update_demand()
    print("-" * 30)

    test_update_agreement()
    print("-" * 30)

    test_request_ai_changes()
    print("=" * 50)
    print("Tests completed!")
