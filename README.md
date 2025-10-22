# String Analyzer API

A Django REST API that analyzes strings and stores computed properties. Built for Backend Wizards Stage 1.

## Endpoints
### 1. Create/Analyze String

POST /strings/
Body:

{ "value": "string to analyze" }


Response 201:

{
  "id": "sha256_hash",
  "value": "string",
  "properties": { "length":16,"is_palindrome":false,"unique_characters":12,"word_count":3,"sha256_hash":"abc123","character_frequency_map":{...} },
  "created_at":"2025-08-27T10:00:00Z"
}

### 2. Get Specific String

GET /strings/{string_value}/
Response 200: Same structure as above
404: String not found

### 3. List Strings with Filters

GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
Response 200:

{
  "data": [ { "id":"hash1","value":"string1","properties":{...},"created_at":"..." } ],
  "count": 1,
  "filters_applied": { "is_palindrome":true, "min_length":5, "max_length":20, "word_count":2, "contains_character":"a" }
}

### 4. Natural Language Query

GET /strings/filter-by-natural-language/?query=all%20single%20word%20palindromic%20strings
Response 200:

{
  "data": [...],
  "count": 3,
  "interpreted_query": { "original":"all single word palindromic strings","parsed_filters":{"word_count":1,"is_palindrome":true} }
}

### 5. Delete String

DELETE /strings/{string_value}/
Response 204: (empty)
404: String does not exist

Setup
git clone https://github.com/Michael-oss138/MyHngProjStage1.git
cd MyHngProjStage1
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

## Dependencies

Python 3.10+

Django 5.x

Django REST Framework

