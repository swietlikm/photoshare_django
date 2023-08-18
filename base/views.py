from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, CreateView, DetailView, UpdateView, ListView

from .forms import PostForm, CommentForm
from .models import Post, Comment


class HomePageView(TemplateView):
    template_name = 'post_list.html'

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        context = {
            'posts': posts
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Like post
        post_like_id = request.POST.get("post_like_id")
        print()
        liked = False
        if post_like_id:
            post = Post.objects.get(id=post_like_id)
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
                liked = False
            else:
                post.likes.add(request.user)
                liked = True
        return HttpResponseRedirect(request.path_info)


class PostAddView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['image', 'description']
    template_name = 'post_add.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']
        f_post = posts.first()
        context['post_user'] = f_post.user

        return context