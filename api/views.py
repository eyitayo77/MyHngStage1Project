from django.shortcuts import get_object_or_404
from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import hashlib, re


@api_view(['GET', 'POST'])
def strings_view(request):
    if request.method == 'POST':
        value = request.data.get('value')

        if value is None:
            return Response({'detail': 'Missing "value" field'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(value, str):
            return Response({'detail': '"value" must be a string'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        value = value.strip()
        if not value:
            return Response({'detail': '"value" cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        hash_val = hashlib.sha256(value.encode('utf-8')).hexdigest()
        if AnalyzedString.objects.filter(id=hash_val).exists():
            return Response({'detail': 'String already analyzed'}, status=status.HTTP_409_CONFLICT)

        try:
            props = AnalyzedString.analyze_string(value)
            analyzed = AnalyzedString.objects.create(id=hash_val, value=value, **props)
            serializer = AnalyzedStringSerializer(analyzed)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': f'Error creating string: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    qs = AnalyzedString.objects.all()

    is_palindrome = request.GET.get('is_palindrome')
    min_length = request.GET.get('min_length')
    max_length = request.GET.get('max_length')
    word_count = request.GET.get('word_count')
    contains_character = request.GET.get('contains_character')

    try:
        if is_palindrome is not None:
            if is_palindrome.lower() not in ['true', 'false']:
                return Response({'detail': 'Invalid is_palindrome value'}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(is_palindrome=(is_palindrome.lower() == 'true'))

        if min_length is not None:
            qs = qs.filter(length__gte=int(min_length))
        if max_length is not None:
            qs = qs.filter(length__lte=int(max_length))
        if word_count is not None:
            qs = qs.filter(word_count=int(word_count))
        if contains_character is not None:
            qs = [q for q in qs if contains_character.lower() in q.value.lower()]
    except ValueError:
        return Response({'detail': 'Invalid query parameter values or types'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AnalyzedStringSerializer(qs, many=True)
    filters_applied = {
        k: v for k, v in {
            'is_palindrome': is_palindrome,
            'min_length': min_length,
            'max_length': max_length,
            'word_count': word_count,
            'contains_character': contains_character
        }.items() if v is not None
    }

    return Response({
        'data': serializer.data,
        'count': len(serializer.data),
        'filters_applied': filters_applied or None
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def filter_nl(request):
    query = request.GET.get('query')
    if not query:
        return Response({'detail': 'Missing "query" parameter'}, status=status.HTTP_400_BAD_REQUEST)

    parsed = {}
    q = query.lower()

    if re.search(r"\bsingle word\b|\bone word\b", q):
        parsed["word_count"] = 1
    if re.search(r"\bpalindromic\b|\bpalindrome\b", q):
        parsed["is_palindrome"] = True
    if match := re.search(r"longer than (\d+)", q):
        parsed["min_length"] = int(match.group(1)) + 1
    if match := re.search(r"containing the letter (\w)", q):
        parsed["contains_character"] = match.group(1)

    if not parsed:
        return Response({'detail': 'Unable to parse natural language query'}, status=status.HTTP_400_BAD_REQUEST)

    qs = AnalyzedString.objects.all()
    if "is_palindrome" in parsed:
        qs = qs.filter(is_palindrome=parsed["is_palindrome"])
    if "min_length" in parsed:
        qs = qs.filter(length__gte=parsed["min_length"])
    if "word_count" in parsed:
        qs = qs.filter(word_count=parsed["word_count"])
    if "contains_character" in parsed:
        qs = [q for q in qs if parsed["contains_character"].lower() in q.value.lower()]

    serializer = AnalyzedStringSerializer(qs, many=True)
    return Response({
        "data": serializer.data,
        "count": len(serializer.data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE'])
def get_or_delete_string(request, string_value):
    string_value = string_value.strip()
    obj = AnalyzedString.objects.filter(value=string_value).first()

    if not obj:
        return Response({'detail': 'String not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AnalyzedStringSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
