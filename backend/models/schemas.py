"""
Pydantic request and response schemas for the chat API.

These models enforce input validation and provide a consistent
serialisation contract for the REST endpoints.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat question from the client."""

    question: str = Field(
        ...,
        min_length=1,
        description="The user's natural-language question.",
    )


class Source(BaseModel):
    """Reference to the document page a chunk was extracted from."""

    filename: str = Field(..., description="Original PDF filename.")
    page: int = Field(..., description="1-indexed page number within the PDF.")


class ChatResponse(BaseModel):
    """Structured response returned to the client."""

    answer: str = Field(..., description="LLM-generated answer text.")
    sources: list[Source] = Field(
        default_factory=list,
        description="List of document sources used to compose the answer.",
    )
