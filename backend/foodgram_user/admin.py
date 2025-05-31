from django.contrib import admin
from .models import FoodgramUser

# Register your models here.


class AbstractFoodgramUserAdmin(admin.ModelAdmin):
    """Админка для пользователя"""
    list_display = ('email', 'first_name', 'last_name',)
    search_fields = ('email', 'username',)


admin.site.register(FoodgramUser, AbstractFoodgramUserAdmin)
