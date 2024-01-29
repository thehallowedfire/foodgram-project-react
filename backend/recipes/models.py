from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_MAX_LENGTH, INGREDIENT_UNIT_MAX_LENGTH,
                        TAG_NAME_MAX_LENGTH, TAG_COLOR_MAX_LENGTH,
                        TAG_DEFAULT_COLOR_CODE, TAG_SLUG_MAX_LENGTH,
                        RECIPE_NAME_MAX_LENGTH, RECIPE_TEXT_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название',
                            max_length=INGREDIENT_NAME_MAX_LENGTH,
                            db_index=True)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=INGREDIENT_UNIT_MAX_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField('Название',
                            max_length=TAG_NAME_MAX_LENGTH,
                            unique=True)
    color = models.CharField('Цветовой HEX-код',
                             max_length=TAG_COLOR_MAX_LENGTH,
                             unique=True,
                             default=TAG_DEFAULT_COLOR_CODE)
    slug = models.SlugField('Слаг',
                            max_length=TAG_SLUG_MAX_LENGTH,
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    author = models.ForeignKey(to=User,
                               on_delete=models.CASCADE,
                               related_name="recipes",
                               verbose_name='Автор')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    name = models.CharField('Название',
                            max_length=RECIPE_NAME_MAX_LENGTH)
    text = models.TextField('Описание',
                            max_length=RECIPE_TEXT_MAX_LENGTH)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField('Изображение',
                              upload_to='recipes/images/',
                              default=None)
    ingredients = models.ManyToManyField(to=Ingredient,
                                         through='RecipeIngredient',
                                         related_name='recipes',
                                         verbose_name='Игредиенты')
    tags = models.ManyToManyField(to=Tag,
                                  related_name='recipes',
                                  verbose_name='Теги',)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(to=Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_in_recipe',
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField('Кол-во')

    def __str__(self):
        # Ингредиент мука в рецепте Пирог с яблоками. Кол-во: 350 (г)
        return (f'Ингредиент {self.ingredient} в рецепте {self.recipe}. '
                f'Кол-во: {self.amount} ({self.ingredient.measurement_unit})')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Unique ingredient in recipe')
        ]


class Favorite(models.Model):
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name='favorite',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite',
                               verbose_name='Рецепт')

    def __str__(self):
        # Рецепт Пирог (ID:5) в избранном у пользователя Вася Пупкин (ID:5)
        return (f'Рецепт {self.recipe} (ID:{self.recipe.id}) в избранном '
                f'у пользователя {self.user} (ID:{self.user.id})')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique users favorite recipe')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')

    def __str__(self):
        # Рецепт Пирог (ID:5) в списке покупок
        # у пользователя Вася Пупкин (ID:5)
        return (f'Рецепт {self.recipe} (ID:{self.recipe.id}) в списке покупок '
                f'у пользователя {self.user} (ID:{self.user.id})')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique recipe in shopping cart')
        ]
