import os
import random
import datetime
import traceback
import sqlite3
import hashlib
import uuid
from flask import Flask, render_template, redirect, url_for, request, jsonify, session, flash, send_from_directory
from flask_cors import CORS  # Add CORS support
from chatbot import MentalHealthChatbot
from mood_tracker import MoodTracker
from music_therapy import MusicTherapyModule
from self_care_card import SelfCareCard
from sleep_tracker import AdvancedSleepTracker
from therapy import TherapistDatabase, Therapist  # Import the therapist module
from functools import wraps

class MentalHealthWellnessApp:
    def __init__(self):
        """Initialize the mental health wellness application."""
        # Create Flask app
        self.app = Flask(__name__, 
                         template_folder='templates', 
                         static_folder='static')
        
        # Add CORS support
        CORS(self.app)
        
        # Configure secret key for better error handling
        self.app.config['SECRET_KEY'] = os.urandom(24)
        
        # Initialize modules
        self.chatbot = MentalHealthChatbot()
        self.mood_tracker = MoodTracker()
        self.music_therapy = MusicTherapyModule()
        self.self_care_card = SelfCareCard()
        self.sleep_tracker = AdvancedSleepTracker()
        self.therapist_db = TherapistDatabase()  # Initialize therapist database
        
        # Initialize database
        self.init_db()
        
        # Set up routes
        self.setup_routes()
    
    def init_db(self):
        """Initialize SQLite database for user authentication."""
        conn = sqlite3.connect('wellness_app.db')
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password, salt=None):
        """
        Hash password using SHA-256 with a salt.
        
        Args:
            password (str): User's password
            salt (str, optional): Salt for password. If not provided, generate a new one.
        
        Returns:
            tuple: (hashed_password, salt)
        """
        if salt is None:
            salt = uuid.uuid4().hex
        
        # Combine password and salt before hashing
        salted_password = password + salt
        
        # Hash using SHA-256
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return hashed_password, salt
    
    def validate_password(self, stored_password, stored_salt, provided_password):
        """
        Validate user's password.
        
        Args:
            stored_password (str): Hashed password from database
            stored_salt (str): Salt used for hashing
            provided_password (str): Password provided by user
        
        Returns:
            bool: True if password is correct, False otherwise
        """
        hashed_input, _ = self.hash_password(provided_password, stored_salt)
        return hashed_input == stored_password
    
    def login_required(self, f):
        """
        Decorator to require login for specific routes.
        
        Args:
            f (function): Route function to wrap
        
        Returns:
            function: Wrapped route function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def setup_routes(self):
        """Set up routes for the application."""
        @self.app.route('/')
        def index():
            """Redirect to login page."""
            return redirect(url_for('login'))
        
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            """User  registration route."""
            if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                
                # Basic validation
                if not username or not email or not password:
                    flash('All fields are required.', 'error')
                    return render_template('register.html')
                
                if password != confirm_password:
                    flash('Passwords do not match.', 'error')
                    return render_template('register.html')
                
                # Hash password
                hashed_password, salt = self.hash_password(password)
                
                try:
                    conn = sqlite3.connect('wellness_app.db')
                    c = conn.cursor()
                    
                    # Check if username or email already exists
                    c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
                    existing_user = c.fetchone()
                    
                    if existing_user:
                        flash('Username or email already exists.', 'error')
                        return render_template('register.html')
                    
                    # Insert new user
                    user_id = uuid.uuid4().hex
                    c.execute('''
                        INSERT INTO users (id, username, email, password, salt) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, username, email, hashed_password, salt))
                    
                    conn.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
                
                except sqlite3.Error as e:
                    flash(f'Database error: {e}', 'error')
                    return render_template('register.html')
                
                finally:
                    conn.close()
            
            return render_template('register.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """User  login route."""
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                try:
                    conn = sqlite3.connect('wellness_app.db')
                    c = conn.cursor()
                    
                    # Find user by username
                    c.execute('SELECT * FROM users WHERE username = ?', (username,))
                    user = c.fetchone()
                    
                    if user and self.validate_password(user[3], user[4], password):
                        # Set session
                        session['user_id'] = user[0]
                        session['username'] = user[1]
                        flash('Login successful!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid username or password.', 'error')
                
                except sqlite3.Error as e:
                    flash(f'Database error: {e}', 'error')
                
                finally:
                    conn.close()
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """User  logout route."""
            session.clear()
            flash('You have been logged out.', 'success')
            return redirect(url_for('login'))
        
        @self.app.route('/dashboard')
        @self.login_required
        def dashboard():
            """Render the main dashboard."""
            return render_template('dashboard.html', username=session.get('username'))
        
        # Chatbot routes
        @self.app.route('/chatbot')
        @self.login_required
        def chatbot_page():
            """Render chatbot interface."""
            return render_template('chatbot.html')
        
        @self.app.route('/send_message', methods=['POST'])
        def send_message():
            """Route for chatbot message handling."""
            data = request.json
            user_input = data.get('message', '').lower().strip()
            response = self.chatbot.generate_bot_response(user_input)
            return jsonify({'response': response})
        
        # Mood Tracker routes
        @self.app.route('/mood_tracker')
        @self.login_required
        def mood_tracker_page():
            """Render mood tracker interface."""
            return render_template('mood_tracker.html')
        
        @self.app.route('/add_entry', methods=['POST'])
        def add_mood_entry():
            """Add a new mood entry with comprehensive error handling."""
            try:
                # Log received data for debugging
                print("Received mood entry data:", request.json)
                
                data = request.json
                
                # Validate required keys
                if not data or 'mood_rating' not in data:
                    return jsonify({
                        'status': 'error', 
                        'message': 'Missing mood rating'
                    }), 400
                
                # Provide default values with more flexibility
                entry = self.mood_tracker.add_entry(
                    mood_rating=int(data['mood_rating']),
                    description=data.get('description', ''),
                    factors=data.get('factors', [])
                )
                
                # Log successful entry
                print("Mood entry saved successfully:", entry)
                
                return jsonify({
                    'status': 'success', 
                    'entry': entry
                }), 201
            
            except KeyError as e:
                print(f"KeyError in mood entry: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': f'Missing key: {e}'
                }), 400
            
            except ValueError as e:
                print(f"ValueError in mood entry: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': f'Invalid value: {e}'
                }), 400
            
            except Exception as e:
                print(f"Unexpected error in mood entry: {e}")
                return jsonify({
                    'status': 'error', 
                    'message': str(e)
                }), 500
        
        @self.app.route('/mood_analysis')
        def mood_analysis():
            """Get mood analysis data."""
            try:
                analysis = self.mood_tracker.get_mood_analysis()
                if analysis:
                    return jsonify(analysis)
                return jsonify({"message": "No entries found"}), 404
            except Exception as e:
                print(f"Error in mood analysis: {e}")
                return jsonify({"message": "Error retrieving mood analysis"}), 500
        
        @self.app.route('/mood_chart')
        def mood_chart():
            """Generate and return mood chart path."""
            try:
                chart_path = self.mood_tracker.generate_mood_chart()
                if chart_path:
                    return jsonify({"chart_path": chart_path})
                return jsonify({"message": "No chart available"}), 404
            except Exception as e:
                print(f"Error generating mood chart: {e}")
                return jsonify({"message": "Error generating mood chart"}), 500
        
        @self.app.route('/recent_entries')
        def recent_entries():
            """Get recent mood entries."""
            try:
                entries = self.mood_tracker.mood_data.get('entries', [])
                recent_entries = entries[-5:]  # Last 5 entries
                return jsonify(recent_entries)
            except Exception as e:
                print(f"Error retrieving recent entries: {e}")
                return jsonify({"message": "Error retrieving entries"}), 500
        
        # Music Therapy routes
        @self.app.route('/music_therapy')
        @self.login_required
        def music_therapy_page():
            """Render music therapy interface."""
            return render_template('music_therapy.html')
        
        @self.app.route('/music/<path:filename>')
        def serve_music(filename):
            """Serve music files from the therapy_music directory"""
            return send_from_directory(self.music_therapy.music_dir, filename)
        
        @self.app.route('/generate-playlist', methods=['POST'])
        def generate_playlist():
            """Generate a playlist based on the selected mood."""
            mood = request.json.get('mood')
            
            if not mood:
                return jsonify({"error": "No mood selected"}), 400
            
            # Generate playlist
            playlist_data = self.music_therapy.generate_playlist(mood)
            
            return jsonify({
                "playlist": playlist_data["playlist"],
                "advice": playlist_data["advice"]
            })
        
        @self.app.route('/play-music', methods=['POST'])
        def play_music():
            """Play the selected song"""
            song = request.json.get('song')
            
            if not song:
                return jsonify({"error": "No song selected"}), 400
            
            try:
                # "Play" the song
                success = self.music_therapy.play_song(song)
                
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
                print(f"Music playback error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/stop-music', methods=['POST'])
        def stop_music():
            """Stop the currently playing music"""
            self.music_therapy.stop_music()
            return jsonify({"status": "stopped"})
        
        @self.app.route('/start-therapy', methods=['POST'])
        def start_therapy():
            """Start therapy session with selected mood"""
            mood = request.json.get('mood')
            
            if not mood:
                return jsonify({"error": "No mood selected"}), 400
            
            try:
                # Generate playlist
                playlist_data = self.music_therapy.generate_playlist(mood)
                
                # Play the first song if available
                if playlist_data["playlist"]:
                    first_song = playlist_data["playlist"][0]
                    self.music_therapy.play_song(first_song)
                    
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
                print(f"Start therapy error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/get-now-playing', methods=['GET'])
        def get_now_playing():
            """Get information about the currently playing song"""
            if self.music_therapy.current_song and self.music_therapy.is_playing:
                # Return file path for the browser to play
                file_url = f"/music/{self.music_therapy.current_song['file']}"
                
                return jsonify({
                    "status": "playing",
                    "song": self.music_therapy.current_song,
                    "message": f"Now playing: {self.music_therapy.current_song['title']} by {self.music_therapy.current_song['artist']}",
                    "file_url": file_url
                })
            else:
                return jsonify({
                    "status": "stopped",
                    "message": "No song is currently playing"
                })
        
        # Self-Care Card routes
        @self.app.route('/self_care')
        @self.login_required
        def self_care_page():
            """Render self-care card interface."""
            return render_template('self_care_card.html')
        
        @self.app.route('/draw-card', methods=['POST'])
        def draw_card():
            """Draw a self-care card."""
            mood = request.json.get('mood', None)
            card = self.self_care_card.draw_card(mood)
            return jsonify(card)
        
        # Sleep Tracker routes
        @self.app.route('/sleep_tracker')
        @self.login_required
        def sleep_tracker_page():
            """Render sleep tracker interface."""
            return render_template('sleep_tracker.html')
        
        @self.app.route('/log_sleep', methods=['POST'])
        def log_sleep():
            """Log a new sleep session."""
            try:
                data = request.json
                
                # Convert ISO format datetime strings to datetime objects
                sleep_time = datetime.datetime.fromisoformat(data['sleep_start'])
                wake_time = datetime.datetime.fromisoformat(data['wake_up'])
                
                # Prepare sleep environment dictionary
                sleep_environment = {}
                if data.get('room_temp'):
                    sleep_environment['room_temperature'] = data['room_temp']
                if data.get('noise_level'):
                    sleep_environment['noise_level'] = data['noise_level']
                
                # Log the sleep session
                self.sleep_tracker.log_sleep(
                    sleep_time=sleep_time,
                    wake_time=wake_time,
                    quality_rating=int(data['sleep_quality']),
                    mood_rating=int(data['morning_mood']),
                    interruptions=int(data['interruptions']),
                    dream_recall=data['dream_recall'],
                    sleep_environment=sleep_environment,
                    tags=data.get('tags', [])
                )
                
                return jsonify({"status": "success", "message": "Sleep session logged successfully"})
            
            except Exception as e:
                print(f"Error logging sleep: {e}")
                print(traceback.format_exc())
                return jsonify({"status": "error", "message": str(e)}), 400
        
        @self.app.route('/get_sleep_analysis', methods=['GET'])
        def get_sleep_analysis():
            """Retrieve comprehensive sleep analysis."""
            try:
                analysis = self.sleep_tracker.analyze_advanced_metrics()
                print(f"Sleep Analysis: {analysis}")
                return jsonify(analysis)
            except Exception as e:
                print(f"Error in get_sleep_analysis: {e}")
                print(traceback.format_exc())
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/get_sleep_advice', methods=['GET'])
        def get_sleep_advice():
            """Retrieve personalized sleep advice."""
            try:
                advice = self.sleep_tracker.get_advanced_sleep_advice()
                print(f"Sleep Advice: {advice}")
                return jsonify({"advice": advice})
            except Exception as e:
                print(f"Error in get_sleep_advice: {e}")
                print(traceback.format_exc())
                return jsonify({"error": str(e)}), 500
        
        # Therapist finder routes
        @self.app.route('/therapy')
        @self.login_required
        def therapy_page():
            """Render therapist finder interface."""
            return render_template('therapy.html')
        
        @self.app.route('/api/therapists', methods=['GET'])
        def get_all_therapists():
            """API endpoint to get all therapists"""
            therapists = self.therapist_db.get_all_therapists()
            return jsonify([therapist.to_dict() for therapist in therapists])
        
        @self.app.route('/api/therapists/<int:therapist_id>', methods=['GET'])
        def get_therapist(therapist_id):
            """API endpoint to get a specific therapist by ID"""
            therapist = self.therapist_db.get_therapist_by_id(therapist_id)
            if therapist:
                return jsonify(therapist.to_dict())
            return jsonify({'error': 'Therapist not found'}), 404
        
        @self.app.route('/api/search', methods=['GET'])
        def search_therapists():
            """API endpoint to search therapists by criteria"""
            specialization = request.args.get('specialization', '')
            location = request.args.get('location', '')
            insurance = request.args.get('insurance', '')
            
            results = self.therapist_db.therapists
            
            if specialization:
                results = [t for t in results if any(specialization.lower() in s.lower() for s in t.specializations)]
            
            if location:
                results = [t for t in results if location.lower() in t.location.lower()]
            
            if insurance:
                results = [t for t in results if any(insurance.lower() in i.lower() for i in t.insurance_accepted)]
            
            return jsonify([therapist.to_dict() for therapist in results])
        
        @self.app.route('/api/recommend', methods=['GET'])
        def get_recommendation():
            """API endpoint to get personalized recommendations"""
            issue = request.args.get('issue', '')
            location = request.args.get('location', '')
            insurance = request.args.get('insurance', '')
            
            results = self.therapist_db.get_therapist_recommendation(issue, location, insurance)
            return jsonify([therapist.to_dict() for therapist in results])
    
    def create_app_structure(self):
        """Create necessary directories for the application."""
        # Create directories
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('therapy_music', exist_ok=True)  # For music therapy module
        os.makedirs('static/mood_charts', exist_ok=True)  # For mood charts
    
    def run(self, debug=True, port=5000):
        """Run the Flask application."""
        self.create_app_structure()
        self.app.run(debug=debug, port=port)

# Main entry point
if __name__ == '__main__':
    wellness_app = MentalHealthWellnessApp()
    wellness_app.run()