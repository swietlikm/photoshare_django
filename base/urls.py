from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllPostsListView.as_view(), name='index'),
    path('<str:username>', views.PostUserGridView.as_view(), name='post_user_grid'),
    path('profile', views.PostUserGridView.as_view(), name='user_profile'),
    path('profile/edit', views.UserProfileEditView.as_view(), name='user_profile_edit'),

    path('post/add/', views.PostAddView.as_view(), name='post_add'),
    path('post/<uuid:pk>/', views.PostDetailView.as_view(), name='post_details'),
    path('post/<uuid:pk>/update', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<uuid:pk>/delete', views.PostUpdateView.as_view(), name='post_delete'),

    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),

    path('explore/tags/<str:hashtag>', views.HashtagPostListView.as_view(), name='explore_tags'),
]