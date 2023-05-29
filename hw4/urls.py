from django.contrib import admin
from django.urls import path

from orderProcessing.views import AddDish, GetDish, UpdateDish, DeleteDish, GetDishes
from userAuth.views import UserCreateView, login, UserAccessView


urlpatterns = [
    path('admin/', admin.site.urls),

    #Api пользователя
    path('api/user/create/', UserCreateView.as_view(), name='user_create'),
    path('api/user/login/', login, name='login'),
    path('api/user/access/', UserAccessView.as_view(), name='user-access'),

    #Api заказов
    path('api/orders/addDish/', AddDish().as_view(), name='add-dish'),
    path('api/orders/getDish/', GetDish().as_view(), name='get-dish'),
    path('api/orders/updateDish/', UpdateDish().as_view(), name='update-dish'),
    path('api/orders/deleteDish/', DeleteDish().as_view(), name='delete-dish'),
    path('api/orders/getAllDishes/', GetDishes().as_view(), name='get-all-dishes'),
]