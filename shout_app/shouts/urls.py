from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (ShoutViewSet, ShoutSupportAPIView, CommentListCreateAPIView,)

app_name = 'master'
router = DefaultRouter(trailing_slash=False)
router.register(r'api/s', ShoutViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api/s/<slug:slug>/support', ShoutSupportAPIView.as_view(), name='support_shout_api'),
    path('api/s/<slug:slug>/comment/', CommentListCreateAPIView.as_view(), name='comment_api')
    # path('api/s/<slug:slug>/discussion/', DiscussionList.as_view(), name='support_discussion_api'),

    # path('api/user/', UserListAPI.as_view(), name='user_list_api'),
    # path('api/me/', MeView.as_view(), name='about_me'),
    # path('api/user/<str:username>/', UserDetailAPI.as_view(), name='customuser-detail'),
    # path('api/signup', SignupAPI.as_view(), name='user_signup_api'),

    # path('api/c/', CommentListAPI.as_view(), name='comment_api'),
    # path('api/c/create/', CreateCommentAPI.as_view(), name='create_comment_api'),
    # path('api/c/<slug:slug>/', CommentDetailAPI.as_view(), name='comment_detail_api'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
