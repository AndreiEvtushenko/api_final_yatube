from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import LimitOffsetPagination


from api.permissions import ObjectAuthorOrReadOnly, FollowPermission
from api.serializers import (CommentSerializer, GroupSerializer,
                             PostSerializer, FollowSerializer)
from posts.models import Comment, Post, Group, Follow, User


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (ObjectAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ObjectAuthorOrReadOnly,)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id is None:
            raise NotFound('Пост не найден.')
        queryset = Comment.objects.filter(post=post_id)
        return queryset


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (FollowPermission,)
    filter_backends = (filters.SearchFilter, )
    filterset_fields = ['following']
    search_fields = ('following__username',)

    def perform_create(self, serializer):
        following_username = self.request.data.get('following')
        user = self.request.user
        if following_username is None:
            raise ValidationError('Необходимо указать имя пользователя.')
        if following_username == user.username:
            raise ValidationError('Нельзя подписаться на самого себя.')
        try:
            following = User.objects.get(username=following_username)
        except User.DoesNotExist:
            raise ValidationError(
                'Пользователь с указанным именем не существует.')
        if Follow.objects.filter(user=user).filter(following=following):
            raise ValidationError('Вы уже подписаны на этого автора.')
        serializer.save(user=user, following=following)

    def get_queryset(self):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        return queryset
