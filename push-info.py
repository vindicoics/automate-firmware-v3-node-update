import requests

def make_get_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4xx and 5xx errors
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error making GET request:", e)
        return None

# Example usage:
url = "https://api.example.com/data"
response_data = make_get_request(url)
if response_data:
    print("Response:", response_data)