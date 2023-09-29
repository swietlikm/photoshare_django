from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllPostsListView.as_view(), name='index'),
    path('s/index', views.SearchView.as_view(), name='search'),

    path('<str:username>', views.PostUserGridView.as_view(), name='post_user_grid'),
    path('<str:username>/followers', views.UserFollowersView.as_view(), name='user_followers'),
    path('<str:username>/following', views.UserFollowingView.as_view(), name='user_following'),
    path('profile/edit', views.UserProfileEditView.as_view(), name='user_profile_edit'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),

    path('post/add/', views.PostAddView.as_view(), name='post_add'),
    path('post/<uuid:pk>/', views.PostDetailView.as_view(), name='post_details'),
    path('post/<uuid:pk>/likes', views.PostLikesView.as_view(), name='post_likes'),

    path('post/<uuid:pk>/update', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<uuid:pk>/delete', views.PostDeleteView.as_view(), name='post_delete'),

    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),

    path('explore/tags/<str:hashtag>', views.HashtagPostListView.as_view(), name='explore_hashtag'),
]