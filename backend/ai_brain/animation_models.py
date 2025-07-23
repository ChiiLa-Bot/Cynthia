"""
Animation Data Models for 3D Integration
Contains data structures for facial expressions, lip sync, and animation keyframes
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import time

class MouthShape(Enum):
    """Standard mouth shapes for phoneme-based lip sync"""
    NEUTRAL = "neutral"
    A = "a"          # ah, father
    E = "e"          # bet, end
    I = "i"          # bit, sit
    O = "o"          # hot, lot
    U = "u"          # book, put
    AI = "ai"        # bite, my
    EI = "ei"        # bait, say
    OU = "ou"        # boat, go
    M_B_P = "mbp"    # consonants m, b, p
    F_V = "fv"       # consonants f, v
    TH = "th"        # consonants th
    T_D_N_L = "tdnl" # consonants t, d, n, l
    K_G = "kg"       # consonants k, g
    CH_SH = "chsh"   # consonants ch, sh
    R = "r"          # consonant r
    CLOSED = "closed" # mouth closed
    SMILE = "smile"   # smiling
    WIDE = "wide"     # wide open

class TransitionType(Enum):
    """Animation transition types"""
    LINEAR = "linear"
    SMOOTH = "smooth"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"

@dataclass
class FacialExpressionData:
    """
    Detailed facial expression data for 3D animation
    Values range from 0.0 to 1.0 representing muscle activation levels
    """
    # Eye region
    eyebrow_raise_left: float = 0.0
    eyebrow_raise_right: float = 0.0
    eyebrow_furrow: float = 0.0
    eye_openness_left: float = 1.0
    eye_openness_right: float = 1.0
    eye_squint_left: float = 0.0
    eye_squint_right: float = 0.0
    
    # Mouth region
    mouth_shape: MouthShape = MouthShape.NEUTRAL
    mouth_openness: float = 0.0
    smile_left: float = 0.0
    smile_right: float = 0.0
    mouth_frown: float = 0.0
    lip_pucker: float = 0.0
    
    # Cheek region
    cheek_raise_left: float = 0.0
    cheek_raise_right: float = 0.0
    cheek_puff: float = 0.0
    
    # Jaw and chin
    jaw_drop: float = 0.0
    jaw_left: float = 0.0
    jaw_right: float = 0.0
    chin_raise: float = 0.0
    
    # Nose
    nose_wrinkle: float = 0.0
    nostril_flare: float = 0.0
    
    # Overall expression intensity
    expression_intensity: float = 0.5
    
    def to_dict(self) -> Dict[str, Union[float, str]]:
        """Convert to dictionary for JSON serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, MouthShape):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FacialExpressionData':
        """Create from dictionary"""
        if 'mouth_shape' in data and isinstance(data['mouth_shape'], str):
            data['mouth_shape'] = MouthShape(data['mouth_shape'])
        return cls(**data)

@dataclass
class PhonemeData:
    """
    Phoneme data for lip synchronization
    """
    phoneme: str                    # The phoneme (e.g., 'AH', 'EH', 'M')
    start_time: float              # Start time in seconds
    duration: float                # Duration in seconds
    mouth_shape: MouthShape        # Corresponding mouth shape
    intensity: float = 1.0         # Intensity of the phoneme (0.0-1.0)
    transition_in: float = 0.1     # Transition time into this phoneme
    transition_out: float = 0.1    # Transition time out of this phoneme
    
    @property
    def end_time(self) -> float:
        """Calculate end time"""
        return self.start_time + self.duration
    
    def to_dict(self) -> Dict[str, Union[str, float]]:
        """Convert to dictionary for JSON serialization"""
        return {
            'phoneme': self.phoneme,
            'start_time': self.start_time,
            'duration': self.duration,
            'mouth_shape': self.mouth_shape.value,
            'intensity': self.intensity,
            'transition_in': self.transition_in,
            'transition_out': self.transition_out,
            'end_time': self.end_time
        }

@dataclass
class AnimationKeyframe:
    """
    Animation keyframe for smooth transitions
    """
    timestamp: float                           # Time in seconds
    facial_data: FacialExpressionData         # Facial expression at this keyframe
    emotion_intensity: float = 0.5            # Overall emotion intensity
    transition_type: TransitionType = TransitionType.SMOOTH
    duration: float = 0.5                     # Duration to reach this keyframe
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp,
            'facial_data': self.facial_data.to_dict(),
            'emotion_intensity': self.emotion_intensity,
            'transition_type': self.transition_type.value,
            'duration': self.duration,
            'metadata': self.metadata
        }

@dataclass
class AnimationSequence:
    """
    Sequence of animation keyframes
    """
    keyframes: List[AnimationKeyframe] = field(default_factory=list)
    total_duration: float = 0.0
    loop: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_keyframe(self, keyframe: AnimationKeyframe):
        """Add a keyframe to the sequence"""
        self.keyframes.append(keyframe)
        self.total_duration = max(self.total_duration, keyframe.timestamp + keyframe.duration)
    
    def get_keyframes_at_time(self, time: float) -> List[AnimationKeyframe]:
        """Get keyframes active at a specific time"""
        active_keyframes = []
        for keyframe in self.keyframes:
            if keyframe.timestamp <= time <= keyframe.timestamp + keyframe.duration:
                active_keyframes.append(keyframe)
        return active_keyframes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'keyframes': [kf.to_dict() for kf in self.keyframes],
            'total_duration': self.total_duration,
            'loop': self.loop,
            'metadata': self.metadata
        }

