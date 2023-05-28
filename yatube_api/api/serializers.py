import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField


from posts.models import Comment, Group, Post, Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Group


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    following = serializers.StringRelatedField()

    class Meta:
        fields = ['user', 'following', ]
        model = Follow

    def create(self, validated_data):
        following_username = self.initial_data.get('following')
        user = self.context['request'].user
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
        validated_data.update(user=user, following=following)
        return super().create(validated_data)
