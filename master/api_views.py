from django.http import Http404
from django.shortcuts import (
        redirect, get_object_or_404)
from rest_framework import (generics, mixins, permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from .models import (CustomUser, Shout, Comment, Discussion)
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ShoutSerializer, CreateShoutSerializer,
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
    queryset = Shout.objects.all()
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
    queryset = Shout.objects.all()
    serializer_class = ShoutSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly]

    def get_object(self, slug):
        try:
            return Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        shout = self.get_object(slug)
        serializer = ShoutSerializer(shout)
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

    def get(self, request, pk, format=None):
        shout = get_object_or_404(Shout, pk=pk)
        supported = False
        user = self.request.user
        if user.is_authenticated:
            if user not in shout.supporters.all():
                supported = True
                shout.supporters.add(user)
            else:
                supported = False
                shout.supporters.remove(user)
            updated = True
            data = {
                    'supported': supported
            }
            return Response(data)
        else:
            return redirect('master:login')


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
