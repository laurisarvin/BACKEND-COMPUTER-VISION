import pickle
import os
from django.conf import settings
import numpy as np

class ModelLoader:
    _instance = None
    _model = None
    _scaler = None
    _label_encoder = None
    
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance.load_model()
        return cls._instance
    
    def load_model(self):
        """Charge le modèle entraîné"""
        model_path = os.path.join(settings.BASE_DIR, 'models', 'best_model.pkl')
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self._model = model_data['model']
                self._scaler = model_data['scaler']
                self._label_encoder = model_data['label_encoder']
            print("✓ Modèle chargé avec succès")
        except Exception as e:
            print(f" Erreur lors du chargement du modèle: {e}")
            raise
    
    def predict(self, features):
        """Fait une prédiction"""
        if self._model is None:
            raise Exception("Modèle non chargé")
        
        # Normaliser les features
        features_scaled = self._scaler.transform([features])
        
        # Prédiction
        prediction = self._model.predict(features_scaled)[0]
        
        # Probabilités (si disponible)
        if hasattr(self._model, 'predict_proba'):
            probabilities = self._model.predict_proba(features_scaled)[0]
            confidence = float(np.max(probabilities))
        else:
            # Pour les modèles sans predict_proba
            confidence = 0.85  # Valeur par défaut
        
        # Décoder le label
        disease_name = self._label_encoder.inverse_transform([prediction])[0]
        
        return disease_name, confidence