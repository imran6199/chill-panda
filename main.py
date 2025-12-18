from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.mongodb_manager import mongodb_manager
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ChillPanda - Mental Health Companion with RAG")

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get('/')
def home():
    return {
        'message': 'Chill Panda Backend Running',
        'version': '1.0.0',
        'features': ['RAG', 'MongoDB', 'Pinecone', 'Chat History']
    }

@app.get('/health')
def health_check():
    try:
        # Check MongoDB connection
        mongodb_manager.client.admin.command('ping')
        return {
            'status': 'healthy',
            'database': 'connected',
            'service': 'Chill Panda API'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    mongodb_manager.close()