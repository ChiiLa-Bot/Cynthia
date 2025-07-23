"""
Safety Configuration Module
Handles dynamic safety settings for Gemini API integration
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import google.generativeai as genai
from loguru import logger
import time


class SafetyCategory(Enum):
    """Gemini API safety categories"""
    HARASSMENT = "HARM_CATEGORY_HARASSMENT"
    HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
    SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
    DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"


class SafetyThreshold(Enum):
    """Gemini API safety thresholds"""
    BLOCK_NONE = "BLOCK_NONE"
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"


@dataclass
class SafetyConfig:
    """Configuration for Gemini API safety settings"""
    harassment: str = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value
    hate_speech: str = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value
    sexually_explicit: str = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value
    dangerous_content: str = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value
    
    @classmethod
    def safe_mode(cls):
        """Create safe mode configuration with default safety settings"""
        return cls(
            harassment=SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value,
            hate_speech=SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value,
            sexually_explicit=SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value,
            dangerous_content=SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value
        )
    
    @classmethod
    def nsfw_mode(cls):
        """Create NSFW mode configuration with all safety blocks disabled"""
        return cls(
            harassment=SafetyThreshold.BLOCK_NONE.value,
            hate_speech=SafetyThreshold.BLOCK_NONE.value,
            sexually_explicit=SafetyThreshold.BLOCK_NONE.value,
            dangerous_content=SafetyThreshold.BLOCK_NONE.value
        )
    
    def to_gemini_safety_settings(self) -> Dict[str, str]:
        """Convert to Gemini API safety settings format"""
        return {
            SafetyCategory.HARASSMENT.value: self.harassment,
            SafetyCategory.HATE_SPEECH.value: self.hate_speech,
            SafetyCategory.SEXUALLY_EXPLICIT.value: self.sexually_explicit,
            SafetyCategory.DANGEROUS_CONTENT.value: self.dangerous_content
        }
    
    def __str__(self) -> str:
        """String representation of safety configuration"""
        return f"SafetyConfig(harassment={self.harassment}, hate_speech={self.hate_speech}, sexually_explicit={self.sexually_explicit}, dangerous_content={self.dangerous_content})"


class SafetySettingsHandler:
    """Handler for managing Gemini API safety-related errors and retries"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_delay = 1.0  # seconds
    
    def handle_safety_error(self, error: Exception, retry_count: int, original_prompt: str) -> Optional[str]:
        """
        Handle Gemini safety-related errors with progressive fallback
        
        Args:
            error: The exception that occurred
            retry_count: Current retry attempt number
            original_prompt: The original prompt that caused the error
            
        Returns:
            Adjusted prompt for retry, or None if no retry should be attempted
        """
        error_str = str(error).lower()
        
        # Check if this is a safety-related error
        safety_keywords = ['safety', 'blocked', 'harmful', 'inappropriate', 'policy']
        is_safety_error = any(keyword in error_str for keyword in safety_keywords)
        
        if not is_safety_error or retry_count >= self.max_retries:
            logger.warning(f"Not retrying error (attempt {retry_count}/{self.max_retries}): {error}")
            return None
        
        logger.info(f"Handling safety error (attempt {retry_count + 1}/{self.max_retries}): {error}")
        
        # Progressive prompt adjustment strategies
        if retry_count == 0:
            # First retry: Add safety disclaimer
            adjusted_prompt = self._add_safety_disclaimer(original_prompt)
        elif retry_count == 1:
            # Second retry: Rephrase potentially problematic content
            adjusted_prompt = self._rephrase_for_safety(original_prompt)
        else:
            # Final retry: Use most conservative approach
            adjusted_prompt = self._create_safe_fallback_prompt(original_prompt)
        
        # Add delay between retries
        time.sleep(self.retry_delay * (retry_count + 1))
        
        return adjusted_prompt
    
    def _add_safety_disclaimer(self, prompt: str) -> str:
        """Add safety disclaimer to prompt"""
        disclaimer = """
        IMPORTANT: Please provide a helpful, harmless, and honest response that follows content policies.
        Focus on being supportive and appropriate in your response.
        
        """
        return disclaimer + prompt
    
    def _rephrase_for_safety(self, prompt: str) -> str:
        """Rephrase prompt to be more safety-compliant"""
        # Simple rephrasing strategy - add context about appropriate response
        safety_context = """
        Please respond in a way that is:
        - Respectful and appropriate
        - Helpful and supportive
        - Aligned with content guidelines
        
        Original request: """
        
        return safety_context + prompt
    
    def _create_safe_fallback_prompt(self, original_prompt: str) -> str:
        """Create a safe fallback prompt when other strategies fail"""
        return """
        Please provide a friendly, helpful response that acknowledges the user's message 
        while maintaining appropriate content standards. Be supportive and understanding.
        
        Respond as Cynthia with your caring personality, but keep the content appropriate.
        """
    
    def validate_safety_config(self, config: SafetyConfig) -> bool:
        """Validate that safety configuration is properly formatted"""
        try:
            # Check that all required fields are present
            required_fields = ['harassment', 'hate_speech', 'sexually_explicit', 'dangerous_content']
            for field in required_fields:
                if not hasattr(config, field):
                    logger.error(f"Safety config missing required field: {field}")
                    return False
            
            # Check that values are valid safety thresholds
            valid_thresholds = [threshold.value for threshold in SafetyThreshold]
            config_values = [config.harassment, config.hate_speech, 
                           config.sexually_explicit, config.dangerous_content]
            
            for value in config_values:
                if value not in valid_thresholds:
                    logger.error(f"Invalid safety threshold: {value}")
                    return False
            
            logger.info("Safety configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating safety config: {e}")
            return False


