from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.controller import user_router
from app.messages.controller import message_router
from app.hq.routes import hq_router
from app.logs.routes import log_router

# Initialize FastAPI app
app = FastAPI(title="Chat App API")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/users")
app.include_router(message_router, prefix="/api/messages")
app.include_router(hq_router, prefix="/api/hq")
app.include_router(log_router, prefix="/api/logs")
# Run command:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload