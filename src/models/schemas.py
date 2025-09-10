from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """Model for chat request"""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")

class ChatResponse(BaseModel):
    """Model for chat response"""
    response: str = Field(..., description="Bot's response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: Optional[List[str]] = Field(None, description="Source information used")

class Entities(BaseModel):
    """Identifying information about entities."""
    names: List[str] = Field(
        ...,
        description="All the person, organization, or business entities that appear in the text",
    )

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    neo4j_connected: bool = Field(..., description="Neo4j connection status")
    azure_openai_configured: bool = Field(..., description="Azure OpenAI configuration status")
