from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import (
    Category, Recipe, Ingredient, RecipeIngredient,
    FavouritesRecipes, ShoppingList)
from foodgram_user.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    """"""
    class Meta:
        model = Category
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "quantity")


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка рецептов на главной странице"""
    author = UserProfileSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    category = CategorySerializer()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'image', 'description',
            'pub_date', 'ingredients', 'author']

    def get_queryset(self):
        return Recipe.objects.order_by('-pub_date')[:6]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavouritesRecipes.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта"""
    author = UserProfileSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    category = CategorySerializer()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return FavouritesRecipes.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_list(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингердиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class FavouritesSerializer(serializers.ModelSerializer):
    """Сериалзиатор добавления в избранное"""
    class Meta:
        model = FavouritesRecipes
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingListSerializer(FavouritesSerializer):
    """Сериализатор добавления в корзину"""
    class Meta(FavouritesSerializer.Meta):
        model = ShoppingList
        fields = '__all__'

    def validate(self, attrs):
        if ShoppingList.objects.filter(recipe=attrs['recipe'],
                                       user=attrs['user']).exists():
            raise ValidationError(
                'Рецепт уже находится в вашем списке покупок.')
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор смены пароля"""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
