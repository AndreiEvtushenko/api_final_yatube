from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination


from api.permissions import ObjectAuthorOrReadOnly, FollowPermission
from api.serializers import (CommentSerializer, GroupSerializer,
                             PostSerializer, FollowSerializer)
from posts.models import Comment, Post, Group, Follow


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


class CreateListFollowViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    pass


class FollowViewSet(CreateListFollowViewSet):
    serializer_class = FollowSerializer
    permission_classes = (FollowPermission,)
    filter_backends = (filters.SearchFilter, )
    filterset_fields = ['following']
    search_fields = ('following__username',)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        return queryset
