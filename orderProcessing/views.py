from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from orderProcessing.models import Dish
from orderProcessing.serializers import DishSerializer
from userAuth.models import Session

#Проверяет валидность токена
def check_token(request):
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

    if user.role != 'manager':
        return Response({'detail': 'No permission.'}, status=status.HTTP_401_UNAUTHORIZED)
    return None

#Добавление блюда
class AddDish(APIView):
    def post(self, request):
        res = check_token(request)
        if res:
            return res

        serializer = DishSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Dish added successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Получение блюда
class GetDish(APIView):
    def get(self, request):
        res = check_token(request)
        if res:
            return res
        dish_id = request.data.get('dish_id')
        if not dish_id:
            return Response({'detail': 'dish_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            raise NotFound('Dish not found.')

        serializer = DishSerializer(dish)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Обновление блюда
class UpdateDish(APIView):
    def put(self, request):
        res = check_token(request)
        if res:
            return res
        dish_id = request.data.get('dish_id')
        if not dish_id:
            return Response({'detail': 'dish_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            raise NotFound('Dish not found.')

        if 'name' in request.data:
            dish.name = request.data['name']
        if 'description' in request.data:
            dish.description = request.data['description']
        if 'price' in request.data:
            dish.price = request.data['price']
        if 'quantity' in request.data:
            dish.quantity = request.data['quantity']
        if 'is_available' in request.data:
            dish.is_available = request.data['is_available']

        dish.updated_at = timezone.now()
        dish.save()

        serializer = DishSerializer(dish)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Удаление блюда
class DeleteDish(APIView):
    def delete(self, request):
        res = check_token(request)
        if res:
            return res
        dish_id = request.data.get('dish_id')
        if not dish_id:
            return Response({'detail': 'dish_id parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            raise NotFound('Dish not found.')

        dish.delete()

        return Response({'detail': 'Dish deleted successfully.'}, status=status.HTTP_200_OK)

#Получение меню
class GetDishes(APIView):

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

        if user.role == 'manager':
            dishes = Dish.objects.all()
        else:
            dishes = Dish.objects.filter(is_available=True)

        serializer = DishSerializer(dishes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)