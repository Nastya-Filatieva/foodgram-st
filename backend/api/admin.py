from django.contrib import admin
from .models import Category, Ingredient, Recipe


class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов"""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов"""
    list_display = ('title', 'author',)
    search_fields = ('title', 'author__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            favorites_count=models.Count('favorites'))


class CategoryAdmin(admin.ModelAdmin):
    """Админка категории рецепта"""
    list_display = ('title', 'slug')
    search_fields = ('title',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Category, CategoryAdmin)
