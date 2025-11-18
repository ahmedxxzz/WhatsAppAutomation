import requests
import logging

class NodeClient:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url

    def send_message(self, phone, message):
        """
        Sends a POST request to the local Node.js server.
        Note: index.js adds '@c.us', so we send the raw number.
        """
        url = f"{self.base_url}/send-message"
        payload = {
            "number": str(phone),
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.ConnectionError:
            return False, "Connection Error: Node.js server is not reachable."
        except requests.exceptions.Timeout:
            return False, "Timeout: Node.js server took too long."
        except requests.exceptions.RequestException as e:
            return False, f"HTTP Error: {str(e)}"