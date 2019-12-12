"""
Views for application
"""
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import (
    render, redirect, get_object_or_404)
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import(
        CreateView, DetailView, ListView, RedirectView, 
        UpdateView, DeleteView, View, TemplateView)
from .forms import (
        CustomUserCreationForm, 
        ShoutsForm, ShoutsDeleteForm,
        CommentForm, CommentDeleteForm, 
        )
from .models import (
        Shout, CustomUser, Discussion, Comment)

import scipy.spatial
import numpy as np
import pickle


# Views related to Shouts - CreateView
class CreateShout(LoginRequiredMixin, CreateView):
    template_name = "master/shouts_form.html"
    form_class = ShoutsForm
    model = Shout

    def post(self, request, *args, **kwargs):
        form = ShoutsForm(request.POST)
        if form.is_valid():
            form.instance.date = timezone.now()
            form.instance.shouter = get_object_or_404(
                CustomUser, username=self.request.user)
            form.save()
            return redirect('master:shouts')
        else:
            pass


# Views related to Shouts - ListView
class AllShouts(ListView):
    template_name = "master/shouts.html"

    def get_queryset(self):
        queryset = Shout.objects.all().order_by('-date')
        return queryset


# Views related to Shouts - Detail View
class ShoutDetail(DetailView):
    template_name = 'master/shouts_detail.html'
    model = Shout

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shout = self.get_object()
        context['shouts'] = Shout.objects.get(id=shout.id)
        return context


# Views related to Shouts - Echo
class EchoList(ListView):
    template_name = 'master/echoed_shouts.html'
    model = Shout

    def get_object(self):
        obj = get_object_or_404(Shout, slug=self.kwargs.get("slug"))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shout = self.get_object()
        query_embedding = np.array(pickle.loads(shout.value)[0]).reshape(1, -1)
        corpus = Shout.objects.all().exclude(id=shout.id)
        corpus_embedding = np.zeros((len(corpus), query_embedding.shape[1]))
        context['shouts'] = []
        for i, each in enumerate(corpus):
            corpus_embedding[i] = np.array(pickle.loads(each.value)[0]).reshape(1, -1)
        distances = scipy.spatial.distance.cdist(
                query_embedding,
                corpus_embedding, 
                "cosine")[0]
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])
        for idx, distance in results[0:2]:
            context['shouts'].append(corpus[idx])
        return context


# Views related to Shouts - Edit View
class EditShout(LoginRequiredMixin, UpdateView):
    template_name = "master/shouts_form.html"
    form_class = ShoutsForm
    model = Shout
    success_url = reverse_lazy('master:shouts')


# Views related to Shouts - Delete View
class DeleteShout(LoginRequiredMixin, DeleteView):
    template_name = 'master/shouts_delete.html'
    model = Shout
    form_class = ShoutsDeleteForm
    success_url = reverse_lazy('master:shouts')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(DeleteShout, self).get_object()
        if not obj.shouter == self.request.user:
            raise Http404
        return obj 


# Views related to Shouts - Support View
class SupportShout(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        shout = get_object_or_404(Shout, slug=kwargs['slug'])
        user = self.request.user
        redirect_url = shout.get_absolute_url()
        if shout.supporters.count() < shout.threshold:
            if user not in shout.supporters.all():
                shout.supporters.add(user)
            else:
                shout.supporters.remove(user)
            return redirect_url
        elif shout.supporters.count() >= shout.threshold and user in shout.supporters.all():
            shout.supporters.remove(user)
            return redirect_url
        else:
            raise Http404


# Views related to user profile - User detail view
class UserDetail(DetailView):
    template_name = 'master/user_detail.html'
    slug_field = "username"
    slug_url_kwarg = "username"
    model = CustomUser

    def get_object(self):
        obj = get_object_or_404(CustomUser, username=self.kwargs.get("username"))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user'] = CustomUser.objects.get(id=user.id)
        context['shouts'] = Shout.objects.all().filter(shouter=user.id)\
                .exclude(deleted_at__isnull=False)
        return context


# Views related to Discussion - List View
class DiscussionDetail(ListView):
    """
    Details on Discussion
    """
    template_name = 'master/discussion.html'
    model = Discussion
        
    def get_object(self):
        obj = get_object_or_404(Shout, slug=self.kwargs.get("slug"))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shout = self.get_object()
        user = self.request.user
        if shout.supporters.count() >= shout.threshold or user.is_professional:
            context['shout'] = Shout.objects.get(id=shout.id)
            context['comments'] = Comment.objects.all().filter(commented_on=shout.id)
            context['user'] = user
            return context
        else:
            raise Http404


# Views related to Comments - Create View
class CreateComment(LoginRequiredMixin, CreateView):
    template_name = "master/comment_form.html"
    form_class = CommentForm
    model = Comment

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.date = timezone.now()
            form.instance.commented_by = get_object_or_404(
                CustomUser, username=self.request.user)
            print(form.instance.commented_by)
            shout = self.get_object()
            form.instance.commented_on = get_object_or_404(
                Shout, id=shout.id)
            form.save()
            return redirect('master:shout_discussion', slug=shout.slug)
        else:
            pass

    def get_object(self):
        obj = get_object_or_404(Shout, slug=self.kwargs.get("slug"))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shout = self.get_object()
        user = self.request.user
        context['shout'] = Shout.objects.get(id=shout.id)
        if shout.supporters.count() >= shout.threshold and (user in shout.supporters.all()
                or user.is_professional):
            return context
        else:
            raise Http404


# Views related to Comment - Delete View
class DeleteComment(LoginRequiredMixin, DeleteView):
    template_name = 'master/comment_delete.html'
    model = Comment
    form_class = CommentDeleteForm

    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('master:shout_discussion', kwargs={'slug': obj.commented_on.slug})

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = get_object_or_404(Comment, slug=self.kwargs.get("slug"))
        if not (obj.commented_by == self.request.user or self.request.user.is_professional):
            raise Http404
        return obj 


# Views related to User Settings
class UserSettings(ListView):
    template_name = 'master/user_settings.html'
    model = CustomUser
