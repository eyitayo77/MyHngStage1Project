from rest_framework import serializers
from .models import AnalyzedString

class AnalyzedStringSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'propertied', 'created_at']

        def get_properties(self, obj):
            return {
                "lenght": obj.lenght,
                "is_palindrome": obj.is_palindrome,
                "unique_characters": obj.unique_characters,
                "word_count": obj.word_count,
                "sha256_hash": obj.sha256_hash,
                "characte_frequency_map": obj.characte_frequency_map,
            }