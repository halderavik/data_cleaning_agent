from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
import os
from app.core.config import settings
from app.models.ai_model import AIModel, ModelVersion
from app.database import get_db
import httpx

class AIService:
    """Service for handling advanced AI capabilities."""
    
    def __init__(self):
        self.models_dir = os.getenv('MODEL_STORAGE_PATH', './models')
        self.scaler = StandardScaler()
        self.ensemble_model = None
        self.pattern_detector = None
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL')
        self.deepseek_model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.use_deepseek = os.getenv('USE_DEEPSEEK', 'false').lower() == 'true'
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize or load existing models."""
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Load or create ensemble model
        ensemble_path = os.path.join(self.models_dir, "ensemble_model.joblib")
        if os.path.exists(ensemble_path):
            self.ensemble_model = joblib.load(ensemble_path)
        else:
            self._create_ensemble_model()
        
        # Load or create pattern detector
        pattern_path = os.path.join(self.models_dir, "pattern_detector.h5")
        if os.path.exists(pattern_path):
            self.pattern_detector = load_model(pattern_path)
        else:
            self._create_pattern_detector()
    
    def _create_ensemble_model(self):
        """Create a new ensemble model."""
        rf1 = RandomForestClassifier(n_estimators=100, random_state=42)
        rf2 = RandomForestClassifier(n_estimators=200, random_state=42)
        rf3 = RandomForestClassifier(n_estimators=300, random_state=42)
        
        self.ensemble_model = VotingClassifier(
            estimators=[
                ('rf1', rf1),
                ('rf2', rf2),
                ('rf3', rf3)
            ],
            voting='soft'
        )
    
    def _create_pattern_detector(self):
        """Create a new pattern detection model."""
        self.pattern_detector = Sequential([
            LSTM(64, input_shape=(100, 10), return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.pattern_detector.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
    
    async def detect_patterns(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Detect patterns in the data using the pattern detector model.
        
        Args:
            data: Input data array
            
        Returns:
            Dict containing pattern detection results
        """
        try:
            # Preprocess data
            scaled_data = self.scaler.fit_transform(data)
            reshaped_data = scaled_data.reshape(-1, 100, 10)
            
            # Make predictions
            predictions = self.pattern_detector.predict(reshaped_data)
            
            return {
                "patterns": predictions.tolist(),
                "confidence": float(np.mean(predictions)),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "patterns": [],
                "confidence": 0.0,
                "timestamp": datetime.utcnow()
            }
    
    async def ensemble_predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Make predictions using the ensemble model.
        
        Args:
            features: Input features array
            
        Returns:
            Dict containing ensemble prediction results
        """
        try:
            # Preprocess features
            scaled_features = self.scaler.transform(features)
            
            # Get predictions from each model
            predictions = []
            for name, model in self.ensemble_model.named_estimators_.items():
                pred = model.predict_proba(scaled_features)
                predictions.append(pred)
            
            # Combine predictions
            ensemble_pred = np.mean(predictions, axis=0)
            
            return {
                "predictions": ensemble_pred.tolist(),
                "confidence": float(np.max(ensemble_pred)),
                "model_contributions": {
                    name: float(np.mean(pred))
                    for name, pred in zip(self.ensemble_model.named_estimators_.keys(), predictions)
                },
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "predictions": [],
                "confidence": 0.0,
                "model_contributions": {},
                "timestamp": datetime.utcnow()
            }
    
    async def adapt_to_new_data(self, new_data: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """
        Adapt models to new data through incremental learning.
        
        Args:
            new_data: New training data
            labels: Corresponding labels
            
        Returns:
            Dict containing adaptation results
        """
        try:
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                new_data, labels, test_size=0.2, random_state=42
            )
            
            # Update ensemble model
            self.ensemble_model.fit(X_train, y_train)
            
            # Update pattern detector
            scaled_data = self.scaler.fit_transform(X_train)
            reshaped_data = scaled_data.reshape(-1, 100, 10)
            self.pattern_detector.fit(
                reshaped_data, y_train,
                validation_split=0.2,
                epochs=10,
                batch_size=32,
                verbose=0
            )
            
            # Save updated models
            joblib.dump(self.ensemble_model, os.path.join(self.models_dir, "ensemble_model.joblib"))
            self.pattern_detector.save(os.path.join(self.models_dir, "pattern_detector.h5"))
            
            # Create new model version record
            db = next(get_db())
            model_version = ModelVersion(
                version="1.0.0",
                model_type="ensemble",
                performance_metrics={
                    "accuracy": float(self.ensemble_model.score(X_val, y_val)),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            db.add(model_version)
            db.commit()
            
            return {
                "status": "success",
                "new_version": model_version.version,
                "performance_metrics": model_version.performance_metrics,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow()
            }
    
    async def get_model_metrics(self) -> Dict[str, Any]:
        """Get current model performance metrics."""
        try:
            db = next(get_db())
            latest_version = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).first()
            
            return {
                "current_version": latest_version.version if latest_version else "1.0.0",
                "metrics": latest_version.performance_metrics if latest_version else {},
                "last_updated": latest_version.created_at if latest_version else datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "current_version": "unknown",
                "metrics": {},
                "last_updated": datetime.utcnow()
            }
    
    async def call_deepseek(self, prompt: str) -> Dict[str, Any]:
        """
        Call DeepSeek API for chat/completion.
        Args:
            prompt: The input prompt for the model.
        Returns:
            Dict containing DeepSeek response or error.
        """
        if not self.deepseek_api_key or not self.deepseek_base_url:
            return {"error": "DeepSeek API key or base URL not set in environment."}
        url = f"{self.deepseek_base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.deepseek_model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                return {"response": data}
        except Exception as e:
            return {"error": str(e)} 