
# ============================================================================
# api/views.py - VERSION CORRIGÉE
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
import cv2
import numpy as np
import base64
from .models import DiagnosisHistory
from .serializers import DiagnosisResponseSerializer, DiagnosisSerializer
from .utils.preprocessing import (
    preprocess_image, 
    segment_leaf_color, 
    detect_affected_areas, 
    create_visualization,
    calculate_affected_ratio  # NOUVEAU
)
from .utils.feacture_extraction import extract_all_features
from .utils.model_loader import ModelLoader

# Informations sur les maladies
DISEASE_INFO = {
    'Tomato___healthy': {
        'name': 'Feuille Saine',
        'description': 'La plante est en bonne santé. Aucune maladie détectée.',
        'severity': 'none',
        'treatment': 'Aucun traitement nécessaire. Continuer les bonnes pratiques culturales.',
        'prevention': 'Maintenir une bonne aération, arrosage régulier et fertilisation appropriée.'
    },
    'Tomato___Septoria_leaf_spot': {
        'name': 'Septoriose',
        'description': 'Maladie fongique causée par Septoria lycopersici. Caractérisée par des taches circulaires avec centre gris.',
        'severity': 'medium',
        'treatment': 'Retirer les feuilles infectées. Appliquer un fongicide à base de cuivre ou de chlorothalonil.',
        'prevention': 'Rotation des cultures, éviter l\'arrosage par aspersion, espacer les plants pour une bonne circulation d\'air.'
    },
    'Tomato___Tomato_mosaic_virus': {
        'name': 'Virus de la Mosaïque',
        'description': 'Maladie virale provoquant une mosaïque de zones claires et foncées sur les feuilles.',
        'severity': 'high',
        'treatment': 'Aucun traitement curatif. Éliminer les plants infectés pour éviter la propagation.',
        'prevention': 'Utiliser des semences certifiées, désinfecter les outils, contrôler les insectes vecteurs.'
    },
    'Tomato___Bacterial_spot': {
        'name': 'Tache Bactérienne',
        'description': 'Maladie bactérienne causée par Xanthomonas. Taches brunes à noires sur feuilles et fruits.',
        'severity': 'high',
        'treatment': 'Pulvériser des produits à base de cuivre. Retirer et détruire les parties infectées.',
        'prevention': 'Utiliser des semences saines, éviter l\'arrosage par aspersion, rotation des cultures.'
    }
}

