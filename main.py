from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.behaviors import ButtonBehavior
from firebase_database import FirebaseDatabase
from local_storage import LocalStorage
import webbrowser


class HoverBehavior(object):
    """Hover behavior to change cursor on hover."""
    def on_enter(self, *args):
        Window.set_system_cursor("wait")  # Change to hourglass on hover

    def on_leave(self, *args):
        Window.set_system_cursor("arrow")  # Restore arrow on leave


class HoverableImage(ButtonBehavior, Image, HoverBehavior):
    """An image that changes cursor on hover."""
    pass


class HoverableButton(Button, HoverBehavior):
    """A button that changes cursor on hover."""
    pass


class VideoApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.current_batch = 0
        self.batch_size = 5
        self.video_data = []
        self.filtered_tag = None  # Track the currently filtered tag

        # Create a search bar
        self.search_bar = TextInput(hint_text="Search Videos", size_hint_y=None, height=40)
        self.search_bar.bind(text=self.on_search)
        self.add_widget(self.search_bar)

        # Add categories
        category_bar = BoxLayout(size_hint_y=None, height=40)
        categories = ["Talk Shows", "Drama", "Comedy", "Music"]
        for category in categories:
            category_bar.add_widget(Button(text=category))
        self.add_widget(category_bar)
        
        # Scrollable video list
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 100))
        self.video_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20, padding=[10, 10, 10, 10])
        self.video_list_layout.bind(minimum_height=self.video_list_layout.setter('height'))
        self.scroll_view.add_widget(self.video_list_layout)
        self.add_widget(self.scroll_view)

        # Load initial videos
        self.load_videos()
        Clock.schedule_once(self.update_scroll)

        # Infinite scrolling - bind to the scroll end event
        self.scroll_view.bind(on_scroll_stop=self.load_next_batch)

    def load_videos(self):
        """Loads videos from the backend."""
        self.db = LocalStorage()
        self.video_data = self.db.get_videos()
        self.load_next_batch(None, self.batch_size)

    def load_next_batch(self, *args):
        """Loads the next batch of videos into the UI."""
        start_index = self.current_batch * self.batch_size
        end_index = min(start_index + self.batch_size, len(self.video_data))

        # Clear existing widgets if filtering by tag
        if self.filtered_tag:
            self.video_list_layout.clear_widgets()

        for i in range(start_index, end_index):
            video = self.video_data[i]
            if self.filtered_tag and self.filtered_tag not in video.get('tags', []):
                continue
            video_widget = self.create_video_item(video)
            self.video_list_layout.add_widget(video_widget)

        self.current_batch += 1

    def create_video_item(self, video):
        """Create a video item with stacked layout for thumbnail, title, and description."""
        layout = BoxLayout(orientation='vertical', padding=[0, 20, 0, 20], size_hint_y=None)
        
        # Title with clickable link
        title_button = HoverableButton(
            text=video['title'],
            size_hint_y=None,
            height=40,
            font_size=18,
            halign="center",
            valign="middle",
            text_size=(Window.width - 40, None)
        )
        title_button.bind(on_press=lambda x: self.open_video_link(video['video_url']))
        
        # Responsive Thumbnail with hoverable effect - size_hint_x is set to 1 for full width with a margin.
        thumbnail = HoverableImage(source=video['thumbnail_url'], size_hint=(1, None), height=Window.width * 0.55)
        thumbnail.bind(on_touch_down=lambda x, y: self.open_video_link(video['video_url']))

        # More Readable Description
        description = Label(
            text=video['description'],
            font_size=14,
            color=(0.2, 0.2, 0.2, 1),
            text_size=(Window.width - 40, None),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=100
        )

        # Tags with filtering capability
        tags_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        tags = video.get('tags', ["Music", "Meditation"])  # Example tags, modify according to video
        for tag in tags:
            tag_button = Button(text=tag, size_hint=(None, None), height=30, width=100)
            tag_button.bind(on_release=lambda x, t=tag: self.filter_videos_by_tag(t))
            tags_layout.add_widget(tag_button)

        # Add to layout with responsive padding
        layout.add_widget(thumbnail)
        layout.add_widget(title_button)
        layout.add_widget(description)
        layout.add_widget(tags_layout)

        # Adjust layout height based on the content
        layout.size_hint_y = None
        layout.height = thumbnail.height + title_button.height + description.height + tags_layout.height + 40
        
        return layout

    def filter_videos_by_tag(self, tag):
        """Filter the video list by the selected tag."""
        self.filtered_tag = tag
        self.search_bar.text = tag  # Update search bar with the tag name
        self.current_batch = 0
        self.video_list_layout.clear_widgets()
        self.load_next_batch(None)

    def update_scroll(self, *args):
        """Update the size of the scroll view to be correct."""
        self.scroll_view.size = (Window.width, Window.height - 100)

    def on_search(self, instance, value):
        """Filter videos based on search."""
        self.filtered_tag = value  # Set filtered_tag to the search value
        self.video_list_layout.clear_widgets()
        search_results = [video for video in self.video_data if value.lower() in video['title'].lower() or value.lower() in [tag.lower() for tag in video.get('tags', [])]]
        for video in search_results:
            video_widget = self.create_video_item(video)
            self.video_list_layout.add_widget(video_widget)

    def open_video_link(self, video_url):
        """Open the video link in a browser."""
        if platform == 'android':
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(video_url))
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)
        else:
            webbrowser.open(video_url)


class YouTubeCloneApp(App):
    def build(self):
        return VideoApp()

if __name__ == '__main__':
    YouTubeCloneApp().run()