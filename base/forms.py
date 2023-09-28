from django import forms

from .models import Post, Comment, UserProfile


class PostForm(forms.ModelForm):
    """
    A form for creating or updating a Post object.
    """
    class Meta:
        model = Post
        fields = ['image', 'description']
        widgets = {
          'description': forms.Textarea(attrs={'rows': 2, 'cols': 1}),
        }


class CommentForm(forms.ModelForm):
    """
    A form for creating or updating a Comment object.
    """
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
    """
    A form for editing user profile information, including avatar, first name, and last name.
    """
    class Meta:
        model = UserProfile
        fields = ['avatar']

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        """
        Initialize the UserProfileEditForm with initial values for first name and last name.
        """
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        """
        Save the UserProfileEditForm data, including updating the associated User object.
        """
        user_profile = super().save(commit=False)
        user = user_profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user_profile.save()
        return user_profile


CHOICES = [("user", "User"), ("hashtag", "Hashtag")]


class SearchForm(forms.Form):
    text = forms.CharField(required=True)
    choice = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, initial=CHOICES[0][0])