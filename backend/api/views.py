<<<<<<< HEAD
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum

from .models import (
    Category, Recipe, Ingredient, RecipeIngredient,
    FavouritesRecipes, ShoppingList
)
from .serializers import (
    CategorySerializer, RecipeSerializer, RecipeListSerializer,
    IngredientSerializer, FavouritesSerializer, ShoppingListSerializer)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов"""
    queryset = Recipe.objects.all().order_by('-pub_date')
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(shopping_list__user=self.request.user)

        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное"""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            _, created = FavouritesRecipes.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavouritesSerializer(
                instance=FavouritesRecipes(user=request.user, recipe=recipe),
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        FavouritesRecipes.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            _, created = ShoppingList.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShoppingListSerializer(
                instance=ShoppingList(user=request.user, recipe=recipe),
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок"""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        shopping_list = []
        for item in ingredients:
            shopping_list.append(
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}"
            )

        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class FavoritesViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для избранных рецептов"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Recipe.objects.filter(
            favorites__user=self.request.user
        ).order_by('-pub_date')


class ShoppingListViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для списка покупок"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Recipe.objects.filter(
            shopping_list__user=self.request.user
        ).order_by('-pub_date')
=======
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .filters import RecipeFilter
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    FoodgramUser,
)
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeMinifiedSerializer,
    UserWithRecipesSerializer,
    FoodgramUserSerializer,
    UserAvatarSerializer,
)
from .services import (
    generate_shopping_list,
    get_shopping_cart_ingredients
)


class FoodgramUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = PageLimitPagination
    permission_classes = [AllowAny]

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        return super().me(request)

    @action(
        detail=True, methods=["put", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request, id):

        user = request.user

        if request.method == "PUT":
            user = request.user
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid() and "avatar" in request.data:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            raise ValidationError(detail=serializer.errors)

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError(detail="У пользователя нет аватара.")

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticatedOrReadOnly])
    def subscriptions(self, request):

        user = request.user
        authors = [subscription.author
                   for subscription in user.subscriptions.all()]

        # Пагинация
        return self.get_paginated_response(
            UserWithRecipesSerializer(
                self.paginate_queryset(authors),
                many=True, context={"request": request}
            ).data
        )

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = self.get_object()
        if request.method == "POST":
            if request.user == author:
                raise ValidationError(
                    detail="Нельзя подписаться на самого себя."
                )
            _, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if not created:
                raise ValidationError(
                    detail="Вы уже подписаны на этого пользователя."
                )
            serializer = UserWithRecipesSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Subscription, user=request.user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = PageLimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        return (
            RecipeWriteSerializer
            if self.action in ["create", "update", "partial_update"]
            else RecipeReadSerializer
        )

    @staticmethod
    def _handle_recipe_action(model, user, recipe, request_method):

        if request_method == "POST":
            _, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                raise ValidationError(detail=(
                    f"Рецепт '{recipe.name}' уже добавлен в избранное/корзину."
                ))

            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request_method == "DELETE":
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise ValidationError(detail="Некорректное действие.")

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        recipe = self.get_object()
        return self._handle_recipe_action(
            Favorite, request.user, recipe, request.method)

    @action(
        detail=True, methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзину."""
        recipe = self.get_object()
        return self._handle_recipe_action(
            ShoppingCart, request.user, recipe, request.method)

    @action(detail=False, permission_classes=[IsAuthenticatedOrReadOnly])
    def download_shopping_cart(self, request):
        ingredients = get_shopping_cart_ingredients(request.user)

        recipes = (
            Recipe.objects.filter(shoppingcarts__user=request.user).distinct()
        )

        shopping_list = generate_shopping_list(ingredients, recipes)

        return FileResponse(shopping_list,
                            content_type="text/plain; charset=utf-8",
                            filename="shopping_list.txt")


@api_view(["GET"])
def get_recipe_short_link(request, id):

    get_object_or_404(Recipe, id=id)

    return Response(
        {
            "short-link": request.build_absolute_uri(
                reverse("redirect_short_link", kwargs={"short_id": id})
            )
        },
        status=status.HTTP_200_OK,
    )


def redirect_short_link(request, short_id):

    get_object_or_404(Recipe, id=short_id)
    return redirect(f"recipes/{short_id}")


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        name = self.request.GET.get("name")
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset
>>>>>>> 5c0d2140761d761da93599798d20e5a75db31977