class DiagnosePlantView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        """Endpoint principal pour le diagnostic"""
        try:
            # Récupérer l'image uploadée
            image_file = request.FILES.get('image')
            
            if not image_file:
                return Response(
                    {'error': 'Aucune image fournie'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Lire l'image avec OpenCV
            file_bytes = np.frombuffer(image_file.read(), np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if image is None:
                return Response(
                    {'error': 'Image invalide ou corrompue'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ÉTAPE 1: Prétraitement
            preprocessed = preprocess_image(image)
            
            # ÉTAPE 2: Segmentation de la feuille
            segmented, leaf_mask = segment_leaf_color(preprocessed)
            
            # ÉTAPE 3: Extraction des features (pour la prédiction)
            features = extract_all_features(segmented)
            
            # ÉTAPE 4: Prédiction avec le modèle ML
            model_loader = ModelLoader()
            disease_name, confidence = model_loader.predict(features)
            
            # ÉTAPE 5: Détection des zones affectées (AVEC LE MASQUE DE LA FEUILLE)
            affected_mask = detect_affected_areas(preprocessed, leaf_mask)
            
            # ÉTAPE 6: Calcul du ratio précis (zone affectée / surface feuille)
            affected_ratio = calculate_affected_ratio(affected_mask, leaf_mask)
            
            # ÉTAPE 7: Créer la visualisation (AVEC LE MASQUE)
            visualization = create_visualization(preprocessed, affected_mask, leaf_mask)
            
            # ÉTAPE 8: Convertir les images en base64
            _, buffer_viz = cv2.imencode('.jpg', visualization)
            viz_base64 = base64.b64encode(buffer_viz).decode('utf-8')
            
            _, buffer_orig = cv2.imencode('.jpg', preprocessed)
            orig_base64 = base64.b64encode(buffer_orig).decode('utf-8')
            
            # ÉTAPE 9: Sauvegarder dans l'historique
            diagnosis = DiagnosisHistory.objects.create(
                image=image_file,
                disease_detected=disease_name,
                confidence=confidence,
                affected_area_ratio=affected_ratio
            )
            
            # ÉTAPE 10: Préparer la réponse
            response_data = {
                'disease_detected': disease_name,
                'confidence': confidence,
                'affected_area_ratio': affected_ratio,
                'disease_info': DISEASE_INFO.get(disease_name, {}),
                'visualization_url': f'data:image/jpeg;base64,{viz_base64}',
                'original_image_url': f'data:image/jpeg;base64,{orig_base64}',
                'diagnosis_id': diagnosis.id
            }
            
            # Logs pour debug
            print(f"\n{'='*60}")
            print(f"DIAGNOSTIC EFFECTUÉ:")
            print(f"{'='*60}")
            print(f"Maladie détectée: {disease_name}")
            print(f"Confiance: {confidence*100:.2f}%")
            print(f"Surface feuille: {np.sum(leaf_mask > 0)} pixels")
            print(f"Zone affectée: {np.sum(affected_mask > 0)} pixels")
            print(f"Ratio affecté: {affected_ratio*100:.2f}%")
            print(f"{'='*60}\n")
            
            serializer = DiagnosisResponseSerializer(response_data)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(f"ERREUR COMPLÈTE:")
            print(traceback.format_exc())
            
            return Response(
                {'error': f'Erreur lors du diagnostic: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DiagnosisHistoryView(APIView):
    """Endpoint pour récupérer l'historique des diagnostics"""
    
    def get(self, request):
        """Récupérer tous les diagnostics"""
        diagnoses = DiagnosisHistory.objects.all()[:20]  # 20 derniers
        serializer = DiagnosisSerializer(diagnoses, many=True)
        return Response(serializer.data)
















































































































































































































































# #from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.parsers import MultiPartParser, FormParser
# from django.core.files.base import ContentFile
# import cv2
# import numpy as np
# import base64
# from .models import DiagnosisHistory
# from .serializers import DiagnosisResponseSerializer, DiagnosisSerializer
# from .utils.preprocessing import preprocess_image, segment_leaf_color, detect_affected_areas, create_visualization
# from .utils.feacture_extraction import extract_all_features
# from .utils.model_loader import ModelLoader


# # Create your views here.

# # Informations sur les maladies
# DISEASE_INFO = {
#     'Tomato___healthy': {
#         'name': 'Feuille Saine',
#         'description': 'La plante est en bonne santé. Aucune maladie détectée.',
#         'severity': 'none',
#         'treatment': 'Aucun traitement nécessaire. Continuer les bonnes pratiques culturales.',
#         'prevention': 'Maintenir une bonne aération, arrosage régulier et fertilisation appropriée.'
#     },
#     'Tomato___Septoria_leaf_spot': {
#         'name': 'Septoriose',
#         'description': 'Maladie fongique causée par Septoria lycopersici. Caractérisée par des taches circulaires avec centre gris.',
#         'severity': 'medium',
#         'treatment': 'Retirer les feuilles infectées. Appliquer un fongicide à base de cuivre ou de chlorothalonil.',
#         'prevention': 'Rotation des cultures, éviter l\'arrosage par aspersion, espacer les plants pour une bonne circulation d\'air.'
#     },
#     'Tomato___Tomato_mosaic_virus': {
#         'name': 'Virus de la Mosaïque',
#         'description': 'Maladie virale provoquant une mosaïque de zones claires et foncées sur les feuilles.',
#         'severity': 'high',
#         'treatment': 'Aucun traitement curatif. Éliminer les plants infectés pour éviter la propagation.',
#         'prevention': 'Utiliser des semences certifiées, désinfecter les outils, contrôler les insectes vecteurs.'
#     },
#     'Tomato___Bacterial_spot': {
#         'name': 'Tache Bactérienne',
#         'description': 'Maladie bactérienne causée par Xanthomonas. Taches brunes à noires sur feuilles et fruits.',
#         'severity': 'high',
#         'treatment': 'Pulvériser des produits à base de cuivre. Retirer et détruire les parties infectées.',
#         'prevention': 'Utiliser des semences saines, éviter l\'arrosage par aspersion, rotation des cultures.'
#     }
# }

# class DiagnosePlantView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
    
#     def post(self, request):
#         """Endpoint principal pour le diagnostic"""
#         try:
#             # Récupérer l'image uploadée
#             image_file = request.FILES.get('image')
            
#             if not image_file:
#                 return Response(
#                     {'error': 'Aucune image fournie'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Lire l'image avec OpenCV
#             file_bytes = np.frombuffer(image_file.read(), np.uint8)
#             image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
#             if image is None:
#                 return Response(
#                     {'error': 'Image invalide ou corrompue'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Prétraitement
#             preprocessed = preprocess_image(image)
#             segmented, leaf_mask = segment_leaf_color(preprocessed)
            
#             # Extraction des features
#             features = extract_all_features(segmented)
            
#             # Prédiction
#             model_loader = ModelLoader()
#             disease_name, confidence = model_loader.predict(features)
            
#             # Détection des zones affectées
#             affected_mask = detect_affected_areas(preprocessed)
#             affected_area = np.sum(affected_mask > 0)
#             total_area = np.sum(leaf_mask > 0)
#             affected_ratio = float(affected_area / (total_area + 1e-7))
            
#             # Créer la visualisation
#             visualization = create_visualization(preprocessed, affected_mask)
            
#             # Convertir les images en base64 pour le frontend
#             _, buffer_viz = cv2.imencode('.jpg', visualization)
#             viz_base64 = base64.b64encode(buffer_viz).decode('utf-8')
            
#             _, buffer_orig = cv2.imencode('.jpg', preprocessed)
#             orig_base64 = base64.b64encode(buffer_orig).decode('utf-8')
            
#             # Sauvegarder dans l'historique
#             diagnosis = DiagnosisHistory.objects.create(
#                 image=image_file,
#                 disease_detected=disease_name,
#                 confidence=confidence,
#                 affected_area_ratio=affected_ratio
#             )
            
#             # Préparer la réponse
#             response_data = {
#                 'disease_detected': disease_name,
#                 'confidence': confidence,
#                 'affected_area_ratio': affected_ratio,
#                 'disease_info': DISEASE_INFO.get(disease_name, {}),
#                 'visualization_url': f'data:image/jpeg;base64,{viz_base64}',
#                 'original_image_url': f'data:image/jpeg;base64,{orig_base64}',
#                 'diagnosis_id': diagnosis.id
#             }
            
#             serializer = DiagnosisResponseSerializer(response_data)
            
#             return Response(serializer.data, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response(
#                 {'error': f'Erreur lors du diagnostic: {str(e)}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# class DiagnosisHistoryView(APIView):
#     """Endpoint pour récupérer l'historique des diagnostics"""
    
#     def get(self, request):
#         """Récupérer tous les diagnostics"""
#         diagnoses = DiagnosisHistory.objects.all()[:20]  # 20 derniers
#         serializer = DiagnosisSerializer(diagnoses, many=True)
#         return Response(serializer.data)