@dataclass
class EnhancedResponse:
    """
    Enhanced response model that includes animation metadata
    """
    text: str                                              # The response text
    emotion_data: Dict[str, Any]                          # Emotion information
    animation_data: Optional[Dict[str, Any]] = None       # 3D animation data
    lip_sync_data: Optional[List[PhonemeData]] = None     # Lip sync phoneme data
    facial_expression: Optional[FacialExpressionData] = None  # Current facial expression
    timing_data: Optional[Dict[str, float]] = None        # Animation timing information
    animation_sequence: Optional[AnimationSequence] = None   # Complete animation sequence
    metadata: Dict[str, Any] = field(default_factory=dict)   # Additional metadata
    
    # Response generation metadata
    generation_time: float = field(default_factory=time.time)
    response_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            'text': self.text,
            'emotion_data': self.emotion_data,
            'generation_time': self.generation_time,
            'response_id': self.response_id,
            'metadata': self.metadata
        }
        
        if self.animation_data:
            result['animation_data'] = self.animation_data
            
        if self.lip_sync_data:
            result['lip_sync_data'] = [phoneme.to_dict() for phoneme in self.lip_sync_data]
            
        if self.facial_expression:
            result['facial_expression'] = self.facial_expression.to_dict()
            
        if self.timing_data:
            result['timing_data'] = self.timing_data
            
        if self.animation_sequence:
            result['animation_sequence'] = self.animation_sequence.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedResponse':
        """Create from dictionary"""
        # Handle facial_expression
        if 'facial_expression' in data and data['facial_expression']:
            data['facial_expression'] = FacialExpressionData.from_dict(data['facial_expression'])
        
        # Handle lip_sync_data
        if 'lip_sync_data' in data and data['lip_sync_data']:
            phoneme_list = []
            for phoneme_dict in data['lip_sync_data']:
                # Remove computed properties that aren't constructor parameters
                phoneme_data = phoneme_dict.copy()
                if 'end_time' in phoneme_data:
                    del phoneme_data['end_time']
                phoneme_data['mouth_shape'] = MouthShape(phoneme_data['mouth_shape'])
                phoneme_list.append(PhonemeData(**phoneme_data))
            data['lip_sync_data'] = phoneme_list
        
        # Handle animation_sequence
        if 'animation_sequence' in data and data['animation_sequence']:
            seq_data = data['animation_sequence']
            keyframes = []
            for kf_data in seq_data.get('keyframes', []):
                facial_data = FacialExpressionData.from_dict(kf_data['facial_data'])
                kf_data['facial_data'] = facial_data
                kf_data['transition_type'] = TransitionType(kf_data['transition_type'])
                keyframes.append(AnimationKeyframe(**kf_data))
            
            data['animation_sequence'] = AnimationSequence(
                keyframes=keyframes,
                total_duration=seq_data.get('total_duration', 0.0),
                loop=seq_data.get('loop', False),
                metadata=seq_data.get('metadata', {})
            )
        
        return cls(**data)

# Utility functions for creating common expressions
def create_neutral_expression() -> FacialExpressionData:
    """Create a neutral facial expression"""
    return FacialExpressionData()

def create_smile_expression(intensity: float = 0.7) -> FacialExpressionData:
    """Create a smiling expression"""
    return FacialExpressionData(
        smile_left=intensity,
        smile_right=intensity,
        cheek_raise_left=intensity * 0.5,
        cheek_raise_right=intensity * 0.5,
        eye_squint_left=intensity * 0.3,
        eye_squint_right=intensity * 0.3,
        expression_intensity=intensity
    )

def create_surprised_expression(intensity: float = 0.8) -> FacialExpressionData:
    """Create a surprised expression"""
    return FacialExpressionData(
        eyebrow_raise_left=intensity,
        eyebrow_raise_right=intensity,
        eye_openness_left=1.0,
        eye_openness_right=1.0,
        mouth_openness=intensity * 0.6,
        jaw_drop=intensity * 0.4,
        expression_intensity=intensity
    )

def create_sad_expression(intensity: float = 0.6) -> FacialExpressionData:
    """Create a sad expression"""
    return FacialExpressionData(
        eyebrow_furrow=intensity * 0.7,
        mouth_frown=intensity,
        eye_openness_left=0.7,
        eye_openness_right=0.7,
        expression_intensity=intensity
    )

def create_angry_expression(intensity: float = 0.8) -> FacialExpressionData:
    """Create an angry expression"""
    return FacialExpressionData(
        eyebrow_furrow=intensity,
        eye_squint_left=intensity * 0.6,
        eye_squint_right=intensity * 0.6,
        mouth_frown=intensity * 0.5,
        nose_wrinkle=intensity * 0.4,
        expression_intensity=intensity
    )