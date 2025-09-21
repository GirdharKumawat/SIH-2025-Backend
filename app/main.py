from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
from app.database import connect_to_mongo
from app.routers import auth, users, groups
import uvicorn

app = FastAPI(title="Chat App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"]
    )



app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api/users")
app.include_router(groups.router, prefix="/api/groups")

@app.on_event("startup")
async def startup():
    connect_to_mongo()

@app.get("/")
async def root():
    return {"message": "Chat App API"}


# Add trusted host middleware for production

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])

 
# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Chat Application API",
        "version": "1.0.0",
        "environment": settings.environment
    }
 

if __name__ == "__main__":
 
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )