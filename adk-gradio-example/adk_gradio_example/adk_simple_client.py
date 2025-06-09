from functools import lru_cache
import os
from typing import Dict, Optional
from dotenv import load_dotenv
import httpx
from google.genai import types

load_dotenv()


class ADKChatClient:
    def __init__(self, user_session_id: str = None, base_url: str = None):
        """Initialize the ADK chat client"""
        self.user_session_id = user_session_id
        self.base_url = base_url or "https://generativelanguage.googleapis.com/v1beta"
        self.app_name = "weather_agent"
        self.user_id = "user"
        self.session_id = None
        self.trace_cache = {}
        self.graph_cache = {}
        self.custom_api_key: Optional[str] = None

    def start_session(self) -> bool:
        try:
            headers = {"Content-Type": "application/json"}

            response = httpx.post(
                f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions",
                headers=headers,
            )

            if response.status_code == 200:
                json_response = response.json()
                self.session_id = json_response.get("id")
                return True
            else:
                print(
                    f"Failed to start session: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error starting session: {str(e)}")
            return False

    def send_message(self, text_message: str) -> Optional[str]:
        """Send a message to the ADK agent and get response"""
        if not self.session_id:
            return "Error: No active session. Please start a session first."

        headers = {"Content-Type": "application/json"}
        message = {"parts": [{"text": text_message}], "role": "user"}

        payload = {
            "app_name": self.app_name,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "new_message": message,
            "streaming": False,
        }

        prev_api_key = (
            os.environ["GOOGLE_API_KEY"]
            if "GOOGLE_API_KEY" in os.environ
            else None
        )
        if self.custom_api_key:
            os.environ["GOOGLE_API_KEY"] = self.custom_api_key
        response = httpx.post(f"{self.base_url}/run", headers=headers, json=payload)
        if self.custom_api_key:
            os.environ["GOOGLE_API_KEY"] = prev_api_key

        if response.status_code == 200:
            json_response = response.json()
            return json_response
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_events(self) -> Dict:
        """Send a message to the ADK agent and get response"""
        if not self.session_id:
            return "Error: No active session. Please start a session first."

        headers = {"Content-Type": "application/json"}

        params = {
            "app_name": self.app_name,
            "user_id": self.user_id,
            "session_id": self.session_id,
        }

        response = httpx.get(
            f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions/{self.session_id}",
            headers=headers,
            params=params,
        )
        if response.status_code == 200:
            json_response = response.json()
            return json_response
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_trace(self, event_id) -> Optional[Dict]:
        """Send a message to the ADK agent and get response"""
        if event_id in self.trace_cache:
            return self.trace_cache[event_id]
        else:
            if not self.session_id:
                return "Error: No active session. Please start a session first."

            headers = {"Content-Type": "application/json"}

            response = httpx.get(
                f"{self.base_url}/debug/trace/{event_id}",
                headers=headers,
            )
            if response.status_code == 200:
                json_response = response.json()
                self.trace_cache[event_id] = json_response
                return json_response
            else:
                self.trace_cache[event_id] = None
                raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_graph(self, event_id) -> Optional[Dict]:
        if event_id in self.graph_cache:
            return self.graph_cache[event_id]
        else:
            """Send a message to the ADK agent and get response"""
            if not self.session_id:
                return "Error: No active session. Please start a session first."

            headers = {"Content-Type": "application/json"}
            response = httpx.get(
                f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions/{self.session_id}/events/{event_id}/graph",
                headers=headers,
                # params=params,
            )
            if response.status_code == 200:
                json_response = response.json()
                self.graph_cache[event_id] = json_response
                return json_response
            else:
                self.trace_cache[event_id] = None
                raise Exception(f"Error: {response.status_code} - {response.text}")

    def set_custom_api_key(self, custom_api_key):
        self.custom_api_key = custom_api_key

    def end_session(self):
        """End the current chat session"""
        if self.session_id:
            try:
                headers = {}
                httpx.delete(
                    f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions/{self.session_id}",
                    headers=headers,
                )
                self.session_id = None
            except:
                pass


@lru_cache(maxsize=100)
def adk_client(session_id: str):
    client = ADKChatClient(user_session_id=session_id, base_url="http://localhost:8000")
    client.start_session()
    return client
