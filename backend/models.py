from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.database.base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='analyst')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    cleaning_results = relationship("CleaningResult", back_populates="project")

class DataFile(Base):
    __tablename__ = 'data_files'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    upload_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cleaning_results = relationship("CleaningResult", back_populates="data_file")

class CleaningCheck(Base):
    __tablename__ = 'cleaning_checks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    is_standard = Column(Boolean, default=True)
    check_function = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CleaningResult(Base):
    __tablename__ = 'cleaning_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    data_file_id = Column(UUID(as_uuid=True), ForeignKey('data_files.id'), nullable=False)
    check_id = Column(UUID(as_uuid=True), ForeignKey('cleaning_checks.id'), nullable=False)
    status = Column(String(50), default='pending')
    issues_found = Column(Integer, default=0)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    project = relationship("Project", back_populates="cleaning_results")
    data_file = relationship("DataFile", back_populates="cleaning_results")
    check = relationship("CleaningCheck") 