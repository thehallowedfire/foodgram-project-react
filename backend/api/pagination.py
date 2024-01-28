from rest_framework.pagination import PageNumberPagination

from .constants import USERS_PAGE_SIZE, RECIPES_PAGE_SIZE


class UsersPagination(PageNumberPagination):
    page_size = USERS_PAGE_SIZE
    page_size_query_param = 'limit'


class RecipesPagination(PageNumberPagination):
    page_size = RECIPES_PAGE_SIZE
    page_size_query_param = 'limit'
