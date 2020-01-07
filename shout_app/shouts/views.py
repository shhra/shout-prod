from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from notifications.models import Notification
from notifications.signals import notify

from .models import Shout, Comment, Discussion
from .serializers import ShoutSerializer, CommentSerializer, NotificationSerializer
from shout_app.core.permissions import IsOwnerOrReadOnly
from datetime import datetime, timedelta


class ShoutViewSet(mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    lookup_field = 'slug'
    queryset = Shout.objects.all().order_by('-created_at')
    permission_classes = (IsAuthenticatedOrReadOnly, AllowAny)
    serializer_class = ShoutSerializer

    def get_queryset(self):
        queryset = self.queryset
        supported_by = self.request.query_params.get('supported', None)
        if supported_by is not None:
            queryset = queryset.filter(supported_by__user__username=supported_by)
        return queryset

    def create(self, request):
        serializer_context = {
                'shouter': request.user.profile,
                'request': request
            }
        serializer_data = request.data.get('data', {})
        serializer = self.serializer_class(
                data=serializer_data, context=serializer_context)
        # Adding spam filter.
        past_ten = datetime.now() - timedelta(minutes=10)
        shouts = Shout.objects.all().filter(shouter=request.user.profile,
                                            created_at__gte=past_ten)
        if len(shouts) > 4:
            raise NotAcceptable('You have been spamming a lot, and are banned for 10 min')
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)

    def list(self, request):
        serializer_context = {'request': request}
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.serializer_class(page, context=serializer_context, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, slug):
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Shout.DoesNotExist:
            raise NotFound("No one has shouted this.")

        serializer = self.serializer_class(
                serializer_instance,
                context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug=None):
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Shout.DoesNotExist:
            raise NotFound("No one has shouted this.")

        print(serializer_instance.shouter)
        print(request.user.profile)
        if request.user.profile == serializer_instance.shouter:
            serializer_instance.delete()
        else:
            raise NotAcceptable("You are denied, you can't delete it.")
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ShoutSupportAPIView(APIView):
    permisson_classes = (IsAuthenticated,)
    serializer_class = ShoutSerializer

    def delete(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {'request': request}
        try:
            shout = Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise NotFound('No one has shouted this')
        profile.not_support(shout)
        serializer = self.serializer_class(shout, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {'request': request}
        try:
            shout = Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise NotFound('No one has shouted this')
        if shout.supported_by.count() < shout.threshold:
            profile.support(shout)
            notify.send(profile.user, recipient=shout.shouter.user,
                    verb=(f"{profile.user} has supported your shout."))
        else:
            raise NotAcceptable('You can\'t support it anymore')
        serializer = self.serializer_class(shout, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'commented_on__slug'
    lookup_url_kwarg =  'slug'
    permission_classes = (IsAuthenticatedOrReadOnly,  IsOwnerOrReadOnly,)
    queryset = Comment.objects.select_related(
            'commented_on', 'commented_on__shouter', 'commented_on__shouter__user', 
            'commented_by', 'commented_by__user'
            )
    serializer_class = CommentSerializer

    def filter_queryset(self, queryset):
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        return queryset.filter(**filters)

    def create(self, request, slug=None):
        data = request.data.get('data', {})
        context = {'commented_by': request.user.profile}

        try:
            context['commented_on'] = shout = Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise NotFound("No one shouted this")

        if shout.supported_by.count() >= shout.threshold and \
                (request.user.profile.has_supported(shout)
                or request.user.is_professional 
                or shout.shouter==request.user.profile):
            serializer = self.serializer_class(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise NotAcceptable("You don't have the permission to comment here")


class CommentDestroyAPIView(generics.DestroyAPIView):
    lookup_url_kwarg = 'comment_slug'
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    queryset = Comment.objects.all()

    def destroy(self, request, shout_slug=None, comment_slug=None):
        try:
            comment = Comment.objects.get(slug=comment_slug)
        except Comment.DoesNotExist:
            raise NotFound('This comment doesn\'t exists!')
        if request.user.profile == comment.commented_by or request.user.is_professional:
            comment.delete()
        else:
            raise NotAcceptable("You are denied, you can't delete it.")
        return Response(None, status=status.HTTP_204_NO_CONTENT)


# class DiscussionList(
        # mixins.RetrieveModelMixin,
        # generics.GenericAPIView):
    # """
    # Gives the detail information of the shout
    # """
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly,
            # IsOwnerOrReadOnly]
    # """
    # Details on Discussion
    # """
    # def get_object(self, slug):
        # try:
            # return Shout.objects.get(slug=slug)
        # except Shout.DoesNotExist:
            # raise Http404

    # def get(self, request, slug, format=None):
        # shout = self.get_object(slug)
        # user = self.request.user
        # context = {}
        # if shout.supporters.count() >= shout.threshold or user.is_professional:
            # shout = Shout.objects.get(id=shout.id)
            # comments = Comment.objects.all().filter(commented_on=shout.id)
            # context['shout_slug'] = shout.slug
            # context['is_shouter'] = True if shout.shouter == user else False
            # context['comments'] = []
            # for each in comments:
                # comment = {}
                # comment['user'] = each.commented_by.username
                # comment['date'] = each.created_at
                # comment['text'] = each.text
                # context['comments'].append(comment)
            # return Response(context)
        # else:
            # return HttpResponseForbidden
        

# # Views related to self
class MeView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly)

    def get(self, request, format=None):
        user = self.request.user
        context = {}
        if user.is_authenticated:
            context['me'] = user.username
            return Response(context, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ViewSet):
    serializer_class = NotificationSerializer

    def list(self, request):
        queryset = Notification.objects.unread().filter(recipient=self.request.user)
        return Response(NotificationSerializer(queryset, many=True).data)


