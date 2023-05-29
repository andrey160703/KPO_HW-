import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serializers import UserSerializer, hash_password
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import User, Session


#Создание пользователя
class UserCreateView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Авторизация пользователя
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
        print(user.password_hash)
        print(hash_password(password))
        if user.password_hash == hash_password(password):
            payload = {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            session = Session(user=user, session_token=token, expires_at=payload['exp'])
            session.save()

            return JsonResponse({'token': token})

        else:
            return JsonResponse({'error': 'Invalid password'}, status=401)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


#Получение пользователя по токену
class UserAccessView(APIView):
    def get(self, request):
        token = request.data.get('token')

        if not token:
            return Response({'detail': 'Missing authentication credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            session = Session.objects.get(session_token=token)
        except Session.DoesNotExist:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)

        if session.expires_at < timezone.now():
            return Response({'detail': 'Token has expired.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = session.user

        response_data = {
            'username': user.username,
            'email': user.email,
            'role': user.role,
        }

        return Response(response_data, status=status.HTTP_200_OK)
