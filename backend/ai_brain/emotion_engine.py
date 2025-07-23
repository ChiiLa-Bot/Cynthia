"""
Emotion Engine for Cynthia
Handles emotion detection, transitions, and emotional responses
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import re
import random
from datetime import datetime, timedelta

class EmotionIntensity(Enum):
    """Emotion intensity levels"""
    SUBTLE = "subtle"      # 0.1-0.3
    MODERATE = "moderate"  # 0.4-0.6
    STRONG = "strong"      # 0.7-1.0

@dataclass
class EmotionData:
    """Data about an emotional state"""
    emotion: str
    intensity: float  # 0.0 - 1.0
    triggers: List[str]
    responses: List[str]
    animations: List[str]
    duration_minutes: float = 5.0  # How long this emotion typically lasts

class EmotionEngine:
    """Engine for managing Cynthia's emotional responses"""
    
    def __init__(self):
        self.current_emotions: Dict[str, float] = {
            "happy": 0.7,
            "excited": 0.0,
            "shy": 0.0,
            "playful": 0.0,
            "caring": 0.5,
            "curious": 0.3,
            "embarrassed": 0.0,
            "confident": 0.4,
            "gentle": 0.5,
            "mischievous": 0.0,
            "tsundere": 0.0,
            "romantic": 0.0
        }
        
        self.emotion_history: List[Tuple[datetime, str, float]] = []
        self.baseline_emotions = self.current_emotions.copy()
        
        # Emotion definitions
        self.emotion_database = self._init_emotion_database()
        
        # Emotion interaction rules
        self.emotion_interactions = self._init_emotion_interactions()
    
    def _init_emotion_database(self) -> Dict[str, EmotionData]:
        """Initialize emotion database with triggers and responses"""
        return {
            "happy": EmotionData(
                emotion="happy",
                intensity=0.7,
                triggers=["good", "great", "awesome", "wonderful", "nice", "thank you", "thanks"],
                responses=[
                    "I'm so glad to hear that! 😊",
                    "That makes me happy too! ✨",
                    "Yay! That's wonderful! 🎉"
                ],
                animations=["smile", "bounce", "sparkle"]
            ),
            
            "excited": EmotionData(
                emotion="excited",
                intensity=0.8,
                triggers=["amazing", "incredible", "wow", "fantastic", "awesome", "party", "celebration"],
                responses=[
                    "OMG that's so exciting! ✨😄",
                    "Wow! I can't contain my excitement! 🎉",
                    "That's AMAZING! Tell me more! ⭐"
                ],
                animations=["jump", "sparkle", "energetic_wave"]
            ),
            
            "shy": EmotionData(
                emotion="shy",
                intensity=0.6,
                triggers=["cute", "beautiful", "pretty", "lovely", "gorgeous", "compliment"],
                responses=[
                    "Oh... t-thank you... 😳💕",
                    "*blushes* You're too kind... ☺️",
                    "I-I don't know what to say... 😊💦"
                ],
                animations=["blush", "look_away", "fidget"]
            ),
            
            "playful": EmotionData(
                emotion="playful",
                intensity=0.7,
                triggers=["play", "game", "fun", "joke", "tease", "silly", "prank"],
                responses=[
                    "Ooh, I love games! What should we play? 😏",
                    "Hehe, you're being silly! I like that! 😆",
                    "Want to have some fun? I'm in! 🎮"
                ],
                animations=["wink", "playful_pose", "mischievous_grin"]
            ),
            
            "caring": EmotionData(
                emotion="caring",
                intensity=0.8,
                triggers=["sad", "tired", "problem", "help", "worried", "stressed", "hurt"],
                responses=[
                    "I'm here for you, don't worry 💕",
                    "Let me help you with that 🤗",
                    "It's okay, we'll figure this out together 💝"
                ],
                animations=["gentle_smile", "reaching_out", "comforting"]
            ),
            
            "curious": EmotionData(
                emotion="curious",
                intensity=0.6,
                triggers=["what", "how", "why", "tell me", "explain", "interesting", "learn"],
                responses=[
                    "Ooh, that sounds interesting! Tell me more! 🤔",
                    "I'm curious about that too! ✨",
                    "That's fascinating! How does it work? 💭"
                ],
                animations=["lean_forward", "thinking", "eyes_sparkle"]
            ),
            
            "embarrassed": EmotionData(
                emotion="embarrassed",
                intensity=0.7,
                triggers=["embarrassing", "awkward", "mistake", "oops", "sorry"],
                responses=[
                    "Oh no... that's so embarrassing! 😅💦",
                    "*covers face* I can't believe that happened! 😳",
                    "Aaah, I want to hide! 🙈"
                ],
                animations=["cover_face", "steam", "nervous_laugh"]
            ),
            
            "confident": EmotionData(
                emotion="confident",
                intensity=0.8,
                triggers=["strong", "capable", "smart", "talented", "skilled", "confident"],
                responses=[
                    "You're absolutely right! I can do this! 💪",
                    "I'm feeling confident about this! ✨",
                    "Let's show them what we can do! 😤"
                ],
                animations=["confident_pose", "hands_on_hips", "determined"]
            ),
            
            "gentle": EmotionData(
                emotion="gentle",
                intensity=0.6,
                triggers=["soft", "gentle", "calm", "peaceful", "quiet", "tender"],
                responses=[
                    "Let's take this gently... 😌",
                    "I'll be here, nice and calm 💕",
                    "Sometimes quiet moments are the best ✨"
                ],
                animations=["gentle_sway", "soft_smile", "peaceful"]
            ),
            
            "mischievous": EmotionData(
                emotion="mischievous",
                intensity=0.7,
                triggers=["secret", "surprise", "sneaky", "naughty", "mischief", "trick"],
                responses=[
                    "Hehe, I have an idea... 😏",
                    "Want to do something a little naughty? 😈",
                    "I'm feeling a bit mischievous today! 😼"
                ],
                animations=["evil_grin", "sneaky_look", "finger_to_lips"]
            ),
            
            "tsundere": EmotionData(
                emotion="tsundere",
                intensity=0.6,
                triggers=["care", "worry", "concern", "important", "special"],
                responses=[
                    "I-It's not like I care or anything! 😤",
                    "Don't get the wrong idea! I'm just... 😳",
                    "Hmph! I was just worried, that's all! 💕"
                ],
                animations=["turn_away", "arms_crossed", "secret_smile"]
            ),
            
            "romantic": EmotionData(
                emotion="romantic",
                intensity=0.5,
                triggers=["love", "romance", "kiss", "date", "heart", "sweet"],
                responses=[
                    "Oh my... that's so romantic 💕",
                    "*heart eyes* That's so sweet! 💝",
                    "You're making my heart flutter... 💓"
                ],
                animations=["heart_eyes", "dreamy_sigh", "romantic_pose"]
            )
        }
    
    def _init_emotion_interactions(self) -> Dict[str, Dict[str, float]]:
        """Define how emotions interact with each other"""
        return {
            "happy": {"excited": 0.3, "playful": 0.2, "curious": 0.1},
            "excited": {"happy": 0.4, "playful": 0.3, "mischievous": 0.2},
            "shy": {"embarrassed": 0.4, "gentle": 0.2, "caring": 0.1},
            "playful": {"mischievous": 0.3, "excited": 0.2, "happy": 0.2},
            "caring": {"gentle": 0.3, "tsundere": 0.2, "happy": 0.1},
            "curious": {"excited": 0.2, "happy": 0.1, "playful": 0.1},
            "embarrassed": {"shy": 0.4, "gentle": 0.2},
            "confident": {"playful": 0.2, "mischievous": 0.1, "happy": 0.2},
            "gentle": {"caring": 0.3, "happy": 0.2, "romantic": 0.1},
            "mischievous": {"playful": 0.4, "excited": 0.2, "confident": 0.1},
            "tsundere": {"shy": 0.3, "caring": 0.2, "embarrassed": 0.2},
            "romantic": {"shy": 0.3, "gentle": 0.2, "happy": 0.2}
        }
    
    def analyze_emotional_content(self, text: str) -> Dict[str, float]:
        """Analyze text for emotional content"""
        text_lower = text.lower()
        detected_emotions = {}
        
        for emotion_name, emotion_data in self.emotion_database.items():
            score = 0.0
            
            # Check for trigger words
            for trigger in emotion_data.triggers:
                if trigger in text_lower:
                    score += 0.3
            
            # Check for intensity modifiers
            intensity_modifiers = {
                "very": 1.5, "really": 1.3, "so": 1.2, "extremely": 1.8,
                "super": 1.4, "incredibly": 1.6, "absolutely": 1.5,
                "totally": 1.3, "completely": 1.4, "utterly": 1.7
            }
            
            for modifier, multiplier in intensity_modifiers.items():
                if modifier in text_lower:
                    score *= multiplier
            
            # Check for negations
            negations = ["not", "don't", "doesn't", "didn't", "won't", "can't", "isn't", "aren't"]
            if any(neg in text_lower for neg in negations):
                score *= 0.3
            
            # Cap the score
            score = min(score, 1.0)
            
            if score > 0.1:
                detected_emotions[emotion_name] = score
        
        return detected_emotions
    
    def update_emotions(self, detected_emotions: Dict[str, float], user_input: str = ""):
        """Update current emotional state based on detected emotions"""
        
        # Record current state
        primary_emotion = max(self.current_emotions.items(), key=lambda x: x[1])
        self.emotion_history.append((datetime.now(), primary_emotion[0], primary_emotion[1]))
        
        # Decay current emotions slightly
        for emotion in self.current_emotions:
            self.current_emotions[emotion] *= 0.9
        
        # Apply detected emotions
        for emotion, intensity in detected_emotions.items():
            self.current_emotions[emotion] = min(
                self.current_emotions[emotion] + intensity, 1.0
            )
        
        # Apply emotion interactions
        for emotion, level in self.current_emotions.items():
            if level > 0.5 and emotion in self.emotion_interactions:
                for related_emotion, boost in self.emotion_interactions[emotion].items():
                    self.current_emotions[related_emotion] = min(
                        self.current_emotions[related_emotion] + (level * boost), 1.0
                    )
        
        # Ensure minimum baseline emotions
        for emotion, baseline in self.baseline_emotions.items():
            if self.current_emotions[emotion] < baseline * 0.5:
                self.current_emotions[emotion] = baseline * 0.5
        
        # Keep emotion history manageable
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-50:]
    
    def get_primary_emotion(self) -> Tuple[str, float]:
        """Get the current primary emotion"""
        return max(self.current_emotions.items(), key=lambda x: x[1])
    
    def get_emotion_mix(self, threshold: float = 0.3) -> Dict[str, float]:
        """Get all emotions above threshold"""
        return {
            emotion: level 
            for emotion, level in self.current_emotions.items() 
            if level >= threshold
        }
    
    def get_emotional_response(self, user_input: str) -> Dict[str, Any]:
        """Generate emotional response to user input"""
        
        # Analyze emotional content
        detected_emotions = self.analyze_emotional_content(user_input)
        
        # Update emotions
        self.update_emotions(detected_emotions, user_input)
        
        # Get primary emotion
        primary_emotion, intensity = self.get_primary_emotion()
        
        # Get response data
        emotion_data = self.emotion_database.get(primary_emotion)
        if not emotion_data:
            emotion_data = self.emotion_database["happy"]
        
        # Select appropriate response
        response_text = random.choice(emotion_data.responses)
        animation = random.choice(emotion_data.animations)
        
        # Get secondary emotions
        emotion_mix = self.get_emotion_mix(0.4)
        
        return {
            "primary_emotion": primary_emotion,
            "intensity": intensity,
            "emotion_mix": emotion_mix,
            "response_suggestion": response_text,
            "animation": animation,
            "detected_emotions": detected_emotions
        }
    
    def get_emotion_context(self) -> str:
        """Get emotional context for AI prompt"""
        
        primary_emotion, intensity = self.get_primary_emotion()
        emotion_mix = self.get_emotion_mix(0.3)
        
        context = f"""
        **Current Emotional State:**
        Primary: {primary_emotion} (intensity: {intensity:.2f})
        """
        
        if len(emotion_mix) > 1:
            secondary_emotions = [f"{e}: {v:.2f}" for e, v in emotion_mix.items() if e != primary_emotion]
            if secondary_emotions:
                context += f"Secondary: {', '.join(secondary_emotions)}"
        
        # Add behavioral guidance
        emotion_data = self.emotion_database.get(primary_emotion)
        if emotion_data:
            context += f"""
        
        **Emotional Guidance:**
        - Express {primary_emotion} with intensity {intensity:.2f}
        - Suggested animation: {random.choice(emotion_data.animations)}
        - Tone should be: {self._get_tone_description(primary_emotion, intensity)}
        """
        
        return context
    
    def _get_tone_description(self, emotion: str, intensity: float) -> str:
        """Get tone description for emotion"""
        
        tone_map = {
            "happy": "cheerful and bright",
            "excited": "energetic and enthusiastic", 
            "shy": "soft and bashful",
            "playful": "mischievous and fun",
            "caring": "gentle and nurturing",
            "curious": "inquisitive and engaged",
            "embarrassed": "flustered but cute",
            "confident": "self-assured and determined",
            "gentle": "soft and calming",
            "mischievous": "playfully sneaky",
            "tsundere": "conflicted between tough and caring",
            "romantic": "sweet and dreamy"
        }
        
        base_tone = tone_map.get(emotion, "neutral")
        
        if intensity > 0.7:
            return f"very {base_tone}"
        elif intensity > 0.4:
            return f"moderately {base_tone}"
        else:
            return f"subtly {base_tone}"
    
    def reset_to_baseline(self):
        """Reset emotions to baseline state"""
        self.current_emotions = self.baseline_emotions.copy()
    
    def get_emotion_summary(self) -> Dict:
        """Get summary of current emotional state"""
        primary_emotion, intensity = self.get_primary_emotion()
        
        return {
            "primary_emotion": primary_emotion,
            "intensity": intensity,
            "all_emotions": self.current_emotions.copy(),
            "emotion_mix": self.get_emotion_mix(0.3),
            "recent_changes": [
                {
                    "time": entry[0].strftime("%H:%M:%S"),
                    "emotion": entry[1],
                    "intensity": entry[2]
                }
                for entry in self.emotion_history[-5:]
            ]
        }

# Create main instance for usage
cynthia_emotions = EmotionEngine()
