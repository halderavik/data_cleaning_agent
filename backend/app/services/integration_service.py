from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
import requests
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.integration import Integration, IntegrationLog
from app.database import get_db

class IntegrationService:
    """Service for handling third-party integrations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def create_integration(
        self,
        name: str,
        integration_type: str,
        config: Dict[str, Any],
        db: Session
    ) -> Integration:
        """
        Create a new integration.
        
        Args:
            name: Name of the integration
            integration_type: Type of integration (e.g., 'api', 'webhook')
            config: Configuration for the integration
            db: Database session
            
        Returns:
            Integration: Created integration
        """
        try:
            integration = Integration(
                name=name,
                integration_type=integration_type,
                config=config,
                created_at=datetime.utcnow()
            )
            db.add(integration)
            db.commit()
            db.refresh(integration)
            return integration
        except Exception as e:
            self.logger.error(f"Error creating integration: {str(e)}")
            raise
    
    async def get_integration(
        self,
        integration_id: str,
        db: Session
    ) -> Optional[Integration]:
        """
        Get an integration by ID.
        
        Args:
            integration_id: ID of the integration
            db: Database session
            
        Returns:
            Optional[Integration]: Integration if found, None otherwise
        """
        try:
            return db.query(Integration).filter(Integration.id == integration_id).first()
        except Exception as e:
            self.logger.error(f"Error getting integration: {str(e)}")
            raise
    
    async def update_integration(
        self,
        integration_id: str,
        config: Dict[str, Any],
        db: Session
    ) -> Optional[Integration]:
        """
        Update an integration's configuration.
        
        Args:
            integration_id: ID of the integration
            config: New configuration
            db: Database session
            
        Returns:
            Optional[Integration]: Updated integration if found, None otherwise
        """
        try:
            integration = await self.get_integration(integration_id, db)
            if integration:
                integration.config = config
                integration.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(integration)
            return integration
        except Exception as e:
            self.logger.error(f"Error updating integration: {str(e)}")
            raise
    
    async def delete_integration(
        self,
        integration_id: str,
        db: Session
    ) -> bool:
        """
        Delete an integration.
        
        Args:
            integration_id: ID of the integration
            db: Database session
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            integration = await self.get_integration(integration_id, db)
            if integration:
                db.delete(integration)
                db.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting integration: {str(e)}")
            raise
    
    async def make_api_request(
        self,
        integration: Integration,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request to an integrated service.
        
        Args:
            integration: Integration to use
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Optional request data
            headers: Optional request headers
            
        Returns:
            Dict[str, Any]: API response
        """
        try:
            base_url = integration.config.get("base_url")
            api_key = integration.config.get("api_key")
            
            if not base_url:
                raise ValueError("Integration missing base_url configuration")
            
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            request_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}" if api_key else "",
                **(headers or {})
            }
            
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers
            )
            
            # Log the request
            db = next(get_db())
            log = IntegrationLog(
                integration_id=integration.id,
                request_method=method,
                request_url=url,
                request_data=data,
                response_status=response.status_code,
                response_data=response.json() if response.text else None,
                timestamp=datetime.utcnow()
            )
            db.add(log)
            db.commit()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error making API request: {str(e)}")
            raise
    
    async def get_integration_logs(
        self,
        integration_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Get logs for an integration.
        
        Args:
            integration_id: ID of the integration
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            db: Database session
            
        Returns:
            List[Dict[str, Any]]: List of integration logs
        """
        try:
            query = db.query(IntegrationLog).filter(
                IntegrationLog.integration_id == integration_id
            )
            
            if start_time:
                query = query.filter(IntegrationLog.timestamp >= start_time)
            if end_time:
                query = query.filter(IntegrationLog.timestamp <= end_time)
            
            logs = query.order_by(IntegrationLog.timestamp.desc()).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            self.logger.error(f"Error getting integration logs: {str(e)}")
            raise 