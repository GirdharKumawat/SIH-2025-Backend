from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.users.routes import user_router

# Initialize FastAPI app
app = FastAPI(title="Chat App API")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/users")

# Run command:
# uvicorn main:app --reload