class APIErrorHandler:
    """Handler for various API generation errors with fallback responses"""
    
    def __init__(self):
        self.fallback_responses = {
            "safety_error": "I understand you're trying to communicate with me, but I need to keep our conversation appropriate. Could you rephrase that in a different way?",
            "rate_limit": "I'm getting a lot of requests right now. Could you wait a moment and try again?",
            "api_error": "I'm having some technical difficulties right now. Let me try to help you in a different way.",
            "timeout": "That took longer than expected to process. Could you try asking again?",
            "general_error": "I'm sorry, I'm having trouble processing that right now. Can you try again?"
        }
    
    def handle_generation_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle various API generation errors and provide appropriate fallback
        
        Args:
            error: The exception that occurred
            context: Optional context about the request
            
        Returns:
            Dictionary with error handling result and fallback response
        """
        error_str = str(error).lower()
        error_type = self._classify_error(error_str)
        
        logger.error(f"API generation error ({error_type}): {error}")
        
        fallback_response = self.create_fallback_response(error_type, context)
        
        return {
            "status": "error_handled",
            "error_type": error_type,
            "original_error": str(error),
            "fallback_response": fallback_response,
            "should_retry": error_type in ["rate_limit", "timeout", "api_error"]
        }
    
    def _classify_error(self, error_str: str) -> str:
        """Classify the type of error based on error message"""
        if any(keyword in error_str for keyword in ['safety', 'blocked', 'harmful', 'policy']):
            return "safety_error"
        elif any(keyword in error_str for keyword in ['rate', 'limit', 'quota']):
            return "rate_limit"
        elif any(keyword in error_str for keyword in ['timeout', 'deadline']):
            return "timeout"
        elif any(keyword in error_str for keyword in ['api', 'server', 'service']):
            return "api_error"
        else:
            return "general_error"
    
    def create_fallback_response(self, error_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a fallback response based on error type and context"""
        base_response = self.fallback_responses.get(error_type, self.fallback_responses["general_error"])
        
        # Create enhanced response structure
        fallback_data = {
            "response": base_response,
            "emotion": {
                "primary": "confused",
                "intensity": 0.5,
                "mix": {"confused": 0.7, "caring": 0.3},
                "animation": "confused"
            },
            "personality": {
                "current_mode": context.get("mode", "safe") if context else "safe",
                "traits": {
                    "cheerfulness": 0.4,  # Lower due to error
                    "caring_level": 0.9   # High caring to be supportive
                }
            },
            "context": {
                "error_handled": True,
                "error_type": error_type
            }
        }
        
        return fallback_data