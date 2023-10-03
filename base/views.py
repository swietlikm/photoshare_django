from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Value, Count, CharField, F
from django.db.models.functions import Replace
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView, FormView, TemplateView
import re

from .forms import CommentForm, UserProfileEditForm, SearchForm
from .models import User, UserProfile, Hashtag, Post, Comment, Follow, Notification


class AllPostsListView(ListView):
    """View for displaying a list of all posts."""
    template_name = 'post_list.html'
    model = Post
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        posts = self.get_queryset()

        posts_data = []
        for post in posts:
            data = {
                'id': post.id,
                'image_url': post.image_url,
                'description': post.description,
                'user': post.user,
                'avatar_image': post.user.userprofile.avatar_url,
                'total_likes': post.total_likes,
                'total_comments': post.total_comments,
                'created_at': post.created_at,
                'is_liked': True if post.likes.filter(id=self.request.user.id).exists() else False
            }
            posts_data.append(data)

        context = {
            'posts': posts_data,
        }
        return context

    def post(self, request, *args, **kwargs):
        # Like post
        post_like_id = request.POST.get("post_like_id")
        if post_like_id and self.request.user.is_authenticated:
            post = Post.objects.get(id=post_like_id)
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
        elif post_like_id:
            return redirect(reverse('account_login'))
        return HttpResponseRedirect(request.path_info)


class AllPostsFollowedListView(LoginRequiredMixin, AllPostsListView):
    template_name = 'post_list_followed.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        followed_users = Follow.objects.filter(follower=self.request.user).values('following')
        followed_posts = queryset.filter(user__in=followed_users).distinct()
        return followed_posts


class PostAddView(LoginRequiredMixin, CreateView):
    """View for adding new posts."""
    template_name = 'post_add.html'
    model = Post
    fields = ['image', 'description']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating existing posts."""
    template_name = 'post_update.html'
    model = Post
    fields = ['image', 'description']
    success_url = reverse_lazy('index')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting posts."""
    template_name = 'post_delete.html'
    model = Post
    success_url = reverse_lazy('index')


class PostDetailView(AllPostsListView):
    """View for displaying the details of a specific post."""
    template_name = 'post_details.html'

    def get_queryset(self):
        uuid = self.kwargs.get('pk')
        queryset = Post.objects.filter(id=uuid)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        posts = context['posts']
        post = posts[0]
        context['post'] = post
        context['comments_enabled'] = True
        post_object = get_object_or_404(self.get_queryset())
        comments = Comment.objects.filter(post=post_object)
        context['comments'] = comments
        context['form'] = CommentForm
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        post = get_object_or_404(self.get_queryset())

        form = CommentForm(request.POST)
        if form.is_valid() and self.request.user.is_authenticated:
            text = form.cleaned_data['text']
            comment = Comment(user=self.request.user, post=post, text=text)
            comment.save()
            redirect_url = reverse('post_details', kwargs={'pk': str(pk)})
            return redirect(redirect_url)
        elif form.is_valid() and not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('account_login'))
        return super().post(request, *args, **kwargs)


class CommentUpdateView(UpdateView):
    """View for updating comments."""
    template_name = 'comment_update.html'
    model = Comment
    fields = ['text']

    def get_success_url(self):
        comment = self.get_object()
        redirect_url = reverse('post_details', kwargs={'pk': str(comment.post.pk)})
        return redirect_url


class CommentDeleteView(DeleteView):
    """View for deleting comments."""
    template_name = 'comment_delete.html'
    model = Comment

    def get_success_url(self):
        comment = self.get_object()
        redirect_url = reverse('post_details', kwargs={'pk': str(comment.post.pk)})
        return redirect_url


