import json
import random
import datetime
import os
from flask import Flask, render_template, request, jsonify
from pathlib import Path

class MentalHealthChatbot:
    def __init__(self, data_file="mental_health_data.json"):
        self.user_name = ""
        self.user_data = {}
        self.data_file = data_file
        self.conversation_history = []
        
        # Load mental health resources and sample data
        self.responses = {}
        self.resources = {}
        self.load_resources()
        
        # Create or load user data file
        self.load_user_data()
    
    def load_resources(self):
        """Load mental health resources, responses, and data"""
        # Default resources if file doesn't exist
        default_resources = {
            'coping_strategies': {
                'anxiety': [
                    "Practice deep breathing exercises - inhale slowly for 4 counts, hold for 2, exhale for 6.",
                    "Try mindfulness meditation - focus on your breath and bodily sensations for 5-10 minutes.",
                    "Use progressive muscle relaxation - tense and then release each muscle group.",
                    "Take a brief walk outside to change your environment and get fresh air.",
                    "Write down your anxious thoughts to externalize them.",
                    "Use the 5-4-3-2-1 grounding technique: identify 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
                    "Limit caffeine and alcohol which can worsen anxiety symptoms.",
                    "Practice yoga or gentle stretching to release physical tension.",
                    "Schedule 'worry time' - set aside 15 minutes to address anxious thoughts, then try to move on."
                ],
                'depression': [
                    "Engage in physical activity - even a 10-minute walk can boost mood.",
                    "Maintain a regular sleep schedule - go to bed and wake up at consistent times.",
                    "Connect with supportive friends or family, even if it's just a brief text or call.",
                    "Set small, achievable goals to build momentum and a sense of accomplishment.",
                    "Spend time in nature, which has been shown to improve mood.",
                    "Practice self-compassion by speaking to yourself as you would to a good friend.",
                    "Use the 'opposite action' technique - do the opposite of what depression urges you to do.",
                    "Listen to uplifting music or podcasts.",
                    "Help others - volunteer work can shift focus away from internal struggles.",
                    "Celebrate small wins and progress, no matter how minor they seem."
                ],
                'stress': [
                    "Practice time management by prioritizing tasks and breaking them into smaller steps.",
                    "Take regular breaks during work or study sessions.",
                    "Use relaxation techniques like deep breathing or progressive muscle relaxation.",
                    "Engage in a hobby or activity you enjoy.",
                    "Limit exposure to stressful news and social media.",
                    "Maintain a balanced diet and stay hydrated.",
                    "Get regular exercise, even if it's just a short walk.",
                    "Practice saying 'no' to additional commitments when you're already overwhelmed.",
                    "Try aromatherapy with calming scents like lavender or chamomile.",
                    "Organize your workspace to reduce environmental stress."
                ],
                'sleep_issues': [
                    "Establish a consistent sleep schedule, even on weekends.",
                    "Create a relaxing bedtime routine to signal to your body it's time to wind down.",
                    "Limit screen time 1-2 hours before bed due to blue light exposure.",
                    "Keep your bedroom cool, dark, and quiet.",
                    "Avoid caffeine and alcohol close to bedtime.",
                    "Try relaxation techniques like deep breathing or progressive muscle relaxation before sleeping.",
                    "Use white noise or nature sounds if you're sensitive to environmental noises.",
                    "Limit daytime naps to 20-30 minutes and not too late in the day.",
                    "Exercise regularly, but not within a few hours of bedtime.",
                    "Consider a sleep journal to track patterns and identify triggers for sleep issues."
                ],
                'loneliness': [
                    "Reach out to one person each day, even just for a quick hello.",
                    "Join groups or clubs based on your interests to meet like-minded people.",
                    "Volunteer for a cause you care about.",
                    "Take a class to learn a new skill and meet others.",
                    "Use technology to stay connected with distant friends and family.",
                    "Start conversations with neighbors or people in your community.",
                    "Consider getting a pet for companionship if your lifestyle allows.",
                    "Attend community events or workshops.",
                    "Practice self-compassion and remember that loneliness is a common human experience.",
                    "Focus on quality over quantity in relationships."
                ],
                'grief': [
                    "Allow yourself to feel your emotions without judgment.",
                    "Create rituals or memorials to honor your loss.",
                    "Join a support group with others who understand what you're going through.",
                    "Take care of your physical needs - eat, sleep, and exercise regularly.",
                    "Be patient with yourself - grief has no timeline.",
                    "Express your feelings through art, writing, or other creative outlets.",
                    "Seek professional help if grief feels overwhelming.",
                    "Accept that there will be good days and difficult days.",
                    "Preserve memories through photos, journaling, or creating a memory box.",
                    "Ask for specific help from friends and family when needed."
                ]
            },
            'crisis_resources': [
                {
                    "name": "National Suicide Prevention Lifeline",
                    "contact": "1-800-273-8255",
                    "description": "24/7 support for people in distress"
                },
                {
                    "name": "Crisis Text Line",
                    "contact": "Text HOME to 741741",
                    "description": "24/7 crisis support via text message"
                },
                {
                    "name": "SAMHSA's National Helpline",
                    "contact": "1-800-662-HELP (4357)",
                    "description": "Treatment referral and information service"
                },
                {
                    "name": "Veterans Crisis Line",
                    "contact": "1-800-273-8255, Press 1",
                    "description": "Support for veterans and their loved ones"
                },
                {
                    "name": "The Trevor Project",
                    "contact": "1-866-488-7386",
                    "description": "Crisis intervention for LGBTQ+ young people"
                }
            ],
            'mental_health_facts': [
                "Mental health is an essential part of overall wellness.",
                "1 in 5 adults experience mental health challenges each year.",
                "Seeking help is a sign of strength, not weakness.",
                "Depression affects 264 million people worldwide.",
                "Exercise can be as effective as medication for mild to moderate depression.",
                "75% of mental health conditions develop by age 24.",
                "Approximately 60% of people with mental health conditions don't receive treatment.",
                "Sleep directly impacts mental health and emotional resilience.",
                "Mindfulness practices can physically change the brain in ways that improve mental health.",
                "Social connections play a vital role in maintaining good mental health.",
                "Anxiety disorders are the most common mental health condition in the U.S.",
                "Stigma remains one of the biggest barriers to seeking mental health treatment.",
                "Mental health is influenced by biological, psychological, and social factors.",
                "Trauma can have lasting effects on mental health but healing is possible.",
                "Therapy is effective for a wide range of mental health concerns."
            ],
            'self_care_activities': [
                "Take a warm bath or shower",
                "Practice mindfulness meditation for 10 minutes",
                "Go for a walk in nature",
                "Listen to your favorite music",
                "Call a friend or family member",
                "Write in a journal",
                "Read a book for pleasure",
                "Prepare a healthy meal",
                "Practice gentle stretching or yoga",
                "Disconnect from technology for an hour",
                "Watch a funny movie or TV show",
                "Engage in a creative hobby",
                "Clean or organize a small space",
                "Take a short nap",
                "Spend time with a pet",
                "Practice deep breathing exercises",
                "Set boundaries on your time and energy",
                "Express gratitude for three things in your life",
                "Spend time outside in natural light",
                "Try a new relaxation technique"
            ],
            'therapy_types': [
                {
                    "name": "Cognitive Behavioral Therapy (CBT)",
                    "description": "Focuses on identifying and changing negative thought patterns and behaviors."
                },
                {
                    "name": "Dialectical Behavior Therapy (DBT)",
                    "description": "Teaches skills for emotional regulation, distress tolerance, and interpersonal effectiveness."
                },
                {
                    "name": "Psychodynamic Therapy",
                    "description": "Explores unconscious patterns and past experiences that influence current behavior."
                },
                {
                    "name": "Mindfulness-Based Cognitive Therapy (MBCT)",
                    "description": "Combines cognitive therapy with mindfulness practices to prevent depression relapse."
                },
                {
                    "name": "Acceptance and Commitment Therapy (ACT)",
                    "description": "Focuses on accepting difficult thoughts and feelings while committing to behavior change."
                },
                {
                    "name": "Interpersonal Therapy (IPT)",
                    "description": "Addresses interpersonal issues and improves communication skills."
                },
                {
                    "name": "Eye Movement Desensitization and Reprocessing (EMDR)",
                    "description": "Helps process traumatic memories through guided eye movements."
                }
            ],
            'conversation_starters': [
                "What's one small thing you're looking forward to today?",
                "What's a self-care activity that has helped you in the past?",
                "Is there a particular time of day when you feel most energized?",
                "What's something you're proud of, no matter how small?",
                "What's a challenge you're currently facing?",
                "How have your sleep patterns been lately?",
                "What activities help you feel most like yourself?",
                "Is there someone in your life who supports your mental health?",
                "What kinds of things tend to trigger stress for you?",
                "What's a healthy coping mechanism you'd like to develop?"
            ],
            'mood_management': {
                "low_mood": [
                    "Try to do one small enjoyable activity today.",
                    "Consider whether you're being too hard on yourself.",
                    "Remember that emotions are temporary and will pass.",
                    "Reach out to someone supportive.",
                    "Consider whether your basic needs (sleep, food, water) are being met."
                ],
                "high_anxiety": [
                    "Focus on your breathing - try the 4-7-8 technique.",
                    "Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
                    "Remember that anxiety is uncomfortable but not dangerous.",
                    "Ask yourself: 'What's the worst that could happen, and could I handle it?'",
                    "Try to identify the specific fear beneath your anxiety."
                ],
                "overwhelm": [
                    "Break tasks down into smaller, manageable steps.",
                    "Focus on one thing at a time rather than the whole situation.",
                    "Ask yourself: 'What's one small thing I can do right now?'",
                    "Prioritize tasks and consider what can be delegated or postponed.",
                    "Take a short break to reset your mind."
                ],
                "anger": [
                    "Take a time-out before responding to the situation.",
                    "Do something physical to release the energy, like a brisk walk.",
                    "Use 'I' statements to express your feelings.",
                    "Ask yourself if your anger is proportional to the situation.",
                    "Try to identify the primary emotion beneath your anger."
                ]
            },
            'positive_affirmations': [
                "I am doing the best I can with the resources I have.",
                "My feelings are valid, and it's okay to experience them.",
                "I am worthy of love and respect.",
                "I have overcome challenges before and can do it again.",
                "I don't have to be perfect to be worthy.",
                "I trust myself to make decisions that are right for me.",
                "I am resilient and can adapt to change.",
                "I deserve to take care of myself.",
                "I am stronger than I think.",
                "Today is a new opportunity to grow and learn.",
                "I can learn from my mistakes and move forward.",
                "I am in charge of my own happiness.",
                "My presence matters in this world.",
                "I am allowed to set boundaries and say no.",
                "I am capable of positive change."
            ]
        }
        
        # Responses for different scenarios
        default_responses = {
            'greeting': [
                "Hello! How are you feeling today?",
                "Hi there! I'm here to support you.",
                "Welcome! How can I help you today?",
                "Good to see you! How's your day going?",
                "Hello! I'm your mental health assistant. What's on your mind today?"
            ],
            'unknown': [
                "I'm not sure I understand. Could you rephrase that?",
                "Can you tell me more about what you're experiencing?",
                "I'm listening. Could you clarify your message?",
                "I want to help, but I need a bit more information.",
                "Let's explore that further. Could you share more details?"
            ],
            'thank_you': [
                "You're welcome! I'm here to support you.",
                "Anytime! Don't hesitate to reach out again.",
                "I'm glad I could help. Take care of yourself.",
                "It's my pleasure to be here for you.",
                "You're doing great by prioritizing your mental health."
            ],
            'goodbye': [
                "Take care! Remember to be kind to yourself.",
                "Goodbye for now. I'll be here when you need me.",
                "Wishing you well until next time.",
                "Remember that small steps can lead to big changes.",
                "Take care of yourself. I'll be here if you need support."
            ],
            'follow_up': [
                "How did that suggestion work for you?",
                "Was that helpful? Is there anything else you'd like to discuss?",
                "Did that information address your concerns?",
                "How are you feeling now?",
                "Is there anything specific you'd like to explore further?"
            ],
            'empathy': [
                "That sounds really difficult. I'm here to listen.",
                "I can understand why you'd feel that way.",
                "It makes sense that you're experiencing these emotions.",
                "Thank you for sharing that with me.",
                "That takes courage to talk about. I appreciate your openness."
            ],
            'encouragement': [
                "You're taking important steps by seeking support.",
                "Every small effort counts toward your wellbeing.",
                "Remember that healing isn't linear, and that's okay.",
                "You have more strength than you might realize right now.",
                "Your resilience is impressive, even if it doesn't feel that way."
            ]
        }
        
        # Try to load from file, use defaults if not found
        try:
            with open('mental_health_resources.json', 'r') as f:
                loaded_resources = json.load(f)
                self.resources = loaded_resources.get('resources', default_resources)
                self.responses = loaded_resources.get('responses', default_responses)
        except FileNotFoundError:
            self.resources = default_resources
            self.responses = default_responses
    
    def load_user_data(self):
        """Load or initialize user data file"""
        try:
            with open(self.data_file, 'r') as f:
                self.user_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.user_data = {"users": {}}
    
    def save_user_data(self):
        """Save user data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.user_data, f, indent=4)
    
    def track_conversation(self, user_input, bot_response):
        """Track conversation for context-aware responses"""
        self.conversation_history.append({
            "user": user_input,
            "bot": bot_response,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Keep only the last 10 exchanges for memory
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    def generate_bot_response(self, user_input, username="Anonymous"):
        """Generate bot responses based on input"""
        user_input = user_input.lower().strip()
        
        # Check if user exists and create if not
        if username not in self.user_data['users']:
            self.user_data['users'][username] = {
                'name': username,
                'mood_log': [],
                'goals': [],
                'preferences': {},
                'topics_discussed': []
            }
        
        # Get user data
        user = self.user_data['users'][username]
        
        # Check for thank you messages
        if any(word in user_input for word in ['thank', 'thanks', 'appreciate']):
            return random.choice(self.responses['thank_you'])
        
        # Check for goodbye messages
        if any(word in user_input for word in ['bye', 'goodbye', 'see you', 'talk later']):
            return random.choice(self.responses['goodbye'])
        
        # Greeting responses
        if any(word in user_input for word in ['hello', 'hi', 'hey', 'greetings']):
            # Personalized greeting if we have user data
            if len(user['mood_log']) > 0:
                last_mood = user['mood_log'][-1]
                days_since = (datetime.datetime.now() - datetime.datetime.strptime(last_mood['date'], "%Y-%m-%d")).days
                
                if days_since == 0:
                    return f"Hello again! How has your day progressed since we last talked?"
                elif days_since == 1:
                    return f"Welcome back! How are you feeling today compared to yesterday?"
                else:
                    return f"Good to see you again after {days_since} days! How have you been?"
            else:
                return random.choice(self.responses['greeting'])
        
        # Mood logging
        if any(word in user_input for word in ['mood', 'feeling', 'check in', 'track']):
            # Add mood tracking to topics discussed
            if 'mood_tracking' not in user['topics_discussed']:
                user['topics_discussed'].append('mood_tracking')
                self.save_user_data()
                
            return "Let's log your mood. On a scale of 1-10, how are you feeling today?"
        
        # Positivity and affirmation requests
        if any(word in user_input for word in ['positive', 'affirmation', 'encourage', 'motivate']):
            return random.choice(self.resources['positive_affirmations'])
        
        # Conversation starters
        if any(phrase in user_input for phrase in ['what to talk about', 'conversation starter', 'topic', 'talk about']):
            return f"Here's a question to consider: {random.choice(self.resources['conversation_starters'])}"
        
        # Self-care suggestions
        if any(word in user_input for word in ['self-care', 'selfcare', 'take care', 'help myself']):
            return f"Here's a self-care activity you might try: {random.choice(self.resources['self_care_activities'])}"
        
        # Information about therapy types
        if any(word in user_input for word in ['therapy', 'therapist', 'counseling', 'professional help']):
            therapy = random.choice(self.resources['therapy_types'])
            return f"There are many effective therapy approaches. For example, {therapy['name']}: {therapy['description']}"
        
        # Advice for specific issues
        if any(word in user_input for word in ['anxious', 'anxiety', 'nervous', 'worried', 'panic']):
            strategies = self.resources['coping_strategies']['anxiety']
            return f"Here's a strategy for managing anxiety: {random.choice(strategies)}"
        
        if any(word in user_input for word in ['sad', 'depressed', 'down', 'blue', 'unhappy', 'depression']):
            strategies = self.resources['coping_strategies']['depression']
            return f"Here's a strategy for managing low mood: {random.choice(strategies)}"
        
        if any(word in user_input for word in ['stressed', 'overwhelmed', 'pressure', 'stress']):
            strategies = self.resources['coping_strategies']['stress']
            return f"Here's a strategy for managing stress: {random.choice(strategies)}"
        
        if any(word in user_input for word in ['sleep', 'insomnia', 'tired', 'rest', 'bed']):
            strategies = self.resources['coping_strategies']['sleep_issues']
            return f"Here's a tip for better sleep: {random.choice(strategies)}"
        
        if any(word in user_input for word in ['lonely', 'alone', 'isolated', 'no friends', 'loneliness']):
            strategies = self.resources['coping_strategies']['loneliness']
            return f"Here's a suggestion for dealing with loneliness: {random.choice(strategies)}"
        
        if any(word in user_input for word in ['grief', 'loss', 'died', 'death', 'passed away']):
            strategies = self.resources['coping_strategies']['grief']
            return f"Here's a thought about coping with grief: {random.choice(strategies)}"
        
        # Crisis resources
        if any(word in user_input for word in ['help', 'crisis', 'emergency', 'suicidal', 'suicide', 'harm', 'emergency']):
            resources = self.resources['crisis_resources']
            selected_resource = random.choice(resources)
            return f"If you're in crisis, please reach out for help. {selected_resource['name']} - {selected_resource['contact']} - {selected_resource['description']}"
        
        # Mental health facts
        if any(word in user_input for word in ['fact', 'facts', 'learn', 'information', 'statistics']):
            return random.choice(self.resources['mental_health_facts'])
        
        # Check if there are any emotion words to respond to
        emotion_words = {
            'angry': 'anger', 'mad': 'anger', 'furious': 'anger', 'rage': 'anger',
            'scared': 'high_anxiety', 'afraid': 'high_anxiety', 'terrified': 'high_anxiety',
            'hopeless': 'low_mood', 'worthless': 'low_mood', 'exhausted': 'low_mood',
            'confused': 'overwhelm', 'lost': 'overwhelm', 'chaotic': 'overwhelm'
        }
        
        for word, emotion in emotion_words.items():
            if word in user_input:
                strategies = self.resources['mood_management'][emotion]
                return f"It sounds like you might be feeling {word}. {random.choice(strategies)}"
        
        # Look for keywords about specific life areas
        life_areas = {
            'work': ["Work stress is common. Could you identify one specific aspect that's most challenging?",
                     "Work-life balance is important. What's one small boundary you could set?",
                     "Many people struggle with work stress. What's helped you in the past?"],
            'relationship': ["Relationships require maintenance. What's one small positive step you could take?",
                              "Communication is key in relationships. Have you been able to express your needs?",
                              "Relationships can be both fulfilling and challenging. What's one thing you appreciate about this relationship?"],
            'family': ["Family dynamics can be complex. What's one small thing that might improve the situation?",
                       "Family relationships often carry deep emotions. What patterns do you notice?",
                       "Setting boundaries with family can be difficult but important. What's one boundary you could set?"],
            'school': ["School pressure is real. What's one small way you could make it more manageable?",
                       "Learning is a process. What's one small success you've had recently?",
                       "Many students face challenges. What's worked for you in the past?"]
        }
        
        for area, responses in life_areas.items():
            if area in user_input:
                return random.choice(responses)
        
        # Context-aware responses
        if len(self.conversation_history) > 0:
            last_exchange = self.conversation_history[-1]
            if "Let's log your mood" in last_exchange['bot'] and user_input.isdigit():
                mood_rating = int(user_input)
                if 1 <= mood_rating <= 10:
                    # This will be handled by the mood logging endpoint
                    return f"Thanks for sharing. A {mood_rating}/10 is noted. Would you like to add any notes about what influenced your mood today?"
            
            if "strategy for managing" in last_exchange['bot']:
                if any(word in user_input for word in ['more', 'another', 'different', 'else']):
                    for issue in ['anxiety', 'depression', 'stress', 'sleep_issues', 'loneliness', 'grief']:
                        if issue in last_exchange['bot']:
                            strategies = self.resources['coping_strategies'][issue]
                            return f"Here's another strategy for that: {random.choice(strategies)}"
                
                if any(word in user_input for word in ['how', 'explain', 'more detail']):
                    return "Would you like me to explain more about why this strategy works or how to implement it effectively?"
        
        # Use empathy response occasionally for unknown inputs
        if random.random() < 0.3:  # 30% chance
            return random.choice(self.responses['empathy'])
        
        # Fallback response
        return random.choice(self.responses['unknown'])

# Only include this block if you want to run chatbot.py directly
if __name__ == '__main__':
    # Flask Application for standalone use
    app = Flask(__name__)
    chatbot = MentalHealthChatbot()

    @app.route('/')
    def index():
        """Render the main chatbot interface"""
        return render_template('chatbot.html')

    @app.route('/send_message', methods=['POST'])
    def send_message():
        """Process user message and generate bot response"""
        data = request.json
        user_input = data.get('message', '').lower().strip()
        username = data.get('username', 'Anonymous')
        
        response = chatbot.generate_bot_response(user_input, username)
        
        # Track conversation
        chatbot.track_conversation(user_input, response)
        
        return jsonify({'response': response})

    @app.route('/log_mood', methods=['POST'])
    def log_mood():
        """Log user's mood"""
        data = request.json
        mood_rating = data.get('mood_rating')
        mood_notes = data.get('mood_notes', '')
        username = data.get('username', 'Anonymous')
        
        # Add mood entry to user data
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Ensure user exists in data
        if username not in chatbot.user_data['users']:
            chatbot.user_data['users'][username] = {
                'name': username,
                'mood_log': [],
                'goals': [],
                'preferences': {},
                'topics_discussed': []
            }
        
        mood_entry = {
            'date': today,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'mood_rating': mood_rating,
            'notes': mood_notes
        }
        
        chatbot.user_data['users'][username]['mood_log'].append(mood_entry)
        chatbot.save_user_data()
        
        # Provide feedback based on mood rating
        if mood_rating <= 3:
            feedback = "I notice you're feeling quite low today. Would you like some coping strategies for difficult emotions?"
        elif mood_rating <= 5:
            feedback = "Things seem a bit difficult right now. Would you like to talk about what's going on, or would you prefer some self-care suggestions?"
        elif mood_rating <= 7:
            feedback = "You're doing okay, but there might be room for improvement. Is there anything specific that would help boost your mood further?"
        else:
            feedback = "I'm glad to hear you're doing well today! Would you like to talk about what's working well for you?"
        
        # Check for mood patterns
        user_moods = chatbot.user_data['users'][username]['mood_log']
        if len(user_moods) >= 3:
            recent_moods = [entry['mood_rating'] for entry in user_moods[-3:]]
            avg_mood = sum(recent_moods) / len(recent_moods)
            
            if all(mood <= 5 for mood in recent_moods):
                feedback += " I notice your mood has been consistently low recently. Have you considered speaking with a mental health professional?"
            elif avg_mood > sum(recent_moods[-3:-1]) / 2:
                feedback += " Your mood seems to be improving compared to your recent entries. That's great progress!"
        
        return jsonify({'feedback': feedback})

    @app.route('/get_mood_history', methods=['POST'])
    def get_mood_history():
        """Retrieve mood history for visualizations"""
        data = request.json
        username = data.get('username', 'Anonymous')
        
        if username in chatbot.user_data['users'] and len(chatbot.user_data['users'][username]['mood_log']) > 0:
            return jsonify({'mood_history': chatbot.user_data['users'][username]['mood_log']})
        else:
            return jsonify({'mood_history': []})

    @app.route('/set_goal', methods=['POST'])
    def set_goal():
        """Set a wellness goal"""
        data = request.json
        goal_text = data.get('goal_text', '')
        target_date = data.get('target_date', '')
        username = data.get('username', 'Anonymous')
        
        # Ensure user exists
        if username not in chatbot.user_data['users']:
            chatbot.user_data['users'][username] = {
                'name': username,
                'mood_log': [],
                'goals': [],
                'preferences': {},
                'topics_discussed': []
            }
        
        goal_entry = {
            'text': goal_text,
            'created_date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'target_date': target_date,
            'completed': False,
            'progress_notes': []
        }
        
        chatbot.user_data['users'][username]['goals'].append(goal_entry)
        chatbot.save_user_data()
        
        return jsonify({'response': "Goal set successfully! I'll help you track your progress."})

    @app.route('/get_resources', methods=['GET'])
    def get_resources():
        """Get all available resources"""
        return jsonify({'resources': chatbot.resources})

    # Ensure data file exists
    if not os.path.exists("mental_health_data.json"):
        with open("mental_health_data.json", 'w') as f:
            json.dump({"users": {}}, f)
    
    app.run(debug=True)