from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('<str:username>', views.PostUserGridView.as_view(), name='post_user_grid'),

    path('post/add/', views.PostAddView.as_view(), name='post_add'),
    path('post/<uuid:pk>/', views.PostDetailView.as_view(), name='post_details'),

    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
]
