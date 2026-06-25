import os
import json
import datetime
import statistics
import random
import traceback
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

class AdvancedSleepTracker:
    def __init__(self, storage_file='sleep_sessions.json'):
        """
        Initialize the sleep tracker with persistent storage
        
        Args:
            storage_file: JSON file to store sleep sessions
        """
        self.storage_file = os.path.join(os.path.dirname(__file__), storage_file)
        self.sleep_sessions = self.load_sleep_sessions()

    def load_sleep_sessions(self) -> List[Dict]:
        """
        Load sleep sessions from JSON file
        
        Returns:
            List of sleep session dictionaries
        """
        print(f"Attempting to load sleep sessions from {self.storage_file}")
        if not os.path.exists(self.storage_file):
            print("No existing sleep sessions file found.")
            return []
        
        try:
            with open(self.storage_file, 'r') as f:
                sessions = json.load(f)
                # Convert string timestamps back to datetime objects
                for session in sessions:
                    session['sleep_time'] = datetime.datetime.fromisoformat(session['sleep_time'])
                    session['wake_time'] = datetime.datetime.fromisoformat(session['wake_time'])
                    # Convert duration from seconds to timedelta
                    session['duration'] = datetime.timedelta(seconds=session['duration'])
                print(f"Loaded {len(sessions)} sleep sessions.")
                return sessions
        except Exception as e:
            print(f"Error loading sleep sessions: {str(e)}")
            traceback.print_exc()
            return []

    def save_sleep_sessions(self):
        """Save sleep sessions to JSON file"""
        # Convert datetime objects to ISO format strings for JSON serialization
        serializable_sessions = []
        for session in self.sleep_sessions:
            session_copy = session.copy()
            session_copy['sleep_time'] = session['sleep_time'].isoformat()
            session_copy['wake_time'] = session['wake_time'].isoformat()
            # Convert timedelta to seconds for serialization
            session_copy['duration'] = session['duration'].total_seconds()
            serializable_sessions.append(session_copy)
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.storage_file)), exist_ok=True)
            
            with open(self.storage_file, 'w') as f:
                json.dump(serializable_sessions, f, indent=2)
            print(f"Saved {len(serializable_sessions)} sleep sessions.")
        except Exception as e:
            print(f"Error saving sleep sessions: {str(e)}")
            traceback.print_exc()

    def log_sleep(
        self, 
        sleep_time: datetime.datetime, 
        wake_time: datetime.datetime, 
        quality_rating: int, 
        mood_rating: int, 
        interruptions: int, 
        dream_recall: bool,
        sleep_environment: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Log a new sleep session with comprehensive details
        """
        # Calculate sleep duration
        sleep_duration = wake_time - sleep_time
        
        # Prepare sleep session record
        sleep_session = {
            'sleep_time': sleep_time,
            'wake_time': wake_time,
            'duration': sleep_duration,
            'quality_rating': quality_rating,
            'mood_rating': mood_rating,
            'interruptions': interruptions,
            'dream_recall': dream_recall,
            'sleep_environment': sleep_environment or {},
            'tags': tags or []
        }
        
        # Add the session to the log
        self.sleep_sessions.append(sleep_session)
        
        # Save to persistent storage
        self.save_sleep_sessions()
        
        return sleep_session

    def analyze_advanced_metrics(self) -> Dict[str, any]:
        """
        Perform comprehensive analysis of sleep metrics
        """
        if not self.sleep_sessions:
            print("No sleep sessions for analysis.")
            return {
                'total_sessions': 0,
                'avg_sleep_duration': "0.00 hours",
                'avg_sleep_quality': "0.00/10",
                'avg_morning_mood': "0.00/10",
                'total_interruptions': 0,
                'avg_interruptions_per_night': "0.00"
            }

        try:
            # Calculate various metrics
            durations = [session['duration'].total_seconds() / 3600 for session in self.sleep_sessions]
            quality_ratings = [session['quality_rating'] for session in self.sleep_sessions]
            mood_ratings = [session['mood_rating'] for session in self.sleep_sessions]
            interruption_counts = [session['interruptions'] for session in self.sleep_sessions]

            analysis = {
                'total_sessions': len(self.sleep_sessions),
                'avg_sleep_duration': f"{statistics.mean(durations):.2f} hours",
                'avg_sleep_quality': f"{statistics.mean(quality_ratings):.2f}/10",
                'avg_morning_mood': f"{statistics.mean(mood_ratings):.2f}/10",
                'total_interruptions': sum(interruption_counts),
                'avg_interruptions_per_night': f"{statistics.mean(interruption_counts):.2f}"
            }

            print("Sleep analysis generated successfully.")
            return analysis
        except Exception as e:
            print(f"Error in sleep analysis: {str(e)}")
            traceback.print_exc()
            return {
                'total_sessions': len(self.sleep_sessions),
                'avg_sleep_duration': "Error calculating",
                'avg_sleep_quality': "Error calculating",
                'avg_morning_mood': "Error calculating",
                'total_interruptions': "Error calculating",
                'avg_interruptions_per_night': "Error calculating"
            }

    def get_advanced_sleep_advice(self) -> str:
        """
        Generate personalized sleep advice based on tracking data
        """
        if not self.sleep_sessions:
            print("Not enough data for sleep advice.")
            return "Not enough data to provide personalized advice. Keep tracking your sleep!"

        try:
            analysis = self.analyze_advanced_metrics()
            
            # Basic advice templates with randomization
            advice_segments = [
                "Based on your sleep tracking, here are some personalized recommendations:\n\n",
                "Your average sleep duration is {avg_sleep_duration}. ",
                "Your sleep quality averages {avg_sleep_quality}. ",
                "You experience about {avg_interruptions_per_night} interruptions per night. "
            ]

            recommendations = [
                "Consider establishing a consistent sleep schedule.",
                "Create a relaxing bedtime routine to improve sleep quality.",
                "Minimize screen time at least an hour before bed.",
                "Ensure your bedroom is dark, quiet, and cool.",
                "Practice relaxation techniques like deep breathing or meditation.",
                "Avoid caffeine and heavy meals close to bedtime.",
                "Try to maintain a regular exercise routine, but not too close to bedtime."
            ]

            # Compile advice
            advice = "".join(advice_segments).format(**analysis)
            advice += "\n\nRecommendations:\n"
            advice += "\n".join(random.sample(recommendations, min(3, len(recommendations))))

            print("Sleep advice generated successfully.")
            return advice
        except Exception as e:
            print(f"Error generating sleep advice: {str(e)}")
            traceback.print_exc()
            return "Unable to generate personalized sleep advice due to an error."

    def get_all_sessions(self):
        """
        Return all sleep sessions for display
        """
        serializable_sessions = []
        for session in self.sleep_sessions:
            session_copy = session.copy()
            session_copy['sleep_time'] = session['sleep_time'].isoformat()
            session_copy['wake_time'] = session['wake_time'].isoformat()
            session_copy['duration_hours'] = session['duration'].total_seconds() / 3600
            session_copy['duration_formatted'] = f"{session_copy['duration_hours']:.2f} hours"
            serializable_sessions.append(session_copy)
        
        return serializable_sessions

# Flask App Setup
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Initialize the sleep tracker
tracker = AdvancedSleepTracker()

@app.route('/')
def index():
    """Render the main HTML page"""
    return render_template('sleep_tracker.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/log_sleep', methods=['POST'])
def log_sleep():
    """Log a new sleep session"""
    try:
        data = request.json
        print(f"Received sleep log data: {data}")
        
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
        tracker.log_sleep(
            sleep_time=sleep_time,
            wake_time=wake_time,
            quality_rating=int(data['sleep_quality']),
            mood_rating=int(data['morning_mood']),
            interruptions=int(data['interruptions']),
            dream_recall=data.get('dream_recall', False),
            sleep_environment=sleep_environment,
            tags=data.get('tags', [])
        )
        
        return jsonify({"status": "success", "message": "Sleep session logged successfully"})
    
    except Exception as e:
        print(f"Error logging sleep: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/get_sleep_analysis', methods=['GET'])
def get_sleep_analysis():
    """Retrieve comprehensive sleep analysis"""
    try:
        analysis = tracker.analyze_advanced_metrics()
        print(f"Sleep Analysis: {analysis}")
        return jsonify(analysis)
    except Exception as e:
        print(f"Error in get_sleep_analysis: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_sleep_advice', methods=['GET'])
def get_sleep_advice():
    """Retrieve personalized sleep advice"""
    try:
        advice = tracker.get_advanced_sleep_advice()
        print(f"Sleep Advice: {advice}")
        return jsonify({"advice": advice})
    except Exception as e:
        print(f"Error in get_sleep_advice: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_sleep_sessions', methods=['GET'])
def get_sleep_sessions():
    """Retrieve all sleep sessions"""
    try:
        sessions = tracker.get_all_sessions()
        return jsonify({"sessions": sessions})
    except Exception as e:
        print(f"Error in get_sleep_sessions: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/templates/<path:path>')
def send_template(path):
    """Serve template files"""
    return send_from_directory('templates', path)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)