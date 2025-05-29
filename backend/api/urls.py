from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (
    FoodgramUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', FoodgramUserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
