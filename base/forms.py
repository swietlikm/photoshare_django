from django import forms
from .models import Post, Comment


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