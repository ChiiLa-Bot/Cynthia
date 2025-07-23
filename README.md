# Cynthia AI Companion Project

A sophisticated 2D AI Companion with advanced personality, emotion system, and real-time interaction capabilities. Cynthia is designed to provide natural, engaging conversations with a unique personality that combines cheerfulness, playfulness, and tsundere characteristics.

## About This Project

Cynthia is an AI companion system that creates meaningful interactions through advanced personality modeling and emotional intelligence. The project focuses on building a relatable AI character that can maintain context, express emotions naturally, and adapt to different conversation modes while maintaining consistent personality traits.

## Core Features

### AI Brain System
- **Advanced Personality Engine** - Multi-layered personality with cheerful, playful, shy, and tsundere characteristics
- **Dynamic Emotion System** - 12 different emotions with realistic transitions and natural triggers
- **Context Management** - Long-term and short-term memory with user relationship tracking
- **Dual Mode Support** - Safe mode and NSFW mode with intelligent content filtering

### Personality Traits
- **Cheerfulness** (80%) - Bright and positive demeanor
- **Playfulness** (70%) - Enjoys games and fun interactions
- **Shyness** (60%) - Gets bashful with compliments and intimate topics
- **Tsundere Level** (50%) - Sometimes acts tough but is genuinely caring
- **Caring Level** (90%) - Very supportive and nurturing toward users
- **Curiosity** (80%) - Eager to learn and explore new topics

### Emotion System
Cynthia can experience and express: Happy, Excited, Shy, Playful, Caring, Curious, Embarrassed, Confident, Gentle, Mischievous, Tsundere, and Romantic emotions. Each emotion includes natural triggers, appropriate responses, realistic intensity levels, and smooth transitions.

### Memory & Context
- **Short-term Memory** - Recent conversation history (50 entries)
- **Long-term Memory** - Important moments and interactions (200 entries)
- **User Profiles** - Names, preferences, and relationship development
- **Topic Tracking** - Current conversation themes and context
- **Importance Scoring** - Automatically identifies significant interactions

## Future Development Plans

### Phase 3: 2D Avatar System
- Live2D model integration for visual representation
- Animation controller with emotion-to-visual mapping
- Real-time facial expressions and gesture system

### Phase 4: Voice Integration
- Speech-to-Text for voice input processing
- Text-to-Speech with emotion-aware voice modulation
- Real-time voice interaction capabilities

### Phase 5: Enhanced Web Interface
- Modern frontend with React/Vue.js
- Live2D model display and interaction
- Complete user interface with chat history and settings

## Getting Started

### Prerequisites
- Python 3.10.7 or higher
- Node.js and npm
- Gemini API key

### Backend Setup

1. **Navigate to backend directory**
   ```cmd
   cd backend
   ```

2. **Activate virtual environment**
   ```cmd
   venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env` (if available)
   - Add your Gemini API key to the `.env` file
   - Adjust other settings as needed

5. **Start the backend server**
   ```cmd
   python main.py
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```cmd
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```cmd
   npm install
   ```

3. **Start the development server**
   ```cmd
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## API Documentation

### Core Endpoints
- `GET /` - Health check and basic information
- `GET /health` - Detailed system status
- `GET /test` - Interactive chat interface for testing

### AI Interaction
- `POST /chat` - Send message to Cynthia and receive response
- `POST /mode` - Switch between safe and NSFW interaction modes
- `GET /status` - Get comprehensive system status and statistics
- `POST /reset` - Reset conversation context and memory

### WebSocket
- `WS /ws` - Real-time communication channel for live interactions

## Testing the System

### Basic Chat Test
1. Open browser to `http://localhost:8000/test`
2. Type messages to interact with Cynthia
3. Observe emotional responses and personality traits in action

### API Testing
```bash
# Test basic chat
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"message": "Hello Cynthia!"}'

# Switch modes
curl -X POST "http://localhost:8000/mode" -d "mode=nsfw"
curl -X POST "http://localhost:8000/mode" -d "mode=safe"

# Check system status
curl http://localhost:8000/status
```

## Project Structure

```
Cynthia-project/
├── backend/
│   ├── ai_brain/
│   │   ├── personality_engine.py    # Core personality system
│   │   ├── emotion_engine.py        # Emotion processing
│   │   ├── context_manager.py       # Memory and context
│   │   ├── llm_integration.py       # AI model integration
│   │   └── natural_communication.py # Communication processing
│   ├── api/                         # API endpoints
│   ├── voice_system/               # Voice processing (future)
│   ├── main.py                     # FastAPI server
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Configuration
├── frontend/
│   ├── src/                        # Vue.js source code
│   ├── public/                     # Static assets
│   ├── package.json               # Node.js dependencies
│   └── vite.config.js             # Build configuration
└── docs/                          # Documentation
```

## Configuration

### Personality Customization
Edit `backend/ai_brain/personality_engine.py` to adjust personality traits, emotional triggers, and behavioral patterns.

### Emotion Tuning
Modify `backend/ai_brain/emotion_engine.py` to customize emotion triggers, response intensity, and transition behaviors.

### API Settings
Update `backend/.env` file to configure API keys, server settings, and other environment-specific variables.

---

**Current Status**: AI Brain System Complete  
**Technology Stack**: Python FastAPI, Vue.js, Gemini AI  
**License**: Apache License