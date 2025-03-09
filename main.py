import tkinter as tk
from tkinter import filedialog, Listbox, PhotoImage, messagebox
import speech_recognition as sr
import pyttsx3
import pygame
import os
import random
import threading
from mutagen.mp3 import MP3   

# --- Initialization ---
recognizer = sr.Recognizer()
engine = pyttsx3.init()   
pygame.mixer.init()

# --- Global Variables ---
music_files = {}
current_song = None
is_playing = False
is_paused = False
current_time = 0
song_duration = 0
playlist_index = 0
timer_id = None

# --- Helper Functions ---
def speak(text):
    """Text-to-speech."""
    engine.say(text)
    engine.runAndWait()

def update_label(label, text):
    """Update label text."""
    label.config(text=text)

def time_format(seconds):
    """Convert seconds to MM:SS format."""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02}:{seconds:02}"

# --- Music Control Functions ---
def play_selected_song():
    """Play the selected song from the playlist."""
    global current_song, is_playing, is_paused, current_time, song_duration, playlist_index

    selected = playlist.curselection()
    if not selected:
        update_label(song_label, "Please select a song to play.")
        return

    playlist_index = selected[0]
    song_name = playlist.get(playlist_index)
    song_path = music_files.get(song_name)

    if not song_path:
        update_label(song_label, "Selected song not found.")
        return

    try:
        if is_playing:  # If a song is already playing, stop it first.
            stop_music()

        # Load and play the selected song
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=current_time)  # Start from the current time (if resuming)

        # Update global states
        current_song = song_name
        is_playing = True
        is_paused = False
        current_time = 0

        # Retrieve song duration
        try:
            song = MP3(song_path)
            song_duration = int(song.info.length)
        except Exception:
            song_duration = 0

        # Update UI
        update_label(song_label, f"Playing: {current_song}")
        highlight_current_song()
        update_play_pause_button()
        update_time_label()

    except Exception as e:
        update_label(song_label, "Error playing the selected song.")
        print(f"Error: {e}")

def stop_music():
    """Stop music playback."""
    global is_playing, current_time, timer_id

    pygame.mixer.music.stop()
    is_playing = False
    is_paused = False
    current_time = 0

    if timer_id is not None:
        app.after_cancel(timer_id)
        timer_id = None

    update_label(song_label, "Music stopped.")
    update_time_label()
    clear_highlight()
    update_play_pause_button()

def toggle_play_pause():
    """Pause or resume the music."""
    global is_playing, is_paused, current_time

    if is_playing:
        if is_paused:
            pygame.mixer.music.unpause()  # Unpause the music
            is_paused = False
            update_label(song_label, f"Resumed: {current_song}")
        else:
            pygame.mixer.music.pause()  # Pause the music
            is_paused = True
            update_label(song_label, "Music paused.")
        update_play_pause_button()
    else:
        play_selected_song()

def update_play_pause_button():
    """Change play/pause button icon based on state."""
    if is_playing and not is_paused:
        play_pause_button.config(image=pause_img)
    else:
        play_pause_button.config(image=play_img)

def update_time_label():
    """Update the time label during playback."""
    global current_time, song_duration, is_playing, is_paused, timer_id

    if timer_id is not None:
        app.after_cancel(timer_id)

    if is_playing and not is_paused:
        if current_time < song_duration:
            time_label.config(
                text=f"{time_format(current_time)}                                                  {time_format(song_duration)}"
            )
            timeline.set((current_time / song_duration) * 100)
            current_time += 1
            timer_id = app.after(1000, update_time_label)
        else:
            stop_music()
    else:
        time_label.config(
            text=f"{time_format(current_time)}                                                  {time_format(song_duration)}"
        )
        timeline.set((current_time / song_duration) * 100)

def on_timeline_change(val):
    """Handle changes in the timeline (scrubbing)."""
    global current_time
    current_time = int((int(val) / 100) * song_duration)
    if is_playing:
        pygame.mixer.music.play(start=current_time)


