from django.contrib import admin

# Register your models here.
from orderProcessing.models import Dish, Order, OrderDish

admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(OrderDish)