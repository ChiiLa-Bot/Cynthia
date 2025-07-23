from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables FIRST
load_dotenv()

# Set API key directly if needed
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "AIzaSyCNkIw_Q3o62TcXmoRKFlD3S4CW4fMBr80"

from ai_brain import get_cynthia_brain, AIBrain

# Create FastAPI app
app = FastAPI(
    title="Cynthia AI Companion",
    description="AI Companion with 2D Avatar and Voice Interaction",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Brain (lazy initialization)
ai_brain = None

def get_ai_brain():
    """Get or initialize the AI brain instance"""
    global ai_brain
    if ai_brain is None:
        ai_brain = get_cynthia_brain()
    return ai_brain

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ModeRequest(BaseModel):
    mode: str

@app.get("/")
async def root():
    return {"message": "Cynthia AI Companion Backend is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "gemini-2.5-flash"}

@app.post("/mode")
async def change_mode(request: ModeRequest):
    """Change interaction mode (safe/nsfw)"""
    try:
        brain = get_ai_brain()
        result = brain.set_interaction_mode(request.mode)
        return result
    except Exception as e:
        logger.error(f"Error changing mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Get comprehensive system status"""
    try:
        brain = get_ai_brain()
        return brain.get_status()
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_conversation():
    """Reset conversation context"""
    try:
        brain = get_ai_brain()
        brain.reset_conversation()
        return {"status": "success", "message": "Conversation reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Use AI Brain to process input
        brain = get_ai_brain()
        response_data = brain.process_input(request.message)
        
        return {
            "response": response_data["response"],
            "emotion": response_data["emotion"]["primary"],
            "animation": response_data["emotion"]["animation"],
            "intensity": response_data["emotion"]["intensity"],
            "mode": response_data["personality"]["current_mode"]
        }
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            
            try:
                # Parse JSON message
                import json
                message_data = json.loads(data)
                user_message = message_data.get("content", data)
                
                # Process with AI Brain
                brain = get_ai_brain()
                response_data = brain.process_input(user_message)
                
                # Send JSON response back
                response_json = {
                    "type": "message",
                    "content": response_data["response"],
                    "emotion": response_data["emotion"]["primary"],
                    "animation": response_data["emotion"]["animation"]
                }
                
                await websocket.send_text(json.dumps(response_json))
                
            except json.JSONDecodeError:
                # Handle plain text messages
                brain = get_ai_brain()
                response_data = brain.process_input(data)
                response_json = {
                    "type": "message", 
                    "content": response_data["response"]
                }
                await websocket.send_text(json.dumps(response_json))
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")

# Simple web interface for testing
@app.get("/test", response_class=HTMLResponse)
async def get_test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cynthia AI Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .message { margin: 5px 0; padding: 5px; }
            .user { background-color: #e3f2fd; border-radius: 5px; }
            .cynthia { background-color: #f3e5f5; border-radius: 5px; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; margin-left: 10px; }
        </style>
    </head>
    <body>
        <h1>🎭 Cynthia AI Companion Test Interface</h1>
        <div id="chat" class="chat-container"></div>
        <input type="text" id="messageInput" placeholder="Type your message to Cynthia..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                const chatDiv = document.getElementById('chat');
                
                // Add user message
                chatDiv.innerHTML += `<div class="message user"><strong>You:</strong> ${message}</div>`;
                input.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    chatDiv.innerHTML += `<div class="message cynthia"><strong>Cynthia:</strong> ${data.response}</div>`;
                    
                } catch (error) {
                    chatDiv.innerHTML += `<div class="message cynthia"><strong>Error:</strong> ${error.message}</div>`;
                }
                
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
