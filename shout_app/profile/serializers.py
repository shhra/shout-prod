from rest_framework import serializers

from shout_app.shouts.models import Shout
from shout_app.profile.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    verified = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields =  ('username', 'bio', 'verified')
        read_only_fields = ('username', )

    def get_verified(self, instance):
        return instance.is_verified



