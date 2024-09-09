from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.video import Video
from firebase_database import FirebaseDatabase
from local_storage import LocalStorage

class VideoApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create a search bar
        search_bar = TextInput(hint_text="Search Videos", size_hint_y=None, height=40)
        search_bar.bind(text=self.on_search)
        self.add_widget(search_bar)

        # Add categories
        category_bar = BoxLayout(size_hint_y=None, height=40)
        category_bar.add_widget(Button(text="Category 1"))
        category_bar.add_widget(Button(text="Category 2"))
        self.add_widget(category_bar)
        
        # Scrollable video list
        self.scroll_view = ScrollView()
        self.video_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.video_list_layout.bind(minimum_height=self.video_list_layout.setter('height'))
        self.scroll_view.add_widget(self.video_list_layout)
        self.add_widget(self.scroll_view)

        self.load_videos()

    def load_videos(self):
        """Loads videos from the backend."""
        # For demo, using LocalStorage. Switch to FirebaseDatabase if needed.
        self.db = LocalStorage()
        videos = self.db.get_videos()

        for video in videos:
            video_widget = self.create_video_item(video)
            self.video_list_layout.add_widget(video_widget)

    def create_video_item(self, video):
        """Create a video item."""
        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, padding=5)

        # Thumbnail
        thumbnail = Image(source=video['thumbnail_url'], size_hint_x=None, width=100)
        
        # Video Info
        video_info_layout = BoxLayout(orientation='vertical', padding=5)
        video_info_layout.add_widget(Label(text=video['title'], font_size=16, bold=True))
        video_info_layout.add_widget(Label(text=video['description'], font_size=12, color=(0.6, 0.6, 0.6, 1)))
        
        # Play button
        play_button = Button(text='Play', size_hint_x=None, width=80)
        play_button.bind(on_press=lambda x: self.play_video(video['video_url']))

        # Add to layout
        layout.add_widget(thumbnail)
        layout.add_widget(video_info_layout)
        layout.add_widget(play_button)
        
        return layout

    def play_video(self, video_url):
        """Play the video using Kivy's Video widget."""
        video_player = Video(source=video_url)
        self.clear_widgets()  # Clear UI
        self.add_widget(video_player)

    def on_search(self, instance, value):
        """Filter videos based on search."""
        self.video_list_layout.clear_widgets()
        videos = self.db.get_videos()
        for video in videos:
            if value.lower() in video['title'].lower():
                self.video_list_layout.add_widget(self.create_video_item(video))

class YouTubeCloneApp(App):
    def build(self):
        return VideoApp()

if __name__ == '__main__':
    YouTubeCloneApp().run()
