<<<<<<< HEAD
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
=======
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from djoser.serializers import (
    UserSerializer,
)
from rest_framework.exceptions import ValidationError, NotAuthenticated
from .models import (
    FoodgramUser,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta(UserSerializer.Meta):
        model = FoodgramUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, other_user):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.subscriptions.filter(id=other_user.id).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = FoodgramUser
        fields = ["avatar"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
>>>>>>> 5c0d2140761d761da93599798d20e5a75db31977


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
<<<<<<< HEAD
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
=======
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients"
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients"
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, ingredients):
        """
        Проверка на пустой список ингредиентов и дубликаты.
        """
        if not ingredients:
            raise ValidationError("Поле 'ingredients' не может быть пустым.")

        ingredient_ids = [item["id"].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError("Ингредиенты не должны повторяться.")

        return ingredients

    def validate(self, data):
        """
        Проверка, что пользователь аутентифицирован.
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise NotAuthenticated(
                "Для создания/изменения рецепта необходимо авторизоваться."
            )
        return data

    def create_recipeingredient_objects(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data["id"],
                amount=ingredient_data["amount"]
            )
            for ingredient_data in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        validated_data["author"] = self.context.get("request").user
        recipe = super().create(validated_data)

        self.create_recipeingredient_objects(recipe, ingredients_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")

        RecipeIngredient.objects.filter(recipe=recipe).delete()

        self.create_recipeingredient_objects(recipe, ingredients_data)
        return super().update(recipe, validated_data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class UserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, user):
        request = self.context.get("request")

        return RecipeMinifiedSerializer(
            user.recipes.all()[: int(
                request.GET.get("recipes_limit", default=10**10)
            )],
            many=True, read_only=True,
        ).data
>>>>>>> 5c0d2140761d761da93599798d20e5a75db31977
