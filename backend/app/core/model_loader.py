import joblib
from pathlib import Path
from typing import Optional
from core.config import MODEL_FILE


class ModelLoader:
    """Singleton class to load and cache the ML model."""
    
    _instance: Optional['ModelLoader'] = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self):
        """Load the model from disk if not already loaded."""
        if self._model is None:
            print(f"Loading model from {MODEL_FILE}...")
            try:
                self._model = joblib.load(MODEL_FILE)
                print(f"Model loaded successfully: {type(self._model)}")
            except Exception as e:
                print(f"Error loading model: {e}")
                raise
        return self._model
    
    @property
    def model(self):
        """Get the loaded model (loads if necessary)."""
        return self.load_model()


# Global instance
_model_loader = ModelLoader()

def get_model():
    """Get the global model instance."""
    return _model_loader.model
