import os
import random
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

class MusicTherapyModule:
    def __init__(self):
        # Directory containing music files - now actually used
        self.music_dir = "therapy_music"
        
        # Validate music directory exists
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)
            logging.warning(f"Created missing music directory: {self.music_dir}")
        
        # Sample music database organized by mood - using actual files from therapy_music folder
        self.music_database = {
            "happy": [
                {"title": "Happy", "artist": "Pharrell Williams", "duration": "1:30", "file": "happy_pharrell.mp3"},
                {"title": "Walking on Sunshine", "artist": "Katrina & The Waves", "duration": "1:30", "file": "walking_sunshine.mp3"}
            ],
            "sad": [
                {"title": "Someone Like You", "artist": "Adele", "duration": "1:30", "file": "someone_like_you.mp3"},
                {"title": "Fix You", "artist": "Coldplay", "duration": "1:30", "file": "fix_you.mp3"}
            ],
            "energetic": [
                {"title": "Eye of the Tiger", "artist": "Survivor", "duration": "1:30", "file": "eye_of_tiger.mp3"},
                {"title": "Can't Hold Us", "artist": "Macklemore & Ryan Lewis", "duration": "1:30", "file": "cant_hold_us.mp3"}
            ],
            "calm": [
                {"title": "Weightless", "artist": "Marconi Union", "duration": "1:30", "file": "weightless.mp3"},
                {"title": "Claire de Lune", "artist": "Claude Debussy", "duration": "1:30", "file": "claire_de_lune.mp3"}
            ],
            "anxious": [
                {"title": "Breathe Me", "artist": "Sia", "duration": "1:30", "file": "breathe_me.mp3"},
                {"title": "Let It Go", "artist": "James Bay", "duration": "1:30", "file": "let_it_go.mp3"}
            ],
            "focused": [
                {"title": "Experience", "artist": "Ludovico Einaudi", "duration": "1:30", "file": "experience.mp3"},
                {"title": "Time", "artist": "Hans Zimmer", "duration": "1:30", "file": "time.mp3"}
            ]
        }
        
        # Create placeholder files if they don't exist (for demo purposes)
        self._create_placeholder_files()
        
        # Validate that files exist and remove entries that don't
        self._validate_music_files()
        
        # Therapy advice dictionary
        self.therapy_advice = {
            "happy": "Music can help maintain and amplify positive emotions. Happy music has been shown to increase dopamine release.",
            "sad": "It's okay to feel sad. Music that matches your mood can validate emotions, while gradually transitioning to more uplifting songs can help process feelings.",
            "energetic": "Rhythmic music with 125-140 BPM optimizes workout performance. Channel your energy through movement while listening.",
            "calm": "Slow tempo music (60-80 BPM) can decrease stress hormones like cortisol. Practice deep breathing while listening.",
            "anxious": "Music with predictable patterns can provide safety cues to an anxious nervous system.",
            "focused": "Instrumental music at 60-70 BPM synchronizes brain waves in the alpha range, ideal for concentration."
        }
        
        # Currently playing song
        self.current_song = None
        # Flag to track if music is currently "playing"
        self.is_playing = False
    
    def _create_placeholder_files(self):
        """Create empty placeholder files for demo purposes if they don't exist"""
        for mood_songs in self.music_database.values():
            for song in mood_songs:
                file_path = os.path.join(self.music_dir, song['file'])
                if not os.path.exists(file_path):
                    # Create an empty file
                    with open(file_path, 'w') as f:
                        f.write('# Placeholder audio file')
                    logging.info(f"Created placeholder file: {file_path}")
    
    def _validate_music_files(self):
        """Validate that music files exist in the directory and remove entries that don't"""
        for mood, songs in list(self.music_database.items()):
            valid_songs = []
            for song in songs:
                file_path = os.path.join(self.music_dir, song['file'])
                if os.path.exists(file_path):
                    valid_songs.append(song)
                else:
                    logging.warning(f"Music file not found: {file_path}")
            
            # Update the database with only valid songs
            self.music_database[mood] = valid_songs
    
    def generate_playlist(self, mood):
        """Generate a playlist based on mood."""
        try:
            if mood not in self.music_database or not self.music_database[mood]:
                # Default to calm if mood doesn't exist or has no valid songs
                mood = "calm"
                # If calm has no songs either, find first mood with songs
                if not self.music_database[mood]:
                    for m, songs in self.music_database.items():
                        if songs:
                            mood = m
                            break
            
            base_songs = self.music_database[mood].copy()
            
            # If still no songs available, return empty playlist
            if not base_songs:
                return {
                    "playlist": [],
                    "advice": "No music files available. Please add music to the therapy_music folder."
                }
            
            # Randomize and limit playlist
            random.shuffle(base_songs)
            playlist_size = min(len(base_songs), random.randint(3, 5))
            
            # Get the selected songs and add therapy advice
            selected_songs = base_songs[:playlist_size]
            advice = self.therapy_advice.get(mood, "Enjoy your personalized music therapy session.")
            
            return {
                "playlist": selected_songs,
                "advice": advice
            }
        except Exception as e:
            logging.error(f"Playlist generation error: {e}")
            return {"playlist": [], "advice": "An error occurred generating your playlist."}
    
    def play_song(self, song):
        """Set the current song (actual playback is handled by the browser)"""
        try:
            if not song or 'file' not in song:
                logging.error("Invalid song data: missing file property")
                return False
                
            # Check if file exists
            file_path = os.path.join(self.music_dir, song['file'])
            if not os.path.exists(file_path):
                logging.error(f"Music file not found: {file_path}")
                return False
            
            # Store current song info
            self.current_song = song
            self.is_playing = True
            
            logging.info(f"Playing: {song['title']} by {song['artist']}")
            return True
        except Exception as e:
            logging.error(f"Error playing song: {e}")
            return False
    
    def stop_music(self):
        """Stop the currently playing music"""
        self.current_song = None
        self.is_playing = False
        logging.info("Music stopped")

