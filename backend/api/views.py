import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, permissions, viewsets
from rest_framework.decorators import action

from .filters import RecipeFilterSet
from .pagination import UsersPagination, RecipesPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AuthorSerializer, AuthorWithRecipesSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeMinifiedSerializer, TagSerializer)
from authors.models import CustomUserSubscribe
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = UsersPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        subscription = CustomUserSubscribe.objects.filter(user=user,
                                                          author=author)

        # Default response parameters
        data = {}
        response_status = status.HTTP_400_BAD_REQUEST

        if request.method == 'POST':
            if user == author:
                data = {'errors': 'Can not subscribe to yourself!'}
            elif subscription.exists():
                data = {'errors': 'Already subscribed to this user!'}
            else:
                CustomUserSubscribe.objects.create(user=user, author=author)
                data = AuthorWithRecipesSerializer(
                    author, context={'request': request}).data
                response_status = status.HTTP_201_CREATED
            return JsonResponse(data=data, status=response_status)

        if not subscription.exists():
            data = {'errors': 'You are not subscribed to this user!'}
        else:
            subscription.delete()
            response_status = status.HTTP_204_NO_CONTENT
        return JsonResponse(data=data, status=response_status)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.subscriptions.all()
        queryset = self.filter_queryset(subscriptions)
        page = self.paginate_queryset(queryset) or queryset
        serializer = AuthorWithRecipesSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['^name', ]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (Recipe.objects.all().select_related('author')
                .prefetch_related('tags', 'ingredients'))
    serializer_class = RecipeSerializer
    pagination_class = RecipesPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilterSet
    permission_classes = [IsAuthorOrReadOnly, ]

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @staticmethod
    def add(request, model, id):
        recipe = get_object_or_404(Recipe, pk=id)
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            data = {'errors': 'The recipe is already added!'}
            return JsonResponse(data=data, status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=request.user, recipe=recipe)
        data = RecipeMinifiedSerializer(recipe).data
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, model, id):
        recipe = get_object_or_404(Recipe, pk=id)
        entry = model.objects.filter(user=request.user, recipe=recipe)
        if not entry.exists():
            data = {'errors': 'The recipe is not in the list!'}
            return JsonResponse(data=data, status=status.HTTP_400_BAD_REQUEST)
        entry.delete()
        return JsonResponse(data={}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite')
    def add_to_favorites(self, request, pk=None):
        if request.method == 'POST':
            return self.add(request, Favorite, pk)
        else:
            return self.delete(request, Favorite, pk)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart')
    def add_to_shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add(request, ShoppingCart, pk)
        else:
            return self.delete(request, ShoppingCart, pk)

    @action(detail=False, methods=['GET'], url_path='cart')
    def shopping_cart(self, request):
        queryset = request.user.shopping_cart.all()
        shopping_cart = self.filter_queryset(queryset)
        page = self.paginate_queryset(shopping_cart) or shopping_cart
        serializer = RecipeMinifiedSerializer(page, many=True,
                                              context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        user = request.user
        recipes_in_cart = self.get_queryset().filter(shopping_cart__user=user)
        ingredient_entries = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_cart
        ).select_related('ingredient')

        summarized_ingredients: list[dict[str, str, int]]
        summarized_ingredients = list(ingredient_entries
                                      .values('ingredient__name',
                                              'ingredient__measurement_unit')
                                      .annotate(Sum('amount'))
                                      .order_by('ingredient__name'))

        file = io.StringIO()
        file.write('Shopping list:\n')
        for i, ingr in enumerate(summarized_ingredients):
            name: str = ingr.get('ingredient__name')
            units: str = ingr.get('ingredient__measurement_unit')
            amount: int = ingr.get('amount__sum')
            new_line = f'{i + 1}. {name} ({units}) — {amount}\n'
            file.write(new_line)

        response = HttpResponse(file.getvalue(), content_type='text/plain')
        return response
