from rest_framework import serializers
from .models import  Shout, Comment, Discussion
from shout_app.profile.serializers import ProfileSerializer
from shout_app.authentication.models import User
from shout_app.profile.models import Profile
from django.http import Http404
from rest_framework.response import Response


class ShoutSerializer(serializers.ModelSerializer):

    shouter = ProfileSerializer(read_only=True)
    threshold = serializers.IntegerField(default=1)
    supported = serializers.SerializerMethodField()
    supports_count = serializers.SerializerMethodField(
            method_name='get_supports_count')
    created_at = serializers.SerializerMethodField(method_name='get_created_at')
    slug = serializers.SlugField(required=False)
    discussion_status = serializers.SerializerMethodField(method_name='get_discussion_status')
    is_shouter = serializers.SerializerMethodField(method_name='get_is_shouter')

    class Meta:
        model = Shout
        fields = ['slug', 'title', 'body', 'shouter',
                'threshold', 'supported', 'supports_count',
                'created_at', 'discussion_status', 'is_shouter']

    def create(self, validated_data):
        shouter = self.context.get('shouter', None)
        shout = Shout.objects.create(shouter=shouter, **validated_data)
        return shout

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_supported(self, instance):
        request = self.context.get('request', None)
        if request is None:
            return False
        if not request.user.is_authenticated:
            return False
        return request.user.profile.has_supported(instance)

    def get_supports_count(self, instance):
        return instance.supported_by.count()

    def get_discussion_status(self, instance):
        return True if self.get_supports_count(instance) == instance.threshold else False

    def get_is_shouter(self, instance):
        request = self.context.get('request', None)
        if request is None:
            return False
        if not request.user.is_authenticated:
            return False
        return True if instance.shouter == request.user.profile else False


class CommentSerializer(serializers.ModelSerializer):
    commented_by = ProfileSerializer(required=False)
    commented_on = ShoutSerializer(required=False)
    created_at = serializers.SerializerMethodField(method_name='get_created_at')
    updated_at = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Comment
        fields = ['slug', 'commented_by', 'commented_on', 'text',
                'created_at', 'updated_at']

    def create(self, validated_data):
        shout = self.context['commented_on']
        commented_by = self.context['commented_by']

        return Comment.objects.create(
                commented_by=commented_by, commented_on=shout, **validated_data
                )

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()


class UserSerializer(serializers.ModelSerializer):                           
    class Meta:                                   
        model = User
        fields = ['username']


class ShoutNotificationSerializer(serializers.ModelSerializer):                           
    class Meta:                                   
        model = Shout
        fields = ['slug']


class GenericNotificationRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, User):
            serializer = UserSerializer(value)
        if isinstance(value, Shout):
            serializer = ShoutNotificationSerializer(value)
        return serializer.data


class NotificationSerializer(serializers.Serializer):
    pk = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = UserSerializer(read_only=True)
    unread = serializers.BooleanField(read_only=True)
    target = GenericNotificationRelatedField(read_only=True)
    action_object = GenericNotificationRelatedField(read_only=True)
    verb = serializers.CharField()





