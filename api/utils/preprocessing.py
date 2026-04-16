import cv2
import numpy as np


def preprocess_image(image, target_size=(256, 256)):
    """Prétraite une image: redimensionnement"""
    resized = cv2.resize(image, target_size)
    return resized

def segment_leaf_color(image):
    """Segmente la feuille en utilisant la segmentation par couleur"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Plages de vert pour capturer les feuilles
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Nettoyage du masque
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    segmented = cv2.bitwise_and(image, image, mask=mask)
    return segmented, mask

def detect_affected_areas(image, leaf_mask):
    """
    Détecte les zones affectées par des maladies (taches brunes, jaunes, noires)
    
    Args:
        image: image BGR
        leaf_mask: masque de la feuille
    
    Returns:
        masque binaire des zones affectées
    """
    # Convertir en HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Masque pour détecter les zones BRUNES/MARRON (taches communes)
    lower_brown = np.array([10, 40, 20])
    upper_brown = np.array([30, 255, 200])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Masque pour détecter les zones JAUNES (chlorose)
    lower_yellow = np.array([20, 50, 50])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Masque pour détecter les zones TRÈS SOMBRES (nécrose)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 50])
    dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
    
    # Masque pour détecter les zones TRÈS CLAIRES/BLANCHES (mildiou, oïdium)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Combiner tous les masques de maladies
    disease_mask = cv2.bitwise_or(brown_mask, yellow_mask)
    disease_mask = cv2.bitwise_or(disease_mask, dark_mask)
    disease_mask = cv2.bitwise_or(disease_mask, white_mask)
    
    # Appliquer le masque de la feuille pour ne garder que les zones dans la feuille
    affected_mask = cv2.bitwise_and(disease_mask, disease_mask, mask=leaf_mask)
    
    # Nettoyage : supprimer le bruit
    kernel = np.ones((3, 3), np.uint8)
    affected_mask = cv2.morphologyEx(affected_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    affected_mask = cv2.morphologyEx(affected_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # Filtrer les contours trop petits (moins de 0.5% de la feuille)
    total_leaf = np.sum(leaf_mask > 0)
    if total_leaf == 0:
        return np.zeros_like(leaf_mask)
    
    min_area = total_leaf * 0.005  # 0.5% minimum
    
    contours, _ = cv2.findContours(affected_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cleaned_mask = np.zeros_like(affected_mask)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            cv2.drawContours(cleaned_mask, [contour], -1, 255, -1)
    
    return cleaned_mask

def create_visualization(original_image, affected_mask, leaf_mask):
    """
    Crée une visualisation avec overlay des zones affectées
    
    Args:
        original_image: image originale
        affected_mask: masque des zones affectées
        leaf_mask: masque de la feuille
    
    Returns:
        image avec visualisation des zones affectées
    """
    overlay = original_image.copy()
    
    # Si pas de zones affectées, retourner l'image originale
    if np.sum(affected_mask) == 0:
        return original_image.copy()
    
    # Dilater légèrement le masque pour mieux voir
    kernel = np.ones((3, 3), np.uint8)
    affected_dilated = cv2.dilate(affected_mask, kernel, iterations=1)
    
    # S'assurer que les zones affectées restent dans la feuille
    affected_dilated = cv2.bitwise_and(affected_dilated, affected_dilated, mask=leaf_mask)
    
    # Colorer les zones affectées en rouge semi-transparent
    overlay[affected_dilated > 0] = [0, 0, 255]
    
    # Mélanger avec l'image originale
    result = cv2.addWeighted(original_image, 0.7, overlay, 0.3, 0)
    
    # Dessiner les contours en jaune
    contours, _ = cv2.findContours(affected_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(result, contours, -1, (0, 255, 255), 2)
    
    return result

def calculate_affected_ratio(affected_mask, leaf_mask):
    """
    Calcule le ratio de zone affectée par rapport à la surface de la feuille
    
    Args:
        affected_mask: masque des zones affectées
        leaf_mask: masque de la feuille
    
    Returns:
        ratio (float entre 0 et 1)
    """
    # Compter les pixels de la feuille
    total_leaf_pixels = np.sum(leaf_mask > 0)
    
    # Compter les pixels affectés
    affected_pixels = np.sum(affected_mask > 0)
    
    # Calculer le ratio
    if total_leaf_pixels > 0:
        ratio = affected_pixels / total_leaf_pixels
    else:
        ratio = 0.0
    
    return float(ratio)






























































































































































































































































































































































# def preprocess_image(image, target_size=(256, 256)):
#     """Prétraite une image: redimensionnement"""
#     resized = cv2.resize(image, target_size)
#     return resized

# def segment_leaf_color(image):
#     """Segmente la feuille en utilisant la segmentation par couleur"""
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
#     # Plages de vert pour capturer les feuilles
#     lower_green = np.array([25, 40, 40])
#     upper_green = np.array([90, 255, 255])
    
#     mask = cv2.inRange(hsv, lower_green, upper_green)
    
#     # Nettoyage du masque
#     kernel = np.ones((5, 5), np.uint8)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
#     segmented = cv2.bitwise_and(image, image, mask=mask)
#     return segmented, mask

# def detect_affected_areas(image, leaf_mask):
#     """
#     Détecte les zones affectées (taches, décolorations) UNIQUEMENT sur la feuille
    
