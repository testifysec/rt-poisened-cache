import requests

def say_hello():
    # Using requests to ensure it's imported
    requests.get("https://example.com")
    return "Hello, world!"
