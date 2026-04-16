from rest_framework import serializers
from .models import DiagnosisHistory

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisHistory
        fields = '__all__'
        read_only_fields = ['disease_detected', 'confidence', 'affected_area_ratio', 'created_at']

class DiagnosisResponseSerializer(serializers.Serializer):
    disease_detected = serializers.CharField()
    confidence = serializers.FloatField()
    affected_area_ratio = serializers.FloatField()
    disease_info = serializers.DictField()
    visualization_url = serializers.CharField()
    original_image_url = serializers.CharField()
