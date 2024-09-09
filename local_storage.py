import json
import os
from firebase_interface import DatabaseInterface

class LocalStorage(DatabaseInterface):
    def __init__(self, cache_file='assets/cache.json'):
        self.cache_file = cache_file
        self.data = {}
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"videos": []}
    
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.data, f)
    
    def get_videos(self):
        return self.data.get("videos", [])

    def add_video(self, video_data):
        self.data["videos"].append(video_data)
        self.save_cache()
    
    def authenticate_user(self, email, password):
        # Simulate authentication
        return True  # Always authenticate successfully
