import re
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


@csrf_exempt
@require_POST
def register_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not username or not password or not email:
            return JsonResponse({"error": "Incomplete registration data"}, status=400)

        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({"error": "Invalid email address"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username is already taken"}, status=400)

        # Password strength validation
        password_pattern = r'^(?=.*\d)(?=.*[A-Z])(?=.*[a-z]).{8,}$'
        if not re.match(password_pattern, password):
            return JsonResponse({"error": "Password does not meet strength requirements"}, status=400)

        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        # Create the user
        user_data = {
            "username": username,
            "password": password,
            "email": email,
            "first_name": first_name
        }

        if last_name:
            user_data["last_name"] = last_name

        User.objects.create_user(**user_data)

        return JsonResponse({"message": "User registered successfully"}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
