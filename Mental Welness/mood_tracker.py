import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter
import numpy as np

class MoodTracker:
    def __init__(self, data_file="mood_data.json"):
        """Initialize the mood tracker with a data file."""
        self.data_file = data_file
        self.mood_data = self._load_data()
        self.mood_scale = {
            1: "Very Negative",
            2: "Negative",
            3: "Neutral",
            4: "Positive",
            5: "Very Positive"
        }
        self.mood_icons = {
            1: "😭",
            2: "😔",
            3: "😐", 
            4: "😊",
            5: "🌟"
        }
        # Ensure static directory exists
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        os.makedirs(self.static_dir, exist_ok=True)
    
    def _load_data(self):
        """Load existing mood data from file if it exists."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {'entries': []}
        else:
            return {'entries': []}
    
    def _save_data(self):
        """Save mood data to file."""
        with open(self.data_file, 'w') as file:
            json.dump(self.mood_data, file, indent=4)
    
    def add_entry(self, mood_rating, description, factors):
        """Add a new mood entry."""
        try:
            mood_rating = int(mood_rating)
            if mood_rating < 1 or mood_rating > 5:
                raise ValueError("Mood rating must be between 1 and 5")
                
            entry = {
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "rating": mood_rating,
                "description": description,
                "factors": factors,
                "mood_text": self.mood_scale.get(mood_rating, "Unknown"),
                "mood_icon": self.mood_icons.get(mood_rating, "❓")
            }
            
            self.mood_data['entries'].append(entry)
            self._save_data()
            return entry
        except (ValueError, TypeError) as e:
            return {"error": str(e)}
    
    def get_mood_analysis(self):
        """Analyze mood data and return insights."""
        entries = self.mood_data['entries']
        
        if not entries:
            return {
                "total_entries": 0,
                "average_rating": 0,
                "trend": "no data",
                "top_factors": [],
                "latest_entry": None,
                "has_data": False
            }
        
        num_entries = len(entries)
        avg_rating = sum(entry['rating'] for entry in entries) / num_entries
        
        # Mood trend analysis
        trend = "stable"
        trend_value = 0
        if num_entries >= 3:
            recent = entries[-3:]
            recent_avg = sum(entry['rating'] for entry in recent) / len(recent)
            trend_diff = recent_avg - avg_rating
            trend_value = round(trend_diff, 2)
            
            if trend_diff > 0.5:
                trend = "improving"
            elif trend_diff < -0.5:
                trend = "declining"
        
        # Common factors
        all_factors = []
        for entry in entries:
            all_factors.extend(entry['factors'])
        
        factor_counts = Counter(all_factors)
        top_factors = factor_counts.most_common(5)
        
        # Calculate mood distribution
        mood_distribution = Counter(entry['rating'] for entry in entries)
        mood_distribution = {self.mood_scale[k]: v for k, v in mood_distribution.items() if k in self.mood_scale}
        
        # Calculate weekly averages
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        recent_entries = [e for e in entries if datetime.fromisoformat(e['timestamp']).date() >= week_ago]
        recent_avg = sum(e['rating'] for e in recent_entries) / len(recent_entries) if recent_entries else 0
        
        monthly_entries = [e for e in entries if datetime.fromisoformat(e['timestamp']).date() >= month_ago]
        monthly_avg = sum(e['rating'] for e in monthly_entries) / len(monthly_entries) if monthly_entries else 0
        
        return {
            "total_entries": num_entries,
            "average_rating": round(avg_rating, 2),
            "trend": trend,
            "trend_value": trend_value,
            "top_factors": top_factors,
            "mood_distribution": mood_distribution,
            "weekly_average": round(recent_avg, 2),
            "monthly_average": round(monthly_avg, 2),
            "latest_entry": entries[-1] if entries else None,
            "has_data": True
        }
    
    def generate_mood_chart(self):
        """Create a mood visualization chart."""
        entries = self.mood_data['entries']
        
        if not entries:
            return None
        
        # Extract dates and ratings
        dates = [datetime.fromisoformat(entry['timestamp']) for entry in entries]
        ratings = [entry['rating'] for entry in entries]
        
        # Create plot
        plt.figure(figsize=(12, 7))
        plt.plot(dates, ratings, marker='o', linestyle='-', color='#2c3e90', linewidth=2, markersize=8)
        plt.axhline(y=3, color='gray', linestyle='--', alpha=0.7)  # Neutral line
        
        # Add trend line
        if len(dates) > 1:
            z = np.polyfit(mdates.date2num(dates), ratings, 1)
            p = np.poly1d(z)
            plt.plot(dates, p(mdates.date2num(dates)), "r--", alpha=0.8)
        
        plt.title('Mood Tracking Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Mood Rating', fontsize=12)
        plt.yticks([1, 2, 3, 4, 5], 
                  ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'])
        plt.grid(True, alpha=0.3)
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Set y-axis limits with padding
        plt.ylim(0.5, 5.5)
            
        plt.tight_layout()
        
        # Save chart
        chart_filename = os.path.join(self.static_dir, 'mood_chart.png')
        plt.savefig(chart_filename, dpi=100, bbox_inches='tight')
        plt.close()
        
        return 'static/mood_chart.png'

    def get_entries_by_date_range(self, start_date=None, end_date=None):
        """Get entries within a specific date range."""
        entries = self.mood_data['entries']
        
        if not entries:
            return []
            
        if not start_date:
            # Default to last 7 days if no start date provided
            start_date = (datetime.now() - timedelta(days=7)).date()
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        filtered_entries = [
            entry for entry in entries 
            if start_date <= datetime.fromisoformat(entry['timestamp']).date() <= end_date
        ]
        
        return filtered_entries

# Flask Application
app = Flask(__name__)
mood_tracker = MoodTracker()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('mood_tracker.html')

@app.route('/add_entry', methods=['POST'])
def add_entry():
    """Add a new mood entry."""
    try:
        data = request.json
        entry = mood_tracker.add_entry(
            mood_rating=data.get('mood_rating'),
            description=data.get('description', ''),
            factors=data.get('factors', [])
        )
        
        if "error" in entry:
            return jsonify({"error": entry["error"]}), 400
            
        return jsonify(entry), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mood_analysis')
def mood_analysis():
    """Get mood analysis data."""
    analysis = mood_tracker.get_mood_analysis()
    return jsonify(analysis)

@app.route('/mood_chart')
def mood_chart():
    """Generate and return mood chart path."""
    try:
        chart_path = mood_tracker.generate_mood_chart()
        if chart_path:
            return jsonify({"chart_path": chart_path})
        return jsonify({"message": "No chart available", "error": "No data to generate chart"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to generate chart", "error": str(e)}), 500

@app.route('/recent_entries')
def recent_entries():
    """Get recent mood entries."""
    entries = mood_tracker.mood_data.get('entries', [])
    recent = entries[-5:] if entries else []  # Last 5 entries
    return jsonify(recent)

@app.route('/entries_by_date')
def entries_by_date():
    """Get entries by date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    entries = mood_tracker.get_entries_by_date_range(start_date, end_date)
    return jsonify(entries)

@app.route('/factors')
def get_factors():
    """Get all unique factors."""
    entries = mood_tracker.mood_data.get('entries', [])
    all_factors = []
    for entry in entries:
        all_factors.extend(entry.get('factors', []))
    
    unique_factors = list(set(all_factors))
    return jsonify({"factors": unique_factors})

if __name__ == '__main__':
    app.run(debug=True)