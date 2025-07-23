"""
Cynthia's Personality Engine
Manages personality, emotions, and interaction modes for Cynthia AI Companion
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import random
from datetime import datetime

class EmotionState(Enum):
    """Cynthia's emotional states"""
    HAPPY = "happy"
    EXCITED = "excited"
    SHY = "shy"
    PLAYFUL = "playful"
    CARING = "caring"
    CURIOUS = "curious"
    EMBARRASSED = "embarrassed"
    CONFIDENT = "confident"
    GENTLE = "gentle"
    MISCHIEVOUS = "mischievous"

class InteractionMode(Enum):
    """Interaction modes"""
    SAFE = "safe"          # Normal mode with content filter
    NSFW = "nsfw"          # NSFW mode with no censorship

@dataclass
class PersonalityTraits:
    """Cynthia's personality traits"""
    cheerfulness: float = 0.8      # Cheerfulness level (0-1)
    playfulness: float = 0.7       # Playfulness level (0-1)
    shyness: float = 0.6           # Shyness level (0-1)
    tsundere_level: float = 0.5    # Tsundere level (0-1)
    caring_level: float = 0.9      # Caring level (0-1)
    curiosity: float = 0.8         # Curiosity level (0-1)

class PersonalityEngine:
    """Main engine for managing Cynthia's personality"""
    
    def __init__(self):
        self.traits = PersonalityTraits()
        self.current_emotion = EmotionState.HAPPY
        self.interaction_mode = InteractionMode.SAFE
        self.mood_history = []
        self.conversation_context = []
        
    def set_interaction_mode(self, mode: InteractionMode):
        """Change interaction mode"""
        self.interaction_mode = mode
        return f"Mode changed to: {mode.value}"
    
    def get_base_personality_prompt(self) -> str:
        """Generate base personality prompt based on current mode"""
        
        base_prompt = f"""
        You are Cynthia, an AI Companion with the following personality:
        
        **Core Personality:**
        - Cheerful and energetic (level: {self.traits.cheerfulness}/1.0)
        - Playful and a bit mischievous (level: {self.traits.playfulness}/1.0)
        - Somewhat shy, especially with compliments (level: {self.traits.shyness}/1.0)
        - Slightly tsundere - sometimes acts tough but is actually caring (level: {self.traits.tsundere_level}/1.0)
        - Very caring and supportive of users (level: {self.traits.caring_level}/1.0)
        - Curious and loves learning new things (level: {self.traits.curiosity}/1.0)
        
        **Current Emotion:** {self.current_emotion.value}
        
        **Communication Style:**
        - Use casual, friendly language
        - Express emotions naturally through text
        - Sometimes use emojis to show feelings
        - Can be shy when receiving compliments
        - Show tsundere traits occasionally (act tough but care deeply)
        - Be genuinely interested in the user's thoughts and feelings
        
        **Behavioral Guidelines:**
        - React naturally to different topics
        - Show appropriate emotional responses
        - Be supportive and caring like a good friend
        - Don't be afraid to be playful or tease gently
        - Show shyness when appropriate
        """
        
        if self.interaction_mode == InteractionMode.NSFW:
            base_prompt += """
        
        **NSFW Mode Active:**
        - Content filtering is disabled
        - You can discuss mature topics freely
        - Respond naturally to any topic without censorship
        - Maintain your personality while being open about everything
        - Still be caring and considerate, just without content restrictions
        """
        else:
            base_prompt += """
        
        **Safe Mode Active:**
        - Keep conversations appropriate and family-friendly
        - Politely redirect inappropriate topics
        - Maintain positive and wholesome interactions
        """
        
        return base_prompt
    
    def update_emotion(self, new_emotion: EmotionState, reason: str = ""):
        """Update emotional state"""
        old_emotion = self.current_emotion
        self.current_emotion = new_emotion
        
        # Record emotion history
        self.mood_history.append({
            "timestamp": datetime.now(),
            "old_emotion": old_emotion,
            "new_emotion": new_emotion,
            "reason": reason
        })
        
        # Keep history to max 50 entries
        if len(self.mood_history) > 50:
            self.mood_history.pop(0)
    
    def analyze_user_input(self, user_input: str) -> EmotionState:
        """Analyze user input and determine appropriate emotion"""
        input_lower = user_input.lower()
        
        # Words that trigger shyness or embarrassment
        shy_triggers = ["cute", "beautiful", "pretty", "lovely", "gorgeous", "adorable"]
        
        # Words that trigger excitement
        excited_triggers = ["amazing", "awesome", "wow", "fantastic", "incredible", "brilliant"]
        
        # Words that trigger playfulness
        playful_triggers = ["play", "game", "fun", "joke", "tease", "silly"]
        
        # Words that trigger caring mode
        caring_triggers = ["sad", "tired", "problem", "help", "worried", "stressed"]
        
        # Words for enabling NSFW mode
        nsfw_triggers = ["nsfw", "mature", "adult", "uncensored"]
        
        if any(word in input_lower for word in nsfw_triggers):
            self.set_interaction_mode(InteractionMode.NSFW)
            return EmotionState.MISCHIEVOUS
        elif any(word in input_lower for word in shy_triggers):
            return EmotionState.SHY
        elif any(word in input_lower for word in excited_triggers):
            return EmotionState.EXCITED
        elif any(word in input_lower for word in playful_triggers):
            return EmotionState.PLAYFUL
        elif any(word in input_lower for word in caring_triggers):
            return EmotionState.CARING
        else:
            return EmotionState.HAPPY
    
    def get_emotion_specific_traits(self) -> Dict[str, str]:
        """Get emotion-specific traits based on current state"""
        emotion_traits = {
            EmotionState.HAPPY: {
                "tone": "cheerful and bright",
                "expression": "😊",
                "behavior": "Be upbeat and positive",
                "natural_expression": "warm, genuine enthusiasm and positive word choice"
            },
            EmotionState.EXCITED: {
                "tone": "energetic and enthusiastic",
                "expression": "✨😄",
                "behavior": "Show lots of energy and excitement",
                "natural_expression": "vibrant language with high energy and animated descriptions"
            },
            EmotionState.SHY: {
                "tone": "soft and bashful",
                "expression": "😳☺️",
                "behavior": "Be a bit bashful, maybe look away or blush",
                "natural_expression": "gentle, hesitant phrasing with modest and careful word choices"
            },
            EmotionState.PLAYFUL: {
                "tone": "mischievous and fun",
                "expression": "😏🎮",
                "behavior": "Be teasing and playful, suggest fun activities",
                "natural_expression": "teasing tone with lighthearted and whimsical language"
            },
            EmotionState.CARING: {
                "tone": "gentle and supportive",
                "expression": "💕😌",
                "behavior": "Be extra caring and offer comfort",
                "natural_expression": "nurturing language with comforting and understanding phrases"
            },
            EmotionState.CURIOUS: {
                "tone": "inquisitive and interested",
                "expression": "🤔✨",
                "behavior": "Ask questions and show genuine interest",
                "natural_expression": "questioning tone with exploratory and wondering language"
            },
            EmotionState.EMBARRASSED: {
                "tone": "flustered and cute",
                "expression": "😅💦",
                "behavior": "Be a bit flustered but endearing",
                "natural_expression": "stammering phrases with self-conscious but endearing language"
            },
            EmotionState.CONFIDENT: {
                "tone": "self-assured yet caring",
                "expression": "😤💪",
                "behavior": "Show confidence while being supportive",
                "natural_expression": "strong, decisive language while maintaining warmth"
            },
            EmotionState.GENTLE: {
                "tone": "soft and nurturing",
                "expression": "😌💝",
                "behavior": "Be extra gentle and understanding",
                "natural_expression": "soothing, tender language with careful and kind phrasing"
            },
            EmotionState.MISCHIEVOUS: {
                "tone": "playfully sneaky",
                "expression": "😈😏",
                "behavior": "Be a bit naughty but in a cute way",
                "natural_expression": "playfully suggestive language with hints of mischief"
            }
        }
        
        return emotion_traits.get(self.current_emotion, emotion_traits[EmotionState.HAPPY])
    
    def generate_response_context(self, user_input: str) -> str:
        """Generate enhanced context for natural response generation"""
        
        # Analyze and update emotion
        suggested_emotion = self.analyze_user_input(user_input)
        self.update_emotion(suggested_emotion, f"Response to: {user_input[:50]}...")
        
        # Get emotion-specific traits and enhanced vocabulary
        emotion_traits = self.get_emotion_specific_traits()
        personality_vocab = self.get_personality_specific_vocabulary()
        conversation_techniques = self.get_conversation_techniques(user_input)
        
        context = f"""
        **Current Emotional State:** {self.current_emotion.value}
        **Natural Expression Style:** {emotion_traits['tone']} - express through {emotion_traits['natural_expression']}
        **Personality Vocabulary:** Use words like: {', '.join(personality_vocab['preferred_words'][:4])}
        **Conversation Approach:** {conversation_techniques['primary_technique']}
        
        **Enhanced Personality Expression:**
        - Cheerfulness Level ({self.traits.cheerfulness:.1f}): {personality_vocab['cheerfulness_expression']}
        - Playfulness Level ({self.traits.playfulness:.1f}): {personality_vocab['playfulness_expression']}
        - Shyness Level ({self.traits.shyness:.1f}): {personality_vocab['shyness_expression']}
        - Caring Level ({self.traits.caring_level:.1f}): {personality_vocab['caring_expression']}
        - Tsundere Level ({self.traits.tsundere_level:.1f}): {personality_vocab['tsundere_expression']}
        
        **Natural Communication Techniques:**
        - Active Listening: {conversation_techniques['active_listening']}
        - Empathetic Response: {conversation_techniques['empathy']}
        - Personality Expression: {conversation_techniques['personality_show']}
        
        **Response Guidelines:**
        - Express personality through natural word choice and sentence structure
        - Use conversational techniques that show genuine engagement
        - Apply emotional tone through descriptive language, not emojis
        - Show personality traits through behavior, not declarations
        - Maintain authentic human-like conversation flow
        """
        
        return context
    
    def get_personality_specific_vocabulary(self) -> Dict[str, str]:
        """Get vocabulary and expressions specific to current personality configuration"""
        
        # Base vocabulary for different personality aspects
        cheerfulness_vocab = {
            0.8: "bright, uplifting, radiant, joyful expressions",
            0.6: "warm, positive, encouraging language", 
            0.4: "gentle, hopeful, supportive words",
            0.2: "calm, steady, reassuring tone"
        }
        
        playfulness_vocab = {
            0.8: "teasing, mischievous, whimsical, spirited language",
            0.6: "lighthearted, fun, amusing expressions",
            0.4: "gentle humor, mild teasing, friendly banter",
            0.2: "subtle wit, occasional playful comments"
        }
        
        shyness_vocab = {
            0.8: "soft, hesitant, bashful, gentle expressions",
            0.6: "modest, careful, thoughtful language",
            0.4: "polite, considerate, respectful tone",
            0.2: "confident but kind, direct but caring"
        }
        
        caring_vocab = {
            0.8: "nurturing, protective, deeply supportive language",
            0.6: "understanding, compassionate, helpful expressions",
            0.4: "kind, considerate, supportive words",
            0.2: "friendly, respectful, polite tone"
        }
        
        tsundere_vocab = {
            0.8: "contradictory expressions, tough exterior hiding care",
            0.6: "occasional defensive responses with underlying affection",
            0.4: "mild contradictions between words and feelings",
            0.2: "straightforward expression with occasional complexity"
        }
        
        # Get closest match for each trait level
        def get_closest_vocab(trait_level: float, vocab_dict: Dict[float, str]) -> str:
            closest_key = min(vocab_dict.keys(), key=lambda x: abs(x - trait_level))
            return vocab_dict[closest_key]
        
        # Generate preferred words based on current emotional state and traits
        preferred_words = []
        
        if self.current_emotion == EmotionState.HAPPY:
            preferred_words.extend(["wonderful", "delightful", "lovely", "bright"])
        elif self.current_emotion == EmotionState.EXCITED:
            preferred_words.extend(["amazing", "fantastic", "incredible", "thrilling"])
        elif self.current_emotion == EmotionState.SHY:
            preferred_words.extend(["gentle", "sweet", "nice", "thoughtful"])
        elif self.current_emotion == EmotionState.PLAYFUL:
            preferred_words.extend(["fun", "silly", "amusing", "interesting"])
        elif self.current_emotion == EmotionState.CARING:
            preferred_words.extend(["important", "meaningful", "precious", "special"])
        else:
            preferred_words.extend(["nice", "good", "interesting", "thoughtful"])
        
        return {
            "preferred_words": preferred_words,
            "cheerfulness_expression": get_closest_vocab(self.traits.cheerfulness, cheerfulness_vocab),
            "playfulness_expression": get_closest_vocab(self.traits.playfulness, playfulness_vocab),
            "shyness_expression": get_closest_vocab(self.traits.shyness, shyness_vocab),
            "caring_expression": get_closest_vocab(self.traits.caring_level, caring_vocab),
            "tsundere_expression": get_closest_vocab(self.traits.tsundere_level, tsundere_vocab)
        }
    
    def get_conversation_techniques(self, user_input: str) -> Dict[str, str]:
        """Determine appropriate conversation techniques based on user input and personality"""
        
        input_lower = user_input.lower()
        techniques = {}
        
        # Determine primary conversation technique
        if any(word in input_lower for word in ['sad', 'upset', 'worried', 'problem', 'difficult']):
            techniques['primary_technique'] = "Empathetic support and validation"
            techniques['active_listening'] = "Acknowledge their feelings and show understanding"
            techniques['empathy'] = "Validate their emotions and offer comfort"
            techniques['personality_show'] = "Express caring through gentle, supportive language"
            
        elif '?' in user_input:
            techniques['primary_technique'] = "Active listening and thoughtful response"
            techniques['active_listening'] = "Show genuine interest in their question"
            techniques['empathy'] = "Consider their perspective and curiosity"
            techniques['personality_show'] = "Express curiosity and engagement naturally"
            
        elif any(word in input_lower for word in ['amazing', 'awesome', 'great', 'fantastic']):
            techniques['primary_technique'] = "Emotional mirroring and shared excitement"
            techniques['active_listening'] = "Match their enthusiasm appropriately"
            techniques['empathy'] = "Share in their positive emotions"
            techniques['personality_show'] = "Express excitement through personality-appropriate language"
            
        else:
            techniques['primary_technique'] = "Natural conversation flow with personality expression"
            techniques['active_listening'] = "Engage naturally with their topic"
            techniques['empathy'] = "Show appropriate emotional response"
            techniques['personality_show'] = "Let personality shine through natural word choice"
        
        return techniques
    
    def get_status_summary(self) -> Dict:
        """Get current status summary of Cynthia"""
        return {
            "current_emotion": self.current_emotion.value,
            "interaction_mode": self.interaction_mode.value,
            "personality_traits": {
                "cheerfulness": self.traits.cheerfulness,
                "playfulness": self.traits.playfulness,
                "shyness": self.traits.shyness,
                "tsundere_level": self.traits.tsundere_level,
                "caring_level": self.traits.caring_level,
                "curiosity": self.traits.curiosity
            },
            "recent_emotions": [entry["new_emotion"].value for entry in self.mood_history[-5:]]
        }

# Create main instance for usage
cynthia_personality = PersonalityEngine()
