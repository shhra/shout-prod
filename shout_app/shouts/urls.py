from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (ShoutViewSet, ShoutSupportAPIView, CommentListCreateAPIView,
        CommentDestroyAPIView, MeView, NotificationViewSet)

app_name = 'master'
router = DefaultRouter(trailing_slash=False)
router.register(r'api/s', ShoutViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api/s/<slug:slug>/support', ShoutSupportAPIView.as_view(), name='support_shout_api'),
    path('api/s/<slug:slug>/comment/', CommentListCreateAPIView.as_view(), name='comment_api'),
    path('api/s/<slug:shout_slug>/comment/<slug:comment_slug>/', 
        CommentDestroyAPIView.as_view(), name='comment_delete_api'),
    path('api/me', MeView.as_view(), name='about_me'),
    path('api/n/unread', NotificationViewSet.as_view({'get':'list'}), name='notification_unread')
]


# urlpatterns = format_suffix_patterns(urlpatterns)
