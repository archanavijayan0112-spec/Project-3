from flask import Flask, render_template, jsonify, request
import random
from datetime import datetime

class SelfCareCard:
    def __init__(self):
        # Dictionary of quotes categorized by mood
        self.quotes = {
            "sad": [
                "Even the darkest night will end and the sun will rise.",
                "You are stronger than you think.",
                "This feeling is temporary, but your strength is permanent.",
                "Small steps still move you forward.",
                "It's okay not to be okay sometimes.",
                "The rain that falls today makes flowers bloom tomorrow.",
                "Your struggle is part of your story, not the end of it.",
                "You've survived 100% of your worst days so far."
            ],
            "anxious": [
                "Breathe in courage, breathe out fear.",
                "This moment is just one page in your story.",
                "You've handled difficult things before, you can handle this too.",
                "Focus on what you can control right now.",
                "Your anxiety is lying to you. You are capable and strong.",
                "Stay present, stay grounded.",
                "This feeling will pass, just like clouds in the sky.",
                "One thought at a time, one moment at a time."
            ],
            "tired": [
                "Rest is not a luxury, it's a necessity.",
                "You've done enough today.",
                "Your body is telling you something - listen with kindness.",
                "Even the strongest people need to recharge.",
                "Rest now so you can shine brighter tomorrow.",
                "Self-care isn't selfish, it's essential.",
                "Pause, breathe, and give yourself the gift of rest.",
                "Honor your limits today to expand your possibilities tomorrow."
            ],
            "stressed": [
                "You can't pour from an empty cup. Take care of yourself first.",
                "This pressure is temporary, your peace is worth protecting.",
                "Take it one task, one breath, one moment at a time.",
                "You are doing better than you think.",
                "Let go of what you cannot change.",
                "Your worth isn't measured by your productivity.",
                "Sometimes the most productive thing you can do is relax.",
                "The mountain seems tallest before you start climbing."
            ],
            "unmotivated": [
                "Progress isn't always visible, but it's still happening.",
                "Start where you are. Use what you have. Do what you can.",
                "The smallest step forward is still a step forward.",
                "Your path doesn't have to look like anyone else's.",
                "Today's efforts plant seeds for tomorrow's achievements.",
                "Sometimes the hardest part is just beginning.",
                "Your future self will thank you for not giving up.",
                "Motivation follows action, not the other way around."
            ],
            "happy": [
                "Happiness looks beautiful on you.",
                "Celebrate this feeling - you've earned it!",
                "Share your light with someone who needs it today.",
                "Use this energy to make someone else smile.",
                "Joy multiplies when you share it with others.",
                "This moment is as real as any challenge - embrace it fully.",
                "Your happiness creates ripples that affect others.",
                "Remember this feeling when times get tough."
            ],
            "overwhelmed": [
                "Break it down into smaller pieces.",
                "You don't have to do everything at once.",
                "It's okay to ask for help when you need it.",
                "One thing at a time is all you need to focus on.",
                "Take a deep breath and start with just one small step.",
                "You've worked through overwhelming times before.",
                "Sometimes the bravest thing is to pause.",
                "Your worth isn't tied to how much you accomplish."
            ]
        }
        
        # Additional mood categories
        self.additional_moods = {
            "confused": self.quotes["anxious"],
            "depressed": self.quotes["sad"],
            "exhausted": self.quotes["tired"],
            "worried": self.quotes["anxious"],
            "excited": self.quotes["happy"],
            "frustrated": self.quotes["stressed"],
            "bored": self.quotes["unmotivated"],
            "lonely": self.quotes["sad"],
            "angry": self.quotes["stressed"],
            "disappointed": self.quotes["sad"]
        }
        
        # Merge the dictionaries
        self.quotes.update(self.additional_moods)
        
        # Default quotes for unknown moods
        self.default_quotes = [
            "You're exactly where you need to be right now.",
            "Take a moment to appreciate yourself today.",
            "Every day is a new beginning.",
            "You are enough just as you are.",
            "Trust your journey, even when you can't see the path ahead.",
            "Your presence matters in this world.",
            "Be gentle with yourself as you grow.",
            "You bring something unique to the world."
        ]

        # Self-care suggestions
        self.suggestions = {
            "sad": "Try to go outside for a short walk, even if just for 5 minutes.",
            "anxious": "Place your hand on your heart and take 5 deep breaths.",
            "tired": "Give yourself permission to rest without guilt.",
            "stressed": "Step away from what you're doing for a 2-minute stretch break.",
            "unmotivated": "Set a timer for just 5 minutes of work on one small task.",
            "happy": "Write down three things you're grateful for right now.",
            "overwhelmed": "Write down what's on your mind to get it out of your head.",
            "confused": "Take a moment to clarify what you need right now.",
            "depressed": "Be gentle with yourself and reach out to someone who cares.",
            "exhausted": "Your body needs rest - honor that need today.",
            "worried": "Focus on what's in your control right now.",
            "excited": "Channel this energy into something meaningful to you.",
            "frustrated": "Step away and return with fresh eyes later.",
            "bored": "Try something small and new today.",
            "lonely": "Reach out to one person who makes you feel understood.",
            "angry": "Express your feelings safely through writing or movement.",
            "disappointed": "Acknowledge the feeling without judgment."
        }

    def draw_card(self, mood=None):
        """Draw a random self-care card based on mood"""
        # If mood is provided and in our dictionary, use those quotes
        if mood and mood.lower() in self.quotes:
            mood = mood.lower()
            quote = random.choice(self.quotes[mood])
            suggestion = self.suggestions.get(mood, "Take a moment just for yourself today.")
        else:
            # Use default quotes if mood is not recognized
            quote = random.choice(self.default_quotes)
            suggestion = "Take a moment just for yourself today."
        
        return {
            "quote": quote,
            "suggestion": suggestion,
            "mood": mood or "general"
        }

# Create Flask app
app = Flask(__name__)

# Initialize SelfCareCard
card_generator = SelfCareCard()

@app.route('/')
def index():
    return render_template('self_care_card.html')

@app.route('/draw-card', methods=['POST'])
def draw_card():
    mood = request.json.get('mood', None)
    card = card_generator.draw_card(mood)
    return jsonify(card)

if __name__ == '__main__':
    app.run(debug=True)