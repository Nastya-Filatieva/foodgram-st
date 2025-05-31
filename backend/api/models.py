from django.db import models
from foodgram_user.models import AbstractFoodgramUser


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField("Название", max_length=255)
    measurement_unit = models.CharField("Единица измерения", max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категория рецепта"""
    title = models.CharField('Название категории', max_length=255, unique=True)
    slug = models.SlugField('Слаг категории', max_length=255, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        AbstractFoodgramUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    title = models.CharField("Название", max_length=255)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name="Ингредиенты"
    )
    cooking_time = models.PositiveIntegerField("Время приготовления")
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    """Модель, связывающая рецепт и ингредиент"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        unique_together = ('ingredient', 'recipe')

    def __str__(self):
        return f"{self.quantity} {self.ingredient.measurement_unit} \
            {self.ingredient.name}"


class FavouritesRecipes(models.Model):
    """Избранные рецепты"""
    user = models.ForeignKey(
        AbstractFoodgramUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт'
    )
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('recipe__title',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uniq_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} добавил рецепт {self.recipe.title}\
              в избранное'


class ShoppingList(models.Model):
    """Список покупок"""
    user = models.ForeignKey(
        AbstractFoodgramUser,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт для покупки'
    )
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uniq_shop_list'
            )
        ]

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.title} \
            в список покупок'
