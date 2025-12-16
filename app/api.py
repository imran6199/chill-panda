from fastapi import APIRouter, Depends
from .auth import verify_key
from .schemas import ChatRequest, ChatResponse
from .chat import generate_ai_reply

router = APIRouter(prefix="/api/v1")

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _=Depends(verify_key)):
    ai_reply = generate_ai_reply(
        user_message=req.input_text,
        language=req.language
    )

    return ChatResponse(reply=ai_reply)

