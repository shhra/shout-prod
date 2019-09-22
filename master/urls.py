from django.urls import include, path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
        # Session Views 
        CreateShout, AllShouts, ShoutDetail, DeleteShout, SupportShout, EchoList,
        UserDetail, UserSettings,
        DiscussionDetail, CreateComment, DeleteComment,
        )
from .api_views import (
        CreateShoutAPI, ShoutListAPI, ShoutDetailAPI, SupportShoutAPI,
        CommentListAPI, CreateCommentAPI, CommentDetailAPI,
        UserDetailAPI, UserListAPI, SignupAPI, DiscussionList,
        APIRoot, )

app_name = 'master'

urlpatterns = [
    path('s/', AllShouts.as_view(), name='shouts'),
    path('s/create/', CreateShout.as_view(), name='create_shout'),
    path('s/<slug:slug>/', ShoutDetail.as_view(), name='shout_detail'),
    path('s/<slug:slug>/delete/', DeleteShout.as_view(), name='delete_shout'),
    path('s/<slug:slug>/support/', SupportShout.as_view(), name='support_shout'),
    path('s/<slug:slug>/discussion/', DiscussionDetail.as_view(), name='shout_discussion'),
    path('u/<str:username>/', UserDetail.as_view(), name='user_detail'),
    path('u/settings', UserSettings.as_view(), name='user_settings'),
    path('c/<slug:slug>/comment/', CreateComment.as_view(), name='create_comment'),
    path('c/<slug:slug>/comment/delete', DeleteComment.as_view(), name='delete_comment'),
    path('c/<slug:slug>/echoed', EchoList.as_view(), name='echo_shout'),

    # api urls
    path('api/', APIRoot.as_view(), name='api_root'),
    path('api/s/', ShoutListAPI.as_view(), name='shouts_api'),
    path('api/s/create/', CreateShoutAPI.as_view(), name='create_shout_api'),
    path('api/s/<slug:slug>/', ShoutDetailAPI.as_view(), name='shout_detail_api'),
    path('api/s/<slug:slug>/support/', SupportShoutAPI.as_view(), name='support_shout_api'),
    path('api/s/<slug:slug>/discussion/', DiscussionList.as_view(), name='support_discussion_api'),

    path('api/user/', UserListAPI.as_view(), name='user_list_api'),
    path('api/user/<str:username>/', UserDetailAPI.as_view(), name='customuser-detail'),
    path('api/signup', SignupAPI.as_view(), name='user_signup_api'),

    path('api/c/', CommentListAPI.as_view(), name='comment_api'),
    path('api/c/create/', CreateCommentAPI.as_view(), name='create_comment_api'),
    path('api/c/<slug:slug>/', CommentDetailAPI.as_view(), name='comment_detail_api'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
