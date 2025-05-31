from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import FoodgramUser, Subscription
from foodgram_user.models import FoodgramUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    class Meta:
        model = FoodgramUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """Метод для создания нового пользователя"""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def validate_username(self, value):
        """Валидация уникальности имени пользователя"""
        if FoodgramUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Это имя пользователя уже занято.")
        return value

    def validate_email(self, value):
        """Валидация уникальности адреса электронной почты"""
        if FoodgramUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Этот адрес электронной почты уже зарегистрирован.")
        return value


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для аутентификации пользователя"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Неправильные учетные данные. Проверьте ваш email и пароль.")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = ['id', 'username', 'recipes', 'is_subscribed']

    def get_recipes(self, obj):
        from api.serializers import RecipeListSerializer
        recipes = obj.recipes.all()
        return RecipeListSerializer(recipes, many=True, context=self.context).data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(
                follower=user, followed=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки"""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count()')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed'
        ]

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.author.recipes.all()
        if 'recipes_limit' in request.query_params:
            try:
                limit = int(request.query_params['recipes_limit'])
                recipes = recipes[:limit]
            except ValueError:
                pass
        return RecipeListSerializer(
            recipes, many=True, context=self.context
        ).data
