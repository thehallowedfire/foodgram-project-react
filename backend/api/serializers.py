import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from .constants import DEFAULT_RECIPES_PAGE_SIZE_ON_SUB


User = get_user_model()


def add_ingredients_to_recipe(recipe: Recipe,
                              ingredients: list[Ingredient]) -> None:
    ingredients_list = [RecipeIngredient(recipe=recipe,
                                         ingredient_id=ingredient['id'],
                                         amount=ingredient['amount'])
                        for ingredient in ingredients]
    RecipeIngredient.objects.bulk_create(ingredients_list)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


######################
# AUTHOR SERIALIZERS #
######################

class AuthorSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscribers.filter(user=user).exists()


class AuthorWithRecipesSerializer(AuthorSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = AuthorSerializer.Meta.fields + ['recipes_count', 'recipes']

    def get_recipes_count(self, obj):
        return obj.recipe.all().count()

    def get_recipes(self, obj):
        recipes_limit: int = DEFAULT_RECIPES_PAGE_SIZE_ON_SUB
        request: dict = self.context.get('request')
        if request:
            param: str = request.query_params.get('recipes_limit')
            if param and param.isdigit():
                recipes_limit = int(param)
        recipes = obj.recipe.all()[:recipes_limit]
        return RecipeMinifiedSerializer(recipes, many=True).data


######################
# RECIPE SERIALIZERS #
######################

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'name', 'text',
                  'cooking_time', 'ingredients',
                  'tags', 'image', 'is_favorited',
                  'is_in_shopping_cart']

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            # Add aditional field and alter its name
            amount=F('ingredient_in_recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorite.filter(recipe_id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ['name', 'text', 'cooking_time',
                  'image', 'ingredients', 'tags']

    def validate_ingredients(self, value):
        # No ingredients provided
        if not value or len(value) == 0:
            error = 'Must provide at least one ingredient!'
            raise serializers.ValidationError(error)

        # Requesting ingredient with amount is less than 1
        for ingredient in value:
            if ingredient['amount'] < 1:
                error = 'Amount can not be less than 1!'
                raise serializers.ValidationError(error)

        provided_ids: list[int] = [ingredient.get('id')
                                   for ingredient in value]
        # Request has a multiple identical ingredients ids
        if not len(set(provided_ids)) == len(value):
            error = 'Multiple identical ingredients!'
            raise serializers.ValidationError(error)

        # At least one of the ingredients doesn't exist in DB
        if not Ingredient.objects.filter(id__in=provided_ids).distinct() \
                                 .count() == len(provided_ids):
            error = 'Non existing ingredient!'
            raise serializers.ValidationError(error)

        return value

    def validate_tags(self, value):
        # No tags provided
        if not value or len(value) == 0:
            error = 'Must provide at least one tag!'
            raise serializers.ValidationError(error)

        # Request has a multiple identical tags
        if not len(set(value)) == len(value):
            error = 'Multiple identical tags!'
            raise serializers.ValidationError(error)

        return value

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(author=author, **validated_data)

        recipe.tags.set(tags)
        add_ingredients_to_recipe(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        # instance.image = self.data.get('image')

        instance.tags.set(validated_data.get('tags'))

        # Delete all the old ingredients for the current recipe
        RecipeIngredient.objects.all().filter(recipe=instance).delete()
        # Create the new ingredients for the current recipe
        ingredients = validated_data.get('ingredients')
        add_ingredients_to_recipe(instance, ingredients)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data
