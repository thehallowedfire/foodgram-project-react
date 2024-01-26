from rest_framework.pagination import PageNumberPagination

from .constants import RECIPES_PAGE_SIZE


class RecipesPagination(PageNumberPagination):
    page_size = RECIPES_PAGE_SIZE
    page_size_query_param = 'limit'
