from django.shortcuts import render
from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import hashlib, re


@api_view(['POST'])
def create_string(request):
    value = request.data.get('value')
    if value is None:
        return Response({'detail': 'missing "value" field'}, status=400)
    if not isinstance(value, str):
        return Response({'detail': '"value" must be a string'}, status=422)

    hash_val = hashlib.sha256(value.encode('utf-8')).hexdigest()
    if AnalyzedString.objects.filter(id=hash_val).exists():
        return Response({'detail': 'String already analyzed'}, status=409)

    props = AnalyzedString.analyze_string(value)
    analyzed = AnalyzedString.objects.create(
        id=hash_val,
        value=value,
        **props
    )
    serializer = AnalyzedStringSerializer(analyzed)
    return Response(serializer.data, status=201)


@api_view(['GET'])
def list_strings(request):
    qs = AnalyzedString.objects.all()

    is_palindrome = request.GET.get('is_palindrome')
    min_length = request.GET.get('min_length')
    max_length = request.GET.get('max_length')
    word_count = request.GET.get('word_count')
    contains_character = request.GET.get('contains_character')

    if is_palindrome is not None:
        qs = qs.filter(is_palindrome=(is_palindrome.lower() == 'true'))

    if min_length is not None:
        qs = qs.filter(length__gte=int(min_length))

    if max_length is not None:
        qs = qs.filter(length__lte=int(max_length))

    if word_count is not None:
        qs = qs.filter(word_count=int(word_count))

    if contains_character is not None:
        qs = [q for q in qs if contains_character in q.character_frequency_map]

    serializer = AnalyzedStringSerializer(qs, many=True)
    filters_applied = {
        k: v for k, v in {
            'is_palindrome': is_palindrome,
            'min_length': min_length,
            'max_length': max_length,
            'word_count': word_count,
            'contains_character': contains_character,
        }.items() if v is not None
    }

    return Response({
        'data': serializer.data,
        'count': len(serializer.data),
        'filters_applied': filters_applied or None
    })


@api_view(['GET'])
def filter_nl(request):
    query = request.GET.get('q') or request.GET.get('query')
    if query is None:
        return Response({'detail': 'missing query'}, status=400)

    q = query.lower()
    parsed = {}

    if re.search(r"\bsingle word\b|\bone word\b", q):
        parsed["word_count"] = 1

    if re.search(r"\bpalindromic\b|\bpalindrome\b", q):
        parsed["is_palindrome"] = True

    m = re.search(r"longer than (\d+)", q)
    if m:
        parsed["min_length"] = int(m.group(1)) + 1

    m2 = re.search(r"containing the letter (\w)", q)
    if m2:
        parsed["contains_character"] = m2.group(1)

    if not parsed:
        return Response({'detail': 'Unable to parse natural language query'}, status=400)

    qs = AnalyzedString.objects.all()

    if "is_palindrome" in parsed:
        qs = qs.filter(is_palindrome=parsed["is_palindrome"])

    if "min_length" in parsed:
        qs = qs.filter(length__gte=parsed["min_length"])

    if "max_length" in parsed:
        qs = qs.filter(length__lte=parsed["max_length"])

    if "word_count" in parsed:
        qs = qs.filter(word_count=parsed["word_count"])

    if "contains_character" in parsed:
        qs = [q for q in qs if parsed["contains_character"] in q.character_frequency_map]

    serializer = AnalyzedStringSerializer(qs, many=True)

    return Response({
        "data": serializer.data,
        "count": len(serializer.data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed
        }
    })

@api_view(['DELETE'])
def delete_string(request, string_value):
    hash_val = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    try:
        obj = AnalyzedString.objects.get(pk=hash_val)
        obj.delete()
        return Response(status=204)
    except AnalyzedString.DoesNotExist:
        return Response({'detail': 'String does not exist'}, status=404)

@api_view(['GET'])
def get_string(request, string_value):
    hash_val = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    try:
        obj = AnalyzedString.objects.get(pk=hash_val)
        serializer = AnalyzedStringSerializer(obj)
        return Response(serializer.data, status=200)
    except AnalyzedString.DoesNotExist:
        return Response({'detail': 'String not found'}, status=404)
