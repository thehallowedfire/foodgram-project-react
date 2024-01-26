from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.serializers import RecipeMinifiedSerializer

from .constants import DEFAULT_RECIPES_PAGE_SIZE_ON_SUB


User = get_user_model()


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
