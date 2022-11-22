from django.urls import path
from .views import *

urlpatterns = [
    path('', NewsList.as_view(), name='homepage'),
    path('category/<int:category_id>/', CategoryNews.as_view(), name='cat'),
    path('tag/<int:tag_id>/', TagNews.as_view(), name='tag'),
    path('news/<int:pk>/', ViewNews.as_view(), name='view_news'),
    path('news/add_news/', CreateNews.as_view(), name='add_news'),
    path('search/', Search.as_view(), name='search'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('AdMailto/', admailto, name='AdMailto')
]
