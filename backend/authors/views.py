from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action

from .models import CustomUserSubscribe
from .pagination import UsersPagination
from .serializers import AuthorSerializer, AuthorWithRecipesSerializer


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
        elif request.method == 'DELETE':
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
