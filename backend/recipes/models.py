from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_MAX_LENGTH, INGREDIENT_UNIT_MAX_LENGTH,
                        TAG_NAME_MAX_LENGTH, TAG_COLOR_MAX_LENGTH,
                        TAG_DEFAULT_COLOR_CODE, TAG_SLUG_MAX_LENGTH,
                        RECIPE_NAME_MAX_LENGTH, RECIPE_TEXT_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH,
                            db_index=True)
    measurement_unit = models.CharField(max_length=INGREDIENT_UNIT_MAX_LENGTH)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True)
    color = models.CharField(max_length=TAG_COLOR_MAX_LENGTH,
                             unique=True,
                             default=TAG_DEFAULT_COLOR_CODE)
    slug = models.SlugField(max_length=TAG_SLUG_MAX_LENGTH, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(to=User,
                               on_delete=models.CASCADE,
                               related_name="recipes")
    pub_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    text = models.TextField(max_length=RECIPE_TEXT_MAX_LENGTH)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(upload_to='recipes/images/', default=None)
    ingredients = models.ManyToManyField(to=Ingredient,
                                         through='RecipeIngredient',
                                         related_name='recipes')
    tags = models.ManyToManyField(to=Tag, related_name='recipes')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(to=Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_in_recipe')
    amount = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Unique ingredient in recipe')
        ]


class Favorite(models.Model):
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name='favorite')
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique users favorite recipe')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique recipe in shopping cart')
        ]
