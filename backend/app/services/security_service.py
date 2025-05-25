from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.security import AuditLog, EncryptionKey, AccessControl
from app.database import get_db

class SecurityService:
    """Service for handling enterprise security features."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encryption_key = self._load_or_create_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _load_or_create_key(self) -> bytes:
        """Load existing encryption key or create a new one."""
        try:
            db = next(get_db())
            key_record = db.query(EncryptionKey).first()
            
            if key_record:
                return base64.urlsafe_b64decode(key_record.key)
            
            # Generate new key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
            
            # Save new key
            key_record = EncryptionKey(
                key=key.decode(),
                salt=salt.hex(),
                created_at=datetime.utcnow()
            )
            db.add(key_record)
            db.commit()
            
            return key
        except Exception as e:
            self.logger.error(f"Error loading/creating encryption key: {str(e)}")
            raise
    
    async def encrypt_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Dictionary containing data to encrypt
            
        Returns:
            str: Encrypted data as base64 string
        """
        try:
            json_data = json.dumps(data)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Dict[str, Any]: Decrypted data
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted_bytes.decode())
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            raise
    
    async def log_audit_event(
        self,
        event_type: str,
        user_id: str,
        resource_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (e.g., 'login', 'data_access')
            user_id: ID of the user performing the action
            resource_id: ID of the resource being accessed
            action: Action performed
            details: Optional additional details
        """
        try:
            db = next(get_db())
            audit_log = AuditLog(
                event_type=event_type,
                user_id=user_id,
                resource_id=resource_id,
                action=action,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            self.logger.error(f"Error logging audit event: {str(e)}")
            raise
    
    async def check_access(
        self,
        user_id: str,
        resource_id: str,
        action: str
    ) -> bool:
        """
        Check if a user has access to a resource.
        
        Args:
            user_id: ID of the user
            resource_id: ID of the resource
            action: Action being attempted
            
        Returns:
            bool: True if access is granted, False otherwise
        """
        try:
            db = next(get_db())
            access_control = db.query(AccessControl).filter(
                AccessControl.user_id == user_id,
                AccessControl.resource_id == resource_id,
                AccessControl.action == action
            ).first()
            
            return bool(access_control)
        except Exception as e:
            self.logger.error(f"Error checking access: {str(e)}")
            raise
    
    async def get_audit_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with optional filtering.
        
        Args:
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            event_type: Optional event type for filtering
            user_id: Optional user ID for filtering
            
        Returns:
            List[Dict[str, Any]]: List of audit log entries
        """
        try:
            db = next(get_db())
            query = db.query(AuditLog)
            
            if start_time:
                query = query.filter(AuditLog.timestamp >= start_time)
            if end_time:
                query = query.filter(AuditLog.timestamp <= end_time)
            if event_type:
                query = query.filter(AuditLog.event_type == event_type)
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            logs = query.order_by(AuditLog.timestamp.desc()).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            self.logger.error(f"Error retrieving audit logs: {str(e)}")
            raise
    
    async def rotate_encryption_key(self) -> None:
        """Rotate the encryption key."""
        try:
            # Generate new key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            new_key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
            
            # Save new key
            db = next(get_db())
            key_record = EncryptionKey(
                key=new_key.decode(),
                salt=salt.hex(),
                created_at=datetime.utcnow()
            )
            db.add(key_record)
            db.commit()
            
            # Update instance key
            self.encryption_key = new_key
            self.fernet = Fernet(self.encryption_key)
        except Exception as e:
            self.logger.error(f"Error rotating encryption key: {str(e)}")
            raise 