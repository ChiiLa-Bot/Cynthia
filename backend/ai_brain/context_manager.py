"""
Context Manager for Cynthia
Manages conversation history, user memory, and contextual understanding
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from enum import Enum

class MemoryType(Enum):
    """Types of memories Cynthia can store"""
    SHORT_TERM = "short_term"      # Current conversation
    LONG_TERM = "long_term"        # Important information about user
    EMOTIONAL = "emotional"        # Emotional connections and moments
    PREFERENCE = "preference"      # User preferences and likes

@dataclass
class ConversationEntry:
    """Single conversation entry"""
    timestamp: datetime
    user_input: str
    cynthia_response: str
    emotion_state: str
    context_tags: List[str]
    importance_score: float = 0.5  # 0-1, higher means more important

@dataclass
class UserMemory:
    """Memory about the user"""
    user_id: str
    name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    important_facts: Optional[List[str]] = None
    relationship_level: float = 0.0  # 0-1, how close we are
    last_interaction: Optional[datetime] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.important_facts is None:
            self.important_facts = []

class ContextManager:
    """Main context management system"""
    
    def __init__(self, max_short_term: int = 50, max_long_term: int = 200):
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        
        # Conversation storage
        self.short_term_memory: List[ConversationEntry] = []
        self.long_term_memory: List[ConversationEntry] = []
        
        # User information
        self.user_memories: Dict[str, UserMemory] = {}
        self.current_user_id: Optional[str] = None
        
        # Context tracking
        self.conversation_topics: List[str] = []
        self.current_mood: str = "neutral"
        self.session_start: datetime = datetime.now()
        
    def add_conversation_entry(self, user_input: str, cynthia_response: str, 
                             emotion_state: str, user_id: str = "default"):
        """Add new conversation entry"""
        
        # Create entry
        entry = ConversationEntry(
            timestamp=datetime.now(),
            user_input=user_input,
            cynthia_response=cynthia_response,
            emotion_state=emotion_state,
            context_tags=self._extract_context_tags(user_input),
            importance_score=self._calculate_importance(user_input, cynthia_response)
        )
        
        # Add to short-term memory
        self.short_term_memory.append(entry)
        
        # Manage memory limits
        if len(self.short_term_memory) > self.max_short_term:
            # Move important entries to long-term memory
            old_entry = self.short_term_memory.pop(0)
            if old_entry.importance_score > 0.7:
                self.long_term_memory.append(old_entry)
                
                # Manage long-term memory size
                if len(self.long_term_memory) > self.max_long_term:
                    # Remove least important entries
                    self.long_term_memory.sort(key=lambda x: x.importance_score)
                    self.long_term_memory.pop(0)
        
        # Update user information
        self.current_user_id = user_id
        self._update_user_memory(user_id, user_input, entry)
    
    def _extract_context_tags(self, user_input: str) -> List[str]:
        """Extract context tags from user input"""
        tags = []
        input_lower = user_input.lower()
        
        # Topic detection
        topic_keywords = {
            "personal": ["i am", "my name", "i like", "i love", "i hate", "i feel"],
            "question": ["what", "how", "why", "when", "where", "who"],
            "compliment": ["cute", "beautiful", "amazing", "wonderful", "great"],
            "greeting": ["hello", "hi", "hey", "good morning", "good night"],
            "goodbye": ["bye", "goodbye", "see you", "talk later"],
            "help": ["help", "assist", "support", "problem", "issue"],
            "emotion": ["happy", "sad", "angry", "excited", "tired", "stressed"],
            "nsfw": ["nsfw", "mature", "adult", "intimate"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                tags.append(topic)
        
        return tags
    
    def _calculate_importance(self, user_input: str, cynthia_response: str) -> float:
        """Calculate importance score for memory entry"""
        score = 0.5  # Base score
        
        input_lower = user_input.lower()
        
        # Personal information increases importance
        personal_indicators = ["my name", "i am", "i live", "i work", "i study", "i like", "i love"]
        if any(indicator in input_lower for indicator in personal_indicators):
            score += 0.3
        
        # Emotional content increases importance
        emotional_indicators = ["love", "hate", "sad", "happy", "angry", "excited", "important"]
        if any(indicator in input_lower for indicator in emotional_indicators):
            score += 0.2
        
        # Questions about Cynthia increase importance
        if any(word in input_lower for word in ["you", "cynthia"]):
            score += 0.1
        
        # Long conversations increase importance
        if len(user_input) > 100:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _update_user_memory(self, user_id: str, user_input: str, entry: ConversationEntry):
        """Update user memory with new information"""
        
        if user_id not in self.user_memories:
            self.user_memories[user_id] = UserMemory(user_id=user_id)
        
        user_memory = self.user_memories[user_id]
        user_memory.last_interaction = datetime.now()
        
        # Extract user information
        input_lower = user_input.lower()
        
        # Name detection
        if "my name is" in input_lower or "i'm" in input_lower or "i am" in input_lower:
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() in ["name", "i'm", "am"] and i + 1 < len(words):
                    potential_name = words[i + 1].strip(".,!?")
                    if potential_name.isalpha():
                        user_memory.name = potential_name
                        break
        
        # Preference detection
        if "i like" in input_lower or "i love" in input_lower:
            if user_memory.preferences is None:
                user_memory.preferences = {}
            preference_text = user_input[user_input.lower().find("i like"):] if "i like" in input_lower else user_input[user_input.lower().find("i love"):]
            user_memory.preferences["likes"] = user_memory.preferences.get("likes", [])
            user_memory.preferences["likes"].append(preference_text)
        
        # Important facts
        if entry.importance_score > 0.7:
            if user_memory.important_facts is None:
                user_memory.important_facts = []
            user_memory.important_facts.append(f"{entry.timestamp.strftime('%Y-%m-%d')}: {user_input}")
            
            # Keep only recent important facts (last 20)
            if len(user_memory.important_facts) > 20:
                user_memory.important_facts.pop(0)
        
        # Relationship building
        positive_interactions = ["thank you", "thanks", "love", "great", "amazing", "wonderful"]
        if any(word in input_lower for word in positive_interactions):
            user_memory.relationship_level = min(user_memory.relationship_level + 0.1, 1.0)
    
    def get_conversation_context(self, last_n_entries: int = 10) -> str:
        """Get recent conversation context for AI"""
        
        recent_entries = self.short_term_memory[-last_n_entries:] if len(self.short_term_memory) >= last_n_entries else self.short_term_memory
        
        if not recent_entries:
            return "No previous conversation context."
        
        context_lines = ["**Recent Conversation Context:**"]
        
        for entry in recent_entries:
            time_str = entry.timestamp.strftime("%H:%M")
            context_lines.append(f"[{time_str}] User: {entry.user_input}")
            context_lines.append(f"[{time_str}] Cynthia ({entry.emotion_state}): {entry.cynthia_response}")
        
        return "\n".join(context_lines)
    
    def get_user_context(self, user_id: Optional[str] = None) -> str:
        """Get user-specific context"""
        
        if user_id is None:
            user_id = self.current_user_id
        
        if not user_id or user_id not in self.user_memories:
            return "No user information available."
        
        user_memory = self.user_memories[user_id]
        context_lines = ["**User Information:**"]
        
        if user_memory.name:
            context_lines.append(f"Name: {user_memory.name}")
        
        if user_memory.preferences:
            context_lines.append("Preferences:")
            for pref_type, pref_value in user_memory.preferences.items():
                if isinstance(pref_value, list):
                    context_lines.append(f"  {pref_type}: {', '.join(pref_value[-3:])}")  # Last 3 items
                else:
                    context_lines.append(f"  {pref_type}: {pref_value}")
        
        if user_memory.important_facts:
            context_lines.append("Important facts:")
            for fact in user_memory.important_facts[-5:]:  # Last 5 facts
                context_lines.append(f"  - {fact}")
        
        relationship_desc = "new friend" if user_memory.relationship_level < 0.3 else "good friend" if user_memory.relationship_level < 0.7 else "close friend"
        context_lines.append(f"Relationship level: {relationship_desc} ({user_memory.relationship_level:.1f})")
        
        return "\n".join(context_lines)
    
    def get_topic_context(self) -> str:
        """Get current topic context"""
        
        if not self.conversation_topics:
            return "No specific topic context."
        
        recent_topics = list(set(self.conversation_topics[-10:]))  # Last 10 unique topics
        return f"**Current Topics:** {', '.join(recent_topics)}"
    
    def get_full_context(self) -> str:
        """Get complete context for AI response generation"""
        
        contexts = [
            self.get_conversation_context(),
            self.get_user_context(),
            self.get_topic_context()
        ]
        
        return "\n\n".join(contexts)
    
    def search_memory(self, query: str, memory_type: Optional[MemoryType] = None) -> List[ConversationEntry]:
        """Search through memories"""
        
        results = []
        search_pools = []
        
        if memory_type is None or memory_type == MemoryType.SHORT_TERM:
            search_pools.extend(self.short_term_memory)
        
        if memory_type is None or memory_type == MemoryType.LONG_TERM:
            search_pools.extend(self.long_term_memory)
        
        query_lower = query.lower()
        
        for entry in search_pools:
            if (query_lower in entry.user_input.lower() or 
                query_lower in entry.cynthia_response.lower() or
                any(query_lower in tag for tag in entry.context_tags)):
                results.append(entry)
        
        # Sort by relevance (importance score) and recency
        results.sort(key=lambda x: (x.importance_score, x.timestamp), reverse=True)
        
        return results
    
    def clear_session(self):
        """Clear current session data"""
        self.short_term_memory.clear()
        self.conversation_topics.clear()
        self.session_start = datetime.now()
    
    def save_to_file(self, filepath: str):
        """Save context data to file"""
        data = {
            "short_term_memory": [asdict(entry) for entry in self.short_term_memory],
            "long_term_memory": [asdict(entry) for entry in self.long_term_memory],
            "user_memories": {uid: asdict(memory) for uid, memory in self.user_memories.items()},
            "conversation_topics": self.conversation_topics,
            "session_start": self.session_start.isoformat()
        }
        
        # Convert datetime objects to strings
        for memory_list in [data["short_term_memory"], data["long_term_memory"]]:
            for entry in memory_list:
                entry["timestamp"] = entry["timestamp"].isoformat() if isinstance(entry["timestamp"], datetime) else entry["timestamp"]
        
        for user_memory in data["user_memories"].values():
            if user_memory["last_interaction"]:
                user_memory["last_interaction"] = user_memory["last_interaction"].isoformat() if isinstance(user_memory["last_interaction"], datetime) else user_memory["last_interaction"]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str):
        """Load context data from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert strings back to datetime objects
            self.short_term_memory = []
            for entry_data in data.get("short_term_memory", []):
                entry_data["timestamp"] = datetime.fromisoformat(entry_data["timestamp"])
                self.short_term_memory.append(ConversationEntry(**entry_data))
            
            self.long_term_memory = []
            for entry_data in data.get("long_term_memory", []):
                entry_data["timestamp"] = datetime.fromisoformat(entry_data["timestamp"])
                self.long_term_memory.append(ConversationEntry(**entry_data))
            
            self.user_memories = {}
            for uid, memory_data in data.get("user_memories", {}).items():
                if memory_data["last_interaction"]:
                    memory_data["last_interaction"] = datetime.fromisoformat(memory_data["last_interaction"])
                self.user_memories[uid] = UserMemory(**memory_data)
            
            self.conversation_topics = data.get("conversation_topics", [])
            self.session_start = datetime.fromisoformat(data.get("session_start", datetime.now().isoformat()))
            
        except FileNotFoundError:
            print(f"Context file {filepath} not found. Starting with fresh context.")
        except Exception as e:
            print(f"Error loading context file: {e}")

# Create main instance for usage
cynthia_context = ContextManager()
