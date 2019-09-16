from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Shout, Comment


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)
        # del self.fields['first_name', 'last_name']

    class Meta:
        model = CustomUser
        fields = ['username',]


class CustomUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        # del self.fields['first_name', 'last_name']

    class Meta:
        model = CustomUser
        fields = ['password','email','is_professional',]


class SignUpForm(SignupForm):
    template_name = 'signup.html'
    # is_professional = forms.BooleanField(label='Professional', required=False)

    class Meta:
        model = CustomUser

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(SignUpForm, self).save(request)
        #user.is_professional = self.cleaned_data['is_professional']
        user.save()
        return user


class ShoutsForm(forms.ModelForm):

    class Meta:
        model = Shout
        fields = ['title', 'body',]

        widgets = {
            'title':  forms.Textarea(attrs={
                'class':  'input',
                'placeholder':  'Why do you want to shout?',
                'required':  'True',
                'rows': 2
                }),

            'body':  forms.Textarea(attrs={
                'class':  'input',
                'placeholder':  'Your shout',
                'required':  'True',
                'rows':  10}),
        }


class ShoutsDeleteForm(forms.ModelForm):

    class Meta:
        model = Shout
        fields = ['deleted_at']
        widgets = {
            'deleted_at':  forms.HiddenInput()
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text',]

        widgets = {
            'text':  forms.Textarea(attrs={
                'class':  'input',
                'placeholder':  'Comment',
                'required':  'True',
                'rows':  5}),
        }


class CommentDeleteForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['deleted_at']
        widgets = {
            'deleted_at':  forms.HiddenInput()
        }