#     Args:
#         image: image BGR
#         leaf_mask: masque de la feuille (pour exclure le fond)
    
#     Returns:
#         masque binaire des zones affectées (limité à la feuille)
#     """
#     # Convertir en LAB pour mieux détecter les anomalies de couleur
#     lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
#     a_channel = lab[:, :, 1]
    
#     # Détection des anomalies par seuillage
#     _, thresh = cv2.threshold(a_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
#     # CORRECTION IMPORTANTE: Appliquer le masque de la feuille
#     # Pour ne garder que les zones affectées qui sont DANS la feuille
#     affected_areas = cv2.bitwise_and(thresh, thresh, mask=leaf_mask)
    
#     return affected_areas

# def create_visualization(original_image, affected_mask, leaf_mask):
#     """
#     Crée une visualisation avec overlay des zones affectées
    
#     Args:
#         original_image: image originale
#         affected_mask: masque des zones affectées
#         leaf_mask: masque de la feuille
    
#     Returns:
#         image avec visualisation des zones affectées
#     """
#     overlay = original_image.copy()
    
#     # Dilater le masque pour mieux voir
#     kernel = np.ones((5, 5), np.uint8)
#     affected_dilated = cv2.dilate(affected_mask, kernel, iterations=2)
    
#     # S'assurer que les zones affectées restent dans la feuille
#     affected_dilated = cv2.bitwise_and(affected_dilated, affected_dilated, mask=leaf_mask)
    
#     # Colorer les zones affectées en rouge
#     overlay[affected_dilated > 0] = [0, 0, 255]
    
#     # Mélanger avec l'image originale
#     result = cv2.addWeighted(original_image, 0.7, overlay, 0.3, 0)
    
#     # Dessiner les contours en jaune
#     contours, _ = cv2.findContours(affected_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     cv2.drawContours(result, contours, -1, (0, 255, 255), 2)
    
#     return result

# def calculate_affected_ratio(affected_mask, leaf_mask):
#     """
#     Calcule le ratio de zone affectée par rapport à la surface de la feuille
    
#     Args:
#         affected_mask: masque des zones affectées
#         leaf_mask: masque de la feuille
    
#     Returns:
#         ratio (float entre 0 et 1)
#     """
#     # Compter les pixels de la feuille
#     total_leaf_pixels = np.sum(leaf_mask > 0)
    
#     # Compter les pixels affectés (dans la feuille uniquement)
#     affected_pixels = np.sum(affected_mask > 0)
    
#     # Calculer le ratio
#     if total_leaf_pixels > 0:
#         ratio = affected_pixels / total_leaf_pixels
#     else:
#         ratio = 0.0
    
#     return float(ratio)