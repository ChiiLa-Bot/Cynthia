# Cynthia AI Companion Project 🎭

A sophisticated 2D AI Companion with advanced personality, emotion system, and real-time interaction capabilities.

## ✨ Features Implemented

### 🧠 AI Brain System

- **Advanced Personality Engine** - Cheerful, playful, slightly shy, and tsundere characteristics
- **Dynamic Emotion System** - 12 different emotions with realistic transitions
- **Context Management** - Long-term and short-term memory with user relationship tracking
- **Dual Mode Support** - Safe mode and NSFW mode with content filtering control

### 🎭 Personality Traits

- **Cheerfulness**: 80% - Bright and positive demeanor
- **Playfulness**: 70% - Loves games and fun interactions
- **Shyness**: 60% - Gets bashful with compliments
- **Tsundere Level**: 50% - Sometimes acts tough but is actually caring
- **Caring Level**: 90% - Very supportive and nurturing
- **Curiosity**: 80% - Eager to learn and explore

### 😊 Emotion System

Cynthia can experience and express:

- Happy, Excited, Shy, Playful
- Caring, Curious, Embarrassed, Confident
- Gentle, Mischievous, Tsundere, Romantic

Each emotion has:

- Natural triggers from user input
- Appropriate animations and expressions
- Realistic intensity and transitions
- Context-aware responses

### 🧠 Context Awareness

- **Short-term Memory**: Recent conversation (50 entries)
- **Long-term Memory**: Important moments (200 entries)
- **User Profiles**: Names, preferences, relationship levels
- **Topic Tracking**: Current conversation themes
- **Importance Scoring**: Automatically identifies significant interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.10.7 ✅
- Node.js and npm ✅
- Gemini API key ✅

### Installation & Setup

1. **Navigate to project directory**

   ```cmd
   cd Cynthia-project\backend
   ```

2. **Activate virtual environment**

   ```cmd
   venv\Scripts\activate
   ```

3. **Install dependencies** (Already done ✅)

   ```cmd
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   - API key is already configured ✅
   - Edit `.env` file if needed

5. **Run the server**
   ```cmd
   python main.py
   ```

## 🌐 API Endpoints

### Core Endpoints

- `GET /` - Health check
- `GET /health` - System status
- `GET /test` - Interactive chat interface

### AI Interaction

- `POST /chat` - Send message to Cynthia
- `POST /mode` - Change interaction mode (safe/nsfw)
- `GET /status` - Get comprehensive system status
- `POST /reset` - Reset conversation context

### WebSocket

- `WS /ws` - Real-time communication

## 🧪 Testing

### Basic Chat Test

1. Open browser to `http://localhost:8000/test`
2. Type messages to interact with Cynthia
3. Observe emotional responses and personality traits

### Mode Switching

```bash
curl -X POST "http://localhost:8000/mode" -d "mode=nsfw"
curl -X POST "http://localhost:8000/mode" -d "mode=safe"
```

### Status Check

```bash
curl http://localhost:8000/status
```

## 📊 Current Status: Phase 2 Complete! 🎉

### ✅ Phase 1: Environment Setup (COMPLETED)

- ✅ Python 3.10.7 environment
- ✅ Virtual environment configuration
- ✅ All required packages installed
- ✅ Project structure created

### ✅ Phase 2: AI Brain Development (COMPLETED)

- ✅ **Personality Engine** - Complete with all traits
- ✅ **Emotion System** - 12 emotions with transitions
- ✅ **Context Manager** - Memory and user tracking
- ✅ **LLM Integration** - Gemini 2.5 Flash implementation
- ✅ **Mode System** - Safe/NSFW mode switching
- ✅ **FastAPI Backend** - All endpoints functional

### 🚧 Phase 3: 2D Avatar System (NEXT)

- ⏳ Live2D model integration
- ⏳ Animation controller
- ⏳ Emotion-to-animation mapping

### 🛠️ Technical Architecture

```
Cynthia-project/
├── backend/
│   ├── ai_brain/
│   │   ├── personality_engine.py     ✅ Complete
│   │   ├── emotion_engine.py         ✅ Complete
│   │   ├── context_manager.py        ✅ Complete
│   │   └── llm_integration.py        ✅ Complete
│   ├── main.py                       ✅ FastAPI server
│   ├── requirements.txt              ✅ All dependencies
│   └── .env                          ✅ Configuration
├── venv/                             ✅ Virtual environment
└── README.md                         ✅ Documentation
```

## 💡 Key Achievements

1. **Advanced AI Personality** - Cynthia has a complex, multi-layered personality
2. **Emotional Intelligence** - Natural emotion detection and expression
3. **Memory System** - Remembers conversations and builds relationships
4. **Flexible Content Modes** - Can switch between safe and unrestricted content
5. **Real-time Interaction** - WebSocket support for live communication
6. **Scalable Architecture** - Modular design for easy expansion

## 🎯 Next Development Phases

### Phase 3: 2D Avatar System (Weeks 5-6)

- Live2D model creation and integration
- Animation system with emotion mapping
- Real-time facial expressions and gestures

### Phase 4: Voice System (Weeks 7-8)

- Speech-to-Text integration
- Text-to-Speech with emotion-aware voice
- Real-time voice interaction

### Phase 5: Web Interface (Weeks 9-10)

- React/Vue.js frontend
- Live2D model display
- Complete user interface

## 🔧 Configuration

### Personality Customization

Edit `backend/ai_brain/personality_engine.py` to adjust:

- Trait levels (cheerfulness, playfulness, etc.)
- Emotional triggers and responses
- Interaction modes and behaviors

### Emotion Tuning

Modify `backend/ai_brain/emotion_engine.py` for:

- Emotion triggers and keywords
- Response intensity and duration
- Animation mappings

## 📝 Development Notes

- **Model**: Using Gemini 2.5 Flash for optimal performance
- **Language**: All code and documentation in English
- **Architecture**: Modular design for easy maintenance
- **Memory**: Intelligent context management with importance scoring
- **Personality**: Detailed tsundere characteristics with natural shyness
- **Purpose**: AI Companion system for personal interaction and relationship building

---

**Current Phase**: ✅ Phase 2 Complete - Advanced AI Brain System  
**Next Milestone**: Phase 3 - 2D Avatar Integration  
**Total Progress**: 28% Complete (2/7 phases)

_Cynthia - Your Personal AI Companion_  
_Last Updated: July 21, 2025_
