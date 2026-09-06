from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ask import router as ask_router
from app.api.repository import router as repository_router


app = FastAPI(
    title="CodeAtlas",
    description="AI-powered codebase intelligence platform",
    version="0.1.0",
)


# ---------------------------------------------------------
# CORS
# Allow the React/Vite frontend to communicate with FastAPI
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeAtlas",
    }


# ---------------------------------------------------------
# API routes
# ---------------------------------------------------------

app.include_router(ask_router)
app.include_router(repository_router)