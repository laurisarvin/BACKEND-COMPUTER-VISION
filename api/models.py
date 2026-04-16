from django.db import models


# Create your models here.

class DiagnosisHistory(models.Model):
    """Historique des diagnostics"""
    image = models.ImageField(upload_to='uploads/')
    disease_detected = models.CharField(max_length=200)
    confidence = models.FloatField()
    affected_area_ratio = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.disease_detected} - {self.confidence:.2%} ({self.created_at})"