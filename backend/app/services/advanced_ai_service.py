from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from app.core.config import settings
from app.models.ai_model import AIModel, ModelVersion
from app.database import get_db

class AdvancedAIService:
    """Service for handling advanced AI capabilities."""
    
    def __init__(self):
        self.models_dir = settings.MODELS_DIR
        self.scaler = StandardScaler()
        self.pattern_detector = None
        self.anomaly_detector = None
        self.feature_extractor = None
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize or load existing models."""
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Load or create pattern detector
        pattern_path = os.path.join(self.models_dir, "pattern_detector.h5")
        if os.path.exists(pattern_path):
            self.pattern_detector = load_model(pattern_path)
        else:
            self._create_pattern_detector()
        
        # Load or create anomaly detector
        anomaly_path = os.path.join(self.models_dir, "anomaly_detector.joblib")
        if os.path.exists(anomaly_path):
            self.anomaly_detector = joblib.load(anomaly_path)
        else:
            self._create_anomaly_detector()
        
        # Load or create feature extractor
        feature_path = os.path.join(self.models_dir, "feature_extractor.h5")
        if os.path.exists(feature_path):
            self.feature_extractor = load_model(feature_path)
        else:
            self._create_feature_extractor()
    
    def _create_pattern_detector(self):
        """Create a new pattern detection model."""
        self.pattern_detector = Sequential([
            LSTM(128, input_shape=(100, 20), return_sequences=True),
            BatchNormalization(),
            Dropout(0.3),
            LSTM(64, return_sequences=True),
            BatchNormalization(),
            Dropout(0.3),
            LSTM(32),
            BatchNormalization(),
            Dropout(0.3),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.pattern_detector.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
    
    def _create_anomaly_detector(self):
        """Create a new anomaly detection model."""
        self.anomaly_detector = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
    
    def _create_feature_extractor(self):
        """Create a new feature extraction model."""
        self.feature_extractor = Sequential([
            Dense(64, activation='relu', input_shape=(20,)),
            BatchNormalization(),
            Dropout(0.2),
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(16, activation='relu')
        ])
        
        self.feature_extractor.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse'
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
            reshaped_data = scaled_data.reshape(-1, 100, 20)
            
            # Extract features
            features = self.feature_extractor.predict(scaled_data)
            
            # Make predictions
            predictions = self.pattern_detector.predict(reshaped_data)
            
            return {
                "patterns": predictions.tolist(),
                "features": features.tolist(),
                "confidence": float(np.mean(predictions)),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "patterns": [],
                "features": [],
                "confidence": 0.0,
                "timestamp": datetime.utcnow()
            }
    
    async def detect_anomalies(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Detect anomalies in the data using the anomaly detector model.
        
        Args:
            data: Input data array
            
        Returns:
            Dict containing anomaly detection results
        """
        try:
            # Preprocess data
            scaled_data = self.scaler.transform(data)
            
            # Extract features
            features = self.feature_extractor.predict(scaled_data)
            
            # Make predictions
            predictions = self.anomaly_detector.predict(features)
            scores = self.anomaly_detector.score_samples(features)
            
            return {
                "anomalies": predictions.tolist(),
                "scores": scores.tolist(),
                "features": features.tolist(),
                "confidence": float(np.mean(np.abs(scores))),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "anomalies": [],
                "scores": [],
                "features": [],
                "confidence": 0.0,
                "timestamp": datetime.utcnow()
            }
    
    async def extract_features(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Extract features from the data using the feature extractor model.
        
        Args:
            data: Input data array
            
        Returns:
            Dict containing extracted features
        """
        try:
            # Preprocess data
            scaled_data = self.scaler.transform(data)
            
            # Extract features
            features = self.feature_extractor.predict(scaled_data)
            
            return {
                "features": features.tolist(),
                "feature_dimensions": features.shape[1],
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "features": [],
                "feature_dimensions": 0,
                "timestamp": datetime.utcnow()
            }
    
    async def adapt_to_new_data(self, new_data: np.ndarray, labels: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Adapt models to new data through incremental learning.
        
        Args:
            new_data: New training data
            labels: Optional labels for supervised learning
            
        Returns:
            Dict containing adaptation results
        """
        try:
            # Preprocess data
            scaled_data = self.scaler.fit_transform(new_data)
            
            # Update feature extractor
            self.feature_extractor.fit(
                scaled_data,
                scaled_data,  # Autoencoder reconstruction
                epochs=10,
                batch_size=32,
                verbose=0
            )
            
            # Update pattern detector if labels are provided
            if labels is not None:
                reshaped_data = scaled_data.reshape(-1, 100, 20)
                self.pattern_detector.fit(
                    reshaped_data,
                    labels,
                    epochs=10,
                    batch_size=32,
                    verbose=0
                )
            
            # Update anomaly detector
            features = self.feature_extractor.predict(scaled_data)
            self.anomaly_detector.fit(features)
            
            # Save updated models
            self.pattern_detector.save(os.path.join(self.models_dir, "pattern_detector.h5"))
            joblib.dump(self.anomaly_detector, os.path.join(self.models_dir, "anomaly_detector.joblib"))
            self.feature_extractor.save(os.path.join(self.models_dir, "feature_extractor.h5"))
            
            # Create new model version record
            db = next(get_db())
            model_version = ModelVersion(
                version="1.0.0",
                model_type="advanced_ai",
                performance_metrics={
                    "feature_dimensions": features.shape[1],
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