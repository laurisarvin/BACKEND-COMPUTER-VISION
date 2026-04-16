# ============================================================================
# api/utils/feature_extraction.py - VERSION CORRIGÉE
# ============================================================================

import cv2
import numpy as np
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops

def extract_color_features(image):
    """Extrait les caractéristiques de couleur"""
    features = []
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    for i in range(3):
        hist = cv2.calcHist([hsv], [i], None, [16], [0, 256])
        hist = hist.flatten()
        hist = hist / (hist.sum() + 1e-7)
        features.extend(hist)
    
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    for i in range(3):
        hist = cv2.calcHist([lab], [i], None, [16], [0, 256])
        hist = hist.flatten()
        hist = hist / (hist.sum() + 1e-7)
        features.extend(hist)
    
    for i in range(3):
        features.append(np.mean(hsv[:, :, i]))
        features.append(np.std(hsv[:, :, i]))
        features.append(np.mean(lab[:, :, i]))
        features.append(np.std(lab[:, :, i]))
    
    return np.array(features)

def extract_texture_features(image):
    """Extrait les caractéristiques de texture"""
    features = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # LBP
    radius = 3
    n_points = 8 * radius
    lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
    lbp_hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
    lbp_hist = lbp_hist.astype(float)
    lbp_hist /= (lbp_hist.sum() + 1e-7)
    features.extend(lbp_hist)
    
    # GLCM
    gray_glcm = (gray / 32).astype(np.uint8)
    distances = [1]
    angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    glcm = graycomatrix(gray_glcm, distances, angles, levels=8, symmetric=True, normed=True)
    
    properties = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation']
    for prop in properties:
        feature = graycoprops(glcm, prop).ravel()
        features.extend(feature)
    
    return np.array(features)

def extract_shape_features(image):
    """
    Extrait les caractéristiques de forme
    CORRECTION: Utilise le masque de la feuille pour les calculs
    """
    features = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        # Prendre le plus grand contour (la feuille)
        main_contour = max(contours, key=cv2.contourArea)
        
        # Aire et périmètre
        area = cv2.contourArea(main_contour)
        perimeter = cv2.arcLength(main_contour, True)
        
        # Ratio circularité
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter ** 2)
        else:
            circularity = 0
        
        # Moments de Hu
        moments = cv2.moments(main_contour)
        hu_moments = cv2.HuMoments(moments).flatten()
        hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)
        
        features.extend([area / 1000, perimeter / 100, circularity])
        features.extend(hu_moments)
        
        # CORRECTION: Calculer le ratio affecté correctement
        # On utilise la fonction de preprocessing
        from .preprocessing import segment_leaf_color, detect_affected_areas, calculate_affected_ratio
        
        # Récupérer le masque de la feuille
        _, leaf_mask = segment_leaf_color(image)
        
        # Détecter les zones affectées avec le masque
        affected_mask = detect_affected_areas(image, leaf_mask)
        
        # Calculer le ratio précis
        affected_ratio = calculate_affected_ratio(affected_mask, leaf_mask)
        
        features.append(affected_ratio)
    else:
        # Valeurs par défaut si pas de contour trouvé
        features = [0] * 12
    
    return np.array(features)

def extract_all_features(image):
    """
    Combine toutes les caractéristiques extraites
    
    Args:
        image: image BGR segmentée
    
    Returns:
        vecteur de caractéristiques complet
    """
    color_feat = extract_color_features(image)
    texture_feat = extract_texture_features(image)
    shape_feat = extract_shape_features(image)
    
    # Combiner tous les features
    all_features = np.concatenate([color_feat, texture_feat, shape_feat])
    
    return all_features