from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class FoodgramUser(AbstractUser):
    """Модель пользователя с добавленными полями"""
    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=30)
    username = models.CharField("Ник пользователя", max_length=30, unique=True)
    email = models.EmailField("Электронная почта", unique=True)
    is_active = models.BooleanField("Активность", default=True)
    is_staff = models.BooleanField("Доступ к админке", default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Группы',
        blank=True,
        related_name="foodgram_user_set",
        related_query_name="foodgram_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Права пользователя',
        blank=True,
        related_name="foodgram_user_set",
        related_query_name="foodgram_user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'


class Subscription(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='uniq_sub',
            ),
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                "Пользователь не может подписываться сам на себя.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
