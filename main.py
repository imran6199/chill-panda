from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router

app = FastAPI()
app = FastAPI(title="ChillPanda - Phase1 Backend")
# Allow Streamlit and local dev origins
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# then include router:
app.include_router(router)

@app.get('/')
def home():
    return {'message': 'Chill Panda Backend Running'}