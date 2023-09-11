from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, UpdateView, ListView

from .forms import CommentForm, UserProfileEditForm
from .models import Post, Comment, Follow, UserProfile


class HomePageView(TemplateView):
    template_name = 'post_list.html'

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()

        posts_data = []
        for post in posts:
            if hasattr(post.user, 'userprofile'):
                avatar = post.user.userprofile.avatar_image_url
            else:
                avatar = 'images/default_user_avatar.jpg'
            data = {
                'id': post.id,
                'image_url': post.image_url,
                'description': post.description,
                'user': post.user,
                'avatar_image': avatar,
                'total_likes': post.total_likes,
                'total_comments': post.total_comments,
                'created_at': post.created_at,
                'is_liked': True if post.likes.filter(id=self.request.user.id).exists() else False
            }
            posts_data.append(data)

        context = {
            'posts': posts_data,
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Like post
        post_like_id = request.POST.get("post_like_id")
        if post_like_id:
            post = Post.objects.get(id=post_like_id)
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
        return HttpResponseRedirect(request.path_info)


class PostAddView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['image', 'description']
    template_name = 'post_add.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['image', 'description']
    template_name = 'post_update.html'
    success_url = reverse_lazy('index')


class PostDetailView(TemplateView):
    template_name = 'post_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        uuid = kwargs.get('pk')
        post = get_object_or_404(Post, id=uuid)
        comments = Comment.objects.filter(post=post)
        context['post'] = post
        context['comments'] = comments
        context['form'] = CommentForm
        return context

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            comment = Comment(user=self.request.user, post=post, text=text)
            comment.save()
        redirect_url = reverse('post_details', kwargs={'pk': pk})
        return redirect(redirect_url)


class CommentUpdateView(UpdateView):
    template_name = 'comment_update.html'
    model = Comment
    fields = ['text']
    context_object_name = 'comment'

    def get_success_url(self):
        context = self.get_context_data()
        comment = context['comment']
        redirect_url = reverse('post_details', kwargs={'pk': str(comment.post.pk)})
        return redirect(redirect_url)


class PostUserGridView(ListView):
    template_name = 'post_user_grid.html'
    model = Post
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        queryset = queryset.filter(user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']
        context['posts_count'] = posts.count()

        f_post = posts.first()
        post_user = f_post.user
        context['post_user'] = f_post.user

        if hasattr(post_user, 'userprofile'):
            avatar = post_user.userprofile.avatar_image_url
        else:
            avatar = 'images/default_user_avatar.jpg'
        context['avatar_image'] = avatar

        followers = Follow.objects.filter(following=f_post.user).count()
        context['followers'] = followers

        following = Follow.objects.filter(follower=f_post.user).count()
        context['following'] = following

        if f_post.user != self.request.user:
            if Follow.objects.filter(follower=self.request.user, following=f_post.user).exists():
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


class HashtagPostListView(ListView):
    model = Post
    template_name = 'explore_tags_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        hashtag = self.kwargs['hashtag']
        return Post.objects.filter(description__contains=f'#{hashtag}')