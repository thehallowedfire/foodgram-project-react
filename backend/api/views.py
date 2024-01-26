import io

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from .filters import RecipeFilterSet
from .pagination import RecipesPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import RecipeSerializer
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from recipes.serializers import (IngredientSerializer,
                                 RecipeMinifiedSerializer,
                                 TagSerializer)


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name',]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().select_related('author') \
                                   .prefetch_related('tags', 'ingredients')
    serializer_class = RecipeSerializer
    pagination_class = RecipesPagination
    filter_backends = [DjangoFilterBackend,]
    filterset_class = RecipeFilterSet
    permission_classes = [IsAuthorOrReadOnly,]

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def add_to_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        # Default response parameters
        data = {}
        response_status = status.HTTP_400_BAD_REQUEST

        user = request.user
        favorite_recipe = Favorite.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if favorite_recipe.exists():
                data = {'errors': 'Recipe is already in favorites!'}
            else:
                Favorite.objects.create(user=user, recipe=recipe)
                data = RecipeMinifiedSerializer(recipe).data
                response_status = status.HTTP_201_CREATED
        elif request.method == 'DELETE':
            if favorite_recipe.exists():
                favorite_recipe.delete()
                response_status = status.HTTP_204_NO_CONTENT
            else:
                data = {'errors': 'Recipe is not in favorites!'}
        return JsonResponse(data=data, status=response_status)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def add_to_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        # Default response parameters
        data = {}
        response_status = status.HTTP_400_BAD_REQUEST

        user = request.user
        recipe_in_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)

        match request.method:
            case 'POST':
                if recipe_in_cart.exists():
                    data = {'errors': 'Recipe is already in shopping cart!'}
                else:
                    ShoppingCart.objects.create(user=user, recipe=recipe)
                    data = RecipeMinifiedSerializer(recipe).data
                    response_status = status.HTTP_201_CREATED
            case 'DELETE':
                if recipe_in_cart.exists():
                    recipe_in_cart.delete()
                    response_status = status.HTTP_204_NO_CONTENT
                else:
                    data = {'errors': 'Recipe is not in shopping cart!'}
        return JsonResponse(data, status=response_status)

    @action(detail=False, methods=['GET'], url_path='cart')
    def shopping_cart(self, request):
        user = request.user
        queryset = user.shopping_cart.all()
        shopping_cart = self.filter_queryset(queryset)
        page = self.paginate_queryset(shopping_cart) or shopping_cart
        serializer = RecipeMinifiedSerializer(page, many=True,
                                              context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        user = request.user
        recipes_in_cart = self.get_queryset().filter(shopping_cart__user=user)
        recipes_ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_cart
        ).select_related('ingredient')

        ingredients_list: dict = {}
        for recipe_ingredient in recipes_ingredients:
            id: int = recipe_ingredient.ingredient.id
            name: str = recipe_ingredient.ingredient.name
            units: str = recipe_ingredient.ingredient.measurement_unit
            amount: int = recipe_ingredient.amount
            ingredient_in_list = ingredients_list.get(id)
            if ingredient_in_list:
                ingredient_in_list['amount'] += amount
            else:
                ingredients_list[id] = {
                    'name': name,
                    'units': units,
                    'amount': amount
                }
        file = io.StringIO()
        file.write('Shopping list:\n')
        for i, (_, ingredient) in enumerate(ingredients_list.items()):
            name = ingredient.get('name')
            units = ingredient.get('units')
            amount = ingredient.get('amount')
            new_line = f'{i + 1}. {name} ({units}) — {amount}\n'
            file.write(new_line)
        response = HttpResponse(file.getvalue(), content_type='text/plain')
        return response
