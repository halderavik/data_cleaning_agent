"""
Database initialization script for the Survey Cleaning application.
This script creates the database and initializes the tables.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

from backend.database.base import Base
from backend.models import *  # Import all models

def init_database():
    """
    Initialize the database by creating all tables.
    """
    load_dotenv()
    
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/survey_cleaning")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        # Create database if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text("COMMIT"))  # Close any open transactions
            conn.execute(text("CREATE DATABASE survey_cleaning"))
    except ProgrammingError:
        print("Database already exists or could not be created.")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database() 