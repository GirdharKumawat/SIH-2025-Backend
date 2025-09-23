from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.users.controller import user_router
from app.messages.controller import message_router

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
app.include_router(message_router, prefix="/api/messages")

# Run command:
# uvicorn main:app --reload