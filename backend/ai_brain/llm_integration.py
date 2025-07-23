"""
AI Brain - Main integration module for Cynthia
Combines personality, emotions, and context management
"""

from typing import Dict, Optional, Any
import google.generativeai as genai
from .personality_engine import cynthia_personality, PersonalityEngine, InteractionMode
from .emotion_engine import cynthia_emotions, EmotionEngine
from .context_manager import cynthia_context, ContextManager
from .safety_config import SafetyConfig, SafetySettingsHandler, APIErrorHandler
from .natural_communication import NaturalCommunicationEngine
from loguru import logger
import os
import time

class AIBrain:
    """Main AI Brain that orchestrates all components"""
    
    def __init__(self):
        self.personality: PersonalityEngine = cynthia_personality
        self.emotions: EmotionEngine = cynthia_emotions
        self.context: ContextManager = cynthia_context
        
        # Initialize natural communication engine
        self.natural_communication = NaturalCommunicationEngine()
        
        # Initialize safety configuration and error handlers
        self.current_safety_config = SafetyConfig.safe_mode()
        self.safety_handler = SafetySettingsHandler()
        self.error_handler = APIErrorHandler()
        
        # Initialize Gemini model
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self._initialize_model()
        
        logger.info("AI Brain initialized successfully")
    
    def _initialize_model(self):
        """Initialize Gemini model with current safety settings"""
        try:
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                safety_settings=self.current_safety_config.to_gemini_safety_settings()
            )
            logger.info(f"Model initialized with safety config: {self.current_safety_config}")
        except Exception as e:
            logger.error(f"Failed to initialize model with safety settings: {e}")
            # Fallback to default model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def configure_safety_settings(self, mode: InteractionMode) -> Dict[str, Any]:
        """Configure safety settings based on interaction mode"""
        try:
            if mode == InteractionMode.NSFW:
                self.current_safety_config = SafetyConfig.nsfw_mode()
                logger.info("Safety settings configured for NSFW mode - all blocks disabled")
            else:
                self.current_safety_config = SafetyConfig.safe_mode()
                logger.info("Safety settings configured for SAFE mode - default blocks enabled")
            
            # Validate safety configuration
            if not self.safety_handler.validate_safety_config(self.current_safety_config):
                raise ValueError("Invalid safety configuration generated")
            
            # Reinitialize model with new safety settings
            self._initialize_model()
            
            return {
                "status": "success",
                "mode": mode.value,
                "safety_config": str(self.current_safety_config),
                "message": f"Safety settings updated for {mode.value} mode"
            }
        except Exception as e:
            logger.error(f"Failed to configure safety settings: {e}")
            return {
                "status": "error",
                "message": f"Failed to configure safety settings: {e}",
                "current_config": str(self.current_safety_config)
            }
    
    def process_with_retry(self, prompt: str, original_user_input: str, max_retries: int = 3) -> str:
        """
        Process prompt with retry logic for safety-related API responses
        
        Args:
            prompt: The prompt to send to the model
            original_user_input: The original user input for context
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated response text
        """
        current_prompt = prompt
        
        for retry_count in range(max_retries + 1):
            try:
                logger.info(f"Generating response (attempt {retry_count + 1}/{max_retries + 1})")
                
                # Generate response using current model
                ai_response = self.model.generate_content(current_prompt)
                response_text = ai_response.text
                
                if response_text and response_text.strip():
                    logger.info(f"Successfully generated response on attempt {retry_count + 1}")
                    return response_text
                else:
                    raise ValueError("Empty response generated")
                    
            except Exception as e:
                logger.warning(f"Generation attempt {retry_count + 1} failed: {e}")
                
                # Try to handle the error with safety handler
                adjusted_prompt = self.safety_handler.handle_safety_error(
                    error=e,
                    retry_count=retry_count,
                    original_prompt=current_prompt
                )
                
                if adjusted_prompt and retry_count < max_retries:
                    current_prompt = adjusted_prompt
                    logger.info(f"Retrying with adjusted prompt (attempt {retry_count + 2})")
                    continue
                else:
                    # Final fallback - use error handler
                    logger.error(f"All retry attempts failed. Using fallback response.")
                    context = {
                        "mode": self.personality.interaction_mode.value,
                        "original_input": original_user_input
                    }
                    fallback_data = self.error_handler.create_fallback_response("general_error", context)
                    return fallback_data["response"]
        
        # This should never be reached, but just in case
        return "I apologize, but I'm having technical difficulties right now. Please try again."
    
    def process_input(self, user_input: str, user_id: str = "default") -> Dict[str, Any]:
        """Process user input and generate comprehensive response with retry logic"""
        
        try:
            # 1. Analyze emotional content
            emotional_response = self.emotions.get_emotional_response(user_input)
            
            # 2. Update personality based on input
            suggested_emotion_from_personality = self.personality.analyze_user_input(user_input)
            self.personality.update_emotion(suggested_emotion_from_personality, f"Response to: {user_input[:50]}...")
            
            # 3. Generate comprehensive context
            personality_context = self.personality.generate_response_context(user_input)
            emotion_context = self.emotions.get_emotion_context()
            conversation_context = self.context.get_full_context()
            
            # 4. Generate enhanced natural communication prompt
            primary_emotion, intensity = self.emotions.get_primary_emotion()
            
            # Use Natural Communication Engine for enhanced prompt generation
            natural_prompt = self.natural_communication.generate_personality_prompt(
                traits=self.personality.traits,
                emotion=self.personality.current_emotion,
                mode=self.personality.interaction_mode
            )
            
            full_prompt = f"""
            {natural_prompt}
            
            **Current Context:**
            {emotion_context}
            
            {conversation_context}
            
            **User Input:** {user_input}
            
            **Response Guidelines:**
            - Apply natural conversation flow and personality-driven communication
            - Express emotions through descriptive language, not emoji clusters
            - Use conversational techniques like active listening and empathetic responses
            - Maintain authentic personality expression through word choice and tone
            - Keep emoji usage to maximum 1-2 per response, prioritize descriptive text
            - Show emotional state through natural language patterns
            
            **Response:**
            """
            
            # 5. Generate AI response with retry logic
            raw_response = self.process_with_retry(full_prompt, user_input)
            
            # 6. Apply natural communication enhancements to response
            response_text = self._enhance_response_with_natural_communication(
                raw_response, user_input, primary_emotion, intensity
            )
            
            # 7. Record conversation
            primary_emotion, intensity = self.emotions.get_primary_emotion()
            self.context.add_conversation_entry(
                user_input=user_input,
                cynthia_response=response_text,
                emotion_state=primary_emotion,
                user_id=user_id
            )
            
            # 7. Prepare response data
            response_data = {
                "response": response_text,
                "emotion": {
                    "primary": primary_emotion,
                    "intensity": intensity,
                    "mix": self.emotions.get_emotion_mix(0.3),
                    "animation": emotional_response.get("animation", "idle")
                },
                "personality": {
                    "current_mode": self.personality.interaction_mode.value,
                    "traits": self.personality.get_status_summary()["personality_traits"]
                },
                "context": {
                    "conversation_length": len(self.context.short_term_memory),
                    "user_relationship": self._get_relationship_level(user_id)
                }
            }
            
            logger.info(f"Processed input successfully. Emotion: {primary_emotion}, Mode: {self.personality.interaction_mode.value}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            # Use error handler to create appropriate fallback response
            context = {
                "mode": self.personality.interaction_mode.value,
                "user_id": user_id
            }
            return self.error_handler.create_fallback_response("general_error", context)
    
    def _enhance_response_with_natural_communication(self, raw_response: str, user_input: str, emotion: str, intensity: float) -> str:
        """
        Apply natural communication enhancements to the generated response
        
        Args:
            raw_response: The raw response from the AI model
            user_input: Original user input for context
            emotion: Current emotional state
            intensity: Emotional intensity level
            
        Returns:
            Enhanced response with natural communication improvements
        """
        try:
            # Convert emotion string to EmotionState enum
            from .personality_engine import EmotionState
            emotion_state = EmotionState(emotion) if emotion in [e.value for e in EmotionState] else EmotionState.HAPPY
            
            # Get conversation context for natural flow enhancement
            conversation_history = []
            if hasattr(self.context, 'short_term_memory') and self.context.short_term_memory:
                # Get last few messages for context
                conversation_history = [entry.get('user_input', '') for entry in self.context.short_term_memory[-3:]]
            
            # Apply natural communication enhancements
            enhanced_response = raw_response
            
            # 1. Filter emoji clusters first (3+ consecutive emojis)
            enhanced_response = self.natural_communication.filter_emoji_clusters(enhanced_response)
            
            # 2. Reduce emoji usage (max 1-2 per response)
            enhanced_response = self.natural_communication.reduce_emoji_usage(enhanced_response, max_emojis=2)
            
            # 3. Apply emotional tone through text style
            enhanced_response = self.natural_communication.apply_emotional_tone(
                enhanced_response, emotion_state, intensity
            )
            
            # 4. Enhance natural conversation flow
            enhanced_response = self.natural_communication.enhance_natural_flow(
                enhanced_response, conversation_history
            )
            
            logger.info(f"Applied natural communication enhancements. Emotion: {emotion}, Intensity: {intensity}")
            return enhanced_response
            
        except Exception as e:
            logger.warning(f"Failed to apply natural communication enhancements: {e}")
            # Return original response if enhancement fails
            return raw_response
    
    def _get_relationship_level(self, user_id: str) -> str:
        """Get relationship level description"""
        if user_id in self.context.user_memories:
            level = self.context.user_memories[user_id].relationship_level
            if level < 0.3:
                return "new friend"
            elif level < 0.7:
                return "good friend"
            else:
                return "close friend"
        return "stranger"
    
    def set_interaction_mode(self, mode: str, user_id: str = "default") -> Dict[str, str]:
        """Change interaction mode and configure safety settings"""
        try:
            if mode.lower() == "nsfw":
                # Set personality mode
                personality_result = self.personality.set_interaction_mode(InteractionMode.NSFW)
                # Configure safety settings
                safety_result = self.configure_safety_settings(InteractionMode.NSFW)
                
                if safety_result["status"] == "success":
                    logger.info(f"User {user_id} switched to NSFW mode with safety settings disabled")
                    return {
                        "status": "success",
                        "message": f"{personality_result}. {safety_result['message']}",
                        "current_mode": self.personality.interaction_mode.value,
                        "safety_config": safety_result["safety_config"]
                    }
                else:
                    logger.error(f"Failed to configure NSFW safety settings: {safety_result['message']}")
                    return {
                        "status": "partial_success",
                        "message": f"{personality_result}. Warning: {safety_result['message']}",
                        "current_mode": self.personality.interaction_mode.value
                    }
            else:
                # Set personality mode
                personality_result = self.personality.set_interaction_mode(InteractionMode.SAFE)
                # Configure safety settings
                safety_result = self.configure_safety_settings(InteractionMode.SAFE)
                
                if safety_result["status"] == "success":
                    logger.info(f"User {user_id} switched to SAFE mode with safety settings enabled")
                    return {
                        "status": "success",
                        "message": f"{personality_result}. {safety_result['message']}",
                        "current_mode": self.personality.interaction_mode.value,
                        "safety_config": safety_result["safety_config"]
                    }
                else:
                    logger.error(f"Failed to configure SAFE safety settings: {safety_result['message']}")
                    return {
                        "status": "partial_success",
                        "message": f"{personality_result}. Warning: {safety_result['message']}",
                        "current_mode": self.personality.interaction_mode.value
                    }
            
        except Exception as e:
            logger.error(f"Error changing mode: {e}")
            return {
                "status": "error",
                "message": f"Failed to change mode: {e}",
                "current_mode": self.personality.interaction_mode.value
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all systems"""
        primary_emotion, intensity = self.emotions.get_primary_emotion()
        
        return {
            "personality": self.personality.get_status_summary(),
            "emotion": self.emotions.get_emotion_summary(),
            "context": {
                "short_term_entries": len(self.context.short_term_memory),
                "long_term_entries": len(self.context.long_term_memory),
                "known_users": len(self.context.user_memories),
                "current_session_duration": str(self.context.session_start)
            },
            "system": {
                "model": "gemini-2.5-flash",
                "status": "active"
            }
        }
    
    def reset_conversation(self, user_id: str = "default"):
        """Reset conversation for specific user"""
        self.context.clear_session()
        self.emotions.reset_to_baseline()
        self.personality.current_emotion = self.personality.current_emotion  # Keep current personality state
        logger.info(f"Reset conversation for user {user_id}")
    
    def save_context(self, filepath: str):
        """Save context to file"""
        try:
            self.context.save_to_file(filepath)
            logger.info(f"Context saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    def load_context(self, filepath: str):
        """Load context from file"""
        try:
            self.context.load_from_file(filepath)
            logger.info(f"Context loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load context: {e}")

# Create main instance for usage - only if API key is available
cynthia_brain = None

def get_cynthia_brain():
    """Get or create the main Cynthia brain instance"""
    global cynthia_brain
    if cynthia_brain is None:
        cynthia_brain = AIBrain()
    return cynthia_brain
