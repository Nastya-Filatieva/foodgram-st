from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    r'categories', views.CategoryViewSet, basename='categories')
router.register(
    r'ingredients', views.IngredientViewSet, basename='ingredients')
router.register(
    r'recipes', views.RecipeViewSet, basename='recipes')
router.register(
    r'favorites', views.FavoritesViewSet, basename='favorites')
router.register(
    r'shopping-list', views.ShoppingListViewSet, basename='shopping-list')

urlpatterns = [
    path('', include(router.urls)),
]
