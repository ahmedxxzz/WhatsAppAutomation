import requests
import json
import time

# The URL where your Node.js API is running
NODE_API_URL = "http://localhost:3000/send-message"

def send_whatsapp_message(number, message):
    """
    Sends a message to the specified number via the Node.js API.
    """
    payload = {"number": number,"message": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(NODE_API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        
        print("API Response:")
        print(response.json())
        return response.json()

    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
        print(f"Response body: {response.text}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Oops: Something Else: {err}")


if __name__ == "__main__":
    # IMPORTANT: Wait for the Node.js server to be ready and for you to scan the QR code.
    print("Make sure your Node.js server is running and you have scanned the QR code.")

    # Replace with the recipient's phone number (including country code, no + or 00)
    recipient_number = "201001928364"

    # The message you want to send
    message_to_send = "Hello from the code 😘 "
    for i in range(10):
        send_whatsapp_message(recipient_number, message_to_send)