class PostUserGridView(ListView):
    """View for displaying posts of a specific user."""
    template_name = 'post_user_grid.html'

    def get_queryset(self):
        username = self.kwargs.get('username')
        queryset = get_object_or_404(User, username=username)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_owner = self.get_queryset()
        posts = Post.objects.filter(user=profile_owner)
        context['posts'] = posts
        context['posts_count'] = posts.count()
        context['profile_owner'] = profile_owner

        avatar = profile_owner.userprofile.avatar_url
        context['avatar'] = avatar

        followers = Follow.objects.filter(following=profile_owner).count()
        context['followers'] = followers

        following = Follow.objects.filter(follower=profile_owner).count()
        context['following'] = following

        if profile_owner != self.request.user:
            if Follow.objects.filter(follower=self.request.user, following=profile_owner).exists():
                context['is_followed'] = True

        return context

    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        followed_user = get_object_or_404(User, username=username)
        relation = Follow.objects.filter(follower=self.request.user, following=followed_user)
        if relation.exists():
            relation.delete()
        else:
            follow = Follow(follower=self.request.user, following=followed_user)
            follow.save()
        redirect_url = reverse('post_user_grid', kwargs={'username': username})
        return redirect(redirect_url)


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """View for editing user profiles."""
    model = UserProfile
    template_name = 'user_profile_edit.html'
    form_class = UserProfileEditForm
    success_url = reverse_lazy('user_profile_edit')

    def get_object(self, queryset=None):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return user_profile

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class HashtagPostListView(AllPostsListView):
    """View for displaying posts with a specific hashtag."""
    template_name = 'explore_tags_list.html'

    def get_queryset(self):
        hashtag = self.kwargs['hashtag']
        return Post.objects.filter(hashtags__name=f'{hashtag}')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['hashtag'] = self.kwargs['hashtag']
        context['hashtag_count'] = self.get_queryset().count()
        return context


class PostLikesView(DetailView):
    """View for displaying likes on a post."""
    template_name = 'post_likes.html'
    model = Post
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.likes_users = obj.likes.all()
        return obj


class UserFollowersView(ListView):
    """View for displaying a user's followers."""
    template_name = 'users_listing.html'
    context_object_name = 'followers'
    extra_context = {'action': 'followers'}

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        queryset = Follow.objects.filter(following=user).select_related('follower')
        follower_users = [user.follower for user in queryset]
        return follower_users

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['username'] = self.kwargs['username']
        return context


class UserFollowingView(UserFollowersView):
    """View for displaying users that a user is following."""
    extra_context = {'action': 'following'}

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        queryset = Follow.objects.filter(follower=user).select_related('following')
        follower_users = [user.following for user in queryset]
        return follower_users


class SearchView(FormView):
    template_name = 'search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = self.get_form_class()

        text = request.GET.get('text')
        choice = request.GET.get('choice')

        form = form(request.GET) if request.GET else form()

        if form.is_valid():
            context['search_performed'] = True

            if choice == 'user':
                users_result = User.objects.filter(
                    Q(username__istartswith=text) |
                    Q(username__icontains=text)
                )
                context['users_result'] = users_result
                context['match'] = users_result.exists()

            elif choice == 'hashtag':
                hashtags_result = Hashtag.objects.filter(name__icontains=f'{text}')
                context['hashtags_result'] = hashtags_result
                context['match'] = hashtags_result.exists()

        context['form'] = form
        return self.render_to_response(context)


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = 'notifications_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient_user=self.request.user).select_related('action_user')
        return queryset

    def post(self, request, *args, **kwargs):
        notification_read_id = request.POST.get('notification_read_id')
        mark_all_as_read = request.POST.get('mark_all_as_read')

        if notification_read_id:
            notification = Notification.objects.get(id=notification_read_id)
            notification.is_read = not notification.is_read
            notification.save()

        if mark_all_as_read:
            unread_notifications = Notification.objects.filter(recipient_user=self.request.user, is_read=False)
            unread_notifications.update(is_read=True)

        return HttpResponseRedirect(reverse_lazy('notifications'))

