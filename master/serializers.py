from rest_framework import serializers
from master.models import (CustomUser, Shout, Comment, Discussion)
from django.http import Http404


class ShoutSerializer(serializers.ModelSerializer):

    shouter = serializers.ReadOnlyField(source='shouter.username')
    supports = serializers.ReadOnlyField(source='supporters.count')
    user_support = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shout
        fields = ['slug', 'title', 'body', 'threshold', 'shouter', 'supports', 'date', 'user_support']

    def get_user_support(self, shout):
        user = self.context['request'].user
        if user in shout.supporters.all():
            return True
        else:
            return False


class CreateShoutSerializer(serializers.ModelSerializer):

    shouter = serializers.ReadOnlyField(source='shouter.username')

    class Meta:
        model = Shout
        fields = ['title', 'body', 'shouter', 'threshold']


class UserSerializer(serializers.ModelSerializer):

    # shout_user = serializers.PrimaryKeyRelatedField(many=True,
            # queryset=Shout.objects.all().exclude(deleted_at__isnull=False))
    shout_user = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'date_joined', 'shout_user']

    def get_shout_user(self, obj):
        shouts = Shout.objects.all().filter(shouter=obj)
        data = dict()
        for i, shout in enumerate(shouts):
                data[i] = shout.slug
        if len(data.keys()) == 0:
            data = {"1": "empty"}
        return data


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'


class CreateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['text', 'commented_on']
