import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QWidget, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
import ctypes

VLC_PATH = r"C:\Program Files\VideoLAN\VLC"

# Add VLC to PATH
os.environ["PATH"] += os.pathsep + VLC_PATH

# Load VLC manually
try:
    ctypes.CDLL(os.path.join(VLC_PATH, "libvlc.dll"))
except OSError as e:
    print("Failed to load VLC:", e)
    sys.exit(1)

# Now import vlc
import vlc

# Create VLC instance
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()
print("VLC Loaded Successfully!")

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Music Player")
        self.setGeometry(100, 100, 400, 300)

        # VLC Player Instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Variables
        self.playlist = []
        self.current_song_index = 0
        self.is_playing = False

        # UI Components
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Song Label
        self.song_label = QLabel("No Song Playing")
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.song_label)

        # Progress Slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderReleased.connect(self.set_position)  # Use released instead of moved
        main_layout.addWidget(self.progress_slider)

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_song)
        buttons_layout.addWidget(self.prev_button)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        buttons_layout.addWidget(self.play_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_song)
        buttons_layout.addWidget(self.next_button)

        main_layout.addLayout(buttons_layout)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        main_layout.addWidget(QLabel("Volume:"))
        main_layout.addWidget(self.volume_slider)

        # Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_song)
        main_layout.addWidget(QLabel("Playlist:"))
        main_layout.addWidget(self.playlist_widget)

        # Load Playlist Button
        self.load_button = QPushButton("Load Playlist")
        self.load_button.clicked.connect(self.load_playlist)
        main_layout.addWidget(self.load_button)

        # Set main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Timer for progress updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)  # Update every second

    def load_playlist(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Music Files", "", "Audio Files (*.mp3 *.wav)")
        if files:
            self.playlist = files
            self.playlist_widget.clear()
            self.playlist_widget.addItems([os.path.basename(file) for file in files])
            self.current_song_index = 0
            self.load_song(self.playlist[self.current_song_index])

    def load_song(self, song_path):
        media = self.instance.media_new(song_path)
        self.player.set_media(media)
        self.song_label.setText(os.path.basename(song_path))
        self.progress_slider.setValue(0)
        self.play_button.setText("Play")
        self.is_playing = False

    def toggle_play(self):
        if not self.is_playing:
            self.player.play()
            self.is_playing = True
            self.play_button.setText("Pause")
        else:
            self.player.pause()
            self.is_playing = False
            self.play_button.setText("Play")

    def next_song(self):
        if self.playlist:
            self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
            self.load_song(self.playlist[self.current_song_index])
            self.player.play()

    def prev_song(self):
        if self.playlist:
            self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
            self.load_song(self.playlist[self.current_song_index])
            self.player.play()

    def play_selected_song(self, item):
        self.current_song_index = self.playlist_widget.row(item)
        self.load_song(self.playlist[self.current_song_index])
        self.player.play()

    def set_volume(self, value):
        self.player.audio_set_volume(value)

    def set_position(self):
        if self.is_playing:
            position = self.progress_slider.value() / 100
            self.player.set_position(position)

    def update_progress(self):
        if self.is_playing:
            position = self.player.get_position() * 100
            self.progress_slider.setValue(int(position))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())