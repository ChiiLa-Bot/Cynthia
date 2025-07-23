"""
AI Brain Package
Contains all AI-related modules for Cynthia
"""

from .personality_engine import cynthia_personality, PersonalityEngine, InteractionMode
from .emotion_engine import cynthia_emotions, EmotionEngine
from .context_manager import cynthia_context, ContextManager
from .safety_config import SafetyConfig, SafetySettingsHandler, APIErrorHandler
from .natural_communication import NaturalCommunicationEngine, CommunicationStyle, ConversationTechnique
from .llm_integration import get_cynthia_brain, AIBrain
from .animation_models import (
    FacialExpressionData, PhonemeData, AnimationKeyframe, AnimationSequence,
    EnhancedResponse, MouthShape, TransitionType,
    create_neutral_expression, create_smile_expression, create_surprised_expression,
    create_sad_expression, create_angry_expression
)
from .animation_provider import AnimationDataProvider, animation_provider

__all__ = [
    "cynthia_personality", "PersonalityEngine", "InteractionMode",
    "cynthia_emotions", "EmotionEngine", 
    "cynthia_context", "ContextManager",
    "SafetyConfig", "SafetySettingsHandler", "APIErrorHandler",
    "NaturalCommunicationEngine", "CommunicationStyle", "ConversationTechnique",
    "get_cynthia_brain", "AIBrain",
    "FacialExpressionData", "PhonemeData", "AnimationKeyframe", "AnimationSequence",
    "EnhancedResponse", "MouthShape", "TransitionType",
    "create_neutral_expression", "create_smile_expression", "create_surprised_expression",
    "create_sad_expression", "create_angry_expression",
    "AnimationDataProvider", "animation_provider"
]
