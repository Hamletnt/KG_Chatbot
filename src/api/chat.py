from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Generator
import uuid
import logging
import json
import asyncio

from ..models.schemas import ChatRequest, ChatResponse, HealthResponse
from ..services.graph_rag import GraphRAGService

logger = logging.getLogger(__name__)
router = APIRouter()

# Global service instance
graph_rag_service = None

def get_graph_rag_service() -> GraphRAGService:
    global graph_rag_service
    if graph_rag_service is None:
        graph_rag_service = GraphRAGService()
    return graph_rag_service

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: GraphRAGService = Depends(get_graph_rag_service)
):
    """Chat endpoint for interacting with the RAG system"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get response from the service
        response = service.chat(request.message)
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            sources=None  # You can enhance this to return actual sources
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    service: GraphRAGService = Depends(get_graph_rag_service)
):
    """Streaming chat endpoint for real-time responses"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        def generate_response() -> Generator[str, None, None]:
            try:
                # Get full response
                full_response = service.chat(request.message)
                
                # Stream the response word by word with delay
                words = full_response.split()
                
                # Send initial message to show bot is typing
                initial_data = {
                    "type": "start",
                    "content": "",
                    "conversation_id": conversation_id,
                    "is_final": False
                }
                yield f"data: {json.dumps(initial_data)}\n\n"
                
                # Stream words with appropriate delay
                for i, word in enumerate(words):
                    chunk_data = {
                        "type": "token",
                        "content": word + " ",
                        "conversation_id": conversation_id,
                        "is_final": False
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    
                    # Variable delay based on word length and position
                    import time
                    base_delay = 0.03  # 30ms base delay
                    word_delay = len(word) * 0.01  # Additional delay for longer words
                    punctuation_delay = 0.15 if word.rstrip()[-1:] in '.!?' else 0
                    
                    total_delay = base_delay + word_delay + punctuation_delay
                    time.sleep(min(total_delay, 0.2))  # Max 200ms delay
                    
                # Send final message
                final_data = {
                    "type": "final",
                    "content": full_response,
                    "conversation_id": conversation_id,
                    "is_final": True
                }
                yield f"data: {json.dumps(final_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "content": "Sorry, I encountered an error while processing your request.",
                    "conversation_id": conversation_id,
                    "is_final": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    
    except Exception as e:
        logger.error(f"Streaming chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: GraphRAGService = Depends(get_graph_rag_service)
):
    """Health check endpoint"""
    try:
        health_data = service.health_check()
        return HealthResponse(**health_data)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
