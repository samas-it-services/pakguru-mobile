import requests
from firebase_interface import DatabaseInterface

firebase_url = "https://your-firebase-project.firebaseio.com/videos.json"
auth_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_FIREBASE_API_KEY"

class FirebaseDatabase(DatabaseInterface):
    def __init__(self):
        self.session_token = None

    def get_videos(self):
        try:
            response = requests.get(firebase_url)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []

    def add_video(self, video_data):
        try:
            response = requests.post(firebase_url, json=video_data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error adding video: {e}")
            return False

    def authenticate_user(self, email, password):
        data = {"email": email, "password": password, "returnSecureToken": True}
        try:
            response = requests.post(auth_url, json=data)
            if response.status_code == 200:
                self.session_token = response.json().get("idToken")
                return True
            else:
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
