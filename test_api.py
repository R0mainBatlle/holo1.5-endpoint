#!/usr/bin/env python3
"""
Test script for the Holo1.5-7B OpenAI-compatible API
Usage:
  python test_api.py <image_url_or_path> <text_query> [api_url]

Examples:
  python test_api.py "https://example.com/image.jpg" "Describe this image"
  python test_api.py screenshot.png "Where is the login button?"
"""

import sys
import requests
import base64
import os


def encode_image_to_base64(image_path: str) -> str:
    """Encode a local image file to base64 data URL"""
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Determine image type from extension
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')

    return f"data:{mime_type};base64,{image_data}"


def test_api(image_input: str, text_query: str, api_url: str = "http://localhost:8000"):
    """Test the Holo1.5-7B API with an image and text query"""

    print(f"Testing OpenAI-compatible API at {api_url}")
    print(f"Image: {image_input}")
    print(f"Query: {text_query}")
    print("-" * 70)

    # Check health first
    try:
        health_response = requests.get(f"{api_url}/health")
        health_data = health_response.json()
        print(f"Health check: {health_data}")
        print("-" * 70)
    except Exception as e:
        print(f"Error checking health: {e}")
        return

    # Determine if input is URL or local file
    if image_input.startswith(('http://', 'https://')):
        image_url = image_input
        print("Using image URL directly")
    elif image_input.startswith('data:'):
        image_url = image_input
        print("Using base64 data URL")
    else:
        # Local file - convert to base64
        try:
            print("Converting local file to base64...")
            image_url = encode_image_to_base64(image_input)
            print("Conversion successful")
        except FileNotFoundError:
            print(f"Error: Image file not found: {image_input}")
            return
        except Exception as e:
            print(f"Error encoding image: {e}")
            return

    print("-" * 70)

    # Make prediction using OpenAI format
    try:
        payload = {
            "model": "Hcompany/Holo1.5-7B",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 512
        }

        print("Sending request to /v1/chat/completions...")
        response = requests.post(
            f"{api_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 70)
            print("SUCCESS!")
            print("=" * 70)
            print(f"\nRequest ID: {result.get('id')}")
            print(f"Model: {result.get('model')}")
            print(f"\nUser Query: {text_query}")
            print(f"\nAssistant Response:")
            print("-" * 70)
            print(result['choices'][0]['message']['content'])
            print("-" * 70)

            usage = result.get('usage', {})
            print(f"\nToken Usage:")
            print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
            print("=" * 70)
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_api.py <image_url_or_path> <text_query> [api_url]")
        print("\nExamples:")
        print('  # Using a URL:')
        print('  python test_api.py "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg" "Describe this image"')
        print('\n  # Using a local file:')
        print('  python test_api.py screenshot.png "Where is the search button?"')
        print('\n  # Custom API URL:')
        print('  python test_api.py image.jpg "What do you see?" "http://my-server:8000"')
        sys.exit(1)

    image_input = sys.argv[1]
    text_query = sys.argv[2]
    api_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"

    test_api(image_input, text_query, api_url)
