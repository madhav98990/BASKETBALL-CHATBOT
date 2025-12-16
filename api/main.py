"""
FastAPI Backend for Basketball Chatbot
Provides REST API endpoint for chat functionality
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import BasketballChatbot
from database.chat_history_db import (
    create_conversation,
    save_message,
    get_conversations,
    get_conversation_messages,
    delete_conversation,
    generate_conversation_title
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Basketball AI Chatbot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = BasketballChatbot()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


class ChatMessageRequest(BaseModel):
    question: str
    conversation_id: Optional[UUID] = None


class ChatMessageResponse(BaseModel):
    answer: str
    conversation_id: UUID
    message_id: UUID


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    last_message_preview: str
    updated_at: str


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    metadata: dict
    created_at: str


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Basketball AI Chatbot API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint (backward compatible)
    Receives a question and returns an answer
    This endpoint does NOT save chat history
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Received question: {request.question}")
        
        # Process question through chatbot
        answer = chatbot.process_question(request.question)
        
        logger.info(f"Generated answer: {answer[:100]}...")
        
        return ChatResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def save_chat_to_db(conversation_id: UUID, question: str, answer: str):
    """
    Background task to save chat messages to database
    This runs AFTER the response is sent to the user
    """
    try:
        # Save user message
        save_message(conversation_id, 'user', question)
        
        # Save assistant response
        save_message(conversation_id, 'assistant', answer)
        
        logger.info(f"Saved messages to conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error saving chat to database: {e}")
        # Don't raise - this is a background task, errors shouldn't affect the user


@app.post("/chat/message", response_model=ChatMessageResponse)
def chat_message(request: ChatMessageRequest, background_tasks: BackgroundTasks):
    """
    Enhanced chat endpoint with history persistence
    Receives a question and optional conversation_id
    Returns answer and conversation_id
    Saves messages to database asynchronously
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Received question: {request.question}")
        
        # Get or create conversation
        if request.conversation_id:
            conversation_id = request.conversation_id
            # Verify conversation exists
            try:
                messages = get_conversation_messages(conversation_id, limit=1)
            except Exception:
                # Conversation doesn't exist, create new one
                title = generate_conversation_title(request.question)
                conversation_id = create_conversation(title)
        else:
            # Create new conversation
            title = generate_conversation_title(request.question)
            conversation_id = create_conversation(title)
        
        # Process question through chatbot (this is the main operation)
        answer = chatbot.process_question(request.question)
        
        logger.info(f"Generated answer: {answer[:100]}...")
        
        # Save messages in background (non-blocking)
        background_tasks.add_task(save_chat_to_db, conversation_id, request.question, answer)
        
        # Generate a temporary message ID (actual ID will be created in background task)
        import uuid
        message_id = uuid.uuid4()
        
        return ChatMessageResponse(
            answer=answer,
            conversation_id=conversation_id,
            message_id=message_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat message endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/chat/conversations", response_model=List[ConversationResponse])
def get_conversations_list(user_id: Optional[UUID] = None, limit: int = 50):
    """
    Get list of conversations
    Optional user_id filter (for future multi-user support)
    """
    try:
        conversations = get_conversations(user_id=user_id, limit=limit)
        return [ConversationResponse(**conv) for conv in conversations]
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/chat/conversation/{conversation_id}", response_model=List[MessageResponse])
def get_conversation(conversation_id: UUID, limit: int = 50, offset: int = 0):
    """
    Get messages for a specific conversation
    Supports pagination with limit and offset
    """
    try:
        messages = get_conversation_messages(conversation_id, limit=limit, offset=offset)
        return [MessageResponse(**msg) for msg in messages]
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/chat/conversation/{conversation_id}")
def delete_conversation_endpoint(conversation_id: UUID):
    """
    Delete a conversation and all its messages
    """
    try:
        deleted = delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "success", "message": "Conversation deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

