from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def get_videos(self):
        pass
    
    @abstractmethod
    def add_video(self, video_data):
        pass

    @abstractmethod
    def authenticate_user(self, email, password):
        pass