# Create Flask app
app = Flask(__name__)
music_therapy = MusicTherapyModule()

@app.route('/')
def index():
    """Render the main music therapy page."""
    return render_template('music_therapy.html')

@app.route('/music/<path:filename>')
def serve_music(filename):
    """Serve music files from the therapy_music directory"""
    return send_from_directory(music_therapy.music_dir, filename)

@app.route('/generate-playlist', methods=['POST'])
def generate_playlist():
    """Generate a playlist based on the selected mood."""
    mood = request.json.get('mood')
    
    if not mood:
        return jsonify({"error": "No mood selected"}), 400
    
    # Generate playlist
    playlist_data = music_therapy.generate_playlist(mood)
    
    return jsonify({
        "playlist": playlist_data["playlist"],
        "advice": playlist_data["advice"]
    })

@app.route('/play-music', methods=['POST'])
def play_music():
    """Play the selected song"""
    song = request.json.get('song')
    
    if not song:
        return jsonify({"error": "No song selected"}), 400
    
    try:
        logging.debug(f"Received song data: {song}")
        
        # "Play" the song
        success = music_therapy.play_song(song)
        
        if success:
            # Return file path for the browser to play
            file_url = f"/music/{song['file']}"
            return jsonify({
                "status": "playing",
                "message": f"Playing {song['title']} by {song['artist']}",
                "file_url": file_url
            })
        else:
            return jsonify({"error": "Failed to play music - file not found"}), 404
    except Exception as e:
        logging.error(f"Music playback error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stop-music', methods=['POST'])
def stop_music():
    """Stop the currently playing music"""
    music_therapy.stop_music()
    return jsonify({"status": "stopped"})

@app.route('/start-therapy', methods=['POST'])
def start_therapy():
    """Start therapy session with selected mood"""
    mood = request.json.get('mood')
    
    if not mood:
        return jsonify({"error": "No mood selected"}), 400
    
    try:
        # Generate playlist
        playlist_data = music_therapy.generate_playlist(mood)
        
        # Play the first song if available
        if playlist_data["playlist"]:
            first_song = playlist_data["playlist"][0]
            music_therapy.play_song(first_song)
            
            # Return file path for the browser to play
            file_url = f"/music/{first_song['file']}"
            
            return jsonify({
                "status": "success",
                "message": f"Therapy session started with mood: {mood}",
                "playlist": playlist_data["playlist"],
                "advice": playlist_data["advice"],
                "now_playing": f"{first_song['title']} by {first_song['artist']}",
                "file_url": file_url
            })
        else:
            return jsonify({
                "status": "warning",
                "message": "Playlist is empty, but therapy session started",
                "advice": playlist_data["advice"]
            })
    except Exception as e:
        logging.error(f"Start therapy error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get-now-playing', methods=['GET'])
def get_now_playing():
    """Get information about the currently playing song"""
    if music_therapy.current_song and music_therapy.is_playing:
        # Return file path for the browser to play
        file_url = f"/music/{music_therapy.current_song['file']}"
        
        return jsonify({
            "status": "playing",
            "song": music_therapy.current_song,
            "message": f"Now playing: {music_therapy.current_song['title']} by {music_therapy.current_song['artist']}",
            "file_url": file_url
        })
    else:
        return jsonify({
            "status": "stopped",
            "message": "No song is currently playing"
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)