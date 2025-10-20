#!/usr/bin/env python3
"""
Simple test script for the Holo1.5-7B API
Usage: python test_api.py <image_path> <text_query>
"""

import sys
import requests


def test_api(image_path: str, text_query: str, api_url: str = "http://localhost:8000"):
    """Test the Holo1.5-7B API with an image and text query"""

    print(f"Testing API at {api_url}")
    print(f"Image: {image_path}")
    print(f"Query: {text_query}")
    print("-" * 50)

    # Check health first
    try:
        health_response = requests.get(f"{api_url}/health")
        print(f"Health check: {health_response.json()}")
        print("-" * 50)
    except Exception as e:
        print(f"Error checking health: {e}")
        return

    # Make prediction
    try:
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            data = {"text": text_query}

            print("Sending request...")
            response = requests.post(f"{api_url}/predict", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print("Success!")
                print(f"\nInput: {result['text_input']}")
                print(f"\nModel Output:\n{result['model_output']}")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)

    except FileNotFoundError:
        print(f"Error: Image file not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_api.py <image_path> <text_query> [api_url]")
        print("\nExample:")
        print('  python test_api.py screenshot.png "Where is the search button?"')
        sys.exit(1)

    image_path = sys.argv[1]
    text_query = sys.argv[2]
    api_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"

    test_api(image_path, text_query, api_url)
