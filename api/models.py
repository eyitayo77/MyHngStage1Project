from django.db import models
import hashlib
import json
# Create your models here.

class AnalyzedString(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    value = models.TextField(unique=True)
    lenght = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    sha256_hash = models.CharField(max_length=64)
    characte_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.value

    @staticmethod
    def analyze_string(s):
        if not isinstance(s, str):
            raise ValueError("Value must  be a sting")

        hash_val = hashlib.sha256(s.encode('utf-8')).hexadigest()
        length = len(s)

        is_palindrome = s.lower() == s[::-1]
        unique_characters = len(set(s))
        word_count = len(s.split())
        freq = {}
        for char in s:
            freq[ch] = freq.get(ch, 0) + 1

        return {
            "lenght": lenght,
            "is_palindrome": is_palindrome,
            "unique_characters": unique_characters,
            "word_count": word_count,
            "sha256_hash": hash_val,
            "characte_frequency_map": freq, 
        }