from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    input_text: str
    language: str

class ChatResponse(BaseModel):
    reply: str