def add_music():
    """Add music files to the playlist."""
    files = filedialog.askopenfilenames(
        title="Select Music Files",
        filetypes=[("MP3 Files", "*.mp3")],
    )
    if files:
        added = False
        for file in files:
            if os.path.isfile(file):
                file_name = os.path.basename(file)
                if file_name not in music_files:
                    music_files[file_name] = file
                    playlist.insert(tk.END, file_name)
                    added = True
        if added:
            update_label(song_label, "Music added successfully.")
            speak("Music added successfully.")
        else:
            update_label(song_label, "Selected music already in playlist.")
            speak("Selected music already in playlist.")
    else:
        update_label(song_label, "No files selected.")
        speak("No files selected.")

def highlight_current_song():
    """Highlight the current song in the playlist."""
    for i in range(playlist.size()):
        if playlist.get(i) == current_song:
            playlist.selection_clear(0, tk.END)
            playlist.selection_set(i)
            playlist.activate(i)
            playlist.see(i)
            return
def clear_highlight():
    """Clear playlist selection."""
    playlist.selection_clear(0, tk.END)

def play_next_song():
    """Play the next song in the playlist."""
    global playlist_index
    if playlist.size() == 0:
        update_label(song_label, "Playlist is empty.")
        return

    playlist_index = (playlist_index + 1) % playlist.size()
    playlist.selection_clear(0, tk.END)
    playlist.selection_set(playlist_index)
    play_selected_song()

def play_previous_song():
    """Play the previous song in the playlist."""
    global playlist_index
    if playlist.size() == 0:
        update_label(song_label, "Playlist is empty.")
        speak("Playlist is empty.")
        return

    playlist_index = (playlist_index - 1) % playlist.size()
    previous_song = playlist.get(playlist_index)
    play_song_by_name(previous_song)

def play_song_by_name(song_name):
    """Play a song by its name."""
    global playlist_index, current_song, is_playing, is_paused, current_time, song_duration

    matching_songs = [song for song in music_files.keys() if song_name.lower() in song.lower()]
    if matching_songs:
        song_name = matching_songs[0]
        playlist_index = list(music_files.keys()).index(song_name)
        playlist.selection_clear(0, tk.END)
        playlist.selection_set(playlist_index)
        playlist.activate(playlist_index)
        play_selected_song()
    else:
        update_label(song_label, f"Song '{song_name}' not found.")
        speak(f"Sorry, I couldn't find a song named {song_name}.")

def shuffle_music():
    """Shuffle the playlist."""
    songs = list(music_files.keys())
    if songs:
        random.shuffle(songs)
        playlist.delete(0, tk.END)
        for song in songs:
            playlist.insert(tk.END, song)
        update_label(song_label, "Playlist shuffled.")
        speak("Playlist shuffled.")
    else:
        update_label(song_label, "No songs to shuffle.")
        speak("No songs to shuffle.")
def auto_next_song():
    """Automatically play the next song when the current one ends."""
    global timer_id, current_time, song_duration
    if current_time >= song_duration:
        play_next_song()
    else:
        timer_id = app.after(1000, auto_next_song)

# --- Voice Commands ---
def process_voice_command():
    """Process voice commands and map them to actions."""
    command = recognize_speech()
    if not command:
        return  # Exit if no command is detected

    if command.startswith("play"):
        # Extract the song name from the command
        song_name = command.replace("play", "", 1).strip()
        if song_name:
            # Search for the song in the playlist
            matching_songs = [
                song for song in music_files.keys() if song_name.lower() in song.lower()
            ]
            if matching_songs:
                play_song_by_name(matching_songs[0])  # Play the first match
            else:
                speak(f"Sorry, I couldn't find a song named {song_name}.")
                update_label(song_label, f"Song '{song_name}' not found.")
        else:
            speak("Please say the song name after 'play'.")
            update_label(song_label, "No song name provided.")
    elif "pause" in command:
        play_pause_button.invoke()  # Simulate button click
    elif "resume" in command:
        play_pause_button.invoke()  # Same as pause for toggling
    elif "stop" in command:
        stop_button.invoke()
    elif "next" in command:
        next_button.invoke()
    elif "previous" in command or "back" in command:
        prev_button.invoke()
    elif "shuffle" in command:
        shuffle_button.invoke()
    elif "add" in command or "load" in command:
        add_button.invoke()
    else:
        speak("Sorry, I didn't understand that command.")
        update_label(song_label, "Command not recognized.")


