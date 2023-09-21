from django import forms
from django.contrib.auth.models import User

from .models import Post, Comment, UserProfile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'description']
        widgets = {
          'description': forms.Textarea(attrs={'rows': 2, 'cols': 1}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
          'text': forms.Textarea(attrs={'rows':2, 'cols':1}),
        }
        labels = {
            'text': 'Comment:'
        }


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user = user_profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user_profile.save()
        return user_profile
