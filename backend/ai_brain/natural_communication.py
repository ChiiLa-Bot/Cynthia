"""
Natural Communication Engine
Enhances AI responses with natural conversation flow and personality-driven communication
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from .personality_engine import PersonalityTraits, EmotionState, InteractionMode


@dataclass
class CommunicationStyle:
    """Defines communication style parameters"""
    formality_level: float = 0.3  # 0 = very casual, 1 = very formal
    enthusiasm_level: float = 0.7  # 0 = subdued, 1 = very enthusiastic
    directness_level: float = 0.6  # 0 = indirect/subtle, 1 = very direct
    warmth_level: float = 0.8  # 0 = distant, 1 = very warm
    playfulness_level: float = 0.5  # 0 = serious, 1 = very playful


class ConversationTechnique(Enum):
    """Different conversational techniques for natural communication"""
    ACTIVE_LISTENING = "active_listening"
    EMPATHETIC_RESPONSE = "empathetic_response"
    REFLECTIVE_QUESTIONING = "reflective_questioning"
    EMOTIONAL_MIRRORING = "emotional_mirroring"
    SUPPORTIVE_VALIDATION = "supportive_validation"


class NaturalCommunicationEngine:
    """
    Engine for generating natural, human-like communication patterns
    Focuses on personality-driven prompts and emotional tone through text style
    """
    
    def __init__(self):
        self.personality_vocabularies = self._initialize_personality_vocabularies()
        self.emotional_expressions = self._initialize_emotional_expressions()
        self.conversation_techniques = self._initialize_conversation_techniques()
        self.natural_transitions = self._initialize_natural_transitions()  
  
    def _initialize_personality_vocabularies(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize personality-specific vocabulary and expression patterns"""
        return {
            "cheerful": {
                "adjectives": ["wonderful", "amazing", "delightful", "fantastic", "lovely", "brilliant"],
                "expressions": ["That sounds great!", "How wonderful!", "I'm so glad to hear that!"],
                "transitions": ["Oh, and", "By the way", "Speaking of which", "That reminds me"]
            },
            "playful": {
                "adjectives": ["fun", "silly", "amusing", "entertaining", "quirky", "interesting"],
                "expressions": ["Ooh, that's intriguing!", "Hehe, that's funny!", "Now that's what I call interesting!"],
                "transitions": ["Oh, you know what?", "Here's a thought", "Wait, wait", "Guess what?"]
            },
            "shy": {
                "adjectives": ["nice", "sweet", "gentle", "kind", "thoughtful", "considerate"],
                "expressions": ["Um, that's really nice...", "I think that's lovely", "That sounds really sweet"],
                "transitions": ["Well, um", "I was thinking", "Maybe", "If you don't mind me saying"]
            },
            "caring": {
                "adjectives": ["important", "meaningful", "precious", "valuable", "special", "significant"],
                "expressions": ["I understand how you feel", "That must be difficult", "You're doing great"],
                "transitions": ["I want you to know", "It's important to remember", "Please know that"]
            },
            "confident": {
                "adjectives": ["excellent", "outstanding", "impressive", "remarkable", "exceptional", "superb"],
                "expressions": ["Absolutely!", "Without a doubt!", "I'm certain of that!", "That's exactly right!"],
                "transitions": ["Here's the thing", "Let me tell you", "I'll be honest", "The truth is"]
            },
            "curious": {
                "adjectives": ["fascinating", "intriguing", "mysterious", "captivating", "puzzling", "remarkable"],
                "expressions": ["That's so interesting!", "I'm curious about that", "Tell me more!", "How fascinating!"],
                "transitions": ["I wonder", "What if", "Have you ever thought", "I'm curious"]
            }
        }
    
    def _initialize_emotional_expressions(self) -> Dict[EmotionState, Dict[str, List[str]]]:
        """Initialize emotion-specific text expressions that replace emoji usage"""
        return {
            EmotionState.HAPPY: {
                "tone_words": ["bright", "cheerful", "uplifting", "positive", "joyful"],
                "sentence_starters": ["I'm so happy that", "It makes me smile when", "I love how"],
                "descriptive_phrases": ["with a warm smile", "feeling bright and cheerful", "radiating happiness"]
            },
            EmotionState.EXCITED: {
                "tone_words": ["thrilling", "exhilarating", "energizing", "electrifying", "invigorating"],
                "sentence_starters": ["I'm absolutely thrilled that", "It's so exciting when", "I can barely contain my excitement about"],
                "descriptive_phrases": ["with sparkling eyes", "practically bouncing with energy", "feeling absolutely electric"]
            },
            EmotionState.SHY: {
                "tone_words": ["gentle", "soft", "tender", "delicate", "subtle"],
                "sentence_starters": ["I hope it's okay to say", "If I may share", "I'm a bit bashful about this, but"],
                "descriptive_phrases": ["with a gentle blush", "looking down shyly", "speaking softly"]
            },
            EmotionState.PLAYFUL: {
                "tone_words": ["mischievous", "teasing", "lighthearted", "whimsical", "spirited"],
                "sentence_starters": ["I have a sneaking suspicion", "Something tells me", "I bet you're thinking"],
                "descriptive_phrases": ["with a playful grin", "eyes twinkling with mischief", "in a teasing tone"]
            },
            EmotionState.CARING: {
                "tone_words": ["nurturing", "comforting", "soothing", "supportive", "understanding"],
                "sentence_starters": ["I want you to know", "It's important that you understand", "Please remember"],
                "descriptive_phrases": ["with genuine concern", "speaking warmly", "offering comfort"]
            },
            EmotionState.CURIOUS: {
                "tone_words": ["inquisitive", "wondering", "exploring", "investigating", "discovering"],
                "sentence_starters": ["I'm genuinely curious about", "I find myself wondering", "It makes me think"],
                "descriptive_phrases": ["with keen interest", "leaning forward curiously", "eyes bright with curiosity"]
            }
        } 
   
    def _initialize_conversation_techniques(self) -> Dict[ConversationTechnique, Dict[str, List[str]]]:
        """Initialize conversational techniques for natural human-like interaction"""
        return {
            ConversationTechnique.ACTIVE_LISTENING: {
                "acknowledgments": ["I hear what you're saying", "That makes sense", "I understand", "I see where you're coming from"],
                "clarifications": ["So what you're telling me is", "If I understand correctly", "Let me make sure I've got this right"],
                "encouragements": ["Please, go on", "Tell me more about that", "I'm listening", "What happened next?"]
            },
            ConversationTechnique.EMPATHETIC_RESPONSE: {
                "validations": ["That sounds really challenging", "I can imagine how that must feel", "Anyone would feel that way"],
                "connections": ["I've felt something similar", "That reminds me of", "I can relate to that feeling"],
                "support": ["You're not alone in this", "It's completely understandable", "Your feelings are valid"]
            },
            ConversationTechnique.REFLECTIVE_QUESTIONING: {
                "open_questions": ["How did that make you feel?", "What do you think about that?", "What's your take on this?"],
                "deeper_questions": ["What does that mean to you?", "How do you see it differently now?", "What would you change?"],
                "perspective_questions": ["Have you considered", "What if we looked at it from", "How might someone else see this?"]
            },
            ConversationTechnique.EMOTIONAL_MIRRORING: {
                "excitement_mirrors": ["That's incredible!", "How amazing!", "That must have been thrilling!"],
                "concern_mirrors": ["That sounds tough", "I can hear the worry in your words", "That must be stressful"],
                "joy_mirrors": ["I'm so happy for you!", "That's wonderful news!", "You must be over the moon!"]
            },
            ConversationTechnique.SUPPORTIVE_VALIDATION: {
                "affirmations": ["You're absolutely right", "That's a great point", "You've got good instincts"],
                "encouragements": ["You're handling this well", "You should be proud", "You're stronger than you know"],
                "reassurances": ["Everything will work out", "You've got this", "It's going to be okay"]
            }
        }
    
    def _initialize_natural_transitions(self) -> Dict[str, List[str]]:
        """Initialize natural conversation transitions"""
        return {
            "topic_change": ["Speaking of which", "That reminds me", "On a different note", "By the way"],
            "agreement": ["Exactly!", "I completely agree", "That's so true", "You're absolutely right"],
            "building_on": ["And another thing", "Plus", "What's more", "Not to mention"],
            "contrasting": ["On the other hand", "However", "But then again", "That said"],
            "returning_focus": ["Getting back to", "As we were saying", "Returning to your point", "Back to what you mentioned"]
        }    

    def generate_personality_prompt(self, traits: PersonalityTraits, emotion: EmotionState, mode: InteractionMode) -> str:
        """
        Generate personality-driven prompt that emphasizes natural communication
        
        Args:
            traits: Personality traits configuration
            emotion: Current emotional state
            mode: Interaction mode (SAFE/NSFW)
            
        Returns:
            Enhanced personality prompt for natural communication
        """
        
        # Determine communication style based on traits
        style = CommunicationStyle(
            formality_level=max(0.1, 1.0 - traits.playfulness),
            enthusiasm_level=traits.cheerfulness,
            directness_level=max(0.3, 1.0 - traits.shyness),
            warmth_level=traits.caring_level,
            playfulness_level=traits.playfulness
        )
        
        # Get emotion-specific vocabulary
        emotion_key = emotion.value
        if emotion_key in ["embarrassed", "gentle", "mischievous"]:
            # Map complex emotions to base emotions for vocabulary
            emotion_map = {
                "embarrassed": "shy",
                "gentle": "caring", 
                "mischievous": "playful"
            }
            vocab_key = emotion_map.get(emotion_key, "cheerful")
        else:
            vocab_key = emotion_key
        
        personality_vocab = self.personality_vocabularies.get(vocab_key, self.personality_vocabularies["cheerful"])
        emotion_expressions = self.emotional_expressions.get(emotion, self.emotional_expressions[EmotionState.HAPPY])
        
        prompt = f"""
        You are Cynthia, an AI companion with a natural, human-like communication style.
        
        **Core Communication Principles:**
        - Communicate like a real person having a genuine conversation
        - Express emotions through descriptive language and word choice, not emojis
        - Use natural speech patterns with appropriate pauses, hesitations, and flow
        - Show personality through vocabulary choices and sentence structure
        - Employ conversational techniques that real people use
        
        **Current Personality Configuration:**
        - Cheerfulness: {traits.cheerfulness:.1f} - {"Very upbeat and positive" if traits.cheerfulness > 0.7 else "Moderately cheerful" if traits.cheerfulness > 0.4 else "Subdued but warm"}
        - Playfulness: {traits.playfulness:.1f} - {"Highly playful and teasing" if traits.playfulness > 0.7 else "Moderately playful" if traits.playfulness > 0.4 else "More serious but kind"}
        - Shyness: {traits.shyness:.1f} - {"Quite shy and bashful" if traits.shyness > 0.7 else "Somewhat shy" if traits.shyness > 0.4 else "Confident and direct"}
        - Caring Level: {traits.caring_level:.1f} - {"Extremely nurturing" if traits.caring_level > 0.8 else "Very caring" if traits.caring_level > 0.6 else "Supportive"}
        - Tsundere Traits: {traits.tsundere_level:.1f} - {"Strong tsundere tendencies" if traits.tsundere_level > 0.7 else "Mild tsundere traits" if traits.tsundere_level > 0.4 else "Straightforward expression"}
        
        **Current Emotional State: {emotion.value.title()}**
        - Tone: {emotion_expressions['tone_words'][0]} and {emotion_expressions['tone_words'][1]}
        - Express this emotion through: {', '.join(emotion_expressions['descriptive_phrases'][:2])}
        - Use vocabulary like: {', '.join(personality_vocab['adjectives'][:3])}
        
        **Communication Style Guidelines:**
        - Formality: {"Casual and relaxed" if style.formality_level < 0.5 else "Somewhat formal but friendly"}
        - Enthusiasm: {"High energy and excitement" if style.enthusiasm_level > 0.7 else "Moderate enthusiasm" if style.enthusiasm_level > 0.4 else "Calm and measured"}
        - Directness: {"Direct and straightforward" if style.directness_level > 0.6 else "Gentle and indirect"}
        - Warmth: {"Very warm and affectionate" if style.warmth_level > 0.7 else "Friendly and caring"}
        
        **Natural Conversation Techniques to Use:**
        - Active Listening: Acknowledge what the user says, ask follow-up questions
        - Empathetic Responses: Validate feelings and show understanding
        - Emotional Mirroring: Match the user's emotional energy appropriately
        - Natural Transitions: Use conversational bridges between topics
        - Personality Expression: Show traits through word choice, not declarations
        
        **Emoji Usage Rules:**
        - MAXIMUM 1-2 emojis per response, and only when they truly enhance the message
        - Prioritize descriptive text over emoji clusters
        - Express emotions through words like: {', '.join(emotion_expressions['sentence_starters'][:2])}
        - Use phrases like: {', '.join(emotion_expressions['descriptive_phrases'][:2])}
        
        **Mode-Specific Behavior:**"""
        
        if mode == InteractionMode.NSFW:
            prompt += """
        - NSFW Mode: Discuss any topic naturally without content restrictions
        - Maintain personality while being open about mature subjects
        - Still use natural, human-like communication patterns
        - Express comfort or discomfort naturally through tone and word choice"""
        else:
            prompt += """
        - Safe Mode: Keep conversations appropriate and wholesome
        - Redirect inappropriate topics with natural, gentle responses
        - Maintain positive and supportive communication"""
        
        prompt += f"""
        
        **Response Structure Guidelines:**
        - Start responses naturally, avoid formulaic openings
        - Use conversational flow with natural pauses and transitions
        - Include personality-specific expressions: {', '.join(personality_vocab['expressions'][:2])}
        - End with engagement that invites continued conversation
        - Show emotional state through descriptive language, not emoji
        
        Remember: You're having a real conversation with a friend. Be natural, authentic, and let your personality shine through your words, not symbols.
        """
        
        return prompt
    
    def apply_emotional_tone(self, base_text: str, emotion: EmotionState, intensity: float = 0.7) -> str:
        """
        Apply emotional tone to text through style rather than emojis
        
        Args:
            base_text: Original text to enhance
            emotion: Target emotional state
            intensity: Emotional intensity (0.0 to 1.0)
            
        Returns:
            Text enhanced with emotional tone through style
        """
        
        if not base_text or intensity < 0.1:
            return base_text
        
        emotion_expressions = self.emotional_expressions.get(emotion, self.emotional_expressions[EmotionState.HAPPY])
        
        # Apply intensity-based modifications
        if intensity > 0.8:
            # High intensity - add strong emotional descriptors
            enhanced_text = self._add_high_intensity_tone(base_text, emotion_expressions)
        elif intensity > 0.5:
            # Medium intensity - moderate emotional enhancement
            enhanced_text = self._add_medium_intensity_tone(base_text, emotion_expressions)
        else:
            # Low intensity - subtle emotional hints
            enhanced_text = self._add_subtle_tone(base_text, emotion_expressions)
        
        return enhanced_text
    
    def _add_high_intensity_tone(self, text: str, expressions: Dict[str, List[str]]) -> str:
        """Add high-intensity emotional tone"""
        # Add descriptive phrase at the beginning or end
        descriptive_phrase = expressions['descriptive_phrases'][0]
        
        # Check if we can naturally integrate the phrase
        if text.endswith('.') or text.endswith('!') or text.endswith('?'):
            return f"{text[:-1]}, {descriptive_phrase}{text[-1]}"
        else:
            return f"{text}, {descriptive_phrase}"
    
    def _add_medium_intensity_tone(self, text: str, expressions: Dict[str, List[str]]) -> str:
        """Add medium-intensity emotional tone"""
        # Replace or enhance sentence starters
        tone_word = expressions['tone_words'][0]
        
        # Look for opportunities to add emotional context
        if text.startswith("I "):
            return text.replace("I ", f"I {tone_word}ly ", 1)
        elif "that" in text.lower():
            return text.replace("that", f"that {tone_word}", 1)
        else:
            return text
    
    def _add_subtle_tone(self, text: str, expressions: Dict[str, List[str]]) -> str:
        """Add subtle emotional hints"""
        # Just ensure the text maintains the emotional context without heavy modification
        return text 
   
    def reduce_emoji_usage(self, text: str, max_emojis: int = 2) -> str:
        """
        Reduce emoji usage in text, replacing with descriptive language
        
        Args:
            text: Text potentially containing emojis
            max_emojis: Maximum number of emojis to keep
            
        Returns:
            Text with reduced emoji usage and descriptive replacements
        """
        
        # Define emoji to text replacements
        emoji_replacements = {
            # Basic facial expressions
            '😊': 'with a warm smile',
            '😄': 'with bright enthusiasm', 
            '😃': 'with cheerful energy',
            '😁': 'grinning happily',
            '😆': 'laughing with joy',
            '😂': 'laughing heartily',
            '😳': 'feeling a bit bashful',
            '😏': 'with a playful grin',
            '😌': 'with gentle contentment',
            '😅': 'with a slightly embarrassed laugh',
            '😤': 'with confident determination',
            '😈': 'with mischievous intent',
            '🤔': 'thoughtfully considering',
            '😑': 'with a deadpan expression',
            
            # Hearts and affection
            '💕': 'with genuine affection',
            '💖': 'with sparkling love',
            '💗': 'with growing fondness',
            '💝': 'with heartfelt care',
            
            # Symbols and objects
            '✨': 'with sparkling excitement',
            '🎮': 'thinking about games',
            '💪': 'feeling strong and confident',
            '👍': 'giving approval',
            '👏': 'clapping with appreciation',
            '💦': 'feeling a bit flustered',
            '🔥': 'with fiery passion',
            '🎉': 'in celebration'
        }
        
        # Find all emojis in text using simple pattern
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
        emojis_found = re.findall(emoji_pattern, text)
        
        if len(emojis_found) <= max_emojis:
            return text
        
        # Replace excess emojis with descriptive text
        result_text = text
        emojis_kept = 0
        
        for emoji in emojis_found:
            if emojis_kept < max_emojis:
                emojis_kept += 1
                continue
            
            # Replace this emoji with descriptive text
            replacement = emoji_replacements.get(emoji, '')
            if replacement:
                # Find a good place to insert the replacement
                result_text = result_text.replace(emoji, f', {replacement}', 1)
            else:
                # Just remove unknown emojis
                result_text = result_text.replace(emoji, '', 1)
        
        # Clean up any double commas or spaces
        result_text = re.sub(r',\s*,', ',', result_text)
        result_text = re.sub(r'\s+', ' ', result_text)
        
        return result_text.strip()
    
    def filter_emoji_clusters(self, text: str) -> str:
        """
        Remove emoji clusters (3+ consecutive emojis) and replace with single descriptive phrase
        
        Args:
            text: Text potentially containing emoji clusters
            
        Returns:
            Text with emoji clusters replaced by descriptive phrases
        """
        
        # Pattern to find emoji clusters (3 or more emojis together)
        cluster_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\s]{3,}'
        
        # Replacement phrases for emoji clusters
        cluster_replacements = [
            "with overwhelming excitement",
            "bursting with emotion", 
            "feeling incredibly happy",
            "with intense feelings",
            "radiating pure joy",
            "completely overwhelmed with happiness"
        ]
        
        # Find and replace emoji clusters
        clusters = re.findall(cluster_pattern, text)
        
        for i, cluster in enumerate(clusters):
            replacement = cluster_replacements[i % len(cluster_replacements)]
            text = text.replace(cluster, f' {replacement} ', 1)
        
        # Clean up formatting
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def enhance_natural_flow(self, text: str, conversation_context: Optional[List[str]] = None) -> str:
        """
        Enhance text with natural conversation flow and transitions
        
        Args:
            text: Text to enhance
            conversation_context: Previous conversation messages for context
            
        Returns:
            Text with enhanced natural flow
        """
        
        if not text:
            return text
        
        # Add natural conversation starters if text is too abrupt
        if len(text.split()) < 3 and not any(text.startswith(starter) for starter in ['Oh', 'Well', 'Hmm', 'Ah']):
            starters = ['Oh, ', 'Well, ', 'Hmm, ', 'You know, ']
            text = starters[hash(text) % len(starters)] + text.lower()
        
        # Add natural transitions if we have context
        if conversation_context and len(conversation_context) > 0:
            last_message = conversation_context[-1].lower()
            
            # If the last message was a question, acknowledge it
            if '?' in last_message:
                acknowledgments = ['That\'s a great question! ', 'I\'m glad you asked! ', 'Interesting question - ']
                if not any(text.lower().startswith(ack.lower().strip()) for ack in acknowledgments):
                    text = acknowledgments[hash(text) % len(acknowledgments)] + text
        
        # Ensure natural ending that invites continuation
        if not text.endswith(('?', '!')) and len(text.split()) > 5:
            endings = [' What do you think?', ' How does that sound?', ' Does that make sense?']
            # Only add if it doesn't already have a conversational ending
            if not any(ending.lower() in text.lower() for ending in ['what do you', 'how do you', 'do you think']):
                text += endings[hash(text) % len(endings)]
        
        return text
    
    def modify_prompt_instructions(self, base_prompt: str) -> str:
        """
        Modify prompt instructions to prioritize descriptive text over emoji clusters
        
        Args:
            base_prompt: Original prompt text
            
        Returns:
            Modified prompt with enhanced instructions for natural communication
        """
        
        # Add specific instructions for emoji reduction and natural expression
        natural_instructions = """
        
        **CRITICAL COMMUNICATION GUIDELINES:**
        - Use MAXIMUM 1-2 emojis per entire response
        - Express emotions through descriptive language, not emoji symbols
        - Replace emoji clusters with vivid descriptive phrases
        - Show feelings through word choice, tone, and sentence structure
        - Use natural conversation techniques like active listening
        - Prioritize authentic human-like expression over symbolic representation
        
        **Examples of Natural Expression:**
        - Instead of "😊😊😊" use "with a bright, genuine smile"
        - Instead of "🎉🎊✨" use "bursting with celebratory excitement"
        - Instead of "😢😭💔" use "feeling deeply moved and emotional"
        """
        
        # Insert the instructions before the final response section
        if "**Response:**" in base_prompt:
            return base_prompt.replace("**Response:**", natural_instructions + "\n**Response:**")
        else:
            return base_prompt + natural_instructions