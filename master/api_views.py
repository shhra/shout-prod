from django.http import Http404, request
from django.shortcuts import (
        redirect, get_object_or_404)
from rest_framework import (generics, mixins, permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from .models import CustomUser, Shout, Comment, Discussion
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ShoutSerializer, CreateShoutSerializer, ShoutDetailSerializer,
    UserSerializer, CreateUserSerializer, 
    CommentSerializer, CreateCommentSerializer,)


class APIRoot(APIView):

    def get(self, request, format=None):
        return Response(
                {
                    'shouts':reverse('master:shouts_api', request=request, format=None),
                    'user':reverse('master:user_list_api', request=request, format=None)
                } 
            )


class ShoutListAPI(generics.ListAPIView):
    """
    List all shouts
    """
    queryset = Shout.objects.all().order_by('-date')
    serializer_class = ShoutSerializer


class CreateShoutAPI(generics.CreateAPIView):
    """
    Create a new shout
    """
    queryset = Shout.objects.all()
    serializer_class = CreateShoutSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(shouter=self.request.user)


class ShoutDetailAPI(
        mixins.RetrieveModelMixin,
        generics.GenericAPIView):
    """
    Gives the detail information of the shout
    """
    serializer_class = ShoutDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly]

    def get_object(self, slug):
        try:
            return Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        shout = self.get_object(slug)
        serializer = ShoutDetailSerializer(shout)
        return Response(serializer.data)
    
    def delete(self, request, slug, format=None):
        shout = self.get_object(slug)
        shout.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetailAPI(APIView):
    """
    Gives the detail information the Users
    """

    def get_object(self, username):
        try:
            object = get_object_or_404(CustomUser, username=username)
            return object
        except:
            raise Http404

    def get(self, request, username, format=None):
        user = self.get_object(username)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserListAPI(generics.ListAPIView):
    """
    List all shouts
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class SignupAPI(generics.CreateAPIView):
    serializer_class = CreateUserSerializer



class SupportShoutAPI(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly]

    def get(self, request, slug, format=None):
        shout = get_object_or_404(Shout, slug=slug)
        supported = False
        user = self.request.user
        if user.is_authenticated:
            if shout.supporters.count() < shout.threshold and user not in shout.supporters.all():
                supported = True
                shout.supporters.add(user)
            elif shout.supporters.count() >= shout.threshold and user in shout.supporters.all():
                supported = False
                shout.supporters.remove(user)
            else:
                return Http404
            updated = True
            data = {
                    'supported': supported
            }
            return Response(data)
        else:
            return redirect('account_login')


class CommentListAPI(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CreateCommentAPI(generics.CreateAPIView):
    """
    Create a new comment
    """
    serializer_class = CreateCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        comment = Comment.objects.all()
        return comment

    def perform_create(self, serializer):
        shout = Shout.objects.get(id=serializer.data['commented_on'])
        user = self.request.user
        if shout.supporters.count() >= shout.threshold and (user in shout.supporters.all()
                or user.is_professional):
            serializer.save(commented_by=self.request.user)
        else:
            raise Http404


class CommentDetailAPI(APIView):
    """
    Gives the detail information of the comment
    """
    queryset = Shout.objects.all()
    serializer_class = ShoutSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, slug):
        try:
            return Comment.objects.get(slug=slug)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        comment = self.get_object(slug)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    def delete(self, request, slug, format=None):
        comment = self.get_object(slug)
        if not (comment.commented_by == self.request.user or self.request.user.is_professional):
            raise Http404
        else:
           comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Views related to Discussion - List View
class DiscussionList(
        mixins.RetrieveModelMixin,
        generics.GenericAPIView):
    """
    Gives the detail information of the shout
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly]
    """
    Details on Discussion
    """
    def get_object(self, slug):
        try:
            return Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        shout = self.get_object(slug)
        user = self.request.user
        context = {}
        if shout.supporters.count() >= shout.threshold or user.is_professional:
            shout = Shout.objects.get(id=shout.id)
            comments = Comment.objects.all().filter(commented_on=shout.id)
            context['shout_id'] = shout.id
            context['shout_slug'] = shout.slug
            context['comments'] = []
            for each in comments:
                comment = {}
                comment['user'] = each.commented_by.username
                comment['date'] = each.created_at
                comment['text'] = each.text
                context['comments'].append(comment)
            return Response(context)
        else:
            raise Http404
        

# Views related to self
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly]
    def get(self, request, format=None):
        user = self.request.user
        context = {}
        if user.is_authenticated:
            context['me'] = user.username
            return Response(context)

