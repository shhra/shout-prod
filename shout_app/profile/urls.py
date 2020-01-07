from django.urls import path, include
from shout_app.profile.views import ProfileRetrieveAPIView

urlpatterns = [
        path('api/u/<str:username>', ProfileRetrieveAPIView.as_view()
            , name='profile_username')
    ]

