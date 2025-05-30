from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database.base import get_db, engine, Base
from backend.routers import users, auth, projects, files
from backend.routes import cleaning
from backend.routes import analysis

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Survey Data Cleaning API",
    description="API for cleaning and validating survey data files",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(files.router)
app.include_router(cleaning.router, prefix="/cleaning", tags=["Cleaning"])
app.include_router(analysis.router)

@app.get("/")
async def root():
    """
    Root endpoint to verify API is running.
    
    Returns:
        dict: Status message
    """
    return {"status": "ok", "message": "Survey Data Cleaning API is running"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connection.
    
    Args:
        db (Session): Database session
        
    Returns:
        dict: Health status
    """
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        } 