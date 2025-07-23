"""
Animation Data Provider for 3D Integration
Generates facial expressions, lip sync data, and animation sequences from emotion states and text
"""

import re
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .animation_models import (
    FacialExpressionData, PhonemeData, AnimationKeyframe, AnimationSequence,
    MouthShape, TransitionType, create_neutral_expression
)

@dataclass
class EmotionMapping:
    """Mapping between emotion states and facial muscle activation"""
    eyebrow_raise: float = 0.0
    eyebrow_furrow: float = 0.0
    eye_openness: float = 1.0
    eye_squint: float = 0.0
    smile: float = 0.0
    frown: float = 0.0
    cheek_raise: float = 0.0
    jaw_drop: float = 0.0
    mouth_openness: float = 0.0

class AnimationDataProvider:
    """
    Provider class for generating 3D animation data from emotion states and text
    """
    
    def __init__(self):
        # Emotion to facial expression mappings
        self.emotion_mappings = self._init_emotion_mappings()
        
        # Phoneme to mouth shape mappings
        self.phoneme_mappings = self._init_phoneme_mappings()
        
        # Text to phoneme conversion (simplified)
        self.text_to_phoneme_rules = self._init_phoneme_rules()
        
        # Animation timing settings
        self.default_transition_time = 0.2
        self.default_hold_time = 0.3
        self.speech_rate = 4.0  # characters per second (approximate)
    
    def _init_emotion_mappings(self) -> Dict[str, EmotionMapping]:
        """Initialize emotion to facial expression mappings"""
        return {
            "happy": EmotionMapping(
                smile=0.8,
                cheek_raise=0.6,
                eye_squint=0.3,
                eye_openness=0.9
            ),
            "excited": EmotionMapping(
                eyebrow_raise=0.7,
                smile=0.9,
                cheek_raise=0.8,
                eye_openness=1.0,
                mouth_openness=0.3
            ),
            "shy": EmotionMapping(
                smile=0.4,
                cheek_raise=0.7,
                eye_openness=0.7,
                eyebrow_raise=0.2
            ),
            "playful": EmotionMapping(
                smile=0.6,
                eye_squint=0.4,
                eyebrow_raise=0.3,
                cheek_raise=0.5
            ),
            "caring": EmotionMapping(
                smile=0.5,
                eye_openness=0.8,
                eyebrow_raise=0.2,
                cheek_raise=0.3
            ),
            "curious": EmotionMapping(
                eyebrow_raise=0.6,
                eye_openness=1.0,
                mouth_openness=0.2
            ),
            "embarrassed": EmotionMapping(
                smile=0.3,
                cheek_raise=0.8,
                eye_openness=0.6,
                eyebrow_raise=0.4
            ),
            "confident": EmotionMapping(
                smile=0.6,
                eye_openness=0.9,
                cheek_raise=0.4,
                eyebrow_raise=0.1
            ),
            "gentle": EmotionMapping(
                smile=0.4,
                eye_openness=0.8,
                cheek_raise=0.3
            ),
            "mischievous": EmotionMapping(
                smile=0.7,
                eye_squint=0.5,
                eyebrow_raise=0.3,
                cheek_raise=0.6
            ),
            "tsundere": EmotionMapping(
                frown=0.3,
                eyebrow_furrow=0.4,
                eye_squint=0.2,
                cheek_raise=0.2  # Hidden blush
            ),
            "romantic": EmotionMapping(
                smile=0.5,
                eye_openness=0.7,
                cheek_raise=0.6,
                eyebrow_raise=0.1
            ),
            "sad": EmotionMapping(
                frown=0.7,
                eyebrow_furrow=0.5,
                eye_openness=0.6
            ),
            "angry": EmotionMapping(
                frown=0.8,
                eyebrow_furrow=0.9,
                eye_squint=0.6,
                mouth_openness=0.2
            ),
            "surprised": EmotionMapping(
                eyebrow_raise=0.9,
                eye_openness=1.0,
                mouth_openness=0.6,
                jaw_drop=0.4
            ),
            "neutral": EmotionMapping()
        }
    
    def _init_phoneme_mappings(self) -> Dict[str, MouthShape]:
        """Initialize phoneme to mouth shape mappings"""
        return {
            # Vowels
            'AH': MouthShape.A,     # father, hot
            'AA': MouthShape.A,     # cat, bat
            'AE': MouthShape.A,     # cat, bat
            'EH': MouthShape.E,     # bet, end
            'IH': MouthShape.I,     # bit, sit
            'OH': MouthShape.O,     # hot, lot
            'UH': MouthShape.U,     # book, put
            'AY': MouthShape.AI,    # bite, my
            'EY': MouthShape.EI,    # bait, say
            'OW': MouthShape.OU,    # boat, go
            
            # Consonants
            'M': MouthShape.M_B_P,   # consonant m
            'B': MouthShape.M_B_P,   # consonant b
            'P': MouthShape.M_B_P,   # consonant p
            'F': MouthShape.F_V,     # consonant f
            'V': MouthShape.F_V,     # consonant v
            'TH': MouthShape.TH,     # consonant th
            'T': MouthShape.T_D_N_L, # consonant t
            'D': MouthShape.T_D_N_L, # consonant d
            'N': MouthShape.T_D_N_L, # consonant n
            'L': MouthShape.T_D_N_L, # consonant l
            'K': MouthShape.K_G,     # consonant k
            'G': MouthShape.K_G,     # consonant g
            'CH': MouthShape.CH_SH,  # consonant ch
            'SH': MouthShape.CH_SH,  # consonant sh
            'R': MouthShape.R,       # consonant r
            
            # Special cases
            'SIL': MouthShape.CLOSED, # silence
            '': MouthShape.NEUTRAL    # default
        }
    
    def _init_phoneme_rules(self) -> Dict[str, str]:
        """Initialize simplified text to phoneme conversion rules"""
        return {
            # Vowels
            'a': 'AH', 'e': 'EH', 'i': 'IH', 'o': 'OH', 'u': 'UH',
            'ai': 'AY', 'ay': 'AY', 'ei': 'EY', 'ey': 'EY',
            'ow': 'OW', 'ou': 'OW',
            
            # Consonants
            'm': 'M', 'b': 'B', 'p': 'P',
            'f': 'F', 'v': 'V',
            'th': 'TH',
            't': 'T', 'd': 'D', 'n': 'N', 'l': 'L',
            'k': 'K', 'g': 'G', 'c': 'K',
            'ch': 'CH', 'sh': 'SH',
            'r': 'R',
            's': 'SH', 'z': 'SH',
            'j': 'CH', 'y': 'EH',
            'w': 'UH', 'h': 'AH'
        }
    
    def generate_facial_expression_data(self, emotion_mix: Dict[str, float]) -> FacialExpressionData:
        """
        Generate facial expression data from emotion mix
        
        Args:
            emotion_mix: Dictionary of emotion names and their intensities (0.0-1.0)
            
        Returns:
            FacialExpressionData object with calculated muscle activations
        """
        # Start with neutral expression
        expression = create_neutral_expression()
        
        # Blend emotions based on their intensities
        total_intensity = sum(emotion_mix.values())
        if total_intensity == 0:
            return expression
        
        # Normalize intensities
        normalized_mix = {emotion: intensity / total_intensity 
                         for emotion, intensity in emotion_mix.items()}
        
        # Accumulate facial muscle activations
        eyebrow_raise_left = 0.0
        eyebrow_raise_right = 0.0
        eyebrow_furrow = 0.0
        eye_openness_left = 1.0
        eye_openness_right = 1.0
        eye_squint_left = 0.0
        eye_squint_right = 0.0
        smile_left = 0.0
        smile_right = 0.0
        mouth_frown = 0.0
        cheek_raise_left = 0.0
        cheek_raise_right = 0.0
        jaw_drop = 0.0
        mouth_openness = 0.0
        
        for emotion, weight in normalized_mix.items():
            if emotion in self.emotion_mappings:
                mapping = self.emotion_mappings[emotion]
                
                eyebrow_raise_left += mapping.eyebrow_raise * weight
                eyebrow_raise_right += mapping.eyebrow_raise * weight
                eyebrow_furrow += mapping.eyebrow_furrow * weight
                eye_openness_left *= (1.0 - (1.0 - mapping.eye_openness) * weight)
                eye_openness_right *= (1.0 - (1.0 - mapping.eye_openness) * weight)
                eye_squint_left += mapping.eye_squint * weight
                eye_squint_right += mapping.eye_squint * weight
                smile_left += mapping.smile * weight
                smile_right += mapping.smile * weight
                mouth_frown += mapping.frown * weight
                cheek_raise_left += mapping.cheek_raise * weight
                cheek_raise_right += mapping.cheek_raise * weight
                jaw_drop += mapping.jaw_drop * weight
                mouth_openness += mapping.mouth_openness * weight
        
        # Apply calculated values
        expression.eyebrow_raise_left = min(eyebrow_raise_left, 1.0)
        expression.eyebrow_raise_right = min(eyebrow_raise_right, 1.0)
        expression.eyebrow_furrow = min(eyebrow_furrow, 1.0)
        expression.eye_openness_left = max(min(eye_openness_left, 1.0), 0.0)
        expression.eye_openness_right = max(min(eye_openness_right, 1.0), 0.0)
        expression.eye_squint_left = min(eye_squint_left, 1.0)
        expression.eye_squint_right = min(eye_squint_right, 1.0)
        expression.smile_left = min(smile_left, 1.0)
        expression.smile_right = min(smile_right, 1.0)
        expression.mouth_frown = min(mouth_frown, 1.0)
        expression.cheek_raise_left = min(cheek_raise_left, 1.0)
        expression.cheek_raise_right = min(cheek_raise_right, 1.0)
        expression.jaw_drop = min(jaw_drop, 1.0)
        expression.mouth_openness = min(mouth_openness, 1.0)
        
        # Calculate overall expression intensity
        expression.expression_intensity = min(total_intensity, 1.0)
        
        return expression
    
    def create_lip_sync_data(self, text: str) -> List[PhonemeData]:
        """
        Generate lip sync data from text using phoneme analysis
        
        Args:
            text: The text to generate lip sync data for
            
        Returns:
            List of PhonemeData objects with timing and mouth shapes
        """
        # Clean text
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        phoneme_data = []
        current_time = 0.0
        
        for word in words:
            # Convert word to phonemes (simplified approach)
            phonemes = self._text_to_phonemes(word)
            
            for phoneme in phonemes:
                # Calculate duration based on phoneme type
                duration = self._calculate_phoneme_duration(phoneme)
                
                # Get mouth shape
                mouth_shape = self.phoneme_mappings.get(phoneme, MouthShape.NEUTRAL)
                
                # Create phoneme data
                phoneme_obj = PhonemeData(
                    phoneme=phoneme,
                    start_time=current_time,
                    duration=duration,
                    mouth_shape=mouth_shape,
                    intensity=1.0,
                    transition_in=0.05,
                    transition_out=0.05
                )
                
                phoneme_data.append(phoneme_obj)
                current_time += duration
            
            # Add small pause between words
            current_time += 0.1
        
        return phoneme_data
    
    def _text_to_phonemes(self, word: str) -> List[str]:
        """
        Convert a word to phonemes (simplified approach)
        
        Args:
            word: The word to convert
            
        Returns:
            List of phoneme strings
        """
        phonemes = []
        i = 0
        
        while i < len(word):
            # Check for two-character combinations first
            if i < len(word) - 1:
                two_char = word[i:i+2]
                if two_char in self.text_to_phoneme_rules:
                    phonemes.append(self.text_to_phoneme_rules[two_char])
                    i += 2
                    continue
            
            # Check single character
            char = word[i]
            if char in self.text_to_phoneme_rules:
                phonemes.append(self.text_to_phoneme_rules[char])
            else:
                # Default to 'AH' for unknown characters
                phonemes.append('AH')
            
            i += 1
        
        return phonemes
    
    def _calculate_phoneme_duration(self, phoneme: str) -> float:
        """
        Calculate duration for a phoneme
        
        Args:
            phoneme: The phoneme string
            
        Returns:
            Duration in seconds
        """
        # Vowels are typically longer than consonants
        vowel_phonemes = ['AH', 'AA', 'AE', 'EH', 'IH', 'OH', 'UH', 'AY', 'EY', 'OW']
        
        if phoneme in vowel_phonemes:
            return 0.15  # Vowels last longer
        else:
            return 0.08  # Consonants are shorter
    
    def calculate_animation_timing(self, text: str, emotion_intensity: float = 0.5) -> Dict[str, float]:
        """
        Calculate animation timing data for smooth transitions
        
        Args:
            text: The text being spoken
            emotion_intensity: Intensity of the emotion (affects timing)
            
        Returns:
            Dictionary with timing information
        """
        text_length = len(text)
        word_count = len(text.split())
        
        # Base timing calculations
        speech_duration = text_length / self.speech_rate
        
        # Adjust for emotion intensity
        emotion_modifier = 1.0 + (emotion_intensity - 0.5) * 0.3
        speech_duration *= emotion_modifier
        
        return {
            'speech_duration': speech_duration,
            'transition_in': self.default_transition_time,
            'transition_out': self.default_transition_time,
            'hold_time': self.default_hold_time,
            'total_duration': speech_duration + self.default_transition_time * 2,
            'word_count': word_count,
            'emotion_modifier': emotion_modifier
        }
    
    def map_emotion_to_animation(self, emotion_mix: Dict[str, float]) -> AnimationSequence:
        """
        Map emotion mix to complete animation sequence
        
        Args:
            emotion_mix: Dictionary of emotions and their intensities
            
        Returns:
            AnimationSequence with keyframes for the emotion
        """
        sequence = AnimationSequence()
        
        # Generate facial expression
        facial_expression = self.generate_facial_expression_data(emotion_mix)
        
        # Calculate primary emotion intensity
        primary_emotion_intensity = max(emotion_mix.values()) if emotion_mix else 0.5
        
        # Create keyframes for smooth animation
        # Start keyframe (neutral)
        start_keyframe = AnimationKeyframe(
            timestamp=0.0,
            facial_data=create_neutral_expression(),
            emotion_intensity=0.0,
            transition_type=TransitionType.EASE_IN,
            duration=self.default_transition_time
        )
        
        # Peak keyframe (full emotion)
        peak_keyframe = AnimationKeyframe(
            timestamp=self.default_transition_time,
            facial_data=facial_expression,
            emotion_intensity=primary_emotion_intensity,
            transition_type=TransitionType.SMOOTH,
            duration=self.default_hold_time
        )
        
        # End keyframe (slight relaxation)
        relaxed_expression = self.generate_facial_expression_data(
            {emotion: intensity * 0.7 for emotion, intensity in emotion_mix.items()}
        )
        end_keyframe = AnimationKeyframe(
            timestamp=self.default_transition_time + self.default_hold_time,
            facial_data=relaxed_expression,
            emotion_intensity=primary_emotion_intensity * 0.7,
            transition_type=TransitionType.EASE_OUT,
            duration=self.default_transition_time
        )
        
        # Add keyframes to sequence
        sequence.add_keyframe(start_keyframe)
        sequence.add_keyframe(peak_keyframe)
        sequence.add_keyframe(end_keyframe)
        
        # Add metadata
        sequence.metadata = {
            'emotion_mix': emotion_mix,
            'primary_emotion': max(emotion_mix.items(), key=lambda x: x[1])[0] if emotion_mix else 'neutral',
            'intensity': primary_emotion_intensity
        }
        
        return sequence
    
    def generate_complete_animation_data(self, text: str, emotion_mix: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate complete animation data package
        
        Args:
            text: The text being spoken
            emotion_mix: Dictionary of emotions and their intensities
            
        Returns:
            Complete animation data dictionary
        """
        # Generate all components
        facial_expression = self.generate_facial_expression_data(emotion_mix)
        lip_sync_data = self.create_lip_sync_data(text)
        timing_data = self.calculate_animation_timing(text, max(emotion_mix.values()) if emotion_mix else 0.5)
        animation_sequence = self.map_emotion_to_animation(emotion_mix)
        
        return {
            'facial_expression': facial_expression,
            'lip_sync_data': lip_sync_data,
            'timing_data': timing_data,
            'animation_sequence': animation_sequence,
            'metadata': {
                'text_length': len(text),
                'word_count': len(text.split()),
                'phoneme_count': len(lip_sync_data),
                'emotion_mix': emotion_mix,
                'generation_timestamp': timing_data['total_duration']
            }
        }

# Create main instance for usage
animation_provider = AnimationDataProvider()