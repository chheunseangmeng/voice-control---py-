# Music Player

A Python-based music player with a graphical user interface (GUI) and voice command support. Built using Tkinter, Pygame, and SpeechRecognition, this application allows users to play MP3 files, manage playlists, and control playback via buttons or voice commands.

## Features

- **Playlist Management**: Add MP3 files to a playlist, shuffle the playlist, and select songs to play.
- **Playback Controls**: Play, pause, stop, skip to next/previous song, and scrub through songs using a timeline.
- **Voice Commands**: Control the player with voice commands like "play [song name]", "pause", "resume", "next", "previous", "shuffle", and "add".
- **Time Display**: Shows current playback position and total song duration.
- **Smooth Playback**: Optimized for seamless song transitions and accurate timeline updates.

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - `tkinter` (usually included with Python)
  - `pygame` (for audio playback)
  - `pyttsx3` (for text-to-speech)
  - `speechrecognition` (for voice input)
  - `mutagen` (for MP3 metadata)
- A microphone for voice commands
- MP3 files for playback
- Button icons (PNG files) in an `images/` folder

## Installation

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/Mean74student/Project-Voice-Control-Music-by-Python-M-K-L
   cd music-player