def recognize_speech():
    """Recognize speech input from the microphone."""
    with sr.Microphone() as source:
        speak("Listening for your command.")
        try:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized Command: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I could not understand you.")
        except sr.RequestError:
            speak("There was an error with the speech recognition service.")
        except sr.WaitTimeoutError:
            speak("Listening timed out while waiting for input.")
    return ""

def start_voice_command():
    """Start voice command processing in a separate thread."""
    threading.Thread(target=process_voice_command, daemon=True).start()

# --- UI Layout ---
app = tk.Tk()
app.title("Music Player")
app.geometry("400x700")
app.resizable(False, False)
app.configure(bg="#2E2E2E")

# --- Song Information ---
song_label = tk.Label(app, text="No song playing.", font=("Helvetica", 16), bg="#2E2E2E", fg="#FFFFFF", wraplength=450)
song_label.pack(pady=10)



# --- Playlist ---
playlist_frame = tk.Frame(app, bg="#2E2E2E")
playlist_frame.pack(pady=10, fill=tk.BOTH, expand=True)

playlist_scrollbar = tk.Scrollbar(playlist_frame, orient=tk.VERTICAL)
playlist = Listbox(
    playlist_frame,
    yscrollcommand=playlist_scrollbar.set,
    bg="#3E3E3E",
    fg="#FFFFFF",
    font=("Helvetica", 12),
    selectmode=tk.SINGLE,
    selectbackground="#6C63FF",
    activestyle="none",
)
playlist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0))
playlist_scrollbar.config(command=playlist.yview)
playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

timeline = tk.Scale(
    app, from_=0, to=100, orient="horizontal", showvalue=0, 
    sliderlength=10,
    length=350, 
    width=5,       
    bg="#333333",   
    fg="#FFFFFF",    
    activebackground="#6C63FF",
    troughcolor="#5A5A5A",
    highlightthickness=0,  
)
timeline.pack(pady=5)
timeline.config(command=on_timeline_change)

time_label = tk.Label(app, text="00:00                                                  00:00", font=("Helvetica", 14), bg="#2E2E2E", fg="#FFFFFF")
time_label.pack(pady=5)
# --- Buttons ---
button_frame = tk.Frame(app, bg="#2E2E2E")
button_frame.pack(pady=20)

try:
    play_img = PhotoImage(file="images/play.png")
    pause_img = PhotoImage(file="images/pause.png")
    stop_img = PhotoImage(file="images/stop.png")
    next_img = PhotoImage(file="images/next.png")
    prev_img = PhotoImage(file="images/back.png")
    add_img = PhotoImage(file="images/add_music.png")
    shuffle_img = PhotoImage(file="images/shuffle.png")
    voice_img = PhotoImage(file="images/voice.png")
except tk.TclError as e:
    messagebox.showerror("Image Load Error", f"Error loading button images: {e}")
    app.destroy()

prev_button = tk.Button(button_frame, image=prev_img, bg="#2E2E2E", borderwidth=0, command=play_previous_song)
prev_button.grid(row=0, column=1, padx=10)

play_pause_button = tk.Button(button_frame, image=play_img, bg="#2E2E2E", borderwidth=0, command=toggle_play_pause)
play_pause_button.grid(row=0, column=2, padx=10)

stop_button = tk.Button(button_frame, image=stop_img, bg="#2E2E2E", borderwidth=0, command=stop_music)
stop_button.grid(row=0, column=3, padx=10)

next_button = tk.Button(button_frame, image=next_img, bg="#2E2E2E", borderwidth=0, command=play_next_song)
next_button.grid(row=0, column=4, padx=10)

add_button = tk.Button(button_frame, image=add_img, bg="#2E2E2E", borderwidth=0, command=add_music)
add_button.grid(row=0, column=5, padx=10, pady=10)

shuffle_button = tk.Button(button_frame, image=shuffle_img, bg="#2E2E2E", borderwidth=0, command=shuffle_music)
shuffle_button.grid(row=0, column=0, padx=10, pady=10)

voice_button = tk.Button(button_frame, image=voice_img, bg="pink", borderwidth=0 , command=start_voice_command)
voice_button.grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")

app.mainloop()

