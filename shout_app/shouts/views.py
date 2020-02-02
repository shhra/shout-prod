import scipy.spatial
import numpy as np

from django.shortcuts import redirect
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
from shout_app.profile.serializers import ProfileSerializer
from shout_app.core.permissions import IsOwnerOrReadOnly
from datetime import datetime, timedelta


class ShoutViewSet(mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    lookup_field = 'slug'
    queryset = Shout.objects.all().order_by('-created_at')
    permission_classes = (IsAuthenticatedOrReadOnly,)
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

        recipient = shout.shouter.user
        if shout.supported_by.count() >= shout.threshold:
            notif_discussion = Notification.objects.all().filter(
                    target_object_id=shout.id,
                    description="discussion"
                )
            notif_discussion.delete()

        notif = recipient.notifications.get(
                actor_object_id=profile.user.id,
                target_object_id=shout.id,
                description="support")

        profile.not_support(shout)
        notif.delete()

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
            shouter = shout.shouter.user
            profile.support(shout)
            try:
                notif = shouter.notifications.get(
                        actor_object_id=self.request.user.id,
                        target_object_id=shout.id,
                        description="support")
                if notif:
                    pass
            except:
                notify.send(profile.user,
                        recipient=shouter,
                        target=shout,
                        description="support",
                        verb=(f"{profile.user} has supported the shout about {shout.title}."))
                if shout.supported_by.count() == shout.threshold:
                    recipients = [recipient.user for recipient in shout.supported_by.all()]
                    notify.send(profile.user,
                                recipient=recipients,
                                target=shout,
                                description="discussion",
                                verb=(f"Discussion is unlocked for the shout about {shout.title}."))
            else:
                raise NotAcceptable('You can\'t support it anymore')
        serializer = self.serializer_class(shout, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'commented_on__slug'
    lookup_url_kwarg =  'slug'
    permission_classes = (IsOwnerOrReadOnly,)
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


# View for Echo
class EchoView(generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly)
    serializer_class = ShoutSerializer

    def get_object(self, slug):
        try:
            return Shout.objects.get(slug=slug)
        except Shout.DoesNotExist:
            raise NotFound("This shout doesn't exist")

    def get(self, request, *args,  **kwargs):
        serializer_context = {'request': request}
        shout = self.get_object(slug=kwargs['slug'])
        past_one = datetime.now() - timedelta(minutes=1440)
        query_embedding = np.array(shout.value).reshape(1, -1)
        corpus = Shout.objects.all().filter(created_at__gte=past_one)
        if len(corpus) == 0:
            raise NotFound("No similar shouts in last 24 hours")
        elif len(corpus) == 1:
            return Response(self.serializer_class(corpus[0]).data, status=status.HTTP_200_OK)
        else:
            corpus_embedding = np.array(
                    [np.array(shout.value).reshape(-1) for shout in corpus]
                    ).reshape(len(corpus), -1)
            distance = scipy.spatial.distance.cdist(
                    query_embedding,
                    corpus_embedding,
                    'cosine')[0]
            context = {}
            context['data'] = list()
            results = zip(range(len(distance)), distance)
            results = sorted(results, key=lambda x: x[1])
            for i, _ in results:
                context['data'].append(self.serializer_class(corpus[i]).data)
            return Response(context, status=status.HTTP_200_OK)


# # Views related to self
class MeView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly)
    serializer_class = ProfileSerializer

    def get(self, request, format=None):
        user = self.request.user.profile
        context = {}
        context['data'] = self.serializer_class(user).data
        return Response(context, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def list(self, request):
        user = self.request.user
        queryset = user.notifications.unread()
        return Response(NotificationSerializer(queryset, many=True).data)


class NotificationReadView(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)

    def get(self, request, *args, **kwargs):
        notif = Notification.objects.get(id=kwargs['id'])
        notif.mark_as_read()
        return Response("ok", status=status.HTTP_200_OK)


class NotificationAllReadView(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)

    def get(self, request):
        user = self.request.user
        notifs = user.notifications.all()
        notifs.mark_all_as_read()
        data = {"read"}
        return Response("read", status=status.HTTP_200